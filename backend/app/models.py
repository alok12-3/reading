# backend/app/models.py
from typing import List, Optional
from datetime import datetime
import sqlalchemy as sa # Ensure this import is present
from sqlmodel import Field, Relationship, SQLModel

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field() # Hashing will be handled in CRUD/routes
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    passages: List["Passage"] = Relationship(back_populates="user")

class PassageBase(SQLModel):
    text: str

class Passage(PassageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional[User] = Relationship(back_populates="passages")
    questions: List["Question"] = Relationship(back_populates="passage")
    vocab_entries: List["VocabEntry"] = Relationship(back_populates="passage")

class QuestionBase(SQLModel):
    question_text: str

class Question(QuestionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    passage_id: int = Field(foreign_key="passage.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    passage: Passage = Relationship(back_populates="questions")
    answers: List["Answer"] = Relationship(back_populates="question")

class AnswerBase(SQLModel):
    answer_text: str

class Answer(AnswerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    question: Question = Relationship(back_populates="answers")

class VocabEntryBase(SQLModel):
    word: str
    meaning: Optional[str] = Field(default=None) # Meaning can be fetched later

class VocabEntry(VocabEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    passage_id: int = Field(foreign_key="passage.id")
    # word: str is inherited from VocabEntryBase and will be part of the table
    # meaning: Optional[str] is inherited
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    passage: Passage = Relationship(back_populates="vocab_entries")

    __table_args__ = (sa.UniqueConstraint("passage_id", "word", name="uix_passage_word"),)
