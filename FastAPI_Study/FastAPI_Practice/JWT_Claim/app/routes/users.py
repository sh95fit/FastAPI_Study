from fastapi import APIRouter
from starlette.requests import Request

from typing import List
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.logger import logger

from common.consts import MAX_API_KEY, MAX_API_WHITELIST
from database.conn import db
from database.schema import Users, ApiKeys, ApiWhiteLists
import models as m
from errors import exceptions as ex

import string
import secrets
from models import MessageOk, UserMe

from errors.exceptions import NotFoundUserEx

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
    """
    `API KEY 조회`\n
    :param request:
    :return:
    """
    user = request.state.user
    api_keys = ApiKeys.filter(user_id=user.id).all()
    return api_keys


@router.post('/apikeys', response_model=m.GetApiKeys)
async def create_api_keys(request: Request, key_info: m.AddApiKey, session: Session = Depends(db.session)):
    """
    `API KEY 생성`\n
    :param request:
    :param key_info:
    :param session:
    :return:
    """

    user = request.state.user

    api_keys = ApiKeys.filter(
        session, user_id=user.id, status="active").count()
    if api_keys == MAX_API_KEY:
        raise ex.MaxKeyCountEx()

    alphabet = string.ascii_letters + string.digits
    s_key = ''.join(secrets.choice(alphabet) for _ in range(40))
    # uid = f"{str(uuid4())[:-12]}{str(uuid4())}"
    uid = None
    while not uid:
        uid_candidate = f"{str(uuid4())[:-12]}{str(uuid4())}"
        uid_check = ApiKeys.get(access_key=uid_candidate)
        if not uid_check:
            uid = uid_candidate

    key_info = key_info.model_dump()

    # try:
    #     new_key = ApiKeys.create(
    #         session, auto_commit=True, secret_key=s_key, user_id=user.id, access_key=uid, **key_info)
    # except Exception as e:
    #     raise ex.SqlFailureEx()
    new_key = ApiKeys.create(session, auto_commit=True, secret_key=s_key,
                             user_id=user.id, access_key=uid, **key_info)
    return new_key


@router.put('/apikeys/{key_id}', response_model=m.GetApiKeyList)
async def update_api_keys(request: Request, key_id: int, key_info: m.AddApiKey):
    """
    API KEY User Memo Update
    :param request:
    :param key_id:
    :param key_info:
    :return:
    """
    user = request.state.user
    key_data = ApiKeys.filter(id=key_id)
    if key_data and key_data.first().user_id == user.id:
        key_data.update(auto_commit=True, **
                        key_info.model_dump())   # 바로 리턴하게 되면 response_model에 적용되기 전에 세션이 종료되는 이슈가 발생

        # 관련 에러
        # {'type': 'get_attribute_error', 'loc': ('response', 'user_memo'), 'msg': 'Error extracting attribute: DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)', 'input': <database.schema.ApiKeys object at 0x000001BBB6C66450>, 'ctx': {'error': 'DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)'}, 'url': 'https://errors.pydantic.dev/2.4/v/get_attribute_error'}\n  {'type': 'get_attribute_error', 'loc': ('response', 'id'), 'msg': 'Error extracting attribute: DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)', 'input': <database.schema.ApiKeys object at 0x000001BBB6C66450>, 'ctx': {'error': 'DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)'}, 'url': 'https://errors.pydantic.dev/2.4/v/get_attribute_error'}\n  {'type': 'get_attribute_error', 'loc': ('response', 'access_key'), 'msg': 'Error extracting attribute: DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)', 'input': <database.schema.ApiKeys object at 0x000001BBB6C66450>, 'ctx': {'error': 'DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)'}, 'url': 'https://errors.pydantic.dev/2.4/v/get_attribute_error'}\n  {'type': 'get_attribute_error', 'loc': ('response', 'created_at'), 'msg': 'Error extracting attribute: DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)', 'input':
        # <database.schema.ApiKeys object at 0x000001BBB6C66450>, 'ctx': {'error': 'DetachedInstanceError: Instance <ApiKeys at 0x1bbb6c66450> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)'}, 'url': 'https://errors.pydantic.dev/2.4/v/get_attribute_error'}\n"}, "client": {"client": "127.0.0.1", "user": 17, "email": "***@token.com"}, "processedTime": "108.26755ms", "datetimeUTC": "2023/11/01 07:24:09", "datetimeKST": "2023/11/01 16:24:09"}

        updated_key_data = ApiKeys.filter(id=key_id).first()
        return updated_key_data

    raise ex.NoKeyMatchEx()


@router.delete('/apikeys/{key_id}')
async def delete_api_keys(request: Request, key_id: int, access_key: str):
    user = request.state.user
    await check_api_owner(user.id, key_id)
    search_by_key = ApiKeys.filter(access_key=access_key)
    if not search_by_key.first():
        raise ex.NoKeyMatchEx()
    search_by_key.delete(auto_commit=True)
    return MessageOk()


@router.get('/apikeys/{key_id}/whitelists', response_model=List[m.GetAPIWhiteLists])
async def get_api_keys(request: Request, key_id: int):
    user = request.state.user
    await check_api_owner(user.id, key_id)
    whitelists = ApiWhiteLists.filter(api_key_id=key_id).all()
    return whitelists


@router.post('/apikey/{key_id}/whitelists', response_model=m.GetAPIWhiteLists)
async def create_api_keys(request: Request, key_id: int, ip: m.CreateAPIWhiteLists, session: Session = Depends(db.session)):
    user = request.state.user
    await check_api_owner(user.id, key_id)

    import ipaddress
    try:
        _ip = ipaddress.ip_address(ip.ip_addr)
    except Exception as e:
        raise ex.InvalidIpEx(ip.ip_addr, e)
    if ApiWhiteLists.filter(api_key_id=key_id).count() == MAX_API_WHITELIST:
        raise ex.MaxWLCountEx()

    ip_dup = ApiWhiteLists.get(api_key_id=key_id, ip_addr=ip.ip_addr)
    if ip_dup:
        return ip_dup
    ip_reg = ApiWhiteLists.create(
        session=session, auto_commit=True, api_key_id=key_id, ip_addr=ip.ip_addr)
    return ip_reg


@router.delete('/apikeys/{key_id}/whitelists/{list_id}')
async def delete_api_keys(request: Request, key_id: int, list_id: int):
    user = request.state.user
    await check_api_owner(user.id, key_id)
    ApiWhiteLists.filter(id=list_id, api_key_id=key_id).delete()

    return MessageOk()


async def check_api_owner(user_id, key_id):
    api_keys = ApiKeys.get(id=key_id, user_id=user_id)
    if not api_keys:
        raise ex.NoKeyMatchEx()
