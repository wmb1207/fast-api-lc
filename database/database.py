from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from os import environ
from typing import Callable, List, Tuple, TypeVar

from psycopg2 import connect as driver
from psycopg2.extensions import connection as Connection
from psycopg2.extensions import cursor as Cursor


class InvalidQuery(Exception):
    pass


@dataclass
class Config:
    db_name: str
    user: str
    password: str
    host: str = "localhost"


# Database Types
Field = str
Model = dict
ModelID = int
TableName = str
Query = str
InsertValues = str
UpdateValues = str

# Database Collections
SelectFields = List[Field]
WhereConstraints = List[str]
QueryResult = List[Tuple]
OrderConstraints = List[Tuple]

# Function Types
AddValuesToQuery = Callable[[InsertValues], str]
AddConstraintToQuery = Callable[[str], str]
UpdateTable = Callable[[int], AddValuesToQuery]
Executor = Callable[[Query], QueryResult]
FromTable = Callable[[TableName], Query]


default_config = Config(
    db_name=environ.get("DB_NAME", "api"),
    user=environ.get("DB_USER", "postgres"),
    password=environ.get("DB_PASSWORD", "postgres"),
    host=environ.get("DB_HOST", "postgres"),
)


def connect(config: Config) -> Connection:
    return driver(
        dbname=config.db_name,
        user=config.user,
        password=config.password,
        host=config.host,
    )


def update_table(table: TableName) -> UpdateTable:
    return lambda item_id: (
        lambda values: f"UPDATE {table} SET {values} WHERE id = {item_id} RETURNING id"
    )


def update_values(item: Model) -> UpdateValues:
    values_list: List[str] = [
        f"{key} = '{value}'" if isinstance(value, str) else f"{key} = {value}"
        for key, value in item.items()
    ]
    return ", ".join(values_list)


def insert_values(item: Model) -> InsertValues:
    keys: str = ", ".join(list(item))
    values: str = ""
    for idx, value in enumerate(item.values()):
        str_value = f"'{value}'" if isinstance(value, str) else str(value)
        values += f"{str_value}" if idx == 0 else f", {str_value}"
    return f"({keys}) VALUES ({values})"


def insert_into(table: TableName) -> AddValuesToQuery:
    return lambda values: f"INSERT INTO {table}{values} RETURNING id"


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


def select(field_list: SelectFields) -> Query:
    return "SELECT {}".format(", ".join(field_list))


def where_constraint(constraints: WhereConstraints) -> AddConstraintToQuery:
    return lambda query: "{query} WHERE {constraints}".format(
        query=query, constraints="AND ".join(constraints)
    )


def from_table(table: TableName) -> FromTable:
    return lambda query: f"{query} FROM {table}"


def order_by_constraint(order_by: OrderConstraints) -> AddConstraintToQuery:
    order_list: List[str] = [f"{order[0]} {order[1]}" for order in order_by]
    order: str = "ORDER BY {}".format(", ".join(order_list))
    return lambda query: f"{query} {order}"
