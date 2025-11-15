from pydantic import BaseModel

class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    token: str


class UserInfoResponse(BaseModel):
    username: str
    login: str
