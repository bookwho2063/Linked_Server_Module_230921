# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
# TITLE : 청구SW용 주민번호 암호화 처리 공통
# DATE : 2022.10.17
# AUTH : JW
"""
import ctypes
from ctypes import *
from ctypes.wintypes import *  # 자료형 모음

import os.path


class common_jmno:
    """
    NOTE : 심평원 주민번호 암호화 클래스
    WARN : ※ 암호화 처리하는 dll 폴더 'ErpCusJmno'의 폴더경로를 시스템 환경변수의 path에 신규로 추가해줘야 dll을 읽을 수 있다
    """

    def __init__(self):
        self.strPasswd = 'hjhwith'

    def encrypt_with_jmno(self, strInputData):
        """
        평문 주민번호를 심평원 주민번호 암호화 dll을 이용하여 암호화 후 리턴한다.
        :param strInputData:
        :return: 암호화 된 바이트형태의 주민번호
        """
        dll_name = "IndvInfmCrypto.dll"
        dll_path = os.getcwd() + os.path.sep + "ErpCusJmno" + os.path.sep + dll_name
        print("##### (심평원) dll_path :: ", dll_path)

        target_lib = CDLL(dll_path)

        #####################################
        # step #1
        # int nRv = initialize(ref long context)
        target_lib.initialize.restype = c_long
        target_lib.initialize.argtypes = [POINTER(c_long)]

        context = c_long(0)
        nRv = c_long(0)
        nRv = target_lib.initialize(byref(context))
        # print('##### step1 nRv :: Result: ', nRv)

        #####################################
        # step #2
        # long nRv2 = setEncryptionPassword(long context, String password)
        # setencryptionpassword ( long context, string password )  returns long
        target_lib.setEncryptionPassword.restype = c_long
        target_lib.setEncryptionPassword.argtypes = [c_long, c_char_p]

        pStrPasswd = c_char_p(self.strPasswd.encode())  # 패스워드 고정
        nRv2 = c_long(0)
        nRv2 = target_lib.setEncryptionPassword(context, pStrPasswd)
        # print('##### nRv2 :: Result: ', nRv2)

        #####################################
        # step #3
        # nRv = encryptDataWithKey(context, strInputData ,nInputData ,nstrOutputData, nOutputData)

        target_lib.encryptDataWithKey.restype = c_long
        target_lib.encryptDataWithKey.argtypes = [c_long, c_char_p, c_int, POINTER(c_long), POINTER(c_long)]

        pStrInputData = c_char_p(strInputData.encode())
        nInputDataLength = len(strInputData)
        strOutputData = c_long(0)
        nOutputDataLength = c_long(0)

        # print('##### nRv3 :: Input: ', strInputData, nInputDataLength)

        nRv3 = c_long(0)
        nRv3 = target_lib.encryptDataWithKey(context, pStrInputData, nInputDataLength, byref(strOutputData), byref(nOutputDataLength))
        # print('##### nRv3 :: Result: ', nRv3)
        # print('##### nRv3 :: Output: ', strOutputData.value, nOutputDataLength.value)

        tempOutputData = cast(strOutputData.value, c_char_p)
        tempOutputDataLength = cast(nOutputDataLength.value, c_void_p)
        # print('##### nRv3 :: Output: ', tempOutputData.value)
        # print('##### nRv3(length) :: Output: ', tempOutputDataLength.value)

        #####################################
        # step #4
        # nRv = encodeBase64(context, aData, nOutputData, nstrEnBase64)
        # encodebase64 ( long context, byte input_data[], integer input_length, ref long output_data )  returns long

        target_lib.encodeBase64.restype = c_long
        target_lib.encodeBase64.argtypes = [c_long, c_char_p, c_int, POINTER(c_long)]

        # inputData = create_string_buffer(tempOutputData.value)
        # inputData = tempOutputData
        # nInputDataLength = sizeof(inputData)
        outputData = c_long(0)
        # print('nRv4 :: Input:', tempOutputData.value, nInputDataLength)

        nRv4 = c_long(0)
        nRv4 = target_lib.encodeBase64(context, tempOutputData, tempOutputDataLength.value, byref(outputData))
        print('nRv4 :: Result: ', nRv4)
        print('nRv4 :: Output:', outputData.value)

        # HALtYoAt21xXKn05c8atvA==
        tempOutputData = cast(outputData.value, c_char_p)
        print('nRv4 :: Output: ', tempOutputData.value)
        CDLL(dll_path)

        return tempOutputData.value


if __name__ == '__main__':

    print("call dll common")
    dll_name = "IndvInfmCrypto.dll"
    dll_path = os.getcwd() + os.path.sep + "ErpCusJmno" + os.path.sep + dll_name
    print("dll_path :: ", dll_path)

    test_lib = CDLL(dll_path)

    #####################################
    # step #1
    # int nRv = initialize(ref long context)
    test_lib.initialize.restype = c_long
    test_lib.initialize.argtypes = [POINTER(c_long)]

    context = c_long(0)
    nRv = c_long(0)
    nRv = test_lib.initialize(byref(context))

    #####################################
    # step #2
    # long nRv2 = setEncryptionPassword(long context, String password)
    # setencryptionpassword ( long context, string password )  returns long
    test_lib.setEncryptionPassword.restype = c_long
    test_lib.setEncryptionPassword.argtypes = [c_long, c_char_p]

    strPasswd = 'hjhwith'
    pStrPasswd = c_char_p(strPasswd.encode())  # 패스워드 고정
    nRv2 = c_long(0)
    nRv2 = test_lib.setEncryptionPassword(context, pStrPasswd)

    #####################################
    # step #3
    # nRv = encryptDataWithKey(context, strInputData ,nInputData ,nstrOutputData, nOutputData)
    # encryptdatawithkey ( long context, string input_data, integer input_length, ref long ouput_data, ref long output_length )  returns long
    test_lib.encryptDataWithKey.restype = c_long
    test_lib.encryptDataWithKey.argtypes = [c_long, c_char_p, c_int, POINTER(c_long), POINTER(c_long)]

    strInputData = '8703101126114'
    pStrInputData = c_char_p(strInputData.encode())
    nInputDataLength = len(strInputData)
    strOutputData = c_long(0)
    nOutputDataLength = c_long(0)

    # print('nRv3 :: Input: ', strInputData, nInputDataLength)

    nRv3 = c_long(0)
    nRv3 = test_lib.encryptDataWithKey(context, pStrInputData, nInputDataLength, byref(strOutputData), byref(nOutputDataLength))
    # print('nRv3 :: Result: ', nRv3)
    # print('nRv3 :: Output: ', strOutputData.value, nOutputDataLength.value)

    tempOutputData = cast(strOutputData.value, c_char_p)
    tempOutputDataLength = cast(nOutputDataLength.value, c_void_p)
    # print('nRv3 :: Output: ', tempOutputData.value)
    # print('nRv3(length) :: Output: ', tempOutputDataLength.value)

    #####################################
    # step #4
    # nRv = encodeBase64(context, aData, nOutputData, nstrEnBase64)
    # encodebase64 ( long context, byte input_data[], integer input_length, ref long output_data )  returns long
    test_lib.encodeBase64.restype = c_long
    test_lib.encodeBase64.argtypes = [c_long, c_char_p, c_int, POINTER(c_long)]

    # inputData = tempOutputData

    # nInputDataLength = len(inputData)
    # nInputDataLength = len(inputData)
    outputData = c_long(0)
    # print('nRv4 :: inputData:', inputData, len(inputData))
    print('nRv4 :: inputData.value:', tempOutputData.value, tempOutputDataLength.value)

    nRv4 = c_long(0)
    nRv4 = test_lib.encodeBase64(context, tempOutputData, tempOutputDataLength.value, byref(outputData))
    print('nRv4 :: Result: ', nRv4)
    print('nRv4 :: Output:', outputData.value)

    # HALtYoAt21xXKn05c8atvA==
    tempOutputData = cast(outputData.value, c_char_p)
    print('nRv4 :: Output: ', tempOutputData.value)

    CDLL(dll_path)