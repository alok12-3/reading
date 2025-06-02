# backend/app/api/questions.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from .. import crud
from ..models import Question, Answer # For response model type hinting
from ..schemas import (
    QuestionReadSchema, AnswerCreateSchema, AnswerReadSchema,
    QuestionWithPossibleAnswerResponse # Custom schema for GET response
)

router = APIRouter()

@router.get("/passage/{passage_id}", response_model=List[QuestionWithPossibleAnswerResponse])
def read_questions_for_passage(
    *,
    session: Session = Depends(get_session),
    passage_id: int
):
    """
    Get all questions for a specific passage.
    For each question, if an answer exists, it's included.
    (Note: This currently assumes one answer per question for simplicity in response.
     If multiple answers are possible, the response model and logic would need adjustment.)
    """
    db_passage = crud.get_passage(db=session, passage_id=passage_id)
    if not db_passage:
        raise HTTPException(status_code=404, detail="Passage not found, cannot fetch questions.")

    questions = crud.get_questions_by_passage(db=session, passage_id=passage_id)

    response_data: List[QuestionWithPossibleAnswerResponse] = []
    for q_model in questions:
        # Fetch the first answer for this question, if any.
        # If a question can have multiple answers, you might want a list here.
        answer_model = crud.get_answers_by_question(db=session, question_id=q_model.id)

        q_response = QuestionWithPossibleAnswerResponse.model_validate(q_model) # SQLModel v1
        if answer_model:
            # Assuming QuestionWithPossibleAnswerResponse.answer expects a single AnswerForQuestionResponse
            # and get_answers_by_question returns a list. Take the first if available.
            q_response.answer = answer_model[0] # Pydantic should convert Answer model to AnswerForQuestionResponse
        else:
            q_response.answer = None
        response_data.append(q_response)

    return response_data

@router.post("/{question_id}/answer", response_model=AnswerReadSchema, status_code=201)
def create_answer_for_question(
    *,
    session: Session = Depends(get_session),
    question_id: int,
    answer_in: AnswerCreateSchema # Assuming AnswerCreateSchema is defined (e.g., just text)
                                 # If AnswerCreateSchema is just AnswerBase, that's fine.
):
    """
    Create an answer for a specific question.
    Currently, this allows creating multiple answers for the same question if called multiple times.
    If only one answer per question is desired, add logic to check/update existing.
    """
    db_question = crud.get_question(db=session, question_id=question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found, cannot create answer.")

    # For simplicity, let's assume AnswerCreateSchema is just AnswerBase.
    # If it has more fields, adjust accordingly.
    # answer_data = AnswerBase(answer_text=answer_in.answer_text)

    # The crud.create_answer expects an AnswerBase like object and question_id
    db_answer = crud.create_answer(db=session, answer_data=answer_in, question_id=question_id)
    if not db_answer:
        raise HTTPException(status_code=500, detail="Failed to create answer.")

    return db_answer

@router.get("/{question_id}", response_model=QuestionWithPossibleAnswerResponse)
def read_single_question_with_answer(
    *,
    session: Session = Depends(get_session),
    question_id: int
):
    """
    Get a single question by its ID, including its answer(s) if available.
    """
    db_question = crud.get_question(db=session, question_id=question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    answers = crud.get_answers_by_question(db=session, question_id=db_question.id)

    response = QuestionWithPossibleAnswerResponse.model_validate(db_question)
    if answers:
        response.answer = answers[0] # Taking the first answer for the response model
    else:
        response.answer = None

    return response

# Potential future endpoint: Update an answer
# @router.put("/answers/{answer_id}", response_model=AnswerReadSchema)
# def update_existing_answer(
#     answer_id: int,
#     answer_in: AnswerCreateSchema, # Or a specific AnswerUpdateSchema
#     session: Session = Depends(get_session)
# ):
#     db_answer = crud.get_answer(db=session, answer_id=answer_id)
#     if not db_answer:
#         raise HTTPException(status_code=404, detail="Answer not found")
#     # Update logic here, e.g.
#     # db_answer.answer_text = answer_in.answer_text
#     # session.add(db_answer)
#     # session.commit()
#     # session.refresh(db_answer)
#     # return db_answer
#     raise HTTPException(status_code=501, detail="Not implemented")

# Potential future endpoint: Delete an answer
# @router.delete("/answers/{answer_id}", status_code=200)
# def delete_existing_answer(
#     answer_id: int,
#     session: Session = Depends(get_session)
# ):
#     # success = crud.delete_answer(db=session, answer_id=answer_id) # Assuming crud.delete_answer exists
#     # if not success:
#     #     raise HTTPException(status_code=404, detail="Answer not found or could not be deleted")
#     # return {"message": "Answer deleted successfully"}
#     raise HTTPException(status_code=501, detail="Not implemented")
