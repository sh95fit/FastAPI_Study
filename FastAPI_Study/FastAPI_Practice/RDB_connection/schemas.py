from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    email: str
    is_active: bool

    # pydantic이 SQLAlchemy를 사용할 수 있도록 설정
    class Config:
        from_attributes = True
        # orm_mode = True
