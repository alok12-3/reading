# backend/app/api/passages.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session

from ..database import get_session
from .. import crud
from ..models import Passage, Question # For response model type hinting
from ..schemas import (
    PassageCreateSchema, PassageReadSchema, PassageReadWithQuestionsSchema,
    QuestionCreateSchema, QuestionReadSchema # For creating questions
)
from ..utils import llm_client # For generating questions

router = APIRouter()

@router.post("/", response_model=PassageReadWithQuestionsSchema, status_code=201)
async def create_passage_with_questions(
    *,
    session: Session = Depends(get_session),
    passage_in: PassageCreateSchema,
    num_questions: Optional[int] = Body(default=5, embed=True) # Number of questions to generate
):
    """
    Create a new passage.
    Then, generate comprehension questions for it using an LLM,
    and save these questions.
    """
    db_passage = crud.create_passage(db=session, passage_data=passage_in)
    if not db_passage:
        raise HTTPException(status_code=500, detail="Failed to create passage.")

    # Generate questions using LLM client
    try:
        # print(f"Generating {num_questions} questions for passage ID: {db_passage.id}")
        generated_q_data = await llm_client.generate_questions_from_passage(
            passage_text=db_passage.text,
            num_questions=num_questions
        )
        # print(f"Generated question data: {generated_q_data}")

        if not generated_q_data or (len(generated_q_data) == 1 and "Error:" in generated_q_data[0].get("question_text", "")):
            # Handle case where LLM returns an error message as a question or empty list
            # Log this, but don't necessarily fail the whole passage creation,
            # The passage is created, questions can be added later.
            # Or, decide if this should be a critical failure.
            # For now, we'll return the passage without questions if generation fails.
            print(f"Warning: Question generation failed or returned error for passage {db_passage.id}.")
            db_passage.questions = [] # Ensure questions list is empty
            return db_passage

        questions_to_create = [QuestionCreateSchema(question_text=q["question_text"]) for q in generated_q_data if q.get("question_text")]

        if questions_to_create:
            # print(f"Creating {len(questions_to_create)} questions in bulk for passage ID: {db_passage.id}")
            created_questions = crud.create_questions_bulk(
                db=session,
                questions_data=questions_to_create,
                passage_id=db_passage.id
            )
            # print(f"Successfully created questions: {[q.id for q in created_questions]}")
            # The db_passage object might not be automatically updated with these relationships
            # depending on session state and ORM configuration.
            # Re-fetch or manually assign if necessary for the response.
            # For PassageReadWithQuestionsSchema, we need the question objects.
            db_passage.questions = created_questions # Assign created questions for the response model
        else:
            # print(f"No valid questions to create for passage ID: {db_passage.id}")
            db_passage.questions = []


    except Exception as e:
        # Log the error, but the passage itself is created.
        # Decide if this should cause a 500 error for the whole request.
        print(f"Error during question generation or saving for passage {db_passage.id}: {e}")
        # Potentially, you might want to delete the passage if question generation is critical
        # crud.delete_passage(db=session, passage_id=db_passage.id)
        # raise HTTPException(status_code=500, detail=f"Passage created, but failed to generate/save questions: {str(e)}")
        # For now, let's return the passage and log the error.
        db_passage.questions = [] # Ensure questions list is empty if error occurred

    # The PassageReadWithQuestionsSchema expects a list of QuestionReadSchema objects.
    # crud.create_questions_bulk should return List[Question], which are SQLModel objects.
    # Pydantic should handle the conversion if the structure matches.
    return db_passage


@router.get("/{passage_id}", response_model=PassageReadWithQuestionsSchema)
def read_passage(
    *,
    session: Session = Depends(get_session),
    passage_id: int
):
    """
    Get a specific passage by its ID, along with its questions.
    Answers are not included here; they can be fetched via a question-specific endpoint.
    """
    db_passage = crud.get_passage(db=session, passage_id=passage_id)
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found")

    # Manually prepare questions for the response schema if not already correctly formatted
    # This is often handled by Pydantic if types match, but explicit conversion can be clearer
    # questions_for_response = [QuestionReadSchema.from_orm(q) for q in db_passage.questions]
    # passage_response = PassageReadWithQuestionsSchema.from_orm(db_passage)
    # passage_response.questions = questions_for_response
    # return passage_response
    # SQLModel's .from_orm (now model_validate) is usually good, direct return should work.

    return db_passage

@router.get("/", response_model=List[PassageReadSchema])
def read_all_passages(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all passages.
    """
    passages = crud.get_all_passages(db=session, skip=skip, limit=limit)
    return passages

@router.delete("/{passage_id}", status_code=200)
def delete_passage_endpoint(
    *,
    session: Session = Depends(get_session),
    passage_id: int
):
    """
    Delete a passage and its related questions, answers, and vocab entries.
    """
    success = crud.delete_passage(db=session, passage_id=passage_id)
    if not success:
        raise HTTPException(status_code=404, detail="Passage not found or could not be deleted")
    return {"message": "Passage and related data deleted successfully"}

# Potential future endpoint: Get passages by user
# @router.get("/user/{user_id}", response_model=List[PassageReadSchema])
# def read_user_passages(
#     user_id: int,
#     session: Session = Depends(get_session),
#     skip: int = 0,
#     limit: int = 10
# ):
#     db_user = crud.get_user(db=session, user_id=user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     passages = crud.get_passages_by_user(db=session, user_id=user_id, skip=skip, limit=limit)
#     return passages
