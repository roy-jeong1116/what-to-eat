from pydantic import BaseModel, field_validator, model_validator

# 회원가입 스키마
class UserCreate(BaseModel):
    username: str
    password1: str
    password2: str

    @field_validator("username", "password1", "password2")
    @staticmethod
    def not_empty(v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @model_validator(mode="after")
    def password_match(self):
        if self.password1 != self.password2:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self

# 로그인 API에 대한 출력 스키마는 FastAPI의 OAuth2PasswordRequestForm 사용
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str