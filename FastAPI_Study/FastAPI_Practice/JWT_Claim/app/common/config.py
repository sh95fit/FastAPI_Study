from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


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


@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False


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
