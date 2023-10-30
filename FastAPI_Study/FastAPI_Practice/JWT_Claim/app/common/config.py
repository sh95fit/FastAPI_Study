from dataclasses import dataclass, asdict
from os import path, environ

import dotenv
import os

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# 데이터베이스 경로
DATABASE_URL = f"mysql+pymysql://{os.environ['db_user']}:{os.environ['db_password']}@{os.environ['db_host']}:{os.environ['db_port']}/{os.environ['db_name']}"


@dataclass    # 딕셔너리 형태로 받기 위해 활용
class Config:
    """
    기본 Configuration
    """
    BASE_DIR = base_dir

    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True


@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True
    DB_URL: str = DATABASE_URL
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


# 상속 테스트

# def abc(DB_ECHO=None, DB_POOL_RECYCLE=None, **kwargs):
#     print(DB_ECHO, DB_POOL_RECYCLE)


# arg = asdict(LocalConfig())  # 딕셔너리 형태로 변경
# abc(arg)
# abc(**arg)  # 값만 출력


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))
