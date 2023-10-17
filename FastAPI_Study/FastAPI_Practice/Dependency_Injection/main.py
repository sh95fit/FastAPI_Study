from typing import Any, Optional, Dict

from fastapi import FastAPI, Depends, Header, HTTPException

from pydantic import BaseModel, Field

app = FastAPI()

items = ({"name": "test"}, {"name": "user"}, {"name": "human"})


async def func_params(
    q: Optional[str] = None, offset: int = 0, limit: int = 100
) -> Dict[str, Any]:
    return {"q": q, "offset": offset, "limit": limit}


@app.get("/items/func")
async def get_items_with_func(params: dict = Depends(func_params)):
    response = {}
    if params["q"]:
        response.update({"q": params["q"]})

    result = items[params["offset"]: params["offset"] + params["limit"]]
    response.update({"items": result})

    return response


# 클래스를 활용한 의존성 주입
# 직접적으로 params.[변수]를 통해 해당 값을 가져와 활용할 수 있다
class ClassParams:
    def __init__(
        self, q: Optional[str] = None, offset: int = 0, limit: int = 100
    ):
        self.q = q
        self.offset = offset
        self.limit = limit


@app.get("/items/class")
async def get_items_with_class(params: ClassParams = Depends(ClassParams)):
    response = {}
    if params.q:
        response.update({"q": params.q})

    result = items[params.offset: params.offset + params.limit]
    response.update({"items": result})

    return response


# Pydantic을 활용한 의존성 주입
# 조금 더 섬세한 데이터 검증이 가능하다
class PydanticParams(BaseModel):
    q: Optional[str] = Field(None, min_length=2)
    offset: int = Field(0, ge=0)  # ge : greater than or equal
    limit: int = Field(100, gt=0)


@app.get("/items/pydantic")
async def get_items_with_pydantic(params: PydanticParams = Depends()):
    response = {}
    if params.q:
        response.update({"q": params.q})

    result = items[params.offset: params.offset + params.limit]
    response.update({"items": result})

    return response


# DI의 DI
async def get_q(q: Optional[str] = None) -> Optional[str]:
    return q


async def func_params_with_sub(
    q: Optional[str] = Depends(get_q), offset: int = 0, limit: int = 100
) -> Dict[str, Any]:
    return {"q": q, "offset": offset, "limit": limit}


@app.get("/items/func/sub")
async def get_items_with_func_sub(
    params: dict = Depends(func_params_with_sub)
):
    response = {}
    if params["q"]:
        response.update({"q": params["q"]})

    result = items[params["offset"]: params["offset"] + params["limit"]]
    response.update({"items": result})

    return response


# route 데코레이터의 DI
async def verify_token(x_token: str = Header(...)) -> None:
    if len(x_token) < 10:
        raise HTTPException(401, detail="Not authorized")


@app.get("/items", dependencies=[Depends(verify_token)])
async def get_items():
    return items
