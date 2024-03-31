from datetime import datetime
from pydantic import BaseModel, Field, constr
from newsfeed_app.common.models.response_model import BaseResponse


class DTOSchoolPageInsert(BaseModel):
    location: constr(min_length=1, max_length=20,
                     strip_whitespace=True, pattern=r'^[가-힣]+$') \
        = Field(...,
                examples=["역삼동"],
                description="지역(1자~20자): 공백 없이 한글만 입력해 주세요.")

    school_name: constr(min_length=1, max_length=20,
                        strip_whitespace=True, pattern=r'^[가-힣]+$') \
        = Field(...,
                examples=["역삼초등학교"],
                description="학교 이름(1자~20자): 공백 없이 한글만 입력해 주세요.")


class DTOSchoolPageInsertResponse(BaseResponse):
    class SchoolPageInsertResult(BaseModel):
        page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")
        user_id: int = Field(..., examples=["1"], description="사용자 ID")
        location: str = Field(..., examples=["역삼동"], description="지역")
        school_name: str = Field(..., examples=["역삼초등학교"], description="학교 이름")

    data: SchoolPageInsertResult


class DTOSchoolNewsInsert(BaseModel):
    page_id: int = Field(..., examples=[1], description="학교 페이지 ID")
    title: constr(min_length=1, max_length=100,
                  strip_whitespace=True, pattern=r'^[a-zA-Z가-힣0-9\s]+$') \
        = Field(..., examples=["역삼초등학교 소식"], description="제목(1자~100자): 특수문자를 제외한 문자를 입력해 주세요.")

    content: constr(min_length=10, max_length=500, strip_whitespace=True) \
        = Field(..., examples=["역삼초등학교 소식입니다."], max_length=500, description="내용(1자~500자)")


class SchoolNewsResult(BaseModel):
    news_id: int = Field(..., examples=["1"], description="학교 소식 ID")
    page_id: int = Field(..., examples=["1"], description="학교 페이지 ID")
    user_id: int = Field(..., examples=["1"], description="사용자 ID")
    title: str = Field(..., examples=["역삼초등학교 소식"], description="학교 소식 제목")
    content: str = Field(..., examples=["역삼초등학교 소식입니다."], description="학교 소식 내용")
    reg_dtm: datetime = Field(..., examples=["2024-03-31T17:01:20.834Z"], description="등록일시")
    upd_dtm: datetime | None = Field(None, examples=["2024-03-31T17:01:20.834Z"], description="수정일시")


class DTOSchoolNewsInsertResponse(BaseResponse):
    data: SchoolNewsResult


class DTOSchoolPageUpdate(BaseModel):
    news_id: int = Field(..., examples=[1], description="학교 소식 ID")
    title: constr(min_length=1, max_length=100, strip_whitespace=True,
                  pattern=r'^[a-zA-Z가-힣0-9\s]+$') \
        = Field(..., examples=["역삼초등학교 소식"], description="제목(1자~100자): 특수문자를 제외한 문자를 입력해주세요.")
    content: constr(min_length=10, max_length=500, strip_whitespace=True) \
        = Field(..., examples=["역삼초등학교 소식입니다."], max_length=500, description="내용(1자~500자)")


class DTOSchoolPageUpdateResponse(BaseResponse):
    data: SchoolNewsResult
