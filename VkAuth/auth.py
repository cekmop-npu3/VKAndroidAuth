from ReadOnly import Private
from aiohttp import ClientSession, CookieJar
from typing import Union, Self
from collections.abc import Generator

from .Enums.enums import *
from .Types import *

__all__ = "MobileAuth",


Data = {
    "v": "5.247",
    "device_id": "cc199ca91e009c93:8a8bdae5c3a8a432135d465f42c86589"
}

Headers = {
    "user-agent": "VKAndroidApp/8.114.2-28264 (Android 12; SDK 32; arm64-v8a; samsung SM-G988N; ru; 1280x720)"
}


class MobileAuth:
    login = Private()
    password = Private()
    cookies = Private()
    session = Private()

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password

    async def __aenter__(self) -> Self:
        self.cookies = CookieJar()
        self.session = ClientSession(cookie_jar=self.cookies)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def getAnonymToken(self) -> AnonymToken:
        async with self.session.post(
            url=AuthEndpoints.getAnonymToken,
            data={
                "client_id": 2274003,
                "client_secret": "hHbZxrka2uZ6jB1inYsH"
            } | Data,
            headers=Headers
        ) as response:
            return AnonymToken(data=await response.json())

    async def validateAccount(self, anonymToken: AnonymToken) -> Union[ValidateAccount, Error]:
        async with self.session.post(
            url=AuthEndpoints.validateAccount,
            data={
                "supported_ways": "push,email,sms,callreset,password,reserve_code",
                "login": self.login,
                "access_token": anonymToken.token
            } | Data,
            headers=Headers
        ) as response:
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else ValidateAccount(data=data)

    async def getVerificationMethods(self, anonymToken: AnonymToken, validateAcc: ValidateAccount) -> Union[Generator[VerMethod], Error]:
        async with self.session.post(
            url=AuthEndpoints.getVerificationMethods,
            data={
                "sid": validateAcc.sid,
                "access_token": anonymToken.token,
            } | Data,
            headers=Headers
        ) as response:
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else (VerMethod(data=method) for method in data.get("methods"))

    async def sendCode(self, anonymToken: AnonymToken, validateAcc: ValidateAccount, verMethod: VerificationMethods) -> Union[SendOTP, Error]:
        async with self.session.post(
            url=verMethod,
            data={
                "access_token": anonymToken.token,
                "sid": validateAcc.sid
            } | Data,
            headers=Headers
        ) as response:
            self.cookies.update_cookies(response.cookies)
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else SendOTP(data=data)

    async def checkCode(self, code: Union[str, int], anonymToken: AnonymToken, validateAcc: ValidateAccount, verMethod: VerificationMethods) -> Union[CheckOTP, Error]:
        async with self.session.post(
            url=AuthEndpoints.checkCode,
            data={
                "access_token": anonymToken.token,
                "sid": validateAcc.sid,
                "code": str(code),
                "verification_method": verMethod.name
            } | Data,
            headers=Headers
        ) as response:
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else CheckOTP(data=data)

    async def authorize(self, anonymToken: AnonymToken, validateAcc: ValidateAccount) -> Union[AccessToken, Error]:
        async with self.session.post(
            url=AuthEndpoints.authorize,
            data={
                "anonymous_token": anonymToken.token,
                "sid": validateAcc.sid,
                "username": self.login,
                "password": self.password,
                "grant_type": "phone_confirmation_sid"
            } | Data,
            headers=Headers
        ) as response:
            return AccessToken(data=rsp) if (rsp := await response.json()).get("error") is None else Error(data=rsp)
