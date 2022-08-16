from typing import List

from fastapi import APIRouter, HTTPException

from .models import User, UserResponse
from .service import (
    UserNotFound,
    delete_user,
    get_user_by_id,
    get_users,
    insert_user,
    update_user,
)

router = APIRouter()


@router.get("/users", responses={404: {"description": "Users Not Found"}})
async def get_users_endpoint() -> List[UserResponse]:
    try:
        return [UserResponse.from_model(user) for user in get_users()]
    except Exception as err:
        import pdb

        pdb.set_trace()
        raise HTTPException(status_code=404, detail="Users not found") from err


@router.get(
    "/users/{user_id}",
    responses={
        404: {"description": "User Not Found"},
        500: {"description": "SERVER ERROR"},
    },
)
async def get_user_by_id_enpoint(user_id: int) -> UserResponse:
    try:
        return UserResponse.from_model(get_user_by_id(user_id))
    except UserNotFound as err:
        raise HTTPException(status_code=404, detail="Users not found") from err
    except Exception as err:
        raise HTTPException(status_code=500, detail="SERVER ERROR") from err


@router.post(
    "/users", status_code=201, responses={500: {"description": "SERVER ERROR"}}
)
async def new_user_endpoint(user: User) -> UserResponse:
    try:
        return UserResponse.from_model(insert_user(user))
    except Exception as err:
        raise HTTPException(status_code=500, detail="SERVER ERROR") from err


@router.put(
    "/users/{user_id}",
    responses={
        404: {"description": "User Not Found"},
        500: {"description": "SERVER ERROR"},
    },
)
async def update_user_endpoint(user_id: int, user: User) -> UserResponse:
    try:
        user.id = user_id
        return UserResponse.from_model(update_user(user))
    except UserNotFound as err:
        raise HTTPException(status_code=404, detail="Users not found") from err
    except Exception as err:
        raise HTTPException(status_code=500, detail="SERVER ERROR") from err


@router.delete(
    "/users/{user_id}",
    status_code=204,
    responses={
        404: {"description": "User Not Found"},
        500: {"description": "SERVER ERROR"},
    },
)
async def delete_user_enpoint(user_id: int) -> None:
    try:
        return delete_user(user_id)
    except UserNotFound as err:
        raise HTTPException(status_code=404, detail="Users not found") from err
    except Exception as err:
        raise HTTPException(status_code=500, detail="SERVER ERROR") from err


if __name__ == "__main__":
    from multiprocessing import Process
    from os import environ
    from time import sleep

    import requests
    import uvicorn
    from fastapi import FastAPI

    from utils.test_server import (
        test_create_data,
        test_delete_data,
        test_router,
        wait_for_server,
    )

    users_url = "http://127.0.0.1:8000/users"
    proc = None

    environ["TEST"] = "True"

    def _run_server(app):
        uvicorn.run(app=app, host="127.0.0.1", port=8000)

    def _start_server():
        app = FastAPI()
        app.include_router(router)
        global proc

        proc = Process(target=_run_server, args=(app,), daemon=True)
        proc.start()

    def _stop_server():
        global proc

        if proc:
            proc.join(0.25)

    @test_router
    @test_create_data("users")
    @test_delete_data("users")
    @wait_for_server
    def _test_get_users():
        res = requests.get(users_url)
        users = res.json()
        assert res.status_code == 200
        assert len(users) > 0
        return

    @test_router
    @test_create_data("users")
    @test_delete_data("users")
    @wait_for_server
    def _test_get_user_by_id():
        users = get_users()
        og_user = users[0]
        res = requests.get(f"{users_url}/{og_user.id}")
        user = res.json()
        assert res.status_code == 200
        assert user["id"] == og_user.id
        assert user["fullname"] == og_user.fullname
        assert user["email"] == og_user.email

    @test_router
    @test_create_data("users")
    @test_delete_data("users")
    @wait_for_server
    def _test_insert_user():
        user = {
            "fullname": "test_inserted_user",
            "email": "test_inserted_email@email.com",
            "phone_number": "3789789789",
        }
        res = requests.post(f"{users_url}", json=user)
        user = res.json()
        assert res.status_code == 201
        assert user["id"] is not None
        db_user = get_user_by_id(user["id"])
        assert db_user.fullname == user["fullname"]
        assert db_user.email == user["email"]

    @test_router
    @test_create_data("users")
    @test_delete_data("users")
    @wait_for_server
    def _test_update_user():
        db_user = get_users()[0]

        update_user = {
            "fullname": "test_update_user",
            "email": "test_user_email@email.com",
            "phone_number": "123078977",
        }
        res = requests.put(f"{users_url}/{db_user.id}", json=update_user)
        user = res.json()
        assert res.status_code == 200
        assert user["id"] is not None
        assert db_user.fullname != user["fullname"]
        assert db_user.email != user["email"]

    @test_router
    @test_create_data("users")
    @test_delete_data("users")
    @wait_for_server
    def _test_delete_user():
        db_users = get_users()
        user = db_users[0]
        res = requests.delete(f"{users_url}/{user.id}")
        assert res.status_code == 204
        new_db_users = get_users()
        assert len(db_users) > len(new_db_users)

    _start_server()
    _test_get_users()
    _test_get_user_by_id()
    _test_insert_user()
    _test_update_user()
    _test_delete_user()
    _stop_server()
