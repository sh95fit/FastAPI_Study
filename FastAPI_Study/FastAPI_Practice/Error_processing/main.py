from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse

from typing import Any, Optional, Dict

app = FastAPI()

users = {
    1: {"name": "test"},
    2: {"name": "user"},
    3: {"name": "human"},
}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in users.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"<User: {user_id}> is not exists.",
        )
    return users[user_id]


# 사용자 정의 에러 (프로젝트 규모가 큰 경우 정의를 해준다)
class SomeError(Exception):
    def __init__(self, name: str, code: int):
        self.name = name
        self.code = code

    def __str__(self):
        return f"<{self.name}> is occured. code: <{self.code}>"


@app.get("/error")
async def get_error():
    # 서버에서 발생한 에러 -> 클라이언트 측에서는 알 수 있는 방법이 없다 (Internal Server Error 표시)
    raise SomeError("Hello", 500)


# 에러 핸들러를 활용하여 에러 확인
@app.exception_handler(SomeError)
async def some_error_handler(request: Request, exc: SomeError):
    return JSONResponse(
        content={"message": f"error is {exc.name}"}, status_code=exc.code
    )


@app.get("/err")
async def get_error():
    raise SomeError("Hello", 500)


# 보다 나은 방법 (핸들러 처리를 별도로 해줄 필요가 없다)
class SomeFastAPIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status_code, detail=detail, headers=headers
        )


@app.get("/geterr")
async def get_error():
    raise SomeFastAPIError(503, "Test")
