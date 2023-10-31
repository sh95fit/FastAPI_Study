from typing import Optional
from dataclasses import asdict

import uvicorn

from fastapi import FastAPI

from common.config import conf
from database.conn import db
from routes import index, auth

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from middlewares.token_validator import AccessControl
from middlewares.trusted_hosts import TrustedHostMiddleware


def create_app():
    """
    앱 함수 실행
    """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)

    # database initialize

    # redis initialize

    # Middleware define
    # 미들웨어는 스택 구조이므로 가장 먼저 정의된 것이 마지막에 실행된다! TrustedHostMiddleware -> CORSMiddleware -> AccessControl
    app.add_middleware(AccessControl, except_path_list=EXCEPT_PATH_LIST,
                       except_path_regex=EXCEPT_PATH_REGEX)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=conf().TRUSTED_HOSTS,
        except_path=["/health"],
    )

    # Router define
    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0",
    #             port=8000, reload=conf().PROJ_RELOAD)
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)
