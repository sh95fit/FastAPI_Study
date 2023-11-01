from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from common.consts import MAX_API_KEY, MAX_API_WHITELIST
from database.conn import db
from database.schema import Users, ApiKeys, ApiWhiteLists
import models as m
from errors import exceptions as ex
import string
import secrets

from models import MessageOk

router = APIRouter(prefix='/services')


@router.get('')
async def get_all_services(request: Request):
    return dict(your_email=request.state.user.email)
