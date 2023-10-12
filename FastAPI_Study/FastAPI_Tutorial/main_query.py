from enum import Enum

from typing import Optional     # 타입 힌트를 지정

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def hello():
    return "Hello World!"


class UserLevel(str, Enum):         # 열거책 지정 테스트
    a = "a"
    b = "b"
    c = "c"


@app.get("/test_1")
def get_test_1(grade: UserLevel = UserLevel.a):         # 기본값 지정 방법
    return {"grade": grade}


@app.get("/test")
# boolean의 경우 pydantic에 의해 파이썬 True -> 타 언어 true로 자동 변환 + yes와 no로도 정의 가능
def get_test(is_admin: bool, limit: int = 100):
    return {"is_admin": is_admin, "limit": limit}


@app.get("/users")
def get_us(limit: Optional[int] = None):    # int가 필수가 아닌 옵션임을 의미
    # 쿼리 매개변수를 이용해 limit값을 적용! (경로에서 지정해주지 못한 것을 쿼리 매개번수로 처리)
    # ex> localhost:8000/users?limit=123
    return {"limit": limit}


@app.get("/users/me")
def get_current_user():
    return {"user_id": 123}


@app.get("/users/{user_id}")
def get_user(user_id: int):     # 매개변수에서 타입을 지정해줘야 여러 가지 함수를 활용하기 편리하다(자동 완성 등)
    return {"user_id": user_id}


# 순서 문제!
# FastAPI도 위에서부터 순차적으로 코드를 실행하므로 me가 위에서 설정된 "/users/{user_id}"의 user_id에 반영되어 에러가 발생한다
# @app.get("/users/me")
# def get_current_user():
#     return {"user_id": 123}


@app.get("/users/user/{user_id:int}")
def get_user_1(user_id: float, request: Request):
    # {'user_id' : 123} 출력   / path_params는 경로에 있는 값을 가져오므로 매개변수보다 우선순위가 높다
    print(request.path_params)
    return {"user_id": user_id}  # {'user_id' : 123.0} 출력


if __name__ == "__main__":
    uvicorn.run("main_query.app", reload=True)
    # uvicorn.run(app)    # reload 옵션을 붙일 수 없음!
