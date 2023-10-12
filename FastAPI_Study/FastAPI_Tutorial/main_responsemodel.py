from enum import Enum

from typing import Optional, List     # 타입 힌트를 지정

import uvicorn

from fastapi import FastAPI, Request, status
from pydantic import BaseModel, HttpUrl, EmailStr

app = FastAPI()


# 응답 모델
# class User(BaseModel):
#     name: str
#     password: str
#     avatar_url: Optional[HttpUrl] = None


# Create와 Get을 분리해 노출되면 안 되는 패스워드를 응답에서 제외한다
# class CreateUser(BaseModel):
#     name: str
#     password: str
#     avatar_url: HttpUrl = "https://test.com"


# class GetUser(BaseModel):
#     name: str
#     avatar_url: HttpUrl = "https://test.com"


# # 중복을 피하는 방법
# class User(BaseModel):
#     name: str
#     avatar_url: HttpUrl = "https://test.com"


# class CreateUser(User):
#     password: str


# # restful하게 활용하려면 body에 응답을 보낼 때는 post를 활용한다


# @app.post("/users", response_model=User)
# def create_user(user: CreateUser):
#     return user


# response_model_include, response_model_exclude, response_model_exclude_unset
# 실제 API와 문서간의 괴리가 생겨 잘 사용되지 않는다!
class User(BaseModel):
    name: str = "test"
    password: str
    avatar_url: HttpUrl = None


@app.post(
    "/include",
    response_model=User,
    response_model_include=("name", "avatar_url"),
)
def get_user_with_include(user: User):
    return user


@app.post(
    "/exclude",
    response_model=User,
    response_model_exclude={"password"},
)
def get_user_with_exclude(user: User):
    return user


@app.post(
    "/unset",
    response_model=User,
    response_model_exclude_unset=True,
)
def get_user_with_exclude_unset(user: User):
    return user


# HTTP는 다양한 상태 코드를 갖는다
# status_code를 지정하여 상태 코드 값을 지정해줄 수 있다
class User(BaseModel):
    name: str
    avatar_url: HttpUrl = "https://test.com"


class CreateUser(User):
    password: str


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser):
    return user


if __name__ == "__main__":
    uvicorn.run("main_responsemodel.app", reload=True)
    # uvicorn.run(app)    # reload 옵션을 붙일 수 없음!
