from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=6)


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=1)


class QueryRequest(BaseModel):
	query: str = Field(min_length=3)
	history: list[str] | None = None


class SummarizeRequest(BaseModel):
	query: str = Field(min_length=3)


class RecommendationRequest(BaseModel):
	query: str = Field(min_length=3)
	issue_type: str | None = None


class CaseSummary(BaseModel):
	issue_type: str
	summary: str
	key_points: list[str]
	suggested_action: str
