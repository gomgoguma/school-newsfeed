from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from newsfeed_app.common.database import SessionLocal
from newsfeed_app.common.models.response_model import BaseResponse
from newsfeed_app.stdent.dto_models import DTOSchoolSubInsert, DTOSchoolSubInsertResponse, DTOMySchoolSubSearchResponse, \
    DTOSchoolNewsSearchResponse
from newsfeed_app.stdent.student_service import insert_school_sub_service, search_my_school_sub_service, \
    delete_school_sub_service, search_school_news_service, search_school_newsfeed_service
from newsfeed_app.user.user_service import validate_student_auth

router = APIRouter()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/school-page/subscriptions",
            response_model=DTOMySchoolSubSearchResponse,
            summary="학교 페이지 구독 목록 조회",
            tags=["Student"],
            status_code=200,
            description="응답 Code 설명\n" +
                        "- 200: 성공\n" +
                        "- 404: 구독 목록 없음\n" +
                        "- 500: 서버 오류"
            )
async def search_my_school_sub(db: Session = Depends(get_db),
                               user_id: int = Depends(validate_student_auth)):
    return await search_my_school_sub_service(db, user_id)


@router.get("/school-page/{page_id}/news",
            response_model=DTOSchoolNewsSearchResponse,
            summary="학교 페이지 별 소식 조회",
            tags=["Student"],
            status_code=200,
            description="응답 Code 설명\n" +
                        "- 200: 성공\n" +
                        "- 403: 권한 오류(구독 하지 않음)\n" +
                        "- 404: 학교 소식 없음\n" +
                        "- 500: 서버 오류"
            )
async def search_school_news(page_id: int,
                             db: Session = Depends(get_db),
                             user_id: int = Depends(validate_student_auth)):
    return await search_school_news_service(page_id, db, user_id)


@router.post("/school-page/subscription",
             response_model=DTOSchoolSubInsertResponse,
             summary="학교 페이지 구독",
             tags=["Student"],
             status_code=201,
             description="응답 Code 설명\n" +
                         "- 200: 성공\n" +
                         "- 404: 학교 페이지 없음\n" +
                         "- 409: 중복 오류(이미 구독 상태인 경우)\n" +
                         "- 422: 입력값 오류\n" +
                         "- 500: 서버 오류"
             )
async def insert_school_sub(dto: DTOSchoolSubInsert,
                            db: Session = Depends(get_db),
                            user_id: int = Depends(validate_student_auth)):
    return await insert_school_sub_service(dto, db, user_id)


@router.delete("/school-page/{page_id}/subscription",
               response_model=BaseResponse,
               summary="학교 페이지 구독 취소",
               tags=["Student"],
               status_code=200,
               description="응답 Code 설명\n" +
                           "- 200: 성공\n" +
                           "- 404: 구독 정보 없음\n" +
                           "- 500: 서버 오류"
               )
async def delete_school_sub(page_id: int,
                            db: Session = Depends(get_db),
                            user_id: int = Depends(validate_student_auth)):
    return await delete_school_sub_service(page_id, db, user_id)


# 추가 구현
@router.get("/school-page/newsfeed",
            response_model=DTOSchoolNewsSearchResponse,
            summary="뉴스피드 모아보기",
            tags=["Student"],
            status_code=200,
            description="응답 Code 설명\n" +
                        "- 200: 성공\n" +
                        "- 404: 뉴스피드 없음\n" +
                        "- 500: 서버 오류"
            )
async def search_school_newsfeed(db: Session = Depends(get_db),
                                 user_id: int = Depends(validate_student_auth)):
    return await search_school_newsfeed_service(db, user_id)
