from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class SignupRequest(BaseModel):
    """Schema for signup request."""
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Schema for simple message response."""
    status: str
    message: str
