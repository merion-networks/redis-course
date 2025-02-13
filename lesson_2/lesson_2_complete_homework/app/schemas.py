from pydantic import BaseModel


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


# BEGIN YOUR SOLUTION HERE
# Схема для создания/регистрации пользователя
class UserCreate(BaseModel):
    name: str
    username: str
    password: str


# Схема для вывода информации о пользователе (без пароля)
class UserOut(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True


# Схема для передачи данных логина
class LoginRequest(BaseModel):
    username: str
    password: str


# Схема для ответа при успешном логине (сессионный токен)
class LoginResponse(BaseModel):
    token: str
# END
