# -*- coding: utf-8 -*-
"""
# TITLE : AES-256-CBC 방식 암,복호화 클래스
# DATE : 2022.10.13
# AUTH : JW
"""
from hashlib import md5
from base64 import b64decode
from base64 import b64encode

from time import time

from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

class AESCipher128:

    def __init__(self):
        self.encoder_key = "1T3J63ET8A9AE6Y3FFB2EK5AV28N0FCM2J4B4M4QA7M69L6WL3"
        self.key_len = len(self.encoder_key)
        self.rot_ptr_set = 128
        self.key = self.encoder_key[:24]
        self.iv = bytes(self.key, 'utf-8')

    # /*
    # | —————————————————————————————————
    # |   자체 암호화 128
    # | —————————————————————————————————
    # */
    def Encrypt128(self, plainText):

        reversedText = plainText.encode()[::-1]
        reversedTextLength = len(reversedText)

        encryptedArray = []

        for idx in range(0, reversedTextLength):
            encoderIndex = idx % self.key_len
            encoderKey = self.encoder_key[encoderIndex]
            reversedChar = reversedText[idx]

            encryptedValue = reversedChar ^ ord(encoderKey)
            encryptedValue = (encryptedValue << 3 & 0xF8) | (encryptedValue >> 5 & 0x07)

            encryptedArray.append(encryptedValue)
        # for end

        base64Text = b64encode(bytes(encryptedArray))[::-1].decode()
        base64Text = base64Text.replace("+", "^")

        return base64Text

    def Decrypt128(self, plainText):
        # /*
        # | -------------------------------------------------------------------
        # |	자체 복호화 128
        # | -------------------------------------------------------------------
        # */
        # print("원본")
        # base64Text = plainText.replace("^", "+")
        # reversedText = b64decode(bytes(base64Text))[::-1]
        # reversedText = reversedText.encode()


        base64Text = plainText.replace("^", "+").encode()[::-1]
        print("base64Text :: ", base64Text)
        reversedText = b64decode(bytes(base64Text))
        reversedTextLength = len(reversedText)

        print("reversedText :: ", reversedText)
        print("reversedTextLength :: ", reversedTextLength)

        encryptedArray = []

        for idx in range(0, reversedTextLength):
            encoderIndex = idx % self.key_len
            encoderKey = self.encoder_key[encoderIndex]
            reversedChar = reversedText[idx]

            encryptedValue = (reversedChar >> 3 & 0x1f) | (reversedChar << 5 & 0xe0)
            encryptedValue = encryptedValue ^ ord(encoderKey)

            encryptedArray.append(encryptedValue)

        print("encryptedArray :: ", encryptedArray)
        # tmp = encryptedArray[::-1]
        tmp = ''.join(chr(s) for s in encryptedArray[::-1])

        print("tmp :: ", tmp)
        return tmp


class AESCipher256:
    def __init__(self, key):
        self.key = md5(key.encode('utf8')).digest()
        # self.key = key

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'), AES.block_size)))

    def decrypt(self, data):
        data = data.encode('utf-8')
        data = data.decode('unicode_escape')
        print("data :: ", data)
        raw = b64decode(data)
        self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
        return unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)

# main
if __name__ == '__main__':
    """
    # key = md5()
    # AES-256-CBC
    # 자체 128 Enc
    """

    print('TESTING ENCRYPTION')
    # msg = input('Message...: ')
    # pwd = input('Password..: ')
    key = 'PharmacyInMyHands'
    msg = 'parkjunwook'
    time = int(time())

    md5_time = md5(str(time).encode('utf-8')).digest()
    # md5 결과를 16진수로 바꾸고 32자리가 안될경우 앞을 0으로 채운다
    md5_time_hex = md5_time.hex()
    if len(md5_time_hex) < 32:
        tt = md5_time_hex.zfill(32)
        print("tt : ", tt)

    # key_md5 = md5(key.encode('utf8')).digest()
    # key = md5(key.encode('utf8')).digest()
    # print('key 텍스트:', key)
    # print('key md5:', key_md5)

    ###########
    # 암호화 처리
    print('AES256 암호화 대상 텍스트:', msg)
    # 시간(md5)+암호대상평문을 인자로
    enc_data = AESCipher256(key).encrypt(md5_time_hex+msg).decode('utf-8')
    print('AES256 암호화 된 코드:', enc_data)

    enc128_data = AESCipher128().Encrypt128(enc_data)
    print('(최종)AES128 암호화 된 코드:', enc128_data)

    #sample
    # enc128_datas = str("NQD7XAJES3H0i^TRW62a06ROE3v1W6bKRqKbTxOfVH0WohLXPwPcKBh7I0rESY3dQEI/7bFIGtr8FSihNseOBjbDgMaX0/^tvK/G16uzBkBU6/2NQbEIH8BqFAlsN8STQYZjcsu6lN/vsX5QtQi0NPSLEqK66D1y22dsx3TUxahI7l^ou5hSywD5OdXd4NMnaA7Hpm4zMXOwVBXuGyhFixjbnEdkEhX6PPKw7ZQY0Q1r8XlIrzQHG7vwennW97hw/16Sk9vkUxDtUqs2O7ypWvkjnkmeRp9GVSovQAiri6pXyqMUlChbLwhSJVgrB/GUtRXfTSHM7UzJoQgVGJX3rPsRbOCe4r7Hh248g8B6HxFNiUonmaijXrrp7TWlH3ElgGpw7EjjDUxt55oDZreOfkpaVnujk9OYlyTClfECLLnIpKBG6OYgdRrbWd8UAwBn")
    enc128_data = "V7webv7tT2Pw9rSCUszGByDy^O5uziFC91ffTciYWDajZ^2ds8iH302q20DjaCYs"
    ###########
    # 복호화 처리

    print("복호화 대상 코드 : ", enc128_data)

    dec128_data = AESCipher128().Decrypt128(enc128_data)
    print('복호화 된 코드 type :', type(dec128_data))
    print(dec128_data)

    dec_data = AESCipher256(key).decrypt(dec128_data).decode('utf-8')
    print('복호화 된 텍스트:', dec_data[32:])