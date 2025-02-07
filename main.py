from VkAuth import MobileAuth
from VkAuth.Types import Error, Credentials
from VkAuth.Enums import VerificationMethods
from asyncio import run
from dotenv import load_dotenv
from os import getenv

load_dotenv('.env')


async def authorize() -> Credentials:
    async with MobileAuth(getenv("LOGIN"), getenv("PASSWORD")) as auth:
        anonym_token = await auth.getAnonymToken()
        validate_acc = await auth.validateAccount(anonym_token)
        if isinstance(validate_acc, Error):
            raise Exception(validate_acc)
        if validate_acc.nextStep.verMethod != VerificationMethods.password:
            await auth.sendCode(anonym_token, validate_acc, VerificationMethods.sms)
            check_code = await auth.checkCode(input("Enter code: "), anonym_token, validate_acc, VerificationMethods.sms)
            if isinstance(check_code, Error):
                raise Exception(check_code)
        return Credentials(await auth.authorize(anonym_token, validate_acc), auth.cookies)


if __name__ == '__main__':
    print(run(authorize()))

