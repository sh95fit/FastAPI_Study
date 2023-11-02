import base64
import hmac

import time
import typing
import jwt

import re

# from fastapi.params import Header
# from jwt import PyJWTError
from jwt.exceptions import ExpiredSignatureError, DecodeError
# from pydantic import BaseModel
from starlette.requests import Request
# from starlette.datastructures import URL, Headers
# from starlette.responses import JSONResponse, Response
from starlette.responses import JSONResponse
# from starlette.responses import PlainTextResponse, RedirectResponse
# from starlette.types import ASGIApp, Receive, Scope, Send

from errors import exceptions as ex
from errors.exceptions import APIException, SqlFailureEx, APIQueryStringEx
from common import config, consts
# from common.config import conf
from common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from models import UserToken

from database.conn import db
from database.schema import Users, ApiKeys

from utils.query_utils import to_dict

from utils.date_utils import D
from utils.logger import api_logger

import sqlalchemy.exc

# class AccessControl:
#     def __init__(
#         self,
#         app: ASGIApp,
#         except_path_list: typing.Sequence[str] = None,
#         except_path_regex: str = None,
#     ) -> None:
#         if except_path_list is None:
#             except_path_list = ["*"]
#         self.app = app
#         self.except_path_list = except_path_list
#         self.except_path_regex = except_path_regex

#     async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
#         # print(self.except_path_list)
#         # print(self.except_path_regex)

#         request = Request(scope=scope)
#         headers = Headers(scope=scope)

#         # request.state.req_time = D.datetime()
#         # print(D.datetime())
#         # print(D.date())
#         # print(D.date_num())

#         request.state.start = time.time()
#         request.state.inspect = None
#         request.state.user = None
#         request.state.is_admin_access = None
#         ip_from = request.headers["x-forwarded-for"] if 'x-forwarded-for' in request.headers.keys() else None

#         if await self.url_pattern_check(request.url.path, self.except_path_regex) or request.url.path in self.except_path_list:
#             return await self.app(scope, receive, send)

#         try:
#             if request.url.path.startswith("/api"):
#                 # api 인경우 헤더로 토큰 검사
#                 if "authorization" in request.headers.keys():
#                     token_info = await self.token_decode(access_token=request.headers.get("Authorization"))
#                     request.state.user = UserToken(**token_info)
#                     # 토큰 없음
#                 else:
#                     if "Authorization" not in request.headers.keys():
#                         # response = JSONResponse(
#                         #     status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
#                         # return await response(scope, receive, send)
#                         raise ex.NotAuthorized()
#             else:
#                 # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
#                 # print(request.cookies)
#                 request.cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTYsImVtYWlsIjoidG9rZW5AZ2VuZXJhdGUuY29tIiwibmFtZSI6bnVsbCwicGhvbmVfbnVtYmVyIjpudWxsLCJwcm9maWxlX2ltYWdlIjpudWxsLCJzbnNfdHlwZSI6bnVsbH0.0g69LXB4Qg6fE03w6awbncGQZPa-fOqA42GQLlV64CU"

#                 if "Authorization" not in request.cookies.keys():
#                     # response = JSONResponse(
#                     #     status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
#                     # return await response(scope, receive, send)
#                     raise ex.NotAuthorized()

#                 # request.state.user = await self.token_decode(access_token=request.cookies.get("Authorization"))
#                 token_info = await self.token_decode(access_token=request.cookies.get("Authorization"))
#                 request.state.user = UserToken(**token_info)

#             request.state.req_time = D.datetime()
#             print(D.datetime())
#             print(D.date())
#             print(D.date_num())

#             print(request.cookies)
#             print(headers)
#             res = await self.app(scope, receive, send)

#         except APIException as e:
#             res = await self.exception_handler(e)
#             res = await res(scope, receive, send)
#         finally:
#             # Logging
#             ...

#         return res

#     @staticmethod
#     async def url_pattern_check(path, pattern):
#         result = re.match(pattern, path)
#         if result:
#             return True
#         return False

#     @staticmethod
#     async def token_decode(access_token):
#         """
#         :param access_token:
#         :return:
#         """
#         try:
#             access_token = access_token.replace("Bearer ", "")
#             payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[
#                                  consts.JWT_ALGORITHM])
#         # except PyJWTError as e:
#         #     print(e)
#             # Raise Error
#         except ExpiredSignatureError:
#             raise ex.TokenExpiredEx()
#         except DecodeError:
#             raise ex.TokenDecodeEx()
#         return payload

#     @staticmethod
#     async def exception_handler(error: APIException):
#         error_dict = dict(status=error.status_code, msg=error.msg,
#                           detail=error.detail, code=error.code)
#         res = JSONResponse(status_code=error.status_code, content=error_dict)
#         return res


async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    request.state.service = None

    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys(
    ) else request.client.host
    request.state.ip = ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    cookies = request.cookies
    url = request.url.path

    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)  # 함수 실행(API) 후 api_logger 함수 실행
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    try:
        if url.startswith("/api"):
            # api인 경우 헤더로 토큰 검사
            # if "authorization" in headers.keys():
            #     token_info = await token_decode(access_token=headers.get("Authorization"))
            #     request.state.user = UserToken(**token_info)
            #     # 토큰 없음
            if url.startswith("/api/services"):
                qs = str(request.query_params)
                qs_list = qs.split("&")
                session = next(db.session())

                if not config.conf().DEBUG:
                    try:
                        qs_dict = {qs_split.split("=")[0]: qs_split.split("=")[
                            1] for qs_split in qs_list}
                    except Exception:
                        raise ex.APIQueryStringEx()

                    qs_keys = qs_dict.keys()

                    if "key" not in qs_keys or "timestamp" not in qs_keys:
                        raise ex.APIQueryStringEx()

                    if "secret" not in headers.keys():
                        raise ex.APIHeaderInvalidEx()

                    # session = next(db.session())
                    api_key = ApiKeys.get(
                        session=session, access_key=qs_dict["key"])

                    if not api_key:
                        raise ex.NotFoundAccessKeyEx(api_key=qs_dict["key"])
                    mac = hmac.new(bytes(api_key.secret_key, encoding='utf8'), bytes(
                        qs, encoding='utf-8'), digestmod='sha256')
                    d = mac.digest()
                    validating_secret = str(
                        base64.b64encode(d).decode('utf-8'))

                    if headers["secret"] != validating_secret:
                        raise ex.APIHeaderInvalidEx()

                    now_timestamp = int(D.datetime(diff=9).timestamp())
                    if now_timestamp - 10 > int(qs_dict["timestamp"]) or now_timestamp < int(qs_dict["timestamp"]):
                        raise ex.APITimestampEx()

                    user_info = to_dict(api_key.users)
                    request.state.user = UserToken(**user_info)

                else:
                    # Request User 가 필요함
                    if "authorization" in headers.keys():
                        key = headers.get("Authorization")
                        api_key_obj = ApiKeys.get(
                            session=session, access_key=key)
                        user_info = to_dict(
                            Users.get(session=session, id=api_key_obj.user_id))
                        request.state.user = UserToken(**user_info)
                        # 토큰 없음
                    else:
                        if "Authorization" not in headers.keys():
                            raise ex.NotAuthorized()

                session.close()

                # try:
                #     qs_dict = {qs_split.split("=")[0]: qs_split.split("=")[
                #         1] for qs_split in qs_list}
                # except Exception:
                #     raise ex.APIQueryStringEx()
                #
                # qs_keys = qs_dict.keys()
                # if "key" not in qs_keys or "timestamp" not in qs_keys:
                #     raise ex.APIQueryStringEx()

                # if "secret" not in headers.keys():
                #     raise ex.APIHeaderInvalidEx()

                # session = next(db.session())
                # api_key = ApiKeys.get(
                #     session=session, access_key=qs_dict["key"])
                # if not api_key:
                #     raise ex.NotFoundAccessKeyEx(api_key=qs_dict["key"])
                # mac = hmac.new(bytes(api_key.secret_key, encoding='utf8'), bytes(
                #     qs, encoding='utf-8'), digestmod='sha256')
                # d = mac.digest()
                # validating_secret = str(base64.b64encode(d).decode('utf-8'))

                # if headers["secret"] != validating_secret:
                #     raise ex.APIHeaderInvalidEx()

                # now_timestamp = int(D.datetime(diff=9).timestamp())

                # if now_timestamp - 10 > int(qs_dict["timestamp"]) or now_timestamp < int(qs_dict["timestamp"]):
                #     raise ex.APITimestampEx()

                # user_info = to_dict(api_key.users)
                # request.state.user = UserToken(**user_info)
                # session.close()

                response = await call_next(request)
                return response
            else:
                # if "Authorization" not in headers.keys():
                #     raise ex.NotAuthorized()

                if "Authorization" in headers.keys():
                    token_info = await token_decode(access_token=headers.get("Authorization"))
                    request.state.user = UserToken(**token_info)
                    # 토큰 없음
                else:
                    if "Authorization" not in headers.keys():
                        raise ex.NotAuthorized()

        else:
            # 템플릿이 렌더링인 경우 쿠키에서 토큰 검사
            # cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTYsImVtYWlsIjoidG9rZW5AZ2VuZXJhdGUuY29tIiwibmFtZSI6bnVsbCwicGhvbmVfbnVtYmVyIjpudWxsLCJwcm9maWxlX2ltYWdlIjpudWxsLCJzbnNfdHlwZSI6bnVsbH0.0g69LXB4Qg6fE03w6awbncGQZPa-fOqA42GQLlV64CU"

            if "Authorization" not in cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)

        response = await call_next(request)
        await api_logger(request=request, response=response)
    except Exception as e:
        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg,
                          detail=error.detail, code=error.code)
        response = JSONResponse(
            status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)

    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[
                             consts.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload


# Exception의 경우 status_code가 없으므로 작성한 APIException으로 대체해주는 함수 필요 (HTTP response 방식으로 return하기 위함)
async def exception_handler(error: Exception):
    print(error)
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = SqlFailureEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error
