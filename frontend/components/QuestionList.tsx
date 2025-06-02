import React from 'react';
import AnswerForm from './AnswerForm';

// Assuming Question and Answer types are defined in a shared types file or passed as generics
// For now, defining them inline for clarity based on previous structures.
interface Answer {
  id: number;
  answer_text: string;
  created_at: string;
  // question_id: number; // Usually part of the Answer model
}

export interface QuestionWithPossibleAnswer {
  id: number;
  question_text: string;
  passage_id: number;
  created_at: string;
  answer?: Answer | null; // Optional answer, as it might not exist
}

interface QuestionListProps {
  questions: QuestionWithPossibleAnswer[];
  onAnswerSubmit: (questionId: number, answerText: string) => Promise<void>;
  // Tracks loading state for each question's answer form
  questionLoadingState: { [key: number]: boolean };
}

const QuestionList: React.FC<QuestionListProps> = ({
  questions,
  onAnswerSubmit,
  questionLoadingState,
}) => {
  if (!questions || questions.length === 0) {
    return <p className="text-light-secondary-text dark:text-dark-secondary-text">No questions available for this passage yet.</p>;
  }

  return (
    <div className="space-y-6">
      {questions.map((question) => (
        <div key={question.id} className="p-4 rounded-lg border border-light-border dark:border-dark-border bg-light-card dark:bg-dark-card shadow-sm">
          <p className="font-semibold text-md mb-2 text-light-text dark:text-dark-text">
            {question.question_text}
          </p>
          {question.answer ? (
            <div className="p-3 rounded-md bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700">
              <p className="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Answer:</p>
              <p className="text-sm text-green-600 dark:text-green-200 whitespace-pre-wrap">
                {question.answer.answer_text}
              </p>
            </div>
          ) : (
            <AnswerForm
              questionId={question.id}
              onSubmit={onAnswerSubmit}
              isLoading={questionLoadingState[question.id] || false}
              // passageId={question.passage_id} // If needed by AnswerForm
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default QuestionList;
