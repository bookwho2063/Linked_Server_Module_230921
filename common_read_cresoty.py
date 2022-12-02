# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
# TITLE : 처방전 2D QR 복호화 처리
# DATE : 2022.11.28
# AUTH : JW
"""
import ctypes
from ctypes import *
from ctypes.wintypes import *  # 자료형 모음
import os.path
import sys
import os

class Custom_Qr_Cipher:
    """
    # 크레소티 처방전 QR 복호화 클래스
    """
    def __init__(self):
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
            print("# 크레소티 QR DLL path 정보 :: {}".format(cresoty_dll_path))

            # DLL import
            cresoty_lib = CDLL(cresoty_dll_path)
            # cresoty_lib = WinDLL(cresoty_dll_path)
            # cresoty_lib = WinDLL(CDLL(cresoty_dll_path))

            # TEST INFO (사업자번호)
            # biz_number = "2"
            biz_number = "2018182695"
            p_biz_number = c_char_p(biz_number.encode())
            # p_biz_number = c_wchar_p(biz_number)
            # p_biz_number = c_char_p(biz_number)

            # TEST INFO (청구SW업체번호)
            # corp_code = "S"
            corp_code = "SD0054"
            p_corp_code = c_char_p(corp_code.encode())
            # p_corp_code = c_wchar_p(corp_code)
            # p_corp_code = c_char_p(corp_code)

            # TEST INFO (암호화 QR)
            decode_qr_msg = "CRESA09/N$1GVLGAHS6GR1I2F4KW:8$1SX.*LV-ZB6ERTZ1LXTFHQN+IAFN3VQPCR9.VG*FG+EN90W*H13VI8JM0W$4NTDWHNAG$2AAMY$B.RMZVS46FZ-74Q0XVB.KXT9*WOF6KJOF46K+381Z1C3TF2N065S$ZB.25$QETN1CP55JSWUVNWWEJ.*W4XS62FJP1K00LX0VTFYNJ69N5*K1IG1WBQ7A*O1OH3%GFZEX70QBTOGJYYAE0PKBO3S0C:BDQPW795$XKGZT:6H.EL$0NWPLDPNZ26$DAO1JZF7S4URRIT4G:AFHBNQ7RSIZ3WOHGQH*YO8HPFKPY4J*XD7QVOHE$H0I~~<"
            p_decode_qr_msg = c_char_p(decode_qr_msg.encode())
            # p_decode_qr_msg = c_wchar_p(decode_qr_msg)
            # p_decode_qr_msg = c_char_p(decode_qr_msg)

            # fnQRDecodeEx2 추가 인자
            outStr = create_string_buffer(4000)
            # outStr_p = byref(outStr)
            retMsg = create_string_buffer(4000)
            # retMsg_p = byref(retMsg)

            # 파워빌더의 string 타입은 파이썬의 ctypes 모듈에서 c_char_p(c->char*) 형태로 사용
            cresoty_lib.fnQRDecodeEx2.restype = c_long        # 리턴 타입 설정 char*
            cresoty_lib.fnQRDecodeEx2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]     # 파라미터 타입 설정 [char*, char*, char*]
            # cresoty_lib.fnQRDecodeEx2.restype = c_wchar_p
            # cresoty_lib.fnQRDecodeEx2.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p]
            # cresoty_lib.fnQRDecodeExQ.restype = c_char_p
            # cresoty_lib.fnQRDecodeExQ.argtypes = [c_char_p, c_char_p, c_char_p]
            # cresoty_lib.fnQRDecodeVC.restype = c_char_p
            # cresoty_lib.fnQRDecodeVC.argtypes = [c_char_p, c_char_p, c_char_p]

            # 리턴 변수 생성
            li_return = c_long(0)

            # 복호화 dll 함수 호출
            li_return = cresoty_lib.fnQRDecodeEx2(p_biz_number, p_corp_code, p_decode_qr_msg, outStr, retMsg)
            print("123")
            # is_return = cresoty_lib.fnQRDecodeExQ(p_biz_number, p_corp_code, p_decode_qr_msg)
            # is_return = cresoty_lib.fnQRDecodeExQ(p_biz_number, p_corp_code, p_decode_qr_msg)
            # is_return = cresoty_lib.fnQRDecodeVC(p_biz_number, p_corp_code, p_decode_qr_msg)
            print(li_return)

            # End
            CDLL(cresoty_dll_path)

        except BaseException as e:
            print("##### (error) decode_qr_cre :: ", e)
            print(e)
        else:
            pass


if __name__ == "__main__":
    print("# 크레소티 QR 복호화 테스트")

    ## 환경변수 적용 완료 여부 확인
    env = os.environ
    print("현재 환경변수 목록 :: ", str(env['PATH']))
    if str(env['PATH']).find('cresoty_qr') == -1:
        print("## 환경변수 path에 dll 경로를 추가합니다 :: ", os.getcwd() + os.path.sep + "cresoty_qr")
        add_path = os.getcwd() + os.path.sep + "cresoty_qr;" + env['PATH']
        print("## add_path :: ", add_path)
        env['PATH'] = add_path
        print("환경변수 추가 완료 :: ", env['PATH'])

    # 크레소티 QR 복호화 테스트
    Custom_Qr_Cipher().decode_qr_cre("1", "11")