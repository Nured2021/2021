"""SQLite database layer using SQLAlchemy — users, documents, workspace, chat, API keys."""

from __future__ import annotations

import os
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
    create_engine, text,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

_DB_PATH = os.environ.get("EASY_AI_DB", str(Path(__file__).parent / "easy_ai.db"))
_ENGINE  = create_engine(f"sqlite:///{_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email       = Column(String(255), unique=True, nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    hashed_pw   = Column(String(255), nullable=False)
    role        = Column(String(32), nullable=False, default="student")  # student|teacher|professor|lawyer|admin
    avatar_url  = Column(String(500), nullable=True)
    is_active   = Column(Boolean, default=True)
    plan        = Column(String(32), default="free")  # free|pro|team|enterprise
    gen_count   = Column(Integer, default=0)           # daily generation counter
    gen_date    = Column(String(10), default="")       # YYYY-MM-DD for daily reset
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    documents    = relationship("Document",      back_populates="owner", cascade="all, delete-orphan")
    api_keys     = relationship("ApiKey",        back_populates="owner", cascade="all, delete-orphan")
    saved_templates = relationship("UserTemplate", back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    title       = Column(String(500), nullable=False)
    module      = Column(String(64), nullable=False, default="document")
    prompt      = Column(Text, nullable=False)
    body        = Column(Text, nullable=False)
    sections_json = Column(Text, nullable=True)       # JSON-encoded sections list
    pdf_url     = Column(String(500), nullable=True)
    docx_url    = Column(String(500), nullable=True)
    pptx_url    = Column(String(500), nullable=True)
    xlsx_url    = Column(String(500), nullable=True)
    version     = Column(Integer, default=1)
    parent_id   = Column(String(36), nullable=True)   # previous version
    is_deleted  = Column(Boolean, default=False)
    share_token = Column(String(64), nullable=True, unique=True, index=True)
    share_mode  = Column(String(16), nullable=True)   # "view" | "edit"
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")


class ApiKey(Base):
    __tablename__ = "api_keys"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    key         = Column(String(64), unique=True, nullable=False, index=True,
                         default=lambda: "eai_" + secrets.token_hex(28))
    name        = Column(String(255), nullable=False, default="My API Key")
    is_active   = Column(Boolean, default=True)
    request_count = Column(Integer, default=0)
    last_used   = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="api_keys")


class UserTemplate(Base):
    __tablename__ = "user_templates"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    module      = Column(String(64), nullable=False)
    label       = Column(String(255), nullable=False)
    prompt      = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="saved_templates")


class SearchIndex(Base):
    """Simple full-text search index. One row per document."""
    __tablename__ = "search_index"
    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id      = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id     = Column(String(36), nullable=True, index=True)
    module      = Column(String(64), nullable=True)
    full_text   = Column(Text, nullable=False)    # title + prompt + body concatenated
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Create all tables
# ---------------------------------------------------------------------------

Base.metadata.create_all(bind=_ENGINE)


# ---------------------------------------------------------------------------
# Session helper
# ---------------------------------------------------------------------------

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def create_user(db: Session, email: str, name: str, hashed_pw: str, role: str = "student") -> User:
    u = User(email=email, name=name, hashed_pw=hashed_pw, role=role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email, User.is_active == True).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def save_document(db: Session, user_id: str | None, title: str, module: str,
                  prompt: str, body: str, sections_json: str,
                  pdf_url: str = None, docx_url: str = None,
                  pptx_url: str = None, xlsx_url: str = None) -> Document:
    import json
    doc = Document(
        user_id=user_id, title=title, module=module, prompt=prompt,
        body=body, sections_json=sections_json,
        pdf_url=pdf_url, docx_url=docx_url, pptx_url=pptx_url, xlsx_url=xlsx_url,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # Index for search
    full_text = f"{title} {prompt} {body}".lower()
    idx = SearchIndex(doc_id=doc.id, user_id=user_id, module=module, full_text=full_text)
    db.add(idx)
    db.commit()
    return doc


def list_documents(db: Session, user_id: str | None, limit: int = 50) -> list[Document]:
    q = db.query(Document).filter(Document.is_deleted == False)
    if user_id:
        q = q.filter(Document.user_id == user_id)
    return q.order_by(Document.created_at.desc()).limit(limit).all()


def get_document_by_share_token(db: Session, token: str) -> Document | None:
    return db.query(Document).filter(Document.share_token == token, Document.is_deleted == False).first()


def search_documents(db: Session, query: str, user_id: str | None,
                     module: str | None = None, limit: int = 20) -> list[dict]:
    """Simple keyword search across full_text index."""
    words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
    if not words:
        return []

    q = db.query(SearchIndex, Document).join(Document, SearchIndex.doc_id == Document.id)
    if user_id:
        q = q.filter(SearchIndex.user_id == user_id)
    if module:
        q = q.filter(SearchIndex.module == module)
    q = q.filter(Document.is_deleted == False)

    results = []
    for idx, doc in q.limit(200).all():
        score = sum(1 for w in words if w in idx.full_text)
        if score:
            results.append((score, doc))

    results.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "id":       d.id,
            "title":    d.title,
            "module":   d.module,
            "prompt":   d.prompt[:150],
            "preview":  d.body[:200],
            "score":    sc,
            "pdf_url":  d.pdf_url,
            "docx_url": d.docx_url,
            "pptx_url": d.pptx_url,
            "xlsx_url": d.xlsx_url,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for sc, d in results[:limit]
    ]


def create_api_key(db: Session, user_id: str, name: str = "My API Key") -> ApiKey:
    k = ApiKey(user_id=user_id, name=name)
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


def get_api_key_owner(db: Session, key: str) -> User | None:
    ak = db.query(ApiKey).filter(ApiKey.key == key, ApiKey.is_active == True).first()
    if not ak:
        return None
    ak.request_count += 1
    ak.last_used = datetime.now(timezone.utc)
    db.commit()
    return get_user_by_id(db, ak.user_id)


def check_rate_limit(db: Session, user: User) -> tuple[bool, int]:
    """Returns (allowed, remaining). Resets daily counter."""
    from datetime import date
    today = date.today().isoformat()
    if user.gen_date != today:
        user.gen_count = 0
        user.gen_date  = today
        db.commit()

    limits = {"free": 10, "pro": 10000, "team": 50000, "enterprise": 999999}
    limit  = limits.get(user.plan, 10)
    if user.gen_count >= limit:
        return False, 0
    return True, limit - user.gen_count


def increment_gen_count(db: Session, user: User) -> None:
    user.gen_count += 1
    db.commit()


def save_user_template(db: Session, user_id: str, module: str, label: str, prompt: str) -> UserTemplate:
    t = UserTemplate(user_id=user_id, module=module, label=label, prompt=prompt)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def list_user_templates(db: Session, user_id: str) -> list[UserTemplate]:
    return db.query(UserTemplate).filter(UserTemplate.user_id == user_id).order_by(UserTemplate.created_at.desc()).all()
