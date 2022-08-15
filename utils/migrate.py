#!/usr/bin/env python3
from typing import List

import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import (
    connect,
    default_config,
)

to_migrate: List = [
    'users'
]

def to_query_str(model: str) -> str:
    query: str
    with open(f'./{model}/{model}.sql', 'r') as file:
        query = file.read().replace('\n', '')
    return query

def create_table():
    connection = connect(default_config)
    cursor = connection.cursor()
    for model in to_migrate:
        cursor.execute(to_query_str(model))
    connection.commit()

def migrate():
    pass

if __name__ == '__main__':
    create_table()
