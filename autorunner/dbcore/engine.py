#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @time   :2024/10/29 14:14
# @Author : liangchunhua
# @Desc   : 数据库引擎
import datetime
import json
import time

from sqlalchemy import create_engine, text, Row
from sqlalchemy.orm import sessionmaker, DeclarativeMeta


class DBEngine(object):
    def __init__(self, db_uri: str):
        """
        db_uri = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4'
        """
        engine = create_engine(db_uri)
        session = sessionmaker(bind=engine)
        from sqlalchemy.orm import scoped_session
        # 多线程
        scoped_session = scoped_session(session)
        self.__session = scoped_session

    @staticmethod
    def __value_decode(row: dict):
        """
        Try to decode value of table
        datetime.datetime-->string
        datetime.date-->string
        json str-->dict
        :param row:
        :return:
        """
        for k, v in row.items():
            if isinstance(v, datetime.datetime):
                row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(v, datetime.date):
                row[k] = v.strftime("%Y-%m-%d")
            elif isinstance(v, str):
                try:
                    row[k] = json.loads(v)
                except ValueError:
                    pass

    def __fetch(self, query: str, size: int = -1, commit: bool = True):
        query = query.strip()
        result = self.__session.execute(text(query))
        self.__session.commit()
        if query.upper()[:6] == "SELECT":
            if size < 0:
                # al = result.fetchall()
                # from itertools import chain
                # al = list(chain.from_iterable(al))
                # al = DBEngine.__default_serialize(al)
                mny = result.fetchall()
                mny = [row._asdict() for row in mny]
                return mny or None
            else:
                mny = result.fetchmany(size)
                mny = [row._asdict() for row in mny]
                # for el in mny:
                #     self.value_decode(el)
                return mny or None
        elif query.upper()[:6] in ("UPDATE", "DELETE", "INSERT"):
            return {"count": result.rowcount}

    @staticmethod
    def __default_serialize(obj):
        """默认序序列化"""
        try:
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(obj, Row):
                return {key: DBEngine.__default_serialize(value) for key, value in
                        dict(zip(obj._fields, obj._data)).items()}
            if isinstance(obj, list):
                return [DBEngine.__default_serialize(e) for e in obj]
            if hasattr(obj, "__class__") and isinstance(obj.__class__, DeclarativeMeta):
                return {c.name: DBEngine.__default_serialize(getattr(obj, c.name)) for c in obj.__table__.columns}
            return obj
        except TypeError as err:
            return repr(obj)

    def fetchone(self, query, commit=True):
        return self.__fetch(query, size=1, commit=commit)

    def fetchmany(self, query, size=1000, commit=True):
        return self.__fetch(query=query, size=size, commit=commit)

    def fetchall(self, query, commit=True):
        return self.__fetch(query=query, size=-1, commit=commit)

    def insert(self, query, commit=True):
        return self.__fetch(query=query, commit=commit)

    def delete(self, query, commit=True):
        return self.__fetch(query=query, commit=commit)

    def update(self, query, commit=True):
        return self.__fetch(query=query, commit=commit)

    def close(self):
        if self.__session:
            self.__session.close()

    def __is_timestamp(value):
        try:
            # 尝试将数据转换为float类型
            timestamp = float(value)
            # 检查时间戳是否在可接受的范围内
            return timestamp > 0 and timestamp < time.time() + 253402300800  # 2106年的时间戳
        except (ValueError, TypeError):
            # 转换失败，不是时间戳
            return False

if __name__ == "__main__":
    user = 'root'
    password = 'rJCuKfeVB6nUZfSk'
    host = '47.101.134.204'
    port = '3306'
    database = 'lykytestplatform'
    # db = DBEngine(f'mysql+pymysql://{user}:'
    #               f'{password}@{host}:'
    #               f'{port}/{database}'
    #               f"?charset=utf8mb4")
    db = DBEngine(f'mysql+pymysql://root:rJCuKfeVB6nUZfSk@47.101.134.204:3306/sit_cas_new?charset=utf8mb4')
    result = db.fetchone('select code from cn_sms_code order by created_at desc limit 1')
    print(result)
