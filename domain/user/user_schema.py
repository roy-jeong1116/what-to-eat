from pydantic import BaseModel, field_validator, model_validator

# 회원가입 스키마
class UserCreate(BaseModel):
    login_id: str
    username: str
    password1: str
    password2: str

    @field_validator("login_id" ,"username", "password1", "password2")  # noqa
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

# 회원탈퇴 스키마
class UserDelete(BaseModel):
    password: str

    @field_validator("password")  # noqa
    @staticmethod
    def not_empty(v):
        if not v or not v.strip():
            raise ValueError("비밀번호를 입력해야 합니다.")
        return v

class UserResponse(BaseModel):
    id: int

class LoginRequest(BaseModel):
    login_id: str
    password: str

    model_config = {
        "from_attributes": True
    }

    @field_validator("login_id", "password")  # noqa
    @staticmethod
    def not_empty(v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

# 로그인 API에 대한 응답 스키마는 FastAPI의 OAuth2PasswordRequestForm 사용
class Token(BaseModel):
    access_token: str
    token_type: str
    login_id: str
    user_id: int