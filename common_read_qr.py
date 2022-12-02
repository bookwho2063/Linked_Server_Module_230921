# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
# TITLE : 처방전 2D QR 복호화 처리
# DATE : 2022.11.28
# AUTH : JW
"""
import ctypes
import traceback
from ctypes import *
from ctypes.wintypes import *  # 자료형 모음
import os.path
import sys
import os

from chardet import detect

class Custom_Qr_Cipher:
    """
    # 각 업체별 종이 처방전 QR 복호화 클래스
    """
    def __init__(self, organ_number):
        self.organ_number = organ_number        # 약국 요양기관기호

    def qr_corp_parse(self, org_qr_msg):
        """
        QR 문장 업체 정보 파싱 (QR을 파싱하여 크레소티/이디비/유비케어 중 리턴)
        :param decode_qr_msg:
        :return:
        """
        try:
            pass
        except Exception as e:
            print("##### (error) qr_corp_parse :: ", e)
            print(e)
        else:
            pass

    def decode_qr_cre(self, biz_number, decode_qr_msg):
        """
        크레소티 암호화 QR 복호화 처리
            cresoty_qr 폴더 내 dll 사용
            LibQRHandle.dll : QR 데이터 복호화 인터페이스
            IRQR.dll : 필수 라이브러리
            ../QRCodeLog 폴더 : 라이브러리 작업 로그 생성 폴더
            위드팜 업체코드 : SD0056
        :param biz_number: 약국 사업자 번호
        :param decode_qr_msg: 암호화 QR 데이터
        :return: 복호화 된 평문 데이터
        """
        try:
            cresoty_dll_name = "LibQRHandle.dll"
            cresoty_dll_path = os.getcwd() + os.path.sep + "cresoty_qr" + os.path.sep + cresoty_dll_name
            print("# 크레소티 QR DLL 정보 :: {}".format(cresoty_dll_path))

            cresoty_lib = CDLL(cresoty_dll_path)
            # cresoty_lib = WinDLL(cresoty_dll_path)
            # cresoty_lib = WinDLL(CDLL(cresoty_dll_path))

            # TEST INFO
            # biz_number = "2"
            biz_number = "2018182695"
            p_biz_number = c_char_p(biz_number.encode())
            # p_biz_number = c_wchar_p(biz_number)
            # p_biz_number = c_char_p(biz_number)

            # corp_code = "S"
            corp_code = "SD0174"
            p_corp_code = c_char_p(corp_code.encode())
            # p_corp_code = c_wchar_p(corp_code)
            # p_corp_code = c_char_p(corp_code)

            decode_qr_msg = "CRESA09/N$1GVLGAHS6GR1I2F4KW:8$1SX.*LV-ZB6ERTZ1LXTFHQN+IAFN3VQPCR9.VG*FG+EN90W*H13VI8JM0W$4NTDWHNAG$2AAMY$B.RMZVS46FZ-74Q0XVB.KXT9*WOF6KJOF46K+381Z1C3TF2N065S$ZB.25$QETN1CP55JSWUVNWWEJ.*W4XS62FJP1K00LX0VTFYNJ69N5*K1IG1WBQ7A*O1OH3%GFZEX70QBTOGJYYAE0PKBO3S0C:BDQPW795$XKGZT:6H.EL$0NWPLDPNZ26$DAO1JZF7S4URRIT4G:AFHBNQ7RSIZ3WOHGQH*YO8HPFKPY4J*XD7QVOHE$H0I~~<"
            p_decode_qr_msg = c_char_p(decode_qr_msg.encode())
            # p_decode_qr_msg = c_wchar_p(decode_qr_msg)
            # p_decode_qr_msg = c_char_p(decode_qr_msg)

            cresoty_lib.fnQRDecodeEx2.restype = c_char_p
            cresoty_lib.fnQRDecodeEx2.argtypes = [c_char_p, c_char_p, c_char_p]
            # cresoty_lib.fnQRDecodeEx2.restype = c_wchar_p
            # cresoty_lib.fnQRDecodeEx2.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p]
            # cresoty_lib.fnQRDecodeExQ.restype = c_char_p
            # cresoty_lib.fnQRDecodeExQ.argtypes = [c_char_p, c_char_p, c_char_p]
            # cresoty_lib.fnQRDecodeVC.restype = c_char_p
            # cresoty_lib.fnQRDecodeVC.argtypes = [c_char_p, c_char_p, c_char_p]

            aa = c_char_p()
            is_return = byref(aa)
            is_return = cresoty_lib.fnQRDecodeEx2(p_biz_number, p_corp_code, p_decode_qr_msg)
            # is_return = cresoty_lib.fnQRDecodeExQ(p_biz_number, p_corp_code, p_decode_qr_msg)
            # is_return = cresoty_lib.fnQRDecodeExQ(p_biz_number, p_corp_code, p_decode_qr_msg)
            # is_return = cresoty_lib.fnQRDecodeVC(p_biz_number, p_corp_code, p_decode_qr_msg)
            print(c_char_p(is_return).value)

            CDLL(cresoty_dll_path)

        except BaseException as e:
            print("##### (error) decode_qr_cre :: ", e)
            print(e)
        else:
            pass

    def decode_qr_edb(self, decode_qr_msg):
        """
        이디비 암호화 QR 복호화 처리
        :param decode_qr_msg:
        :return:
        """
        try:
            edb_dll_name = "EDBdeker.dll"
            edb_dll_path = os.getcwd() + os.path.sep + "edb_qr" + os.path.sep + edb_dll_name
            print("# 이디비 QR DLL path 정보 :: {}".format(edb_dll_path))

            edb_lib = CDLL(edb_dll_path)

            ###################################################
            # 이디비 프로세스 initialize
            ###################################################
            ret_init = c_int(0)
            edb_lib.EDB_BPD_Initialize.restype = c_int          # 반환타입지정
            ret_init = edb_lib.EDB_BPD_Initialize()             # initialize 함수 호출
            print("##### ret_init :: ", c_int(ret_init).value)  # 리턴 결과 확인 (성공시 0 실패시 에러코드)

            ###################################################
            # 이디비 약국 사용자 인증정보 확인
            # TODO 221202 :: 약국 요양기관기호, 약국 전산업체코드 별도 수집할 필요가 있음
            ###################################################
            ret_check_user = c_int(0)
            param_lp_pharm_code_py = '00000091'                 # 약국 요양기관 기호
            param_lp_r_pcode_py = '09'                          # 약국 전산업체 코드
            param_lp_ret_py = create_string_buffer(4000)        # 실패 시 에러 메시지

            # 인자 ctypes 형태로 변환
            param_lp_pharm_code = c_char_p(param_lp_pharm_code_py.encode())
            param_lp_r_pcode = c_char_p(param_lp_r_pcode_py.encode())
            param_lp_ret = c_long(0)

            # 파라미터 및 리턴타입 설정
            edb_lib.EDB_CheckUser.argtypes = [c_char_p, c_char_p, POINTER(c_long)]
            edb_lib.EDB_CheckUser.restype = c_int

            # 이디비 약국사용자 인증 실행
            ret_check_user = edb_lib.EDB_CheckUser(param_lp_pharm_code, param_lp_r_pcode, param_lp_ret)
            print("##### ret_check_user :: ", c_int(ret_check_user).value)  # 리턴 결과 확인 (성공시 0 실패시 에러코드)
            print("##### param_lp_ret.value :: ", param_lp_ret.value)       # 리턴 결과 확인 (성공시 0 실패시 에러코드)

            ###################################################
            # 이디비 바코드 데이터 decode
            ###################################################
            ret_decode_data = c_int(0)
            param_barcode_datas_py = decode_qr_msg
            print("encode")
            print(param_barcode_datas_py.encode())
            param_barcode_datas = c_char_p(param_barcode_datas_py.encode())

            # edb_lib.EDB_DecodeData.argtypes = [c_char_p, POINTER(c_char)]
            # edb_lib.EDB_DecodeData.argtypes = [c_char_p, POINTER(c_long)]
            edb_lib.EDB_DecodeData.argtypes = [c_char_p, POINTER(c_char)]
            edb_lib.EDB_DecodeData.restype = c_int

            # ret_datas = POINTER(c_char)

            # outputData = c_long(0)
            outputData = create_string_buffer(4000)
            # ret_decode_data = edb_lib.EDB_DecodeData(param_barcode_datas, byref(outputData))
            ret_decode_data = edb_lib.EDB_DecodeData(param_barcode_datas, outputData)

            print("ret_decode_data :: ", ret_decode_data)
            print("outputData.value :: ", outputData.value)
            decode_msg = outputData.value

            ###################################################
            # 이디비 바코드 약처방 및 주사처방의 총 개수를 구한다.
            ###################################################
            ret_b_count = c_int(0)
            ret_b_type_py = '#B'
            ret_b_type = c_char_p(ret_b_type_py.encode())
            ret_c_count = c_int(0)
            ret_c_type_py = '#C'
            ret_c_type = c_char_p(ret_c_type_py.encode())

            decode_msg_param = c_char_p(decode_msg)

            edb_lib.EDB_GetPrescriptionCount.argtypes = [c_char_p, c_char_p]
            edb_lib.EDB_GetPrescriptionCount.restype = c_int

            # 약 처방 갯수
            ret_drug_count = edb_lib.EDB_GetPrescriptionCount(decode_msg_param, ret_b_type)
            print("(EDB_GetPrescriptionCount) ret_drug_count :: ", ret_drug_count)

            # 주사 처방 갯수
            ret_inject_count = edb_lib.EDB_GetPrescriptionCount(decode_msg_param, ret_c_type)
            print("(EDB_GetPrescriptionCount) ret_inject_count :: ", ret_inject_count)

            ###################################################
            # 이디비 바코드 SearchData
            # 처방정보 > 약정보 > 주사정보
            ###################################################
            edb_lib.EDB_SearchData.argtypes = [c_char_p, c_int, c_int, POINTER(c_char)]
            edb_lib.EDB_SearchData.restype = c_int


            # 전체데이터가 들어갈 list 정보 [0] : 환자정보, [1] : 약처방정보, [2] : 주사처방정보
            prescription_info_list = list()

            ####################################
            # 환자정보 : param_sd_tag_py = A
            param_sd_tag_py = 'A'
            param_sd_tag = c_char_p(param_sd_tag_py.encode())
            patient_info_dict = dict()  # 환자정보수집 dict
            for idx in range(1, 34):
                param_sd_x = c_int(1)           # 환자정보일때는 1 고정
                param_sd_y = c_int(idx)
                ret_msg = create_string_buffer(4000)
                ret_sd_count = c_int()
                ret_sd_count = edb_lib.EDB_SearchData(param_sd_tag, param_sd_x, param_sd_y, ret_msg)
                # print("##### (환자정보) idx(",idx,") :: ret_msg :: ", ret_msg.value.decode('euc-kr'))

                # TODO 221202 신버전이 아닌 구버전 코드일때는 변경 필요있음..
                patient_info_dict[idx] = ret_msg.value.decode('euc-kr')

            print("## (추출한 환자정보) :: ", patient_info_dict)
            # 환자정보 dict append
            prescription_info_list.append(patient_info_dict)

            ####################################
            # 약처방정보 : param_sd_tag_py = B
            param_sd_tag_py = 'B'
            param_sd_tag_drug = c_char_p(param_sd_tag_py.encode())

            drug_info_list = list()
            if int(ret_drug_count) > 0:
                for cIdx in range(1, int(ret_drug_count)+1):
                    print("##### ({}번째 약정보 추출)".format(cIdx))
                    drug_info_dict = dict()  # 약처방정보수집 dict
                    for dIdx in range(1, 10):       # 약정보
                        param_sd_x = c_int(cIdx)  # 약정보일때는 cIdx 번째 로 변경
                        param_sd_y = c_int(dIdx)
                        ret_msg = create_string_buffer(4000)
                        ret_sd_count = c_int()
                        ret_sd_count = edb_lib.EDB_SearchData(param_sd_tag_drug, param_sd_x, param_sd_y, ret_msg)
                        # print("##### (약정보) dIdx(", dIdx, ") :: ret_msg :: ", ret_msg.value.decode('euc-kr'))

                        # TODO 221202 신버전이 아닌 구버전 코드일때는 변경 필요있음..
                        drug_info_dict[dIdx] = ret_msg.value.decode('euc-kr')

                    drug_info_list.append(drug_info_dict)
                print("## (추출한 약정보) :: ", drug_info_list)
            else:
                print("### 추출할 약정보가 존재하지 않습니다.")

            ####################################
            # 주사처방정보 : param_sd_tag_py = C
            param_sd_tag_py = 'C'
            param_sd_tag_inject = c_char_p(param_sd_tag_py.encode())

            inject_info_list = list()       # 최종 주사정보 리스트
            if int(ret_inject_count) > 0:
                for eIdx in range(1 ,int(ret_inject_count)+1):
                    print("##### ({}번째 주사정보 추출)".format(eIdx))
                    inject_info_dict = dict()
                    for fIdx in range(1, 10):
                        param_sd_x = c_int(eIdx)  # 주사정보일때는 eIdx 번째 로 변경
                        param_sd_y = c_int(fIdx)
                        ret_msg = create_string_buffer(4000)
                        ret_sd_count = c_int()
                        ret_sd_count = edb_lib.EDB_SearchData(param_sd_tag_inject, param_sd_x, param_sd_y, ret_msg)
                        # print("##### (주사정보) fIdx(", fIdx, ") :: ret_msg :: ", ret_msg.value.decode('euc-kr'))

                        # TODO 221202 신버전이 아닌 구버전 코드일때는 변경 필요있음..
                        inject_info_dict[fIdx] = ret_msg.value.decode('euc-kr')
                    print("## (추출한 주사정보) :: ", inject_info_dict)
                inject_info_list.append(inject_info_dict)
            else:
                print("### 추출할 주사 정보가 존재하지 않습니다.")

            # 이디비 프로세스 종료
            edb_lib.EDB_BPD_Terminate()

        except UnicodeDecodeError as ue:
            print("##### (error) 유니코드")
            print(ue)
        except Exception as e:
            print("##### (error) decode_qr_edb :: ")
            print(traceback.format_exc())

        else:
            pass

    def parsing_datas_edb(self, patient_list, drug_list, inject_list):
        """
        이디비 복호화된 데이터를 위드팜 DB큐에 맞춰 파싱 처리한다.
        :param patient_list: 환자정보 리스트
        :param drug_list: 약정보 리스트
        :param inject_list: 주사정보 리스트
        :return: 위드팜 DB 큐 테이블에 맞춘 파싱 데이터 dict
        """
        try:
            pass
        except BaseException as e:
            print(traceback.format_exc())
        else:
            pass

    def decode_qr_ubi(self, decode_qr_msg):
        """
        유비케어 암호화 QR 복호화 처리
        :param decode_qr_msg:
        :return:
        """
        try:
            ubi_dll_name = "LibQRHandle.dll"
            cresoty_dll_path = os.getcwd() + os.path.sep + "cresoty_qr" + os.path.sep + ubi_dll_name
            print("# 크레소티 QR DLL 정보 :: {}".format(cresoty_dll_path))

            cresoty_lib = CDLL(cresoty_dll_path)
        except Exception as e:
            print("##### (error) decode_qr_cre :: ", e)
        else:
            pass

if __name__ == "__main__":
    print("# 크레소티 QR 복호화 테스트")

    ## 환경변수 적용 완료 여부 확인
    env = os.environ
    print("현재 환경변수 목록 :: ", str(env['PATH']))
    if str(env['PATH']).find('cresoty_qr') == -1:
        print("## 환경변수 path에 cresoty dll 경로를 추가합니다 :: ", os.getcwd() + os.path.sep + "cresoty_qr")
        add_path = os.getcwd() + os.path.sep + "cresoty_qr;" + env['PATH']
        print("## 환경변수 path에 edb dll 경로를 추가합니다 :: ", os.getcwd() + os.path.sep + "edb_qr")
        add_path = os.getcwd() + os.path.sep + "edb_qr;" + add_path

        env['PATH'] = add_path
        print("환경변수 추가 완료 :: ", env['PATH'])

    # 크레소티 QR 복호화 테스트 (진행중)
    # Custom_Qr_Cipher().decode_qr_cre("1", "11")

    # 0 ~ 65535까지 유니코드 출력하기
    # count = 0
    # for i in range(0xac00, 0xd7a4):
    #     if i % 15 == 0:
    #         print()
    #     print(hex(i), '|', chr(i), end=' ')

    # TODO 221202 신버전URL, 구버전URL 둘다 처리해야함..
    # 구버전 (둘다 처리 해야함.... 해당은 ansi... QR 리딩할 때 아래 구버전 처럼 한글이 utf8처리 되는것이 아니라 euckr 처리되어 들어와야한다)
    # edb_qr_str = "http://www.edb.co.kr/m.htm?+MLK88:S<^.;;-/.)/)--////////////.;7주6Z[];7/,.6'/&-2,///;7/,.6'/&-2,//.;z2{}_z{}1|p1tm;응디빌;읜삵;.-,+*;응화잗;'//*/..-,+*)(.;.-,+*)('&//;;;;;;;;;;./;;I-*-(;//c)1.1.1'c;/.c^////.c]///,ccc.)/(,/c;<]..)+,&/.)*/;,;.+;;c.////c/c^]\;<\..)(/)/,(*.;.;,;;c./,+-c/cOP;<Z"
    # 신버전 (base64 처리된 신버전)
    edb_qr_str = "http://www.edb.co.kr/m.htm?+MLK+eJxVTjtuAlEMvM3u+/jZelsAyuwFEKAgpQN2U7hGSpEKwpEoaZJm6fYElLkBEgUHiEEoSqawxjMje+JsOhmNnl7qloEk7MWnJH/AGB5Pg8WywVCIB6UUqSLT/6+MTbXdvW62u/zxlt/X6LrD5fOKrv86gxPFYEq/775RigThu+Qd40HKwi7+go2PU0gOIuozZ8qiENb23kgbm6Sq1taROXXD7CMVVj8ICBwB5VtWRdtmhXplASdeyAX7aZGbTzGZ/zxHvfgBA7tFCjAwMDAwMTA3"
    Custom_Qr_Cipher('0000009').decode_qr_edb(edb_qr_str)