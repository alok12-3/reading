import React, { useState } from 'react';

interface AnswerFormProps {
  questionId: number;
  onSubmit: (questionId: number, answerText: string) => Promise<void>; // Make onSubmit async
  isLoading: boolean;
  passageId?: number; // Optional: if needed for context, though API endpoint uses questionId
}

const AnswerForm: React.FC<AnswerFormProps> = ({
  questionId,
  onSubmit,
  isLoading,
}) => {
  const [answerText, setAnswerText] = useState<string>('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!answerText.trim()) {
      alert('Answer cannot be empty.'); // Basic validation
      return;
    }
    await onSubmit(questionId, answerText);
    // Optionally clear the form if it's still visible (e.g. if submission doesn't hide it)
    // setAnswerText(''); // This might be better handled by parent component re-rendering
  };

  return (
    <form onSubmit={handleSubmit} className="mt-2 space-y-3">
      <textarea
        value={answerText}
        onChange={(e) => setAnswerText(e.target.value)}
        placeholder="Type your answer here..."
        rows={3}
        disabled={isLoading}
        className={`
          w-full p-3 border rounded-md shadow-sm
          text-sm leading-relaxed
          bg-light-background dark:bg-dark-card
          text-light-text dark:text-dark-text
          border-light-border dark:border-dark-border
          focus:ring-1 focus:ring-light-primary dark:focus:ring-dark-primary
          focus:border-transparent outline-none transition-shadow duration-150 ease-in-out
          resize-y
          ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}
        `}
        aria-label={`Answer for question ${questionId}`}
      />
      <button
        type="submit"
        disabled={isLoading || !answerText.trim()}
        className="btn btn-primary text-sm py-2 px-4 rounded-md
                   disabled:opacity-60 disabled:cursor-not-allowed
                   bg-light-primary/80 hover:bg-light-primary
                   dark:bg-dark-primary/80 dark:hover:dark-primary"
      >
        {isLoading ? 'Submitting...' : 'Submit Answer'}
      </button>
    </form>
  );
};

export default AnswerForm;
