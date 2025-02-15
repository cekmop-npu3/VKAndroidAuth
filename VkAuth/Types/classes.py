from JSObject import JSObject, Field, annotation
from typing import Optional
from datetime import datetime

from .raw import *
from VkAuth.Enums.enums import VerificationMethods

__all__ = (
    "AnonymToken",
    "NextStep",
    "ValidateAccount",
    "SendOTP",
    "Param",
    "Error",
    "Profile",
    "SignupParams",
    "CheckOTP",
    "AccessToken",
    "VerMethod"
)


class AnonymToken(metaclass=JSObject[AnonymTokenDict]):
    token: str = Field()
    expiredAt: datetime = Field(alias="expired_at", base=datetime.fromtimestamp)

    @annotation
    def __init__(
        self,
        token: str,
        expiredAt: int
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: AnonymTokenDict
    ) -> None:
        pass


class NextStep(metaclass=JSObject[NextStepDict]):
    verMethod: VerificationMethods = Field("verification_method", base=lambda x: VerificationMethods[x])
    hasAnotherVerMethods: bool = Field("has_another_verification_methods")
    externalId: Optional[str] = Field("external_id", default=None)
    serviceCode: Optional[int] = Field("service_code", default=None)

    @annotation
    def __init__(
        self,
        verMethod: str,
        hasAnotherVerMethods: bool,
        externalId: Optional[str] = None,
        serviceCode: Optional[int] = None
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: NextStepDict
    ) -> None:
        pass


class ValidateAccount(metaclass=JSObject[ValidateAccountDict]):
    flowName: str = Field("flow_name")
    flowNames: list[str] = Field("flow_names")
    isEmail: Optional[bool] = Field("is_email", default=None)
    isPhone: Optional[bool] = Field("is_phone", default=None)
    nextStep: Optional[NextStep] = Field("next_step", default=None, base=NextStep)
    rememberHash: str = Field("remember_hash")
    sid: str = Field()

    @annotation
    def __init__(
        self,
        flowName: str,
        flowNames: list[str],
        rememberHash: str,
        sid: str,
        nextStep: Optional[NextStep] = None,
        isEmail: Optional[bool] = None,
        isPhone: Optional[bool] = None
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: ValidateAccountDict
    ) -> None:
        pass


class SendOTP(metaclass=JSObject[SendOTPDict]):
    status: int = Field()
    sid: str = Field()
    codeLength: int = Field("code_length")
    info: str = Field()

    @annotation
    def __init__(
        self,
        status: int,
        sid: str,
        codeLength: int,
        info: str
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: SendOTPDict
    ) -> None:
        pass


class Param(metaclass=JSObject[ParamDict]):
    key: str = Field()
    value: str = Field()

    @annotation
    def __init__(
        self,
        key: str,
        value: str
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: ParamDict
    ) -> None:
        pass


class Error(metaclass=JSObject[ErrorDict]):
    errorCode: int = Field("error_code")
    errorMsg: str = Field("error_msg")
    error: Optional[str] = Field(default=None)
    errorType: Optional[str] = Field("error_type", default=None)
    errorText: Optional[str] = Field("error_text", default=None)
    requestParams: Optional[list[Param]] = Field("request_params", default=None, base=lambda params: [Param(param) for param in params])
    redirectUri: Optional[str] = Field("redirect_uri", default=None)
    captchaSid: Optional[int] = Field("captcha_sid", default=None)
    isRefreshEnabled: Optional[bool] = Field("is_refresh_enabled", default=None)
    captchaImg: Optional[str] = Field("captcha_img", default=None)
    captchaTs: Optional[float] = Field("captcha_ts", default=None)
    captchaAttempt: Optional[int] = Field("captcha_attempt", default=None)
    captchaRatio: Optional[float] = Field("captcha_ratio", default=None)
    captchaHeight: Optional[int] = Field("captcha_height", default=None)
    captchaWidth: Optional[int] = Field("captcha_width", default=None)
    isSoundCaptchaAvailable: Optional[bool] = Field("is_sound_captcha_available", default=None)

    @annotation
    def __init__(
        self,
        errorCode: int,
        errorMsg: str,
        requestParams: Optional[list[Param]] = None,
        errorText: Optional[str] = None,
        error: Optional[str] = None,
        errorType: Optional[str] = None,
        redirectUri: Optional[str] = None,
        captchaSid: Optional[int] = None,
        isRefreshEnabled: Optional[bool] = None,
        captchaImg: Optional[str] = None,
        captchaTs: Optional[float] = None,
        captchaAttempt: Optional[int] = None,
        captchaRatio: Optional[float] = None,
        captchaHeight: Optional[int] = None,
        captchaWidth: Optional[int] = None,
        isSoundCaptchaAvailable: Optional[bool] = None
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: ErrorDict
    ) -> None:
        pass


class Profile(metaclass=JSObject[ProfileDict]):
    firstName: str = Field("first_name")
    lastName: str = Field("last_name")
    has_2fa: bool = Field()
    photo_200: str = Field()
    phone: str = Field()
    canUnbindPhone: bool = Field("can_unbind_phone")

    @annotation
    def __init__(
        self,
        firstName: str,
        lastName: str,
        has_2fa: bool,
        photo_200: str,
        phone: str,
        canUnbindPhone: bool
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: ProfileDict
    ) -> None:
        pass


class SignupParams(metaclass=JSObject[SignupParamsDict]):
    passwordMinLength: int = Field("password_min_length")
    birthDateMax: str = Field("birth_date_max")

    @annotation
    def __init__(
        self,
        passwordMinLength: int,
        birthDateMax: str
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: SignupParamsDict
    ) -> None:
        pass


class CheckOTP(metaclass=JSObject[CheckOTPDict]):
    authHash: str = Field("auth_hash")
    sid: str = Field()
    profileExist: bool = Field("profile_exist")
    canSkipPassword: bool = Field("can_skip_password")
    signupRestrictionReason: str = Field("signup_restriction_reason")
    profile: Profile = Field(base=Profile)
    signupFields: list[str] = Field("signup_fields")
    signupParams: SignupParams = Field("signup_params", base=SignupParams)

    @annotation
    def __init__(
        self,
        authHash: str,
        sid: str,
        profileExist: bool,
        canSkipPassword: bool,
        signupRestrictionReason: str,
        profile: Profile,
        signupFields: list[str],
        signupParams: SignupParams
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: CheckOTPDict
    ) -> None:
        pass


class AccessToken(metaclass=JSObject[AccessTokenDict]):
    accessToken: str = Field("access_token")
    expiresIn: datetime = Field("expires_in", base=lambda x: datetime.fromtimestamp(int(x)))
    userId: int = Field("user_id")
    trustedHash: str = Field("trusted_hash")
    webviewRefreshToken: str = Field("webview_refresh_token")
    webviewRefreshTokenExpiresIn: datetime = Field("webview_refresh_token_expires_in", base=lambda x: datetime.fromtimestamp(int(x)))
    webviewAccessToken: str = Field("webview_access_token")
    webviewAccessTokenExpiresIn: datetime = Field("webview_access_token_expires_in", base=lambda x: datetime.fromtimestamp(int(x)))

    @annotation
    def __init__(
        self,
        accessToken: str,
        expiresIn: int,
        userId: int,
        trustedHash: str,
        webviewRefreshToken: str,
        webviewRefreshTokenExpiresIn: int,
        webviewAccessToken: str,
        webviewAccessTokenExpiresIn: str
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: AccessTokenDict
    ) -> None:
        pass


class VerMethod(metaclass=JSObject[VerMethodDict]):
    canFallback: bool = Field("can_fallback")
    info: str = Field()
    name: str = Field()
    priority: int = Field()
    timeout: int = Field()

    @annotation
    def __init__(
        self,
        canFallback: bool,
        info: str,
        name: str,
        priority: int,
        timeout: int
    ) -> None:
        pass

    @annotation
    def __init__(
        self,
        data: VerMethodDict
    ) -> None:
        pass
