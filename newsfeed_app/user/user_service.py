import logging
import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session
from starlette.requests import Request

from newsfeed_app.common.env import JWT_SECRET_KEY, JWT_ALGORITHM
from newsfeed_app.user.dto_models import DTOSignUpResponse, DTOSignUp, DTOSignIn, DTOSignInResponse
from newsfeed_app.common.models.entity_models import User, UserInfo
from fastapi import status, Depends, HTTPException

logging.basicConfig(level=logging.INFO)


async def sign_up_service(dto: DTOSignUp, db: Session) -> DTOSignUpResponse:

    # 기존 사용자 확인 > 아이디 중복 검사
    existing_user = db.query(User).filter(User.username == dto.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="사용 중인 아이디입니다.")

    # 패스워드 해싱
    hashed_password = hashlib.sha256(dto.password.encode()).hexdigest()

    user_info = UserInfo(name=dto.name, role=dto.role)
    user = User(username=dto.username, password=hashed_password, user_info=user_info)

    db.add(user)
    db.commit()
    db.refresh(user)

    data = DTOSignUpResponse.SignUpData(username=user.username,
                                        name=user.user_info.name,
                                        role=user.user_info.role)
    response = DTOSignUpResponse(message="회원가입 성공", data=data)
    return response


async def sign_in_service(dto: DTOSignIn, db: Session) -> DTOSignInResponse:

    # 사용자 확인
    user = db.query(User).filter(User.username == dto.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디가 존재하지 않습니다.")

    # 해시된 패스워드 비교
    hashed_password = hashlib.sha256(dto.password.encode()).hexdigest()
    if hashed_password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호가 일치하지 않습니다.")

    # 로그인 토큰 발급
    access_token = create_access_token(user)
    data = DTOSignInResponse.LoginToken(access_token=access_token)
    response = DTOSignInResponse(message="로그인 성공", data=data)
    return response


def create_access_token(user: User):
    to_encode = {
        "user_id": user.user_id,
        "role": user.user_info.role,
    }
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)  # 토큰 만료 = 현재 시간 + 60분
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


class CustomHTTPBearer(HTTPBearer):
    # HTTPBearer 기본 동작: 토큰이 없는 경우 403 반환
    # 수정: 401 반환
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except HTTPException as exc:
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인 후 이용해 주세요.")


auth_scheme = CustomHTTPBearer()


def validate_auth(required_role: str):
    def _validate_auth(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        try:
            # 토큰 검증
            access_token = token.credentials
            payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except DecodeError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰입니다.")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다.")
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인 후 이용해 주세요.")

        # 권한 확인
        role = payload.get('role')
        if not role or role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

        # user_id 반환
        return payload.get('user_id')

    return _validate_auth


validate_student_auth = validate_auth('student')  # 학생 권한 검사
validate_admin_auth = validate_auth('admin')  # 학교 관리자 권한 검사


# 테스트 후 데이터 삭제를 위한 함수
def delete_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
