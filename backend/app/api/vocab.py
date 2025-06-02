# backend/app/api/vocab.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session

from ..database import get_session
from .. import crud
from ..models import VocabEntry, Passage # For type hinting and fetching passage text
from ..schemas import VocabEntryCreateSchema, VocabEntryReadSchema
from ..config import settings # To check if GOOGLE_API_KEY is set

router = APIRouter()

@router.post("/", response_model=VocabEntryReadSchema, status_code=201)
async def create_or_update_vocab_entry(
    *,
    session: Session = Depends(get_session),
    vocab_in: VocabEntryCreateSchema
):
    """
    Create a new vocabulary entry or update an existing one (if found for the same word & passage).
    If the meaning is not provided or is null on an existing entry,
    and GOOGLE_API_KEY is configured, it attempts to fetch the meaning using an LLM.
    """
    passage_text_for_context: Optional[str] = None
    if vocab_in.passage_id:
        passage = crud.get_passage(db=session, passage_id=vocab_in.passage_id)
        if not passage:
            raise HTTPException(status_code=404, detail=f"Passage with id {vocab_in.passage_id} not found.")
        passage_text_for_context = passage.text

    # crud.create_vocab_entry handles both creation, fetching meaning, and duplicate checks
    try:
        db_vocab_entry = await crud.create_vocab_entry(
            db=session,
            vocab_data=vocab_in,
            passage_text_for_context=passage_text_for_context
        )
        if not db_vocab_entry:
            # This case should ideally be handled within crud.create_vocab_entry by raising an error
            # or returning the existing one. If it returns None, it's an unexpected state.
            raise HTTPException(status_code=500, detail="Could not create or retrieve vocabulary entry.")
        return db_vocab_entry

    except HTTPException as e: # Catch HTTPExceptions from deeper calls if any
        raise e
    except Exception as e:
        # Log the full error for debugging
        print(f"Unexpected error in create_or_update_vocab_entry: {e}")
        # Potentially catch specific errors like IntegrityError if not handled in CRUD
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/passage/{passage_id}", response_model=List[VocabEntryReadSchema])
def read_vocab_entries_for_passage(
    *,
    session: Session = Depends(get_session),
    passage_id: int
):
    """
    Get all vocabulary entries associated with a specific passage.
    """
    # Check if passage exists first (optional, but good practice)
    db_passage = crud.get_passage(db=session, passage_id=passage_id)
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found, cannot fetch vocabulary entries.")

    vocab_entries = crud.get_vocab_entries_by_passage(db=session, passage_id=passage_id)
    return vocab_entries


@router.put("/{vocab_entry_id}/update-meaning", response_model=VocabEntryReadSchema)
async def update_meaning_for_vocab_entry(
    *,
    session: Session = Depends(get_session),
    vocab_entry_id: int
):
    """
    Explicitly request to update the meaning of a vocabulary entry using the LLM.
    This is useful if an entry was created without a meaning or if the meaning needs refreshing.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="Cannot update meaning: GOOGLE_API_KEY is not configured.")

    db_vocab_entry = await crud.update_vocab_entry_meaning(db=session, vocab_entry_id=vocab_entry_id)

    if not db_vocab_entry:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found.")

    if not db_vocab_entry.meaning:
        # This might happen if LLM failed to provide a meaning
        # The status code here could be 200 with a message, or still 200 with the entry
        # For now, return the entry as is. Client can check if meaning is populated.
        print(f"Warning: Meaning for vocab entry {vocab_entry_id} could not be fetched or was empty.")

    return db_vocab_entry


@router.get("/{vocab_entry_id}", response_model=VocabEntryReadSchema)
def read_single_vocab_entry(
    *,
    session: Session = Depends(get_session),
    vocab_entry_id: int
):
    """
    Get a single vocabulary entry by its ID.
    """
    db_vocab_entry = crud.get_vocab_entry(db=session, vocab_entry_id=vocab_entry_id)
    if not db_vocab_entry:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")
    return db_vocab_entry

@router.delete("/{vocab_entry_id}", status_code=200)
def delete_vocab_entry_endpoint(
    *,
    session: Session = Depends(get_session),
    vocab_entry_id: int
):
    """
    Delete a vocabulary entry.
    """
    success = crud.delete_vocab_entry(db=session, vocab_entry_id=vocab_entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vocabulary entry not found or could not be deleted")
    return {"message": "Vocabulary entry deleted successfully"}
