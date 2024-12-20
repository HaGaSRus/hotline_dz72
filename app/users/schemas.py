from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Role(BaseModel):
    name: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    password: str
    firstname: str
    roles: list

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    firstname: str
    roles: list

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    firstname: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateUserRolesRequest(BaseModel):
    roles: List[str]


class AllUserResponse(BaseModel):
    id: int
    username: str
    email: str
    firstname: str
    roles: List[str]

    class Config:
        from_attributes = True
