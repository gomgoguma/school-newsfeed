from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    message: str = Field(..., examples=["성공"], description="결과 메시지")
