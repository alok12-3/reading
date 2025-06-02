# backend/app/utils/llm_client.py
import os
import re
import json
from typing import List, Dict, Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlmodel import Session

from ..config import settings
from ..models import VocabEntry # Assuming VocabEntry is needed for context or type hinting

# Configure the LLM client (Gemini Flash)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GOOGLE_API_KEY)

def strip_markdown_json(json_string: str) -> str:
    """
    Strips the markdown "```json" prefix/suffix and leading/trailing whitespace
    from a JSON string.
    """
    match = re.search(r"```json\s*(.*?)\s*```", json_string, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return json_string.strip()

async def generate_questions_from_passage(passage_text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generates comprehension questions from a given passage using an LLM.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI assistant that generates comprehension questions based on a given text passage."),
            ("human",
             "Please generate {num_questions} distinct comprehension questions based on the following passage. "
             "Ensure the questions are relevant and cover different aspects of the text. "
             "Return the questions as a JSON list of objects, where each object has a 'question_text' field. "
             "For example: [{\"question_text\": \"What is the main idea?\"}, ...]\n\n"
             "Passage:\n{passage}")
        ]
    )
    parser = StrOutputParser()
    chain = prompt_template | llm | parser

    try:
        raw_response = await chain.ainvoke({"passage": passage_text, "num_questions": num_questions})
        # print(f"Raw LLM response for questions: {raw_response}") # For debugging

        cleaned_response = strip_markdown_json(raw_response)
        # print(f"Cleaned LLM response for questions: {cleaned_response}") # For debugging

        questions_data = json.loads(cleaned_response)

        if not isinstance(questions_data, list):
            raise ValueError("LLM did not return a list of questions.")

        validated_questions = []
        for q_data in questions_data:
            if isinstance(q_data, dict) and "question_text" in q_data and isinstance(q_data["question_text"], str):
                validated_questions.append({"question_text": q_data["question_text"]})
            else:
                # print(f"Skipping invalid question data: {q_data}") # For debugging
                pass # Skip malformed entries

        return validated_questions[:num_questions] # Ensure we don't exceed num_questions

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from LLM for questions: {e}")
        print(f"Problematic response string: {cleaned_response}")
        return [{"question_text": "Error: Could not parse questions from LLM response."}]
    except Exception as e:
        print(f"An unexpected error occurred in generate_questions_from_passage: {e}")
        return [{"question_text": f"Error: An unexpected error occurred - {str(e)}"}]


async def fetch_word_meaning(word: str, passage_context: Optional[str] = None) -> Optional[str]:
    """
    Fetches the meaning of a word, optionally using passage context, via LLM.
    Returns the meaning as a string or None if not found or an error occurs.
    """
    system_message = (
        "You are an AI assistant that provides concise definitions for words. "
        "If context from a passage is provided, prioritize the meaning relevant to that context. "
        "Return only the definition as a plain string, without any introductory phrases like 'The meaning is...' or markdown."
    )

    human_message_template = "What is the meaning of the word '{word}'?"
    if passage_context:
        human_message_template += "\n\nConsider this context from the passage: \"{passage_context}\""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", human_message_template)
    ])
    parser = StrOutputParser()
    chain = prompt | llm | parser

    try:
        response = await chain.ainvoke({"word": word, "passage_context": passage_context})
        # print(f"Raw LLM response for meaning of '{word}': {response}") # For debugging

        # Basic cleaning: remove potential markdown-like quotes or common LLM fluff.
        cleaned_response = response.strip().replace("```", "").replace("\"", "")

        if not cleaned_response or len(cleaned_response) < 3: # Arbitrary short length check
            # print(f"Meaning too short or empty for '{word}', likely not found.") # For debugging
            return None # Or a more specific "Meaning not found"

        return cleaned_response

    except Exception as e:
        print(f"An error occurred while fetching meaning for '{word}': {e}")
        return None


# Example usage (can be removed or commented out)
if __name__ == "__main__":
    import asyncio

    async def main():
        # Test question generation
        sample_passage = (
            "The quick brown fox jumps over the lazy dog. This sentence is famous "
            "for containing all letters of the English alphabet. It's often used "
            "for testing typewriters and keyboards."
        )
        print(f"Generating questions for: \"{sample_passage[:50]}...\"")
        questions = await generate_questions_from_passage(sample_passage, num_questions=2)
        print("Generated Questions:")
        for q in questions:
            print(f"- {q['question_text']}")

        print("\n---\n")

        # Test word meaning
        sample_word = "quick"
        print(f"Fetching meaning for '{sample_word}' with context...")
        meaning_with_context = await fetch_word_meaning(sample_word, passage_context=sample_passage)
        if meaning_with_context:
            print(f"Meaning of '{sample_word}' (with context): {meaning_with_context}")
        else:
            print(f"Could not fetch meaning for '{sample_word}' with context.")

        sample_word_no_context = "alphabet"
        print(f"\nFetching meaning for '{sample_word_no_context}' without context...")
        meaning_no_context = await fetch_word_meaning(sample_word_no_context)
        if meaning_no_context:
            print(f"Meaning of '{sample_word_no_context}' (no context): {meaning_no_context}")
        else:
            print(f"Could not fetch meaning for '{sample_word_no_context}' without context.")

        print("\n---\n")
        # Test with a word that might not have a straightforward meaning or is too common
        tricky_word = "the"
        print(f"Fetching meaning for tricky word '{tricky_word}'...")
        meaning_tricky = await fetch_word_meaning(tricky_word)
        if meaning_tricky:
            print(f"Meaning of '{tricky_word}': {meaning_tricky}")
        else:
            print(f"Could not fetch meaning for '{tricky_word}' (or it was deemed too short/empty).")

    # Python 3.7+
    # asyncio.run(main()) # This will not run in the agent's environment but is useful for local testing.
    # For older Python versions, you might need:
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
