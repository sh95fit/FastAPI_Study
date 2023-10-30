from typing import Optional
from dataclasses import asdict

import uvicorn

from fastapi import FastAPI

from common.config import conf
from database.conn import db
from routes import index


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

    # Router define
    app.include_router(index.router)

    return app


app = create_app()

if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0",
    #             port=8000, reload=conf().PROJ_RELOAD)
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)
