from fastapi import APIRouter
from starlette.requests import Request

from typing import List
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.logger import logger

from common.consts import MAX_API_KEY
from database.conn import db
from database.schema import Users, ApiKeys
import models as m
from errors import exceptions as ex

import string
import secrets
from models import MessageOk

from database.schema import Users
from errors.exceptions import NotFoundUserEx
from models import UserMe

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserMe)
async def get_me(request: Request, session: Session = Depends(db.session)):
    """
    get my info
    :param request:
    :return:
    """
    user = request.state.user
    user_info = Users.get(id=user.id)
    # BaseMixin에 정의된 SQLAlchemy Wrapper 함수들을 활용한 쿼리
    # user_info = Users.filter(
    #     session=session, id__gt=user.id).order_by("email").count()  # session은 ACID를 유지하기 위해 사용 / 간단한 쿼리의 경우 생략해도 무방
    # SQLAlchemy 방식의 쿼리
    # user_info = session.query(Users).filter(Users.id > user.id).order_by(Users.email.asc()).count()
    return user_info


@router.put("/me")
async def put_me(request: Request):
    ...


@router.delete("/me")
async def delete_me(request: Request):
    ...


@router.get('/apikeys', response_model=List[m.GetApiKeyList])
async def get_api_keys(request: Request):
    user = request.state.user
    api_keys = ApiKeys.filter(user_id=user.id).filter(id_gt=1).all()
    return api_keys


@router.post('/apikeys', response_model=m.GetApiKeys)
async def create_api_keys(request: Request, key_info: m.AddApiKey, session: Session = Depends(db.session)):
    user = request.state.user

    api_keys = ApiKeys.filter(
        session, user_id=user.id, status="active").count()
    if api_keys == MAX_API_KEY:
        raise ex.MaxKeyCountEx()

    alphabet = string.ascii_letters + string.digits
    s_key = ''.join(secrets.choice(alphabet) for i in range(40))
    uid = f"{str(uuid4())[:-12]}{str(uuid4())}"

    key_info = key_info.model_dump()

    try:
        new_key = ApiKeys.create(
            session, auto_commit=True, secret_key=s_key, user_id=user.id, access_key=uid, **key_info)
    except Exception as e:
        raise ex.SqlFailureEx()
    return new_key


@router.delete('/apikeys/{key_id}')
async def delete_api_keys(request: Request, key_id: int, access_key: str):
    user = request.state.user
    key_data = ApiKeys.get(access_key=access_key)
    if key_data and key_data.id == key_id and key_data.user_id == user.id:
        ApiKeys.filter(id=key_id).delete(auto_commit=True)
        return MessageOk()
    else:
        raise ex.NoKeyMatchEx()
