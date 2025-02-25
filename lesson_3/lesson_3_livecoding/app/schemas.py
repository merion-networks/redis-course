from pydantic import BaseModel


# BEGIN YOUR SOLUTION HERE
class ItemBase(BaseModel):
    name: str
    description: str

    class Config:
        from_attributes = True


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True


# END


class UserCreate(BaseModel):
    name: str
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
