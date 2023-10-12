from fastapi import FastAPI

from typing import Optional, List     # 타입 힌트를 지정

import uvicorn

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, parse_obj_as, Field

app = FastAPI()

# 데이터 검증 (by pydantic)

# inventory = (
#     {
#         "id": 1,
#         "user_id": 1,
#         "name": "test1",
#         "price": 2500.0,
#         "amount": 100,
#     },
#     {
#         "id": 2,
#         "user_id": 1,
#         "name": "test2",
#         "price": 300.0,
#         "amount": 50.0,
#     },
# )


# class Item(BaseModel):
#     name: str
#     price: float
#     amount: int = 0


# @app.get("/users/{user_id}/inventory", response_model=List[Item])
# def get_item(
#     user_id: int = Path(..., gt=0, title="사용자 id",
#                         description="DB의 user.id"),    # ... : 필수값을 의미, gt : greater than
#     name: str = Query(None, min_length=1, max_length=2, title="아이템 이름"),
# ):
#     user_items = []
#     for item in inventory:
#         if item["user_id"] == user_id:
#             user_items.append(item)

#     response = []
#     for item in user_items:
#         if name is None:
#             response = user_items
#             break
#         if item["name"] == name:
#             response.append(item)

#     return response


# pydantic의 Field 사용
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, title="이름")
    price: float = Field(None, ge=0)
    amount: int = Field(
        default=1,
        gt=0,
        le=100,   # less than equal
        title="수량",
        description="아이템 개수. 1~100개까지 소지 가능"
    )


@app.post("/user/{user_id}/item")  # user_id에 대한 데이터 검증이 되지 않음 => 의존성 주입
def create_item(item: Item):
    return item


if __name__ == "__main__":
    uvicorn.run("main.app", reload=True)
