from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Form : HTML 태그 중 하나
# 보통 어떤 정보를 입력 받는 폼에 대한 컴포넌트를 렌더링하기 위한 용도로 쓴다

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
