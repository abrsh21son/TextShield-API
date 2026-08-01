# utility/database/model.py
import uuid
from typing import Optional, List
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    email: str = Field(sa_column=Column(String, nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column(String, nullable=False))
    credits: int = Field(default=100, sa_column=Column(Integer, nullable=False))
    createdat: datetime = Field(default_factory=now_utc, sa_column=Column("createdAt", DateTime(timezone=True), nullable=False, server_default=text("NOW()")))

    apikeys: List["APIKey"] = Relationship(back_populates="user")
    text_analysis_requests: List["TextAnalysisRequest"] = Relationship(back_populates="user")


class Admin(SQLModel, table=True):
    __tablename__ = "admins"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    email: str = Field(sa_column=Column(String, nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column(String, nullable=False))
    createdat: datetime = Field(default_factory=now_utc, sa_column=Column("createdAt", DateTime(timezone=True), nullable=False, server_default=text("NOW()")))


class APIKey(SQLModel, table=True):
    __tablename__ = "apikeys"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    thekey: str = Field(sa_column=Column("theKey", String, unique=True, nullable=False))
    isactive: bool = Field(default=True, sa_column=Column("isActive", Boolean, nullable=False))
    createdat: datetime = Field(default_factory=now_utc, sa_column=Column("createdAt", DateTime(timezone=True), nullable=False, server_default=text("NOW()")))

    userid: uuid.UUID = Field(default=None, sa_column=Column("userId", PGUUID(as_uuid=True), ForeignKey("users.id")))
    user: Optional[User] = Relationship(back_populates="apikeys")


class TextAnalysisRequest(SQLModel, table=True):
    __tablename__ = "text_analysis_requests"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    inputtext: str = Field(sa_column=Column("inputText", String, nullable=False))
    isprofane: Optional[bool] = Field(default=None, sa_column=Column("isProfane", Boolean))
    toxicityscore: Optional[float] = Field(default=None, sa_column=Column("toxicityScore", Float))
    createdat: datetime = Field(default_factory=now_utc, sa_column=Column("createdAt", DateTime(timezone=True), nullable=False, server_default=text("NOW()")))

    userid: Optional[uuid.UUID] = Field(default=None, sa_column=Column("userId", PGUUID(as_uuid=True), ForeignKey("users.id")))
    user: Optional[User] = Relationship(back_populates="text_analysis_requests")

    usagelogs: List["UsageLog"] = Relationship(back_populates="request")


class UsageLog(SQLModel, table=True):
    __tablename__ = "usagelogs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    statuscode: int = Field(sa_column=Column("statusCode", Integer))
    issuccessful: bool = Field(default=False, sa_column=Column("isSuccessful", Boolean, nullable=False))
    endpointurl: str = Field(sa_column=Column("endpointUrl", String))
    ipaddress: str = Field(sa_column=Column("ipAddress", String))
    createdat: datetime = Field(default_factory=now_utc, sa_column=Column("createdAt", DateTime(timezone=True), nullable=False, server_default=text("NOW()")))

    requestid: Optional[uuid.UUID] = Field(default=None, sa_column=Column("requestId", PGUUID(as_uuid=True), ForeignKey("text_analysis_requests.id")))
    request: Optional[TextAnalysisRequest] = Relationship(back_populates="usagelogs")

    userid: Optional[uuid.UUID] = Field(default=None, sa_column=Column("userId", PGUUID(as_uuid=True), ForeignKey("users.id")))
