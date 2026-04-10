from pydantic import BaseModel, Field


class CandidateEmailDraftSchema(BaseModel):
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=6000)
