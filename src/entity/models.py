from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserTypeEnum(str, enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    type = Column(Enum(UserTypeEnum), nullable=False)
    birthdate = Column(DateTime, nullable=True)
    password = Column(String, nullable=False)
    description = Column(String, nullable=True)
    img_link = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    ratings = relationship("PostRating", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    tags = relationship("PostTag", back_populates="post")
    ratings = relationship("PostRating", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Tag(Base):
    __tablename__ = "tags"
    name = Column(String, primary_key=True)

    post_tags = relationship("PostTag", back_populates="tag")

class PostTag(Base):
    __tablename__ = "post_tags"
    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"))
    tag_name = Column(String, ForeignKey("tags.name", ondelete="CASCADE"))

    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="post_tags")

class PostRating(Base):
    __tablename__ = "post_ratings"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)

    user = relationship("User", back_populates="ratings")
    post = relationship("Post", back_populates="ratings")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)

    user = relationship("User", back_populates="refresh_tokens")
