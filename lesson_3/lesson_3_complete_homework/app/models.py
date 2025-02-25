from sqlalchemy import String, Integer, Column
from app.database import Base


# BEGIN YOUR SOLUTION HERE
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    author_id = Column(Integer, index=True)  # идентификатор автора поста


# END


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
