from pydantic import BaseModel

class UserCreate(BaseModel):
    username:str
    password:str
    name:str
    age:int


class ShowUserJWT(BaseModel):
    id:int
    username:str
    password:str
    name:str
    age:int
    isActive:bool


class LoginUser(BaseModel):
    username:str
    password:str

class ShowUserFreeData(BaseModel):
    username:str
    age:int