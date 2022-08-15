from __future__ import annotations
from os import environ
from typing import Callable, List, Tuple
from dataclasses import dataclass
from psycopg2 import connect as driver
from psycopg2.extensions import connection as Connection
from psycopg2.extensions import cursor as Cursor
from collections import namedtuple


class InvalidQuery(Exception):
    pass


@dataclass
class Config:
    db_name: str
    user: str
    password: str
    host: str = 'localhost'


default_config = Config(
    db_name=environ.get('DB_NAME', 'api'),
    user=environ.get('DB_USER', 'postgres'),
    password=environ.get('DB_PASSWORD', 'postgres'),
    host=environ.get('DB_HOST', 'postgres'),
)

def connect(config: Config) -> Connection:
    return driver(
        dbname=config.db_name,
        user=config.user,
        password=config.password,
        host=config.host,
    )

def update_table(table: str) -> Callable[[int], Callable[[dict], str]]:
    def key(item_id: int) -> Callable[[dict], str]:
        def internal(item: dict) -> str:
            values_list: List[str] = [f'{key} = \'{value}\'' if isinstance(value, str)
                            else f'{key} = {value}' for key, value in item.items()]
            values: str = ', '.join(values_list)
            return f'UPDATE {table} SET {values} WHERE id = {item_id} RETURNING id'
        return internal
    return key

def insert_into_table(table: str) -> Callable[[dict], str]:
    def insert(item: dict) -> str:
        keys: str = ', '.join(list(item))
        values: str = ''
        for idx, value in enumerate(item.values()):
            str_value = f'\'{value}\'' if isinstance(value, str) else str(value)
            values += f'{str_value}' if idx == 0 else f', {str_value}'
        return f'INSERT INTO {table}({keys}) VALUES ({values}) RETURNING id'
    return insert

def query_executor(connection: Connection) -> Callable[[str], List[Tuple]]:
    def executor(query: str) -> List[Tuple]:
        cursor: Cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    return executor

def query(query: str) -> List[Tuple]:
    connection: Connection = connect(default_config)
    result: List[Tuple] = query_executor(connection)(query)
    connection.commit()
    return result

def select_query(field_list: List[str]) -> str:
    return 'SELECT {}'.format(', '.join(field_list)) 

def where_constraint(constraints: List[str]) -> Callable[[str], str]:
    return lambda query: '{query} WHERE {constraints}'.format(
        query=query,
        constraints='AND '.join(constraints)
    )

def from_table(table: str) -> Callable[[str], str]:
    return lambda query: f'{query} FROM {table}'

def order_by_constraint(order_by: List[Tuple]) -> Callable[[str], str]:
    order_list: List[str] = [f'{order[0]} {order[1]}' for order in order_by]
    order: str = 'ORDER BY {}'.format( ', '.join(order_list))
    return lambda query: f'{query} {order}'

