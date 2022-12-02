# -*- coding: utf-8 -*-

"""
# DATE : 22.10.17
# AUTH : JW
# NOTE : Flask Server Main
"""
import sys
import os

from flask import Flask, session, redirect, url_for, escape, request, json, jsonify

from threading import Thread
from threading import Timer

import pystray
from pystray import MenuItem
from PIL import Image

import common_process
import common_func

app = Flask(__name__)

# TODO (운영/개발 전환) config 파일 위는 개발시, 아래는 운영시 path
ini_config = common_func.conn_ini_func(os.path.dirname(os.path.realpath(__file__)) + "\\resources\\drxsolution.ini").read_ini_file()
# ini_config = common_func.conn_ini_func("C:\\DRxSolutionModule\\resources\\drxsolution.ini").read_ini_file()

global start_switch    # 실행버튼 중복 방지를 위한 스위치
start_switch = False

if(type(ini_config) == str and str(ini_config) == 'INI_READ_ERROR'):
    print("### (INI_PARSE_ERROR) INI 파일 로드에 실패하였습니다.")

flask_thread_kwargs_run = { 'host': str(ini_config['DRXS']['vpn-ip']), 'port': int(ini_config['DRXS']['vpn-port']), 'threaded': True, 'use_reloader': False, 'debug': False}
flask_thread_kwargs_dev = { 'host': str(ini_config['DRXS']['vpn-ip']), 'port': int(ini_config['DRXS']['vpn-port']), 'threaded': True, 'use_reloader': True, 'debug': True}

@app.route("/trans_qr_data", methods=["POST"])
def trans_qr_data():
    """
    내손안의약국 으로부터 QR 및 개인정보 데이터를 전달받아 처방등록을 진행하는 프로세스
    :return:
    """
    try:
        post_datas = json.loads(request.get_data())
        print("출력 post_datas : ", post_datas)
        print("출력 post_datas : ", post_datas['qr-num'])
        print("출력 post_datas : ", post_datas['pharmacy-idx'])

        # 주민번호 자체 복호화 및 심평원 암호화 처리
        dec_jmno_str = common_process.common_process().proc_pip_decrypt(post_datas["license-str"])
        # print("##### 복호화 된 주민번호 : ", dec_jmno_str)

        # QR 데이터 복호화

        # TODO 221129 : 약국의 신규/기존회원에 관계없이 QR데이터 처리를 해야하는가?

        return "SUCCESS"
    except Exception as e:
        print("##### (error) trans_qr_data :: ", e)
        # TODO 221128 : 에러 전송 처리 필요

@app.route("/jmno_auth_check", methods=["POST"])
def jmno_auth_check():
    """
    내손안의약국으로부터 회원정보를 전달받고 해당 약국에 회원정보가 존재하는지 확인
    :return: 리턴결과 json
    """
    post_result = json.loads(request.get_data())
    print("출력 post_result : ", post_result)
    print("출력 : ", post_result["drxs"])

    # json 데이터 수집
    enc_datas = post_result["drxs"]

    # POST 수신 데이터 json 'drxs' 데이터 복호화 처리
    dec_send_data = common_process.common_process().proc_pip_decrypt(enc_datas)

    # 암호화 전송 데이터 string to json 화 처리
    send_data_json = json.loads(dec_send_data)



    # 전송 데이터 체크 (이거 아님.. 받은 데이터 체크할 필요없음)
    # parse_result_type, parse_result_code = common_process.common_process().proc_receive_data_check(send_data_json)
    # print("##### (전송데이터 체크 결과) {} {}".format(parse_result_type, parse_result_code))

    ## 주민번호 복호화
    dec_jmno_str = common_process.common_process().proc_pip_decrypt(send_data_json["member-jumin"])
    # print("##### 복호화 된 주민번호 : ", dec_jmno_str)

    if len(dec_jmno_str) != 13:
        print("##### (주민번호자릿수오류) :: 전달받은 주민번호가 13자리가 아닙니다.")
        err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW104')
        print("(ERROR) 최종 리턴데이터 :: {}".format(err_send_data))
        return err_send_data

    # 평문 주민번호 심평원 DLL 암호화 처리
    enc_jmno_data = common_process.common_process().proc_jmno_encrypt(dec_jmno_str)

    ## TODO : DB Connection 초기화 (sqlAlchemy 와 비교 및 교체 필요함)
    conn_db = common_func.conn_db_func(str(ini_config['DRXS']['server-ip']))
    connection_info = conn_db.openDB()

    if type(connection_info) == str and str(connection_info) == 'DB_CONN_ERROR':
        print("##### (openDB ERROR) :: DB 커넥션 오류")
        err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW100')
        print("(ERROR) 최종 리턴데이터 :: {}".format(err_send_data))
        return err_send_data

    # 암호화 주민번호 대상 회원 존재 여부 쿼리 스트링 생성
    print("##### enc_jmno_data decode before :: ", enc_jmno_data)
    jmno_auth_check_query = common_process.common_process().create_jmno_auth_query_func(send_data_json["member-name"], enc_jmno_data.decode('utf-8'))

    ## 암호화 주민번호 MS-SQL DB 비교 (주민번호비교는 한명일 수 밖에 없을 듯 리스트로 안나올듯)
    query_result_dict = conn_db.sendQuery(jmno_auth_check_query)
    conn_db.closeDB()
    ##########################################################
    # 주민번호 조회 쿼리 오류가 발생한 경우
    if type(query_result_dict) is str and query_result_dict == 'DB_SEND_QUERY_ERROR':
        err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW100')
        print("(ERROR) 최종 리턴데이터 :: {}".format(err_send_data))
        return err_send_data
    ##########################################################
    # 주민번호에 해당하는 회원 정보가 존재하지 않을 경우 회원정보 없음 리턴처리 (비회원)
    if len(query_result_dict['CusNo']) == 0 and len(query_result_dict['CusNm']) == 0:
        err_send_data = common_process.common_process().proc_error_return_func('FAILED', '', 'BSW109')
        print("(FAILED-query_result_dict) 최종 리턴데이터 :: {}".format(err_send_data))
        return err_send_data

    ##########################################################
    # 주민번호가 존재하는 회원정보가 존재할 경우 (회원)
    else:
        # 주민번호가 존재하는 회원의 정보에 CI 등 인증 정보를 약국DB에 업데이트 처리
        auth_user_data_param = dict(send_data_json, **query_result_dict)    # dict + dict merge

        # 회원정보가 DrxsCustomerAuth 에 존재하는지 조회
        conn_db.openDB()
        query_result_select_dict = conn_db.sendQuery(common_process.common_process().select_drxscustomerauth_info_query(str(auth_user_data_param['CusNo'][0])))
        conn_db.closeDB()
        if type(query_result_select_dict) is str and query_result_select_dict == 'DB_SEND_QUERY_ERROR':
            err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW100')
            print("(ERROR-query_result_select_dict) 최종 리턴데이터 :: {}".format(err_send_data))
            return err_send_data

        # print("query_result_select_dict :: ", query_result_select_dict)
        # print("query_result_select_dict len :: ", len(query_result_select_dict))
        # print("query_result_select_dict len2 :: ", len(query_result_select_dict['CusNo']))

        # 회원정보 미 존재시 DrxsCustomerAuth CI 및 인증정보 INSERT
        if len(query_result_select_dict['CusNo']) == 0:
            conn_db.openDB()
            query_result_insert_user_ci = conn_db.send_query_update(common_process.common_process().insert_jmno_user_info_query_func(auth_user_data_param))
            conn_db.closeDB()
            if type(query_result_insert_user_ci) is str and query_result_insert_user_ci == 'DB_SEND_QUERY_ERROR':
                err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW100')
                print("(ERROR-query_result_insert_user_ci) 최종 리턴데이터 :: {}".format(err_send_data))
                return err_send_data

            # print("##### (query_result_insert_user_ci) :: ", query_result_insert_user_ci)
            # print("##### (query_result_insert_user_ci.len) :: ", len(query_result_insert_user_ci))

        # 회원정보 존재시 DrxsCustomerAuth CI 및 인증정보 UPDATE
        elif len(query_result_select_dict['CusNo']) == 1:
            conn_db.openDB()
            query_result_update_user_ci = conn_db.send_query_update(common_process.common_process().update_jmno_user_info_query_func(auth_user_data_param))
            conn_db.closeDB()
            if type(query_result_update_user_ci) is str and query_result_update_user_ci == 'DB_SEND_QUERY_ERROR':
                err_send_data = common_process.common_process().proc_error_return_func('ERROR', '', 'BSW100')
                print("(ERROR-query_result_update_user_ci) 최종 리턴데이터 :: {}".format(err_send_data))
                return err_send_data
            # print("##### (update_jmno_user_info_query_func) result :: ", query_result_update_user_ci)
            # print("##### (query_result_update_dict.len) :: ", len(query_result_update_user_ci))

        # # 쿼리 오류 체크(오류 코드 리턴)
        # if type(query_result_dict) is str and query_result_dict == 'DB_SEND_QUERY_ERROR':
        #     res_dict = common_process.common_process().proc_return_json_func('ERROR', '', 'BSW100')
        #     res_dict['res_data'] = ''  # 오류상태값 보낼 때 별도로 res_data 공백으로 전송
        #
        #     err_data_json = json.dumps(res_dict)
        #
        #     # json 암호화
        #     enc_err_data = common_process.common_process().proc_pip_encrypt(err_data_json)
        #
        #     # drxs : 암호 로 dict 포장 후 json 처리 및 리턴
        #     err_send_data = common_process.common_process().proc_packing_drxs(enc_err_data)
        #     print("##### (ERROR-DB) 최종 리턴 정보 :: ", err_send_data)
        #     return err_send_data

        # (회원인증성공) 결과 데이터 리턴 작업
        res_dict = common_process.common_process().proc_return_json_func('SUCCESS', '', '')
        res_dict['res_data'] = ''

        success_data_json = json.dumps(res_dict)
        enc_success_data = common_process.common_process().proc_pip_encrypt(success_data_json)

        # drxs : 암호 로 dict 포장 후 json 처리 및 리턴
        success_send_data = common_process.common_process().proc_packing_drxs(enc_success_data)
        print("##### (SUCCESS-회원정보인증완료) 최종 리턴 정보 :: ", success_send_data)
        return success_send_data

def flask_thread_exit():
    """
    트레이 메뉴의 종료버튼 클릭
    :return:
    """
    global start_switch
    print("## 종료 버튼 클릭(start_switch) :: ", start_switch)
    if start_switch:
        start_switch = False
        tray_icon.stop()
        sys.exit()

def flask_thread_init():
    """
    트레이 메뉴의 시작버튼 클릭
    :return:
    """
    global start_switch
    print("## 시작 버튼 클릭(start_switch) :: ", start_switch)
    if not start_switch:
        start_switch = True
        t1 = Thread(target=app.run, kwargs=flask_thread_kwargs_run)
        t1.daemon = True
        t1.start()

# TODO : 이미지 경로를 pyinstaller 로 패키징 시 안나올 수 있음 별도 바깥의 리소스 폴더로 지정해야할지도..
# tray_ico_image = Image.open(os.path.dirname(os.path.realpath(__file__))+"\\img\\image_16_48.ico")
tray_ico_image = Image.open(os.getcwd() + os.path.sep + "img\\image_16_48.ico")
tray_menu = (MenuItem('서버시작', flask_thread_init), MenuItem('프로그램종료', flask_thread_exit))
tray_icon = pystray.Icon("내손안의약국", tray_ico_image, "내손안의약국 회원인증모듈", tray_menu)

if __name__ == "__main__":

    # 모듈 실행전 필수체크 사항
    # 1. ErpCusJmno 폴더 경로 (설치경로)를 환경변수 path에 추가했는지 체크 후 처리
    env = os.environ
    print("현재 환경변수 목록 :: ", str(env['PATH']))
    if str(env['PATH']).find('ErpCusJmno') == -1:
        print("## 환경변수 path에 dll 경로를 추가합니다 :: ", os.getcwd() + os.path.sep + "ErpCusJmno")
        add_path = os.getcwd() + os.path.sep + "ErpCusJmno;"+env['PATH']
        print("## add_path :: ", add_path)
        env['PATH'] = add_path
        print("환경변수 추가 완료 :: ", env['PATH'])

    if str(ini_config['DRXS']['debug']) == 'True':
        print("### 디버그 모드로 프로세스 실행합니다. ###")
        app.run(host=str(ini_config['DRXS']['vpn-ip']), port=int(ini_config['DRXS']['vpn-port']), debug=str(ini_config['DRXS']['debug']))
    elif str(ini_config['DRXS']['debug']) == 'False':
        # 운영모드에서는 트레이아이콘 스레드를 먼저 실행 시킨 뒤, 서버모듈 스레드 동작하도록!! ini파일의 debug 항목을 False로 전환
        print("### 운영 모드로 프로세스 실행합니다. ###")
        Timer(3, flask_thread_init).start()
        tray_icon.run()  # pystray 트레이 아이콘 실행
    else:
        print("### 디버그 모드로 프로세스 실행합니다. ###")
        app.run(host=str(ini_config['DRXS']['vpn-ip']), port=int(ini_config['DRXS']['vpn-port']), debug=str(ini_config['DRXS']['debug']))

