from pydantic import BaseModel, EmailStr

# Схема для реєстрації користувача
class UserRegister(BaseModel):
    email: EmailStr
    password: str

# Схема для логіну
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Схема для токену
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
