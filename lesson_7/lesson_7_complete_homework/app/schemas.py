from pydantic import BaseModel


class PostBase(BaseModel):
    name: str
    description: str

    class Config:
        from_attributes = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        from_attributes = True


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

# Схема для постановки лайка посту
class LikeOperation(BaseModel):
    post_id: int
    user_id: int
    author_id: int