import asyncio
import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from newsfeed_app.admin.dto_models import DTOSchoolPageInsert, DTOSchoolPageInsertResponse, DTOSchoolNewsInsert, \
    DTOSchoolNewsInsertResponse, SchoolNewsResult, DTOSchoolPageUpdate, DTOSchoolPageUpdateResponse
from newsfeed_app.common.models.entity_models import SchoolPage, SchoolNews
from newsfeed_app.common.models.response_model import BaseResponse
from newsfeed_app.stdent.student_service import insert_user_newsfeed

logging.basicConfig(level=logging.INFO)


async def insert_school_page_service(dto: DTOSchoolPageInsert,
                                     db: Session,
                                     user_id: int) -> DTOSchoolPageInsertResponse:

    # 학교 페이지 등록
    school_page = SchoolPage(user_id=user_id, location=dto.location, school_name=dto.school_name)
    db.add(school_page)
    db.commit()
    db.refresh(school_page)

    data = DTOSchoolPageInsertResponse.SchoolPageInsertResult(**school_page.__dict__)
    response = DTOSchoolPageInsertResponse(message="학교 페이지가 등록되었습니다.", data=data)
    return response


async def insert_school_news_service(dto: DTOSchoolNewsInsert,
                                     db: Session,
                                     user_id: int) -> DTOSchoolNewsInsertResponse:
    
    # 학교 페이지 확인
    school_page = db.query(SchoolPage).filter(SchoolPage.page_id == dto.page_id).first()
    if not school_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="학교 페이지가 존재하지 않습니다.")

    # 학교 페이지 권한 확인 (본인 등록 페이지 여부)
    if school_page.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    school_news = SchoolNews(school_page=school_page, title=dto.title, content=dto.content, user_id=user_id)

    db.add(school_news)
    db.commit()
    db.refresh(school_news)

    data = SchoolNewsResult(**school_news.__dict__)
    response = DTOSchoolNewsInsertResponse(message="학교 소식이 등록되었습니다.", data=data)

    # 백그라운드 작업 (학교 페이지 구독 중인 모든 사용자 > 소식 ID 등록)
    asyncio.create_task(insert_user_newsfeed(db, school_page.page_id, school_news.news_id))
    return response


async def delete_school_news_service(news_id: int,
                                     db: Session,
                                     user_id: int) -> BaseResponse:
    # 학교 소식 확인
    school_news = db.query(SchoolNews).filter(SchoolNews.news_id == news_id, SchoolNews.is_del == False).first()
    if not school_news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="학교 소식이 존재하지 않습니다.")

    # 권한 확인 (본인 등록 소식 여부)
    if school_news.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    school_news.is_del = True
    school_news.del_dtm = datetime.now()
    db.commit()

    response = BaseResponse(message="소식을 삭제하였습니다.")
    return response


async def update_school_news_service(dto: DTOSchoolPageUpdate, db: Session, user_id: int) -> DTOSchoolPageUpdateResponse:
    
    # 학교 소식 확인
    school_news = db.query(SchoolNews).filter(SchoolNews.news_id == dto.news_id, SchoolNews.is_del == False).first()
    if not school_news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="학교 소식이 존재하지 않습니다.")

    # 권한 확인 (본인 등록 소식 여부)
    if school_news.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

    school_news.title = dto.title
    school_news.content = dto.content
    school_news.upd_dtm = datetime.now()
    db.commit()
    db.refresh(school_news)

    data = SchoolNewsResult(**school_news.__dict__)
    response = DTOSchoolPageUpdateResponse(message="학교 소식이 수정되었습니다.", data=data)
    return response
