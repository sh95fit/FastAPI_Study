from typing import Optional

import uvicorn

from fastapi import FastAPI

from app.common.config import conf


def create_app():
    """
    앱 함수 실행
    """

    app = FastAPI()

    # database initialize

    # redis initialize

    # Middleware define

    # Router define

    return app


app = create_app()

if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0",
    #             port=8000, reload=conf().PROJ_RELOAD)
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)
