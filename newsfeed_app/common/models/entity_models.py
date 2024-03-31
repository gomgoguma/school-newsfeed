from datetime import datetime

from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from newsfeed_app.common.database import Base


class User(Base):
    __tablename__ = "tb_users"
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    reg_dtm = Column(DateTime, nullable=False, default=datetime.now)

    user_info = relationship("UserInfo", uselist=False, cascade="all, delete-orphan")


class UserInfo(Base):
    __tablename__ = "tb_user_info"
    user_id = Column(BigInteger, ForeignKey("tb_users.user_id"), primary_key=True)
    name = Column(String(10), nullable=False)
    role = Column(String(10), nullable=False)

    school_page = relationship("SchoolPage", back_populates="user", cascade="all, delete-orphan")
    school_news = relationship("SchoolNews", back_populates="user", cascade="all, delete-orphan")
    user_newsfeed = relationship("UserNewsfeed", cascade="all, delete-orphan")


class UserNewsfeed(Base):
    __tablename__ = "tb_user_newsfeed"
    user_id = Column(BigInteger, ForeignKey("tb_user_info.user_id"), primary_key=True)
    news_id = Column(BigInteger, ForeignKey("tb_school_news.news_id"), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'news_id'),
    )


class SchoolPage(Base):
    __tablename__ = "tb_school_pages"
    page_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("tb_user_info.user_id"))
    location = Column(String(20), nullable=False)
    school_name = Column(String(20), nullable=False)
    reg_dtm = Column(DateTime, nullable=False, default=datetime.now)

    user = relationship("UserInfo", back_populates="school_page")
    news = relationship("SchoolNews", cascade="all, delete-orphan")
    school_sub = relationship("SchoolSub", back_populates="school_page", cascade="all, delete-orphan")


class SchoolNews(Base):
    __tablename__ = "tb_school_news"
    news_id = Column(BigInteger, primary_key=True)
    page_id = Column(BigInteger, ForeignKey("tb_school_pages.page_id"))
    user_id = Column(BigInteger, ForeignKey("tb_user_info.user_id"))
    title = Column(String(100), nullable=False)
    content = Column(String(500), nullable=False)
    reg_dtm = Column(DateTime, nullable=False, default=datetime.now)
    upd_dtm = Column(DateTime, nullable=True)
    is_del = Column(Boolean, nullable=False, default=False)
    del_dtm = Column(DateTime, nullable=True)

    user = relationship("UserInfo", back_populates="school_news")
    school_page = relationship("SchoolPage", back_populates="news")
    user_newsfeed = relationship("UserNewsfeed", cascade="all, delete-orphan")


class SchoolSub(Base):
    __tablename__ = "tb_school_subscriptions"
    user_id = Column(BigInteger, ForeignKey("tb_user_info.user_id"), primary_key=True)
    page_id = Column(BigInteger, ForeignKey("tb_school_pages.page_id"), primary_key=True)
    reg_dtm = Column(DateTime, nullable=False, default=datetime.now)

    school_page = relationship("SchoolPage", back_populates="school_sub")

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'page_id'),
    )
