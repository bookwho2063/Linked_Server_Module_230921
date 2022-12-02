# -*- coding: utf-8 -*-

"""
# TITLE : 공통 소스 클래스
# DATE : 2022.10.13
# AUTH : JW
"""

import os, sys
import pyodbc
import pymssql
import pandas as pd
from win32api import GetComputerName
from sqlalchemy import create_engine

import configparser
from pprint import pprint

class conn_ini_func:
    """
    INI 파일 관련 공통 함수
    """
    def __init__(self, ini_file_path):
        self.ini_path = ini_file_path   # 원본
        self.runPath = r"C:\DRxSolution\resources\drxsolution.ini"

    def read_ini_file(self):
        """
        경로에 존재하는 INI 파일을 읽어 객체 리턴
        :return: INI 객체
        """
        try:
            print("##### " + self.ini_path + "경로의 INI 파일을 불러옵니다.")

            config = configparser.ConfigParser()
            config.read(self.ini_path, encoding='utf-8')
            sec = config.sections()
            print("### INI 파일 내 섹션 list :: {}".format(sec))
        except Exception as e:
            print("##### drxsolution.ini 파일 읽기 실패!")
            print(e)
            return 'INI_READ_ERROR'
        else:
            return config

    # def common_method(self):
    #     try:
    #         pass
    #     except Exception as e:
    #         print(e)
    #         return 'INI_PARSE_ERROR'
    #     else:
    #         pass

class conn_db_func:
    """
    DB Control 관련 공통 함수
    """
    def __init__(self, server_ip):
        # TODO (221025) : DB 정보는 위드팜 우선해두고 추후 해당 청구SW에따라 DB 연결정보 변경해서 사용하도록 변경필요
        # self.server = GetComputerName() + "\TOOD2008"
        # self.server = "localhost\\tood2008"
        self.server = server_ip+"\\tood2008"
        self.user = "sa"
        self.password = "$dnlemvka3300$32!"
        self.dbName = "WithpharmErp"

    def open_sqlalchemy_db(self):
        """
        sqlalchemy db 접속
        :return:
        """
        try:
            print("##### (open_sqlalchemy_db) 연결테스트...")
            self.engine = create_engine('mssql+pymssql://'+self.user+':'+self.password+'@'+self.server+'/'+self.dbName, echo=True, connect_args={"timeout": 30},)
            args, kwargs = self.engine.dialect.create_connect_args(self.engine.url)
            print(args, kwargs)
        except Exception as e:
            print("##### (open_sqlalchemy_db) Connection Error")
            print(e)
            return "DB_CONN_ERROR"
        else:
            pass

    def openDB(self):
        """
        MS-SQL DB 커넥션 OPEN
        :return:
        """
        print("(로그) DB Connection 을 수행합니다.")
        print("(openDB) self.server :: ", self.server)
        print("(openDB) self.user :: ", self.user)
        print("(openDB) self.password :: ", self.password)
        print("(openDB) self.dbName :: ", self.dbName)
        try:
            # self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.dbName + ';UID=' + self.user + ';PWD=' + self.password)
            # self.conn = pymssql.connect(self.server, self.user, self.password, self.dbName, charset='utf8')
            self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.dbName + ';UID=' + self.user + ';PWD=' + self.password)
            self.cursor = self.conn.cursor()
            print("dbName:", self.dbName)
            print("(로그) DB Connection 수행을 완료하였습니다.")
        except Exception as e:
            print("(에러) DB Connection 중 오류가 발생하였습니다.")
            print("(에러 Detail) ", e)
            return 'DB_CONN_ERROR'


    def closeDB(self):
        """
        MS-SQL DB 커넥션 CLOSE
        :return:
        """
        print("(로그) DB Disconnection 을 수행합니다.")
        try:
            self.conn.close()
        except Exception as e:
            print("(에러) DB Disconnection 중 오류가 발생하였습니다.")
            print("(에러 Detail) ", e)
            return 'DB_CLOSE_ERROR'

    def queryRollback(self):
        """
        직전 쿼리를 롤백 처리한다.
        :return:
        """
        try:
            print("(connDB) 직전 쿼리 작업을 롤백 처리합니다.")
            self.conn.rollback()
        except Exception as e:
            print("(에러) Query Rollback 중 오류가 발생하였습니다.")
            print("(에러 Detail) ", e)
            return 'DB_ROLL_BACK_ERROR'


    def send_query_update(self, queryMsg):
        """
        쿼리 발송 처리 (UPDATE 용 쿼리- pandas에서는 UPDATE 가 UPSERT 로 동작하는데, 유니크키가없으면 동작하지않으므로 별도제작)
        :param queryMsg:
        :return: 결과데이터를 pandas dataframe 처리하여 리턴
        """
        print("##### (Query-update) ", queryMsg)
        print("##### (Query-update) ", type(queryMsg))
        try:
            # count = self.cursor.execute("""UPDATE dbo.DrxsCustomersAuth SET CustomerAuthFlag = ?, CustomerAuthDte = GETDATE() WHERE CusNo = ?""", dataArray[0], dataArray[1])
            count = self.cursor.execute(queryMsg)
            print("##### count :: ", count)
            self.conn.commit()
        except Exception as e:
            print("(에러) sendQuery 중 오류가 발생하였습니다.")
            print(e)
            return 'DB_SEND_QUERY_ERROR'
        else:
            return 'ok'

    def sendQuery(self, queryMsg):
        """
        쿼리 발송 처리
        :param queryMsg:
        :return: 결과데이터를 pandas dataframe 처리하여 리턴
        """
        print("##### (Query) ", queryMsg)
        print("##### (Query) ", type(queryMsg))
        try:
            resultData = pd.read_sql(sql=queryMsg, con=self.conn)
            print("##### (Query_result_type) :: ")
            print(type(resultData))
            print("##### (Query_result) :: ", resultData)
            resultDict = dict()
            resultDict = self.parsingDfToDict(resultData)
        except Exception as e:
            print("(에러) sendQuery 중 오류가 발생하였습니다.")
            print(e)
            return 'DB_SEND_QUERY_ERROR'
        else:
            return resultDict

    def parsingDfToDict(self, dataframe):
        """
        DataFrame 객체를 dictionary list 로 반환한다.
        :param dataframe:
        :return:
        """
        try:
            # print("##### (parsingDfToDict) DataFrame 객체를 dictionary list 로 반환합니다.")
            # print("##### 변환전 dataframe :: ", dataframe)
            dictFromDf = dataframe.to_dict('list')
            # print("##### 변환후 dataframe :: ", dictFromDf)
        except BaseException as e:
            print("(에러) parsingDfToDict 중 오류가 발생하였습니다.")
            print("(에러 Detail) ", e)
            return 'DB_TO_DICT_ERROR'
        else:
            return dictFromDf