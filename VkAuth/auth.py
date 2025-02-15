from ReadOnly import Private
from aiohttp import ClientSession, CookieJar, TCPConnector
from typing import Union, Self
from collections.abc import Generator
from logging import getLogger

from .Enums.enums import *
from .Types import *

__all__ = "MobileAuth",


logger = getLogger(__name__)


class MobileAuth:
    login = Private()
    password = Private()
    cookies = Private()
    session = Private()
    data = Private()
    headers = Private()

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password
        self.data = {
            "v": "5.247",
            "device_id": "9ad02e1f0054d231:8a8bdae5c3a8a432135d465f42c86589"
        }
        self.headers = {
            "user-agent": "VKAndroidApp/8.114.2-28264 (Android 12; SDK 32; arm64-v8a; samsung SM-G988N; ru; 1280x720)"
        }

    async def __aenter__(self) -> Self:
        self.cookies = CookieJar()
        self.session = ClientSession(
            cookie_jar=self.cookies,
            connector=TCPConnector(limit=20),
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def getAnonymToken(self) -> AnonymToken:
        async with self.session.post(
            url=AuthEndpoints.getAnonymToken,
            data={
                "client_id": 2274003,
                "client_secret": "hHbZxrka2uZ6jB1inYsH"
            } | self.data
        ) as response:
            logger.info(f"{self.getAnonymToken.__name__} -> {response.status}")
            return AnonymToken(data=await response.json())

    async def validateAccount(self, anonymToken: AnonymToken) -> Union[ValidateAccount, Error]:
        async with self.session.post(
            url=AuthEndpoints.validateAccount,
            data={
                "supported_ways": "push,email,sms,callreset,password,reserve_code",
                "login": self.login,
                "access_token": anonymToken.token
            } | self.data
        ) as response:
            logger.info(f"{self.validateAccount.__name__} -> {response.status}")
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else ValidateAccount(data=data)

    async def getVerificationMethods(self, anonymToken: AnonymToken, validateAcc: ValidateAccount) -> Union[Generator[VerMethod], Error]:
        async with self.session.post(
            url=AuthEndpoints.getVerificationMethods,
            data={
                "sid": validateAcc.sid,
                "access_token": anonymToken.token,
            } | self.data
        ) as response:
            logger.info(f"{self.getVerificationMethods.__name__} -> {response.status}")
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else (VerMethod(data=method) for method in data.get("methods"))

    async def sendCode(self, anonymToken: AnonymToken, validateAcc: ValidateAccount, verMethod: VerificationMethods) -> Union[SendOTP, Error]:
        async with self.session.post(
            url=verMethod,
            data={
                "access_token": anonymToken.token,
                "sid": validateAcc.sid
            } | self.data
        ) as response:
            logger.info(f"{self.sendCode.__name__} -> {response.status}")
            return Error(data=rsp.get("error")) if (data := (rsp := await response.json()).get("response")) is None else SendOTP(data=data)

    async def checkCode(self, code: Union[str, int], anonymToken: AnonymToken, validateAcc: ValidateAccount, verMethod: VerificationMethods) -> Union[CheckOTP, Error]:
        async with self.session.post(
            url=AuthEndpoints.checkCode,
            data={
                "access_token": anonymToken.token,
                "sid": validateAcc.sid,
                "code": str(code),
                "verification_method": verMethod.name
            } | self.data
        ) as response:
            logger.info(f"{self.checkCode.__name__} -> {response.status}")
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
            } | self.data
        ) as response:
            logger.info(f"{self.authorize.__name__} -> {response.status}")
            return AccessToken(data=rsp) if (rsp := await response.json()).get("error") is None else Error(data=rsp)
