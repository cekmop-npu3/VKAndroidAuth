from enum import StrEnum
from ReadOnly import ReadOnly


__all__ = "VerificationMethods", "AuthEndpoints"


class VerificationMethods(StrEnum):
    sms = "https://api.vk.com/method/ecosystem.sendOtpSms"
    callreset = "https://api.vk.com/method/ecosystem.sendOtpCallReset"
    push = "https://api.vk.com/method/ecosystem.sendOtpPush"
    email = "https://api.vk.com/method/ecosystem.sendOtpEmail"
    password = "password"


class AuthEndpoints(metaclass=ReadOnly):
    getAnonymToken = "https://api.vk.com/oauth/get_anonym_token"
    validateAccount = "https://api.vk.com/method/auth.validateAccount"
    getVerificationMethods = "https://api.vk.com/method/ecosystem.getVerificationMethods"
    checkCode = "https://api.vk.com/method/ecosystem.checkOtp"
    authorize = "https://api.vk.com/oauth/token"
