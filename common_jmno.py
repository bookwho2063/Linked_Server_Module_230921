# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
# TITLE : 청구SW용 주민번호 암호화 처리 공통
# DATE : 2022.10.17
# AUTH : JW
"""
import ctypes
from ctypes import *
from ctypes.wintypes import *   # 자료형 모음

import os.path

class common_jmno:

    def __init__(self):
        pass

if __name__ == '__main__':
    """
    # 심평원 모듈 
    Function long initialize(ref long context) LIBRARY "IndvInfmCrypto.dll"
    Function long release(ref long context) LIBRARY "IndvInfmCrypto.dll" 
    Function long free_memory(ref long buf) LIBRARY "IndvInfmCrypto.dll"
    Subroutine getErrorCode(long context, ref long error_code) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "getErrorCode;ansi"
    Subroutine getErrorMessage(long context, ref long err_msg) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "getErrorMessage;ansi"
    Function long encodeBase64(long context, byte input_data[], int input_length, ref long output_data) LIBRARY "IndvInfmCrypto.dll"
    Function long decodeBase64(long context, String input_data, ref long ouput_data, ref long ouput_length) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "decodeBase64;ansi"
    Function long setEncryptionPassword(long context, String password) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "setEncryptionPassword;ansi"
    Function long encryptDataWithKey(long context, String input_data, int input_length, ref long ouput_data, ref long output_length) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "encryptDataWithKey;ansi"
    Function long decryptDataWithKey(long context, byte input_data[], int input_length, ref long ouput_data, ref long output_length) LIBRARY "IndvInfmCrypto.dll" ALIAS FOR "decryptDataWithKey;ansi"

    Function long lstrlenW(long lpString ) LIBRARY "kernel32"  
    Subroutine CopyMemory( REF blob dst, uLONG src, LONG nSize ) LIBRARY "kernel32.dll" ALIAS FOR "RtlMoveMemory;Ansi" 
    """

    print("call dll common")
    dll_name = "IndvInfmCrypto.dll"
    # dll_name = "dll_test.dll"
    # dll_name = "jk_test.dll"
    dll_path = os.getcwd() + os.path.sep + "ErpCusJmno" + os.path.sep + dll_name

    # dll_path = 'C:\\Users\\user.DESKTOP-579ONGM\\PycharmProjects\\Linked_server_module\\template\\dll_test.dll'
    print("dll_path :: ", dll_path)

    target_jmno_str = "8703101126114"
    b_target_jmno_str = target_jmno_str.encode('utf-8')
    target_jmno_str_len = len(b_target_jmno_str)

    test_lib = CDLL(dll_path)
    print(test_lib)

    #####################################
    # step #1
    # int nRv = initialize(ref long context)
    test_lib.initialize.restype = c_long
    test_lib.initialize.argtypes = [POINTER(c_long)]
    context = c_long(test_lib._handle)
    # contextPk = pointer(context)

    # nRv = c_int(0)
    nRv = c_long(0)
    nRv = test_lib.initialize(byref(context))
    print('nRv :: ', nRv)

    #####################################
    # step #2
    # long nRv2 = setEncryptionPassword(long context, String password)
    nRv2 = c_long(0)
    strPasswd = 'hjhwith'   # 패스워드 고정
    strPassWdPk = c_wchar_p(strPasswd)
    nRv2 = test_lib.setEncryptionPassword(context, strPassWdPk)
    # print('# step2')
    # print('nRv2 :: ', nRv2)
    # print('context :: ', context)
    # print('contextPk :: ', contextPk)

    #####################################
    # step #3
    # nRv = encryptDataWithKey(context, strInputData ,nInputData ,nstrOutputData, nOutputData)
    # nstrOutputData = ref long, nOutputData = ref long

    nstrOutputData = c_long(0)
    nstrOutputDataPk = pointer(nstrOutputData)
    nOutputData = c_long(0)
    nOutputDataPk = pointer(nOutputData)

    # nRv = test_lib.encryptDataWithKey(context, target_jmno, c_int(13), nstrOutputDataPk, nOutputDataPk)
    # nRv = test_lib.encryptDataWithKey()
    # test_lib.encryptDataWithKey.argtypes = [c_long, c_wchar_p, c_int, POINTER(c_long), POINTER(c_long)]

    # context, "8703101234567", 13, 0, 0
    # nRv = test_lib.encryptDataWithKey(context, create_string_buffer(b_target_jmno_str), target_jmno_str_len, nstrOutputDataPk, nOutputDataPk)
    # nRv = test_lib.encryptDataWithKey(context, c_wchar_p(b_target_jmno_str), target_jmno_str_len, nstrOutputDataPk, nOutputDataPk)
    jmno_str = create_string_buffer(b_target_jmno_str)
    nRv = test_lib.encryptDataWithKey(context.value, jmno_str.value, len(jmno_str.value), nstrOutputDataPk, nOutputDataPk)
    # nRv = test_lib.encryptDataWithKey(context, jmno_str, len(jmno_str), nstrOutputDataPk, nOutputDataPk)
    print('# step3')
    print('# context :: ', context.value)
    print('# nstrOutputData :: ', nstrOutputData.value)
    print('# nOutputData :: ', nOutputData.value)

    step3_output_data = cast(nstrOutputDataPk, c_char_p)
    print("tttt :: ")
    print(step3_output_data.value)

    #####################################
    # step #4
    # blob -> memoryCopy -> byteArray생성

    # end dll load
    CDLL(dll_path)

