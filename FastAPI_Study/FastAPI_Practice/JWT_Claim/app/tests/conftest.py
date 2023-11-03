import asyncio
import os
from os import path
from typing import List

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from sqlalchemy import text

from database.schema import Users
from database.conn import db, Base
from main import create_app
from models import UserToken
from routes.auth import create_access_token

"""
1. DB 생성
2. 테이블 생성
3. 테이블 코드 작동
4. 테이블 레코드 삭제
"""


@pytest.fixture(scope="session")
def app():
    os.environ["API_ENV"] = "test"
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    # Create tables
    Base.metadata.create_all(db.engine)
    return TestClient(app=app)


@pytest.fixture(scope="function", autouse=True)
def session():
    sess = next(db.session())
    yield sess
    clear_all_table_data(
        session=sess,
        metadata=Base.metadata,
        except_tables=[]
    )


@pytest.fixture(scope="function")
def login(session):
    """
    테스트 전 사용자 미리 등록
    :param session:
    :return:
    """
    db_user = Users.create(
        session=session, email="test@test.com", pw="test1234")
    session.commit()
    access_token = create_access_token(data=UserToken.model_validate(
        db_user).model_dump(exclude={'pw', 'marketing_agree'}),)
    return dict(Authorization=f"Bearer {access_token}")


def clear_all_table_data(session: Session, metadata, except_tables: List[str] = None):
    session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    for table in metadata.sorted_tables:
        if table.name not in except_tables:
            session.execute(table.delete())
    session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    session.commit()
