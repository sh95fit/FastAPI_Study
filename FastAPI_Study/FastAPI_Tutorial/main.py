from enum import Enum

from typing import Optional, List     # 타입 힌트를 지정

import uvicorn

from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl, EmailStr

app = FastAPI()


# Pydantic으로 요청 본문(Request body) 받기
class Item(BaseModel):
    name: str
    price: float
    amount: int = 0


class User(BaseModel):
    name: str
    password: str       # 비밀번호 암호화는 필수이다!!
    avatar_url: Optional[HttpUrl] = None
    inventory: List[Item] = []


@app.post("/users")
def create_user(user: User):
    return user


@app.get("/users/me")
def get_user():
    fake_user = User(
        name="test",
        password="1234",
        inventory=[
            Item(name="tool1", price=1_000_000),
            Item(name="tool2", price=900_000),
        ]
    )
    return fake_user


if __name__ == "__main__":
    uvicorn.run("main.app", reload=True)
    # uvicorn.run(app)    # reload 옵션을 붙일 수 없음!
