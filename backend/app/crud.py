# backend/app/crud.py
from typing import List, Optional, Sequence
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from sqlalchemy.orm import joinedload # For eager loading if needed

from .models import (
    User, UserBase,
    Passage, PassageBase,
    Question, QuestionBase,
    Answer, AnswerBase,
    VocabEntry, VocabEntryBase
)
from .schemas import (
    UserCreateSchema,
    PassageCreateSchema,
    QuestionCreateSchema,
    # AnswerCreateSchema, # Assuming Answer creation might be direct or part of Question handling
    VocabEntryCreateSchema
)
# Assuming llm_client might be used for fetching meanings if not provided
from .utils import llm_client


# --- User CRUD ---
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def create_user(db: Session, user_data: UserCreateSchema) -> User:
    # In a real app, hash the password here before saving
    # For now, storing plain text password from schema for simplicity
    db_user = User(email=user_data.email, hashed_password=user_data.password) # Hashing should be done in routes/services
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> Sequence[User]:
    statement = select(User).offset(skip).limit(limit)
    return db.exec(statement).all()

# --- Passage CRUD ---
def create_passage(db: Session, passage_data: PassageCreateSchema, user_id: Optional[int] = None) -> Passage:
    db_passage = Passage.model_validate(passage_data) #SQLModel v1 style
    if user_id:
        db_passage.user_id = user_id
    db.add(db_passage)
    db.commit()
    db.refresh(db_passage)
    return db_passage

def get_passage(db: Session, passage_id: int) -> Optional[Passage]:
    # Eager load questions and vocab along with the passage
    statement = select(Passage).where(Passage.id == passage_id).options(
        joinedload(Passage.questions),
        joinedload(Passage.vocab_entries)
    )
    return db.exec(statement).first()
    # return db.get(Passage, passage_id) # Simpler version without eager loading

def get_passages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> Sequence[Passage]:
    statement = select(Passage).where(Passage.user_id == user_id).offset(skip).limit(limit)
    return db.exec(statement).all()

def get_all_passages(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Passage]:
    statement = select(Passage).offset(skip).limit(limit)
    return db.exec(statement).all()

def delete_passage(db: Session, passage_id: int) -> bool:
    db_passage = db.get(Passage, passage_id)
    if db_passage:
        # Manually delete related questions, answers, and vocab entries if cascade is not set up or reliable
        # For Questions (and their Answers)
        questions_to_delete = db.exec(select(Question).where(Question.passage_id == passage_id)).all()
        for question in questions_to_delete:
            # Delete answers related to this question
            answers_to_delete = db.exec(select(Answer).where(Answer.question_id == question.id)).all()
            for answer in answers_to_delete:
                db.delete(answer)
            db.delete(question)

        # For VocabEntries
        vocab_entries_to_delete = db.exec(select(VocabEntry).where(VocabEntry.passage_id == passage_id)).all()
        for vocab_entry in vocab_entries_to_delete:
            db.delete(vocab_entry)

        db.delete(db_passage)
        db.commit()
        return True
    return False

# --- Question CRUD ---
def create_question(db: Session, question_data: QuestionCreateSchema, passage_id: int) -> Question:
    db_question = Question.model_validate(question_data, update={"passage_id": passage_id})
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def create_questions_bulk(db: Session, questions_data: List[QuestionCreateSchema], passage_id: int) -> List[Question]:
    db_questions = [Question.model_validate(q, update={"passage_id": passage_id}) for q in questions_data]
    db.add_all(db_questions)
    db.commit()
    # Refreshing each individually if IDs are needed immediately, or skip if not
    for db_q in db_questions:
        db.refresh(db_q)
    return db_questions

def get_question(db: Session, question_id: int) -> Optional[Question]:
    return db.get(Question, question_id)

def get_questions_by_passage(db: Session, passage_id: int) -> Sequence[Question]:
    statement = select(Question).where(Question.passage_id == passage_id)
    return db.exec(statement).all()

# --- Answer CRUD ---
# Assuming AnswerCreateSchema is similar to AnswerBase or defined elsewhere
# For simplicity, using AnswerBase directly for creation
def create_answer(db: Session, answer_data: AnswerBase, question_id: int) -> Answer:
    db_answer = Answer.model_validate(answer_data, update={"question_id": question_id})
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def get_answer(db: Session, answer_id: int) -> Optional[Answer]:
    return db.get(Answer, answer_id)

def get_answers_by_question(db: Session, question_id: int) -> Sequence[Answer]:
    statement = select(Answer).where(Answer.question_id == question_id)
    return db.exec(statement).all()


# --- VocabEntry CRUD ---
async def create_vocab_entry(db: Session, vocab_data: VocabEntryCreateSchema, passage_text_for_context: Optional[str] = None) -> VocabEntry:
    """
    Creates a vocabulary entry.
    If meaning is not provided and GOOGLE_API_KEY is set, it attempts to fetch it.
    Checks for duplicates (same word for the same passage).
    """
    # Check for existing entry for the same word and passage
    existing_entry_stmt = select(VocabEntry).where(
        VocabEntry.passage_id == vocab_data.passage_id,
        col(VocabEntry.word).ilike(vocab_data.word) # Case-insensitive check for word
    )
    existing_entry = db.exec(existing_entry_stmt).first()
    if existing_entry:
        # If meaning is not set on existing, and new data has meaning, update it
        if not existing_entry.meaning and vocab_data.meaning:
            existing_entry.meaning = vocab_data.meaning
            db.add(existing_entry)
            db.commit()
            db.refresh(existing_entry)
        elif not existing_entry.meaning and settings.GOOGLE_API_KEY and passage_text_for_context:
            # Fetch meaning if existing one is empty and new one isn't provided but can be fetched
            fetched_meaning = await llm_client.fetch_word_meaning(vocab_data.word, passage_text_for_context)
            if fetched_meaning:
                existing_entry.meaning = fetched_meaning
                db.add(existing_entry)
                db.commit()
                db.refresh(existing_entry)
        return existing_entry # Return the existing or updated entry

    # If no existing entry, create a new one
    db_vocab_entry = VocabEntry.model_validate(vocab_data)

    if not db_vocab_entry.meaning and settings.GOOGLE_API_KEY and passage_text_for_context:
        # print(f"Attempting to fetch meaning for '{db_vocab_entry.word}' as it's not provided.")
        fetched_meaning = await llm_client.fetch_word_meaning(db_vocab_entry.word, passage_text_for_context)
        if fetched_meaning:
            db_vocab_entry.meaning = fetched_meaning
        else:
            # print(f"Could not fetch meaning for '{db_vocab_entry.word}'. Will save without it.")
            pass # Save without meaning if not fetched

    try:
        db.add(db_vocab_entry)
        db.commit()
        db.refresh(db_vocab_entry)
        return db_vocab_entry
    except IntegrityError: # Handles race conditions if another request created it
        db.rollback()
        existing_entry = db.exec(existing_entry_stmt).first()
        if existing_entry:
            # Similar update logic as above if a race condition led to creation by another process
            if not existing_entry.meaning and vocab_data.meaning:
                existing_entry.meaning = vocab_data.meaning
            elif not existing_entry.meaning and settings.GOOGLE_API_KEY and passage_text_for_context:
                 fetched_meaning = await llm_client.fetch_word_meaning(vocab_data.word, passage_text_for_context)
                 if fetched_meaning:
                    existing_entry.meaning = fetched_meaning
            db.add(existing_entry)
            db.commit()
            db.refresh(existing_entry)
            return existing_entry
        else: # Should not happen if IntegrityError was due to uix_passage_word
            raise

async def update_vocab_entry_meaning(db: Session, vocab_entry_id: int, passage_text_for_context: Optional[str] = None) -> Optional[VocabEntry]:
    """
    Updates the meaning of an existing vocabulary entry using LLM if GOOGLE_API_KEY is set.
    If passage_text_for_context is provided, it's used for better meaning generation.
    """
    db_vocab_entry = db.get(VocabEntry, vocab_entry_id)
    if not db_vocab_entry:
        return None

    if not settings.GOOGLE_API_KEY:
        # print("Cannot update meaning: GOOGLE_API_KEY not configured.")
        return db_vocab_entry # Or raise an error, or return None to indicate no update

    # Fetch passage context if not directly provided and entry is linked to a passage
    if not passage_text_for_context and db_vocab_entry.passage_id:
        passage = get_passage(db, db_vocab_entry.passage_id)
        if passage:
            passage_text_for_context = passage.text

    # print(f"Attempting to fetch and update meaning for '{db_vocab_entry.word}'.")
    fetched_meaning = await llm_client.fetch_word_meaning(db_vocab_entry.word, passage_text_for_context)

    if fetched_meaning and fetched_meaning != db_vocab_entry.meaning:
        db_vocab_entry.meaning = fetched_meaning
        db.add(db_vocab_entry)
        db.commit()
        db.refresh(db_vocab_entry)
        # print(f"Meaning updated for '{db_vocab_entry.word}'.")
    # else:
        # print(f"Meaning not updated for '{db_vocab_entry.word}' (either no new meaning fetched or it's the same).")

    return db_vocab_entry


def get_vocab_entry(db: Session, vocab_entry_id: int) -> Optional[VocabEntry]:
    return db.get(VocabEntry, vocab_entry_id)

def get_vocab_entries_by_passage(db: Session, passage_id: int) -> Sequence[VocabEntry]:
    statement = select(VocabEntry).where(VocabEntry.passage_id == passage_id)
    return db.exec(statement).all()

def delete_vocab_entry(db: Session, vocab_entry_id: int) -> bool:
    db_vocab_entry = db.get(VocabEntry, vocab_entry_id)
    if db_vocab_entry:
        db.delete(db_vocab_entry)
        db.commit()
        return True
    return False
