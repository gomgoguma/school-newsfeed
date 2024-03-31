from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from newsfeed_app.admin.admin_service import insert_school_page_service, insert_school_news_service, \
    delete_school_news_service, update_school_news_service
from newsfeed_app.admin.dto_models import DTOSchoolPageInsert, DTOSchoolPageInsertResponse, DTOSchoolNewsInsertResponse, \
    DTOSchoolNewsInsert, DTOSchoolPageUpdate, DTOSchoolPageUpdateResponse
from newsfeed_app.common.database import SessionLocal
from newsfeed_app.user.user_service import validate_admin_auth

router = APIRouter()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/school-page",
             response_model=DTOSchoolPageInsertResponse,
             summary="학교 페이지 등록",
             tags=["Admin"],
             status_code=201,
             description="응답 Code 설명\n" +
                         "- 201: 성공\n" +
                         "- 422: 입력값 오류\n" +
                         "- 500: 서버 오류"
             )
async def insert_school_page(dto: DTOSchoolPageInsert,
                             db: Session = Depends(get_db),
                             user_id: int = Depends(validate_admin_auth)):
    return await insert_school_page_service(dto, db, user_id)


@router.post("/school-page/news",
             response_model=DTOSchoolNewsInsertResponse,
             summary="학교 소식 등록",
             tags=["Admin"],
             status_code=201,
             description="응답 Code 설명\n" +
                         "- 201: 성공\n" +
                         "- 403: 권한 오류 (본인이 등록한 학교 페이지 아닌 경우)\n" +
                         "- 404: 학교 페이지 없음\n" +
                         "- 422: 입력값 오류\n" +
                         "- 500: 서버 오류"
             )
async def insert_school_news(dto: DTOSchoolNewsInsert,
                             db: Session = Depends(get_db),
                             user_id: int = Depends(validate_admin_auth)):
    return await insert_school_news_service(dto, db, user_id)


@router.delete("/school-page/news/{news_id}",
               summary="학교 소식 삭제",
               tags=["Admin"],
               description="응답 Code 설명\n" +
                           "- 200: 성공\n" +
                           "- 403: 권한 오류 (본인이 등록한 학교 소식 아닌 경우)\n" +
                           "- 404: 학교 소식 없음\n" +
                           "- 500: 서버 오류"
               )
async def delete_school_news(news_id: int,
                             db: Session = Depends(get_db),
                             user_id: int = Depends(validate_admin_auth)):
    return await delete_school_news_service(news_id, db, user_id)


@router.put("/school-page/news",
            response_model=DTOSchoolPageUpdateResponse,
            summary="학교 소식 수정",
            tags=["Admin"],
            description="응답 Code 설명\n" +
                        "- 200: 성공\n" +
                        "- 403: 권한 오류 (본인이 등록한 학교 소식 아닌 경우)\n" +
                        "- 404: 학교 소식 없음\n" +
                        "- 422: 입력값 오류\n" +
                        "- 500: 서버 오류"
            )
async def update_school_page_news(dto: DTOSchoolPageUpdate,
                                  db: Session = Depends(get_db),
                                  user_id: int = Depends(validate_admin_auth)):
    return await update_school_news_service(dto, db, user_id)
