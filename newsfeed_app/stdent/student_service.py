import logging

from fastapi import HTTPException
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session, joinedload
from starlette import status

from newsfeed_app.common.models.entity_models import SchoolPage, SchoolSub, SchoolNews, UserNewsfeed
from newsfeed_app.common.models.response_model import BaseResponse
from newsfeed_app.stdent.dto_models import DTOSchoolSubInsert, DTOSchoolSubInsertResponse, DTOMySchoolSubSearchResponse, \
    DTOSchoolNewsSearchResponse

logging.basicConfig(level=logging.INFO)


async def search_my_school_sub_service(db: Session,
                                       user_id: int) -> DTOMySchoolSubSearchResponse:
    # 구독 목록
    school_sub_list = (db.query(SchoolSub).filter(SchoolSub.user_id == user_id)
                       .order_by(desc(SchoolSub.reg_dtm))
                       .all())

    if not school_sub_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="구독 목록이 없습니다.")

    data = [
        DTOMySchoolSubSearchResponse.SchoolSubSearchResult(
            page_id=sub.page_id,
            school_name=sub.school_page.school_name,
            location=sub.school_page.location,
            reg_dtm=sub.reg_dtm
        )
        for sub in school_sub_list
    ]

    response = DTOMySchoolSubSearchResponse(message="구독 목록 조회에 성공하였습니다.", data=data)
    return response


async def search_school_news_service(page_id: int,
                                     db: Session,
                                     user_id: int) -> DTOSchoolNewsSearchResponse:
    # 기존 구독 확인
    existing_sub = db.query(SchoolSub).filter(SchoolSub.page_id == page_id,
                                              SchoolSub.user_id == user_id).first()
    if not existing_sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="구독 상태가 아닙니다.")

    # 학교 소식 조회
    school_news_list = (db.query(SchoolNews).filter(SchoolNews.page_id == page_id,
                                                    SchoolNews.is_del == False)
                        .order_by(desc(SchoolNews.reg_dtm))
                        .options(joinedload(SchoolNews.school_page),
                                 joinedload(SchoolNews.user))
                        .all())

    if not school_news_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="소식이 없습니다.")

    data = [
        DTOSchoolNewsSearchResponse.SchoolNewsSearchResult(
            news_id=news.news_id,
            title=news.title,
            content=news.content,
            location=news.school_page.location,
            page_id=news.school_page.page_id,
            school_name=news.school_page.school_name,
            admin_name=news.user.name,
            reg_dtm=news.reg_dtm,
            upd_dtm=news.upd_dtm
        )
        for news in school_news_list
    ]

    response = DTOSchoolNewsSearchResponse(message="학교 소식 조회에 성공하였습니다.", data=data)
    return response


async def insert_school_sub_service(dto: DTOSchoolSubInsert,
                                    db: Session,
                                    user_id: int) -> DTOSchoolSubInsertResponse:

    # 학교 페이지 확인
    school_page = db.query(SchoolPage).filter(SchoolPage.page_id == dto.page_id).first()
    if not school_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="학교 페이지가 존재하지 않습니다.")

    # 기존 구독 확인
    existing_sub = db.query(SchoolSub).filter(SchoolSub.page_id == dto.page_id,
                                              SchoolSub.user_id == user_id).first()
    if existing_sub:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 구독하였습니다.")

    school_sub = SchoolSub(user_id=user_id, page_id=dto.page_id)
    db.add(school_sub)
    db.commit()
    db.refresh(school_sub)

    data = DTOSchoolSubInsertResponse.SchoolSubInsertResult(**school_sub.__dict__)
    response = DTOSchoolSubInsertResponse(message="구독에 성공하였습니다.", data=data)
    return response


async def delete_school_sub_service(page_id: int,
                                    db: Session,
                                    user_id: int) -> BaseResponse:
    
    # 기존 구독 확인
    existing_sub = db.query(SchoolSub).filter(SchoolSub.page_id == page_id,
                                              SchoolSub.user_id == user_id).first()
    if not existing_sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="구독 상태가 아닙니다.")

    db.delete(existing_sub)
    db.commit()

    response = BaseResponse(message="구독 취소하였습니다.")
    return response


async def search_school_newsfeed_service(db: Session,
                                         user_id: int) -> DTOSchoolNewsSearchResponse:

    # 뉴스피드 모아보기
    newsfeed_list = (db.query(SchoolNews, UserNewsfeed)
                     .join(UserNewsfeed,
                           and_(SchoolNews.news_id == UserNewsfeed.news_id,
                                UserNewsfeed.user_id == user_id))
                     .filter(SchoolNews.is_del == False)
                     .order_by(desc(SchoolNews.reg_dtm))
                     .options(joinedload(SchoolNews.school_page),
                              joinedload(SchoolNews.user))
                     .all())

    if not newsfeed_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="뉴스피드가 없습니다.")

    data = [
        DTOSchoolNewsSearchResponse.SchoolNewsSearchResult(
            news_id=news.news_id,
            title=news.title,
            content=news.content,
            location=news.school_page.location,
            page_id=news.school_page.page_id,
            school_name=news.school_page.school_name,
            admin_name=news.user.name,
            reg_dtm=news.reg_dtm,
            upd_dtm=news.upd_dtm
        )
        for news, newsfeed in newsfeed_list]

    return DTOSchoolNewsSearchResponse(message="뉴스피드 조회에 성공하였습니다.", data=data)


async def insert_user_newsfeed(db: Session, page_id: int, news_id: int):
    try:
        # 학교 페이지 구독 정보
        school_sub_list = db.query(SchoolSub).filter(SchoolSub.page_id == page_id).all()

        # 구독 중인 모든 사용자 > 새로운 소식 ID 등록
        if school_sub_list:
            newsfeed_list = [UserNewsfeed(user_id=sub.user_id,
                                          news_id=news_id)
                             for sub in school_sub_list]

            db.add_all(newsfeed_list)
            db.commit()
    except Exception as e:
        logging.error("Exception during user newsfeed insert : %s", str(e), exc_info=True)
