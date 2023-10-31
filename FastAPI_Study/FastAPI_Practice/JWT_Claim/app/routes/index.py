from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.requests import Request

from database.conn import db
from database.schema import Users

from inspect import currentframe as frame

router = APIRouter()


@router.get("/")
async def index(session: Session = Depends(db.session),):
    """
    ELB 상태 체크용 API
    :return:
    """
    # user = Users(status="active", name="JWT Claim Test")
    # session.add(user)
    # session.commit()

    # Users().create(session, auto_commit=True, name='KSH')

    current_time = datetime.utcnow()
    return Response(f"JWT TEST API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크용 몌ㅑ
    :return:
    """
    print("state.user", request.state.user)
    try:
        a = 1/0
    except Exception as e:
        request.state.inspect = frame()
        raise e
    current_time = datetime.utcnow()
    return Response(f"JWT Test API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")
