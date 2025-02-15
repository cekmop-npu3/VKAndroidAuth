from typing import TypedDict, NotRequired

__all__ = (
    "AnonymTokenDict",
    "NextStepDict",
    "ValidateAccountDict",
    "SendOTPDict",
    "ParamDict",
    "ErrorDict",
    "ProfileDict",
    "SignupParamsDict",
    "CheckOTPDict",
    "AccessTokenDict",
    "VerMethodDict"
)


class AnonymTokenDict(TypedDict):
    token: str
    expired_at: int


class NextStepDict(TypedDict, total=False):
    verification_method: str
    has_another_verification_methods: bool
    external_id: NotRequired[str]
    service_code: NotRequired[int]


class ValidateAccountDict(TypedDict, total=False):
    flow_name: str
    flow_names: list[str]
    is_email: NotRequired[bool]
    is_phone: NotRequired[bool]
    next_step: NotRequired[NextStepDict]
    remember_hash: str
    sid: str


class SendOTPDict(TypedDict, total=False):
    status: int
    sid: str
    code_length: int
    info: str


class ParamDict(TypedDict):
    key: str
    value: str


class ErrorDict(TypedDict, total=False):
    error_code: int
    error_msg: str
    error_text: NotRequired[str]
    error: NotRequired[str]
    error_type: NotRequired[str]
    request_params: NotRequired[list[ParamDict]]
    redirect_uri: NotRequired[str]
    captcha_sid: NotRequired[int]
    is_refresh_enabled: NotRequired[bool]
    captcha_img: NotRequired[str]
    captcha_ts: NotRequired[float]
    captcha_attempt: NotRequired[int]
    captcha_ratio: NotRequired[float]
    captcha_height: NotRequired[int]
    captcha_width: NotRequired[int]
    is_sound_captcha_available: NotRequired[bool]


class ProfileDict(TypedDict, total=False):
    first_name: str
    last_name: str
    has_2fa: bool
    photo_200: str
    phone: str
    can_unbind_phone: bool


class SignupParamsDict(TypedDict):
    password_min_length: int
    birth_date_max: str


class CheckOTPDict(TypedDict, total=False):
    auth_hash: str
    sid: str
    profile_exist: bool
    can_skip_password: bool
    signup_restriction_reason: str
    profile: ProfileDict
    signup_fields: list[str]
    signup_params: SignupParamsDict


class AccessTokenDict(TypedDict, total=False):
    access_token: str
    expires_in: int
    user_id: int
    trusted_hash: str
    webview_refresh_token: str
    webview_refresh_token_expires_in: int
    webview_access_token: str
    webview_access_token_expires_in: str


class VerMethodDict(TypedDict, total=False):
    can_fallback: bool
    info: str
    name: str
    priority: int
    timeout: int
