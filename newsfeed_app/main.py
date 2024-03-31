from fastapi import FastAPI, HTTPException

from newsfeed_app.admin import admin_router
from newsfeed_app.common.database import engine
from newsfeed_app.common.exception.exception_handler import custom_exception_handler
from newsfeed_app.common.models import entity_models
from newsfeed_app.stdent import student_router
from newsfeed_app.user import user_router

# DB 테이블 초기화
entity_models.Base.metadata.create_all(bind=engine)

# swagger 정보
app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        title="뉴스피드 API",
        version="1.0.0",
        description="학교 소식을 전달하고 받아보는 '학교소식 뉴스피드'",
    )

# 예외 핸들러
app.add_exception_handler(HTTPException, custom_exception_handler)
app.add_exception_handler(Exception, custom_exception_handler)

# 라우터 추가
app.include_router(user_router.router, prefix="/api/v1/auth")
app.include_router(admin_router.router, prefix="/api/v1/admin")
app.include_router(student_router.router, prefix="/api/v1/student")
