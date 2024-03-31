from enum import Enum

from pydantic import BaseModel, Field, constr

from newsfeed_app.common.models.response_model import BaseResponse


class RoleEnum(str, Enum):
    student = "student"
    admin = "admin"


class DTOSignUp(BaseModel):
    name: constr(min_length=1, max_length=10, pattern=r'^[a-zA-Z가-힣0-9]+$', strip_whitespace=True) \
        = Field(...,
                examples=["사용자000000"],
                description="이름(1자~10자): 특수문자,공백없이 입력해 주세요.")
    role: RoleEnum = Field(...,
                           examples=["admin"],
                           description="사용자 권한: student 또는 admin 중 하나를 정확히 입력해 주세요.")
    username: constr(min_length=4, max_length=20, pattern=r'^[a-zA-Z0-9]+$', strip_whitespace=True) \
        = Field(...,
                examples=["user000000"],
                description="아이디(4자~20자): 알파벳 대소문자와 숫자만 입력해 주세요.")
    password: constr(min_length=4, max_length=30,
                     pattern=r'^[a-zA-Z0-9~!@#$%^&*()-_+=\s]+$', strip_whitespace=True) \
        = Field(...,
                examples=["1234"],
                description="패스워드(4자~30자): 알파벳 대소문자와 숫자, 특수문자(!@#$%^&*()-_=+), 공백만 입력해 주세요.")


class DTOSignUpResponse(BaseResponse):
    class SignUpData(BaseModel):
        name: str = Field(..., examples=["사용자123"], description="사용자 이름")
        username: str = Field(..., examples=["user123"], description="사용자 아이디")
        role: RoleEnum = Field(..., examples=["admin"], description="사용자 권한")

    data: SignUpData


class DTOSignIn(BaseModel):
    username: constr(min_length=4, max_length=20, pattern=r'^[a-zA-Z0-9]+$') \
        = Field(...,
                examples=["user000000"],
                description="아이디(4자~20자): 알파벳 대소문자와 숫자만 입력해 주세요.")
    password: constr(min_length=4, max_length=30, pattern=r'^[a-zA-Z0-9~!@#$%^&*()-_+=]+$') \
        = Field(...,
                examples=["1234"],
                description="패스워드(4자~30자): 알파벳 대소문자와, 숫자, 특수기호(!@#$%^&*()-_=+)만 입력해 주세요.")


class DTOSignInResponse(BaseResponse):
    class LoginToken(BaseModel):
        access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX"], description="로그인 토큰")

    data: LoginToken
