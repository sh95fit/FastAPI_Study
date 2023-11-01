from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field, constr
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    # name: str = None
    email: EmailStr = None
    pw: str = None
    # phone_number: str = None
    # sns_type: str = None


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    Authorization: str = None


class MessageOk(BaseModel):
    message: str = Field(default="OK")


class UserToken(BaseModel):
    id: int
    pw: str = None
    email: str = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None
    sns_type: Optional[str] = None

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    id: int
    email: str = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None
    sns_type: Optional[str] = None

    class Config:
        from_attributes = True


class AddApiKey(BaseModel):
    user_memo: str = None

    class Config:
        from_attributes = True


class GetApiKeyList(AddApiKey):
    id: int = None
    access_key: str = None
    created_at: datetime = None


class GetApiKeys(GetApiKeyList):
    secret_key: str = None


class CreateAPIWhiteLists(BaseModel):
    ip_addr: str = None


class GetAPIWhiteLists(CreateAPIWhiteLists):
    id: int

    class Config:
        from_attributes = True
