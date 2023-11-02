from models import MessageOk, KakaoMsgBody
import secrets
import string
from errors import exceptions as ex
import models as m
from database.schema import Users, ApiKeys, ApiWhiteLists
from database.conn import db
from common.consts import MAX_API_KEY, MAX_API_WHITELIST
from starlette.requests import Request
from sqlalchemy.orm import Session
from fastapi.logger import logger
from fastapi import APIRouter, Depends
from uuid import uuid4
from typing import List
import json
import requests
import os
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


router = APIRouter(prefix='/services')


@router.get('')
async def get_all_services(request: Request):
    return dict(your_email=request.state.user.email)


@router.post('/kakao/send')
async def send_kakao(request: Request, body: KakaoMsgBody):
    token = os.environ['KAKAO_KEY']
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/x-www-form-urlencoded"}
    body = dict(object_type="text", text=body.msg,
                link=dict(web_url="https://itsmore.co.kr", mobile_web_url="https://itsmore.co.kr"), button_title="바로 가기")
    data = {"template_object": json.dumps(body, ensure_ascii=False)}

    res = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data=data)

    try:
        res.raise_for_status()
        if res.json()["result_code"] != 0:
            raise Exception("KAKAO SEND FAILED")

    except Exception as e:
        print(res.json())
        logger.warning(e)
        raise ex.KakaoSendFailureEx

    return MessageOk()
