from multiprocessing import Process
from os import getcwd
from typing import Any, Callable

import requests

from database.database import connect, default_config

Decorator = Callable[[Callable], Any]


def __get_query(filename: str) -> str:
    query: str
    with open(filename, "r") as file:
        query = file.read().replace("\n", "")
    return query


def test_create_data(model: str) -> Decorator:
    directory: str = f"{getcwd()}/{model}"

    def __decorator(func) -> Callable:
        def __fn():
            insert_query: str = __get_query(f"{directory}/insert_test.sql")
            create_table_query: str = __get_query(f"{directory}/create_test_table.sql")
            connection = connect(default_config)
            cursor = connection.cursor()

            cursor.execute(create_table_query)
            connection.commit()
            cursor.execute(insert_query)
            connection.commit()
            return func()

        return __fn

    return __decorator


def test_delete_data(model: str) -> Decorator:
    directory: str = f"{getcwd()}/{model}"

    def __decorator(func) -> Callable:
        def __fn():
            try:
                func()
            finally:
                delete_query: str = __get_query(f"{directory}/delete_test.sql")
                connection = connect(default_config)
                cursor = connection.cursor()
                cursor.execute(delete_query)
                connection.commit()
            return

        return __fn

    return __decorator


def test_router(func):
    def __decorator():
        internal_proc = Process(target=func, args=(), daemon=False)
        internal_proc.start()
        internal_proc.join(0.25)

    return __decorator


def wait_for_server(func):
    def __decorator():
        while True:
            try:
                func()
                return
            except requests.exceptions.ConnectionError:
                continue

    return __decorator
