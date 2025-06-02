# backend/app/schemas.py
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel
from .models import UserBase, PassageBase, QuestionBase, AnswerBase, VocabEntryBase # Ensure relative import

# User Schemas
class UserCreateSchema(UserBase):
    password: str

class UserReadSchema(UserBase):
    id: int
    created_at: datetime

# Passage Schemas
class PassageCreateSchema(PassageBase):
    user_id: Optional[int] = None # Optional user association

class PassageReadSchema(PassageBase):
    id: int
    user_id: Optional[int]
    created_at: datetime

class QuestionReadSchema(QuestionBase): # Basic Question info
    id: int
    passage_id: int
    created_at: datetime

class PassageReadWithQuestionsSchema(PassageReadSchema):
    questions: List[QuestionReadSchema] = []

# Question Schemas
class QuestionCreateSchema(QuestionBase):
    pass

class AnswerReadSchema(AnswerBase):
    id: int
    question_id: int
    created_at: datetime

# VocabEntry Schemas
class VocabEntryCreateSchema(VocabEntryBase):
    passage_id: int

class VocabEntryReadSchema(VocabEntryBase):
    id: int
    passage_id: int
    created_at: datetime

# --- API Specific Response Schemas ---
class QuestionInPassageResponse(SQLModel):
    id: int
    question_text: str

class PassageResponse(PassageReadSchema):
    questions: List[QuestionInPassageResponse] = []

class AnswerForQuestionResponse(SQLModel):
    id: int
    answer_text: str
    created_at: datetime

class QuestionWithPossibleAnswerResponse(QuestionReadSchema):
    answer: Optional[AnswerForQuestionResponse] = None
