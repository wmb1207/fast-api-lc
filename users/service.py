from typing import Callable, Tuple, List
from dataclasses import fields
from datetime import datetime, timezone
from os import environ

from .models import User
from database.database import (
    insert_into_table,
    where_constraint,
    from_table,
    select_query,
    update_table,
    query,
    order_by_constraint,
)

def table_name():
    return 'test_users' if bool(environ.get('TEST', 'False')) else 'users'

class DuplicateID(Exception):
    pass

class UserNotFound(Exception):
    pass

def __get_users_fields() -> List[str]:
    user_fields_tuple: Tuple = fields(User)
    return [field.name for field in user_fields_tuple]


def get_users() -> List[User]:
    user_fields: List[str] = __get_users_fields()
    from_users_table: Callable = from_table(table_name())
    where_is_not_deleted: Callable = where_constraint([f'deleted_at IS NULL'])
    order_by_created_at_desc: Callable = order_by_constraint([('created_at', 'DESC')])
    select_all_users_query: str = order_by_created_at_desc(
        where_is_not_deleted(
            from_users_table(
                select_query(
                    user_fields
                )
            )
        )
    )
    query_result: List[Tuple] = query(select_all_users_query)


    users: List[User] = [User(*user) for user in query_result]
    return users

def get_user_by_id(id: int) -> User:
    user_fields: List[str] = __get_users_fields()
    from_users_table: Callable = from_table(table_name())
    where_id_equals: Callable = where_constraint([f'id = {id}'])
    select_user_by_id: str = where_id_equals(from_users_table(select_query(user_fields)))

    query_result: List[Tuple] = query(select_user_by_id)
    if not query_result:
        raise  UserNotFound(f'User not found with id {id}')

    if len(query_result) > 1:
        raise DuplicateID(f'More than one user with id {id}')
    
    return User(*query_result[0])

def insert_user(user: User) -> User:
    insert_into_users: Callable = insert_into_table(table_name())
    insert_user_query: str = insert_into_users(user.insert_dict())
    result = query(insert_user_query)
    if result and len(result) == 1:
        user.id = result[0][0] # First element of the list of tuples
        return user

    raise Exception('Unexpected issue creating a user')

def update_user(user: User) -> User:
    if user.id is None:
        raise Exception('No id in update request')

    user.updated_at = str(datetime.now(timezone.utc))
    og_user_dict: dict = get_user_by_id(user.id).update_dict()
    update: dict = {}

    for key, value in user.update_dict().items():
        if value != og_user_dict[key]:
            update[key] = value

    update_table_users: Callable = update_table(table_name())
    update_user: Callable = update_table_users(user.id)
    update_user_query: str = update_user(update)
    result = query(update_user_query)
    if result and len(result) == 1:
        user.id = result[0][0]
        return user

    raise Exception(f'Unexpected issue while updating the user: {user.id}')

def delete_user(user_id: int) -> None:
    user: User = get_user_by_id(user_id)
    user.deleted_at = str(datetime.now(timezone.utc))
    update_user(user)
    return


if __name__ == '__main__':

    import os
    from copy import deepcopy
    from .test_decorators import test_create_data, test_delete_data

    os.environ['TEST'] = 'True'


    @test_create_data
    @test_delete_data
    def _test_get_users():
        users: List[User] = get_users()
        assert(len(users) >= 6)

    @test_create_data
    @test_delete_data
    def _test_get_user_by_id():
        users: List[User] = get_users()
        user_id = users[0].id
        user_id_2 = users[1].id
        if user_id is None or user_id_2 is None:
            raise Exception('User not found')

        user_1 = get_user_by_id(user_id)
        user_2 = get_user_by_id(user_id_2)
        assert(user_1.id == user_id)
        assert(user_2.id == user_id_2)

    @test_create_data
    @test_delete_data
    def _test_insert_user():
        user: User = User(fullname='test_insert', email='test_insert@insert.com', phone_number='3333333333')
        inserted_user = insert_user(user)
        assert(inserted_user.id is not None)

        new_id = inserted_user.id
        found_user = get_user_by_id(new_id)
        assert(found_user.fullname == user.fullname)

    @test_create_data
    @test_delete_data
    def _test_update_user():
        users: List[User] = get_users()
        og_user: User = users[0]
        user_to_update: User = deepcopy(og_user)
        user_to_update.fullname = 'test_updated_user'
        updated_user: User = update_user(user_to_update)
        assert(updated_user.id == og_user.id == user_to_update.id)
        assert(updated_user.fullname == user_to_update.fullname != og_user.fullname)

    @test_create_data
    @test_delete_data
    def _test_delete_user():
        users: List[User] = get_users()
        first_user: User = users[0]
        second_user: User = users[1]
        if first_user.id is None or second_user.id is None:
            raise Exception("ERROR NO ID IN USERS")

        delete_user(first_user.id)
        delete_user(second_user.id)

        users_after_delete: List[User] = get_users()
        assert((len(users) - len(users_after_delete)) == 2)

    _test_get_users()
    _test_get_user_by_id()
    _test_insert_user()
    _test_update_user()
    _test_delete_user()
