# -*- coding: utf-8 -*-
"""
# TITLE : 공통 프로세스 작업 클래스
# DATE : 2022.10.13
# AUTH : JW
"""
import json

import common_crypt_leedm
import time
import hashlib
import common_jmno2

class common_process:

    def __init__(self):
        pass

    def proc_check_environ_path(self):
        """
        환경변수 path에 심평원 암호화 dll 경로를 추가한다.
        :return:
        """
        try:
            pass
        except Exception as e:
            print('##### (proc_jmno_encrypt) Error : ', e)
            return 'ERROR_ENV_PATH'
        else:
            return "SUCCESS"


    def proc_jmno_encrypt(self, plain_text):
        """
        주민번호 평문을 심평원 DLL을 이용하여 암호화 처리한다.
        :return: encrypt byte
        """
        try:
            print("##### (proc_jmno_encrypt) 심평원 DLL 암호화 처리중..")
            enc_jmmo = common_jmno2.common_jmno().encrypt_with_jmno(plain_text)
        except Exception as e:
            print('##### (proc_jmno_encrypt) Error : ', e)
            return 'ERROR_SIM_ENCRYPT'
        else:
            return enc_jmmo

    def proc_pip_encrypt(self, plain_json_text):
        """
        내손안의약국으로 전달할 json 데이터 str을 내부 암호화 후 리턴한다.
        :param plain_json_text:
        :return:
        """
        try:
            print('##### 자체 암호화 평문 ::', plain_json_text)
            milliseconds = str(int(time.time() * 1000))
            # prefix = hashlib.shake_128(milliseconds.encode()).digest(16)
            prefix = hashlib.md5(milliseconds.encode()).digest()
            aseEncryptedBytes = common_crypt_leedm.AESCipher256().encrypt(prefix + plain_json_text.encode())
            customEncryptedText = common_crypt_leedm.CustomCipher().encryptBytes(aseEncryptedBytes)
            print('##### 자체 암호화 결과 ::', customEncryptedText)
        except Exception as e:
            print('##### (proc_pip_encrypt) Error : ', e)
            return 'ERROR_PIP_ENCRYPT'
        else:
            return customEncryptedText

    def proc_pip_decrypt(self, enc_datas):
        """
        내손안의약국에서 전달받은 json 데이터를 내부 복호화하여 리턴한다.
        :param dec_text:
        :return: 복호화 결과 str
        """
        try:
            milliseconds = str(int(time.time() * 1000))
            prefix = hashlib.md5(milliseconds.encode()).digest()

            customDecryptedBytes = common_crypt_leedm.CustomCipher().decrypt(enc_datas)
            print("##### 자체 복호화 결과 :: ", customDecryptedBytes, len(customDecryptedBytes))

            aseDecryptedBytes = common_crypt_leedm.AESCipher256().decrypt(customDecryptedBytes)
            dec_data = aseDecryptedBytes[len(prefix):].decode()
            print('##### 최종 복호화 결과:', dec_data)
            print('##### 최종 복호화 결과 type :', type(dec_data))
        except Exception as e:
            print('##### (proc_pip_decrypt) Error : ', e)
            return 'ERROR_PIP_DECRYPT'
        else:
            return dec_data

    def create_jmno_auth_query_func(self, user_name, jmno_data):
        """
        암호화 주민번호 회원정보 존재 여부 쿼리 생성
        :param user_name: 회원명
        :param jmno_data: 회원주민번호(암호화)
        :return: 쿼리 str 전달
        """
        try:
            print("##### (proc_jmno_auth_query_func) 회원정보존재여부확인 쿼리생성 :: ", jmno_data)
            print("##### (proc_jmno_auth_query_func) 기준 회원명 : ", user_name)
            print("##### (proc_jmno_auth_query_func) 기준 주민번호 : ", jmno_data)
            userInfoQuery = []
            userInfoQuery.append("SELECT")
            userInfoQuery.append("CusNo")
            userInfoQuery.append(", FamNo")
            userInfoQuery.append(", CusNm")
            userInfoQuery.append(", CusJmno")
            userInfoQuery.append(", RealBirth")
            userInfoQuery.append(", Sex")
            userInfoQuery.append(", HpTel")
            userInfoQuery.append(", CertiNo")
            userInfoQuery.append("FROM dbo.PatientCustomers")
            userInfoQuery.append("WHERE 1=1")
            userInfoQuery.append("AND CusNm = '" + str(user_name) + "'")
            userInfoQuery.append("AND CusJmno = '" + str(jmno_data) + "'")
            userInfoQueryStr = " ".join(userInfoQuery)
            print("##### (proc_jmno_auth_query_func) 쿼리 :: \n{}".format(userInfoQueryStr))
        except Exception as e:
            print('##### (proc_jmno_auth_query_func) Error : ', e)
            # return 'ERROR_CREATE_JMNO_STR'
            return 'BSW100'     # 내부 쿼리 오류 코드
        else:
            return userInfoQueryStr
        
    def update_jmno_user_info_query_func(self, user_data):
        """
        주민번호 일치 회원의 CI 및 개인정보 업데이트 쿼리 생성
        :param user_data: 사용자정보 dict
        :return: 쿼리 str 전달
        """
        try:
            print("##### (update_jmno_user_info_query_func) 주민번호 일치 회원의 CI 및 개인정보 업데이트 쿼리 생성")
            print("##### (update_jmno_user_info_query_func) 회원정보 : ", user_data)
            print("##### (update_jmno_user_info_query_func) 회원정보type : ", type(user_data))

            print("##### user_data[member-sms-ci]", user_data["member-sms-ci"])
            print("##### user_data[CusNo]", user_data["CusNo"][0])

            userInfoQuery = []
            userInfoQuery.append("UPDATE dbo.DrxsCustomersAuth ")
            userInfoQuery.append("SET ")
            userInfoQuery.append("CusNo  = '" + user_data["CusNo"][0] + "'")
            userInfoQuery.append(", UserId = '" + user_data["member-idx"] + "'")
            # userInfoQuery.append(", UserId = '9999'")
            userInfoQuery.append(", UserSmsCi = '" + user_data["member-sms-ci"] + "'")
            userInfoQuery.append(", UserSmsCiDte = GETDATE() ")
            # userInfoQuery.append(", PharmAuthAutoDte = GETDATE()")    # 약사 자동승인 주석처리
            userInfoQuery.append("WHERE 1=1 ")
            userInfoQuery.append("AND CusNo = '" + user_data["CusNo"][0] + "'")
            userInfoQueryStr = "".join(userInfoQuery)

            print("##### (update_jmno_user_info_query_func) 쿼리 :: \n{}".format(userInfoQueryStr))
        except Exception as e:
            print('##### (update_jmno_user_info_query_func) Error : ', e)
            # return 'ERROR_CREATE_JMNO_STR'
            return 'BSW100'     # 내부 쿼리 오류 코드
        else:
            return userInfoQueryStr

    def insert_jmno_user_info_query_func(self, user_data):
        """
        주민번호 일치 회원의 CI 및 개인정보 insert 쿼리 생성
        :param user_data: 사용자정보 dict
        :return: 쿼리 str 전달
        """
        try:
            print("##### (insert_jmno_user_info_query_func) 주민번호 일치 회원의 CI 및 개인정보 INSERT 쿼리 생성")
            print("##### (insert_jmno_user_info_query_func) 회원정보 : ", user_data)
            print("##### (insert_jmno_user_info_query_func) 회원정보type : ", type(user_data))

            print("##### user_data[member-sms-ci]", user_data["member-sms-ci"])
            print("##### user_data[CusNo]", user_data["CusNo"][0])

            # count = self.cursor.execute("""INSERT INTO dbo.DrxsCustomersAuth (CusNo, UserId, CustomerAuthFlag, PharmAuthFlag, CustomerAuthDte) VALUES (?,?,?,'N',GETDATE())""",dataArray[0], dataArray[1], dataArray[2])
            # self.conn.commit()

            userInfoQuery = []
            userInfoQuery.append("INSERT INTO dbo.DrxsCustomersAuth")
            userInfoQuery.append("(CusNo, UserId, CustomerAuthFlag, PharmAuthFlag, CustomerAuthDte, UserSmsCi, UserSmsCiDte, PharmAuthAutoDte, PharmAuthDte) ")
            userInfoQuery.append("VALUES('"+user_data['CusNo'][0]+"','"+user_data['member-idx']+"','Y','Y',GETDATE(),'"+user_data['member-sms-ci']+"',GETDATE(),GETDATE(),GETDATE())")
            userInfoQueryStr = "".join(userInfoQuery)
            print("##### (insert_jmno_user_info_query_func) 쿼리 :: \n{}".format(userInfoQueryStr))
        except Exception as e:
            print('##### (insert_jmno_user_info_query_func) Error : ', e)
            print(e)
            # return 'ERROR_CREATE_JMNO_STR'
            return 'BSW100'     # 내부 쿼리 오류 코드
        else:
            return userInfoQueryStr

    def select_drxscustomerauth_info_query(self, cusNo):
        """
        회원 인증정보 DB 조회 쿼리 생성
        :return:
        """
        try:
            print('##### (select_drxscustomerauth_info_query) 회원 인증정보 조회 쿼리 생성')
            tempQuery = []
            tempQuery.append('SELECT CusNo, PharmAuthFlag, CustomerAuthFlag FROM dbo.DrxsCustomersAuth')
            tempQuery.append("WHERE CusNo = '" + cusNo + "'")
            sendSql = " ".join(tempQuery)
            print('##### (select_drxscustomerauth_info_query) 쿼리 :: ', sendSql)
        except Exception as e:
            print('##### (select_drxscustomerauth_info_query) Error : ', e)
            # return 'ERROR_CREATE_JMNO_STR'
            return 'BSW100'  # 내부 쿼리 오류 코드
        else:
            return sendSql

    def proc_receive_data_check(self, recv_data_json):
        """
        전송된 데이터의 실패 또는 에러체크
        :param recv_data_json: 전송된 데이터
        :return: 리턴코드 및 에러코드 (성공시 에러코드는 공백)
        """
        try:
            # ERROR 상태 체크
            # if recv_data_json['member-idx'] == '':
            #     print("##### BSW100 : 내부 쿼리가 오류인 경우 (result : ERROR)")
            #     return "ERROR", "BSW100"
            # elif recv_data_json['member-idx'] == '':
            #     print("##### BSW101 : 기타 (result : ERROR)")
            #     return "ERROR", "BSW101"

            # FAILED 상태 체크
            if recv_data_json['member-idx'] == '':
                print("##### BSW102 : 회원 고유키값 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW102"
            elif recv_data_json['member-name'] == '':
                print("##### BSW103 : 회원 이름 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW103"
            elif recv_data_json['member-jumin'] == '':
                print("##### BSW104 : 회원 주민번호(암호화된) 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW104"
            elif recv_data_json['member-mobile'] == '':
                print("##### BSW105 : 회원 휴대폰번호 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW105"
            elif recv_data_json['member-email'] == '':
                print("##### BSW106 : 회원 이메일 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW106"
            elif recv_data_json['member-sms-ci'] == '':
                print("##### BSW107 : 회원 SMS CI 전송 데이터가 없는 경우 (result : FAILED)")
                return "FAILED", "BSW107"
            # elif recv_data_json['member-idx'] == '':
            #     print("##### BSW108 : 기타 (result : FAILED)")
            #     return "FAILED", "BSW108"

        except Exception as e:
            return "ERROR"
        else:
            print("##### (전달받은 데이터 정합성체크) SUCCESS")
            return "SUCCESS", ""

    def proc_return_json_func(self, result_code, res_data, err_code):
        """
        리턴용 json 데이터 설정
        :param result_code: SUCCESS, FAILED, ERROR
        :param res_data:
        :param err_code:
            # 사용
            BSW100 : 내부 쿼리가 오류인 경우 (result : ERROR)
            BSW101 : 기타 (result : ERROR)

            # 사용
            BSW109 : 약국DB내 해당 회원 정보가 존재하지 않음. (result : FAILED)

            # 보류
            # BSW102 : 회원 고유키값 전송 데이터가 없는 경우 (result : FAILED)
            # BSW103 : 회원 이름 전송 데이터가 없는 경우 (result : FAILED)
            # BSW104 : 회원 주민번호(암호화된) 전송 데이터가 없는 경우 (result : FAILED)
            # BSW105 : 회원 휴대폰번호 전송 데이터가 없는 경우 (result : FAILED)
            # BSW106 : 회원 이메일 전송 데이터가 없는 경우 (result : FAILED)
            # BSW107 : 회원 SMS CI 전송 데이터가 없는 경우 (result : FAILED)
            # BSW108 : 기타 (result : FAILED)
        :return: dict 데이터 리턴
        """
        try:
            info_dict = dict()
            info_dict['result'] = result_code
            info_dict['res_data'] = res_data
            info_dict['err_code'] = err_code
        except Exception as e:
            print('##### (proc_jmno_auth_query_func) Error : ', e)
            return 'ERROR_CREATE_RETURN_JSON'
        else:
            return info_dict

    def proc_packing_drxs(self, packing_enc_data):
        """
        최종 전달할 암호데이터를 {"drxs":"암호문"} JSON 형태로 패킹 후 리턴한다.
        :param packing_enc_data: 전송할 암호문 스트링
        :return: 패킹결과 json
        """
        try:
            pack_dict = dict()
            pack_dict['drxs'] = packing_enc_data
        except Exception as e:
            print('##### (proc_packing_drxs) Error : ', e)
            return 'ERROR_JSON_PACKING'
        else:
            return json.dumps(pack_dict)

    def proc_error_return_func(self, type, content, err_code):
        """
        DB 오류로 인하여 에러 리턴시 데이터 생성 험수
        :return:
        """
        try:
            print("##### (오류) 리턴데이터 생성")
            print("## TYPE : {}\n## CONTENT : {}\n##ERR_CODE : {}".format(type, content, err_code))
            print("##########################")

            res_dict = dict()
            res_dict = self.proc_return_json_func(type, content, err_code)
            err_data_json = json.dumps(res_dict)

            enc_err_data = self.proc_pip_encrypt(err_data_json)
            err_send_data = self.proc_packing_drxs(enc_err_data)


        except Exception as e:
            print('##### (proc_error_return_func) Error : ', e)
            return 'ERROR_RETURN_PACKING'
        else:
            return err_send_data

    # def proc_default_func(self):
    #     """
    #     디폴트함수 템플릿
    #     :return:
    #     """
    #     try:
    #         pass
    #     except Exception as e:
    #         pass
    #     else:
    #         pass