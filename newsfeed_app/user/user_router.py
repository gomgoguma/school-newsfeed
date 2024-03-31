from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from newsfeed_app.common.database import SessionLocal
from newsfeed_app.user.dto_models import DTOSignUp, DTOSignUpResponse, DTOSignInResponse, DTOSignIn
from newsfeed_app.user.user_service import sign_up_service, sign_in_service

router = APIRouter()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/sign-up",
             response_model=DTOSignUpResponse,
             summary="회원가입",
             tags=["Auth"],
             status_code=201,
             description="응답 Code 설명\n" +
                         "- 201: 성공\n" +
                         "- 409: 아이디 중복\n" +
                         "- 422: 입력값 오류\n" +
                         "- 500: 서버 오류"
             )
async def sign_up(dto: DTOSignUp,
                  db: Session = Depends(get_db),
                  ):
    return await sign_up_service(dto, db)


@router.post("/sign-in",
             response_model=DTOSignInResponse,
             summary="로그인",
             tags=["Auth"],
             status_code=200,
             description="응답 Code 설명\n" +
                         "- 200: 성공\n" +
                         "- 401: 아이디, 패스워드 불일치\n" +
                         "- 422: 입력값 오류\n" +
                         "- 500: 서버 오류"
             )
async def sign_in(dto: DTOSignIn
                  , db: Session = Depends(get_db)):
    return await sign_in_service(dto, db)
