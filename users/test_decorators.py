from os import getcwd
from time import sleep
from multiprocessing import Process
import requests
from database.database import (
    connect,
    default_config,
)


def __get_query(filename: str) -> str:
    query: str 
    with open(filename, 'r') as file:
        query = file.read().replace('\n', '')
    return query

def test_create_data(func):
    cwd: str = getcwd()
    def __decorator():
        insert_query: str = __get_query(f'{cwd}/users/test_users.sql')
        create_table_query: str = __get_query(f'{cwd}/users/create_test_table.sql')
        connection = connect(default_config)
        cursor = connection.cursor()

        cursor.execute(create_table_query)
        connection.commit()
        cursor.execute(insert_query)
        connection.commit()
        return func()
    return __decorator

def test_delete_data(func):
    cwd: str = getcwd()
    def __decorator():
        try:
            func()
        finally:
            delete_query: str = __get_query(f'{cwd}/users/delete_test_users.sql')
            connection = connect(default_config)
            cursor = connection.cursor()
            cursor.execute(delete_query)
            connection.commit()
        return
    return __decorator

def test_router(func):
    def __decorator():
        internal_proc = Process(target=func, args=(), daemon=False)
        internal_proc.start()
        internal_proc.join(0.25)
    return __decorator
