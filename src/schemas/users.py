from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from enum import Enum
from fastapi import Form, HTTPException

class UserTypeEnum(str, Enum):
    user = "user"
    admin = "admin"

class MyselfOut(BaseModel):
    id: UUID
    username: str
    name: str | None
    email: EmailStr
    phone: str | None
    type: UserTypeEnum
    birthdate: datetime | None
    description: str | None
    img_link: str | None
    location: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    id: UUID
    name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None
    description: Optional[str] = None
    img_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate:
    def __init__(
        self,
        name: Optional[str] = Form(None),
        email: Union[EmailStr, str, None] = Form(None),
        phone: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        birthdate: Union[datetime, str, None] = Form(None),
        description: Optional[str] = Form(None),
    ):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.birthdate = birthdate
        self.description = description

        if birthdate:
            try:
                self.birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid birthdate format. Use YYYY-MM-DD.")
        else:
            self.birthdate = None

    def dict(self, exclude_unset=True):
        return {
            k: v for k, v in self.__dict__.items()
            if v not in ("", None)
        }