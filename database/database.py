from __future__ import annotations
from os import environ
from typing import Callable, List, Tuple, TypeVar
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

# Database Types
Field = str
Model = dict
ModelID = int
TableName = str
Query = str

# Database Collections
SelectFields = List[Field]
WhereConstraints = List[str]
QueryResult = List[Tuple]
OrderConstraints = List[Tuple]

# Function Types
AddValuesToQuery = Callable[[dict], str]
AddConstraintToQuery = Callable[[str], str]
UpdateTable = Callable[[int], AddValuesToQuery]
Executor = Callable[[Query], QueryResult]
FromTable = Callable[[TableName], Query]


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

def update_table(table: TableName) -> UpdateTable:
    def key(item_id: ModelID) -> AddValuesToQuery:
        def internal(item: Model) -> Query:
            values_list: List[str] = [f'{key} = \'{value}\'' if isinstance(value, str)
                            else f'{key} = {value}' for key, value in item.items()]
            values: str = ', '.join(values_list)
            return f'UPDATE {table} SET {values} WHERE id = {item_id} RETURNING id'
        return internal
    return key

def insert_into_table(table: TableName) -> AddValuesToQuery:
    def insert(item: Model) -> Query:
        keys: str = ', '.join(list(item))
        values: str = ''
        for idx, value in enumerate(item.values()):
            str_value = f'\'{value}\'' if isinstance(value, str) else str(value)
            values += f'{str_value}' if idx == 0 else f', {str_value}'
        return f'INSERT INTO {table}({keys}) VALUES ({values}) RETURNING id'
    return insert

def query_executor(connection: Connection) -> Executor:
    def executor(query: Query) -> QueryResult:
        cursor: Cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    return executor

def query(query: Query) -> QueryResult:
    connection: Connection = connect(default_config)
    result: List[Tuple] = query_executor(connection)(query)
    connection.commit()
    return result

def select_query(field_list: SelectFields) -> Query:
    return 'SELECT {}'.format(', '.join(field_list)) 

def where_constraint(constraints: WhereConstraints) -> AddConstraintToQuery:
    return lambda query: '{query} WHERE {constraints}'.format(
        query=query,
        constraints='AND '.join(constraints)
    )

def from_table(table: TableName) -> FromTable:
    return lambda query: f'{query} FROM {table}'

def order_by_constraint(order_by: OrderConstraints) -> AddConstraintToQuery:
    order_list: List[str] = [f'{order[0]} {order[1]}' for order in order_by]
    order: str = 'ORDER BY {}'.format( ', '.join(order_list))
    return lambda query: f'{query} {order}'

