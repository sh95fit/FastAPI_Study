from fastapi import FastAPI

from typing import Optional, List     # 타입 힌트를 지정

import uvicorn

from fastapi import FastAPI, Cookie, Header

app = FastAPI()

# 헤더, 쿠키, 매개변수

# 쿠키


@app.get("/cookie")
def get_cookies(ga: str = Cookie(None)):
    return {"ga": ga}


# 헤더

@app.get("/header")
def get_headers(x_token: str = Header(None, title="토큰", convert_underscores=True)):
    return {"X-token": x_token}


if __name__ == "__main__":
    uvicorn.run("main.app", reload=True)
