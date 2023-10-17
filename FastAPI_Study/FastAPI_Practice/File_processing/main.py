from fastapi import FastAPI, File, UploadFile

from typing import IO
from tempfile import NamedTemporaryFile

app = FastAPI()


# bytes로 받게 되면 파일 이름, 확장자 등 정보를 얻을 수 없다!
@app.post("/file/size")
def get_filesize(file: bytes = File(...)):
    return {"file_size": len(file)}


# 위 제약사항을 보완하기 위해 UploadFile을 사용한다
# Uplaodfile :  기존 파이썬 입출력 IO 객체를 비동기로 지원
# 따라서 write, read, seek, close 메소드 지원 (비동기 메서드들이므로 await와 함께 써야한다)
@app.post("/file/info")
async def get_file_info(file: UploadFile = File(...)):
    file_like_obj = file.file   # 비동기 객체
    contents = await file.read()    # async 함수일 때만 await 사용가능

    return {
        "content_type": file.content_type,
        "filename": file.filename,
    }


async def save_file(file: IO):
    # AWS s3 업로드 가정
    # delete=True(기본값)이면 현재 함수가 닫히고 파일도 지워진다.
    with NamedTemporaryFile("wb", delete=False) as tempfile:
        tempfile.write(file.read())
        return tempfile.name


@app.post("/file/store")
async def store_file(file: UploadFile = File(...)):
    path = await save_file(file.file)
    return {"filepath": path}
