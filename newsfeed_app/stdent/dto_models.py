from datetime import datetime

from pydantic import BaseModel, Field

from newsfeed_app.common.models.response_model import BaseResponse


class DTOSchoolSubInsert(BaseModel):
    page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")


class DTOSchoolSubInsertResponse(BaseResponse):
    class SchoolSubInsertResult(BaseModel):
        page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")
        user_id: int = Field(..., examples=["1"], description="사용자 ID")
        reg_dtm: datetime = Field(..., examples=["2024-03-31T17:01:20.834Z"], description="등록일시")

    data: SchoolSubInsertResult


class DTOMySchoolSubSearchResponse(BaseResponse):
    class SchoolSubSearchResult(BaseModel):
        page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")
        school_name: str = Field(..., examples=["역삼초등학교"], description="학교 이름")
        location: str = Field(..., examples=["역삼동"], description="지역")
        reg_dtm: datetime = Field(..., examples=["2024-03-31T17:01:20.834Z"], description="등록일시")

    data: list[SchoolSubSearchResult] | None = None


class DTOSchoolNewsSearchResponse(BaseResponse):
    class SchoolNewsSearchResult(BaseModel):
        news_id: int = Field(..., examples=["1"], description="학교 소식 ID")
        title: str = Field(..., examples=["역삼초등학교 소식"], description="학교 소식 제목")
        content: str = Field(..., examples=["역삼초등학교 소식입니다."], description="학교 소식 내용")
        location: str = Field(..., examples=["역삼동"], description="지역")
        page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")
        school_name: str = Field(..., examples=["역삼초등학교"], description="학교 이름")
        admin_name: str = Field(..., examples=["역삼초관리자"], description="학교 관리자 이름")
        reg_dtm: datetime = Field(..., examples=["2024-03-31T17:01:20.834Z"], description="등록일시")
        upd_dtm: datetime | None = Field(None, examples=["2024-03-31T17:01:20.834Z"], description="수정일시")

    data: list[SchoolNewsSearchResult] | None = None
