import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import React, { useEffect, useState, useCallback } from 'react';
import apiClient from '@/lib/api';
import PassageViewer from '@/components/PassageViewer';
import VocabTooltip from '@/components/VocabTooltip';
import QuestionList, { QuestionWithPossibleAnswer } from '@/components/QuestionList'; // Import new component and type

// Types (can be moved to a dedicated types file later)
// Interface for Answer as expected by QuestionWithPossibleAnswer
interface Answer {
  id: number;
  answer_text: string;
  created_at: string;
  question_id: number;
}

interface VocabEntry {
  id: number;
  word: string;
  meaning?: string | null;
  passage_id: number;
  created_at: string;
}

// Updated PassageData to use QuestionWithPossibleAnswer
interface PassageData {
  id: number;
  text: string;
  user_id?: number | null;
  created_at: string;
  questions: QuestionWithPossibleAnswer[]; // Use the more detailed question type
}

interface TooltipState {
  word: string | null;
  meaning: string | null;
  position: { x: number; y: number } | null;
  isVisible: boolean;
  isLoading: boolean;
  error: string | null;
  passageIdContext: number | null;
}

const PassageDetailPage = () => {
  const router = useRouter();
  const { id } = router.query;

  const [passageData, setPassageData] = useState<PassageData | null>(null);
  const [vocabEntries, setVocabEntries] = useState<VocabEntry[]>([]);
  const [tooltipState, setTooltipState] = useState<TooltipState>({
    word: null,
    meaning: null,
    position: null,
    isVisible: false,
    isLoading: false,
    error: null,
    passageIdContext: null,
  });
  const [pageLoading, setPageLoading] = useState<boolean>(true);
  const [pageError, setPageError] = useState<string | null>(null);

  // State for answer submission loading, mapping questionId to boolean
  const [questionLoadingState, setQuestionLoadingState] = useState<{ [key: number]: boolean }>({});

  // Fetch passage details (includes questions, potentially with answers if API provides them)
  useEffect(() => {
    if (id && typeof id === 'string') {
      setPageLoading(true);
      setPageError(null);
      // API endpoint might need to be adjusted if it doesn't return answers with questions
      // For now, assuming /passages/{id} returns PassageReadWithQuestionsSchema
      // and questions there might not have answers.
      // A separate call or updated backend schema might be needed for Q&A page.
      // Let's assume for now that `GET /passages/{id}` returns questions without answers,
      // and we'll fetch answers separately or rely on a different endpoint if needed.
      // OR, the backend for `GET /passages/{id}` could be enhanced to embed answers.
      // For this subtask, we'll assume `passageData.questions` might not have answers initially.
      // The answers will be populated by `handleAnswerSubmit` or if QuestionList fetches them.
      // The `GET /questions/passage/{passage_id}` endpoint in questions.py returns Qs with Answers.
      // Let's use that for populating questions with their answers.

      Promise.all([
        apiClient.get<PassageData>(`/passages/${id}`), // Fetches passage text and basic question structure
        apiClient.get<QuestionWithPossibleAnswer[]>(`/questions/passage/${id}`) // Fetches questions with answers
      ]).then(([passageRes, questionsRes]) => {
          const fetchedPassage = passageRes.data;
          fetchedPassage.questions = questionsRes.data; // Replace questions with those that include answers
          setPassageData(fetchedPassage);
      }).catch(err => {
          console.error("Error fetching passage or questions:", err);
          setPageError(`Failed to load passage data (ID: ${id}). It might not exist or an API error occurred.`);
      }).finally(() => {
          // Vocab fetch is independent for now
      });

      // Fetch vocabulary
      apiClient.get<VocabEntry[]>(`/vocab/passage/${id}`)
        .then(response => {
          setVocabEntries(response.data);
        })
        .catch(err => {
          console.error("Error fetching vocabulary:", err);
        })
        .finally(() => {
          setPageLoading(false); // All initial data fetches attempted
        });
    }
  }, [id]);

  const handleWordHighlight = useCallback(async (word: string, x: number, y: number) => {
    if (!passageData) return;
    setTooltipState({
      word, meaning: null, position: { x, y }, isVisible: true, isLoading: true, error: null, passageIdContext: passageData.id,
    });
    try {
      const response = await apiClient.post<VocabEntry>('/vocab/', { word: word, passage_id: passageData.id });
      const newOrUpdatedEntry = response.data;
      setTooltipState(prev => ({ ...prev, meaning: newOrUpdatedEntry.meaning || "Meaning not found.", isLoading: false }));
      setVocabEntries(prevEntries => {
        const existingIndex = prevEntries.findIndex(entry => entry.id === newOrUpdatedEntry.id);
        if (existingIndex > -1) {
          const updatedEntries = [...prevEntries];
          updatedEntries[existingIndex] = newOrUpdatedEntry;
          return updatedEntries;
        } else {
          return [...prevEntries, newOrUpdatedEntry];
        }
      });
    } catch (err: any) {
      console.error("Error fetching/creating vocab entry:", err);
      const apiErrorMessage = err.response?.data?.detail || "Could not fetch meaning.";
      setTooltipState(prev => ({ ...prev, meaning: null, error: apiErrorMessage, isLoading: false }));
    }
  }, [passageData]);

  const handleCloseTooltip = () => {
    setTooltipState(prev => ({ ...prev, isVisible: false, word: null, meaning: null, error: null }));
  };

  const handleAnswerSubmit = async (questionId: number, answerText: string) => {
    setQuestionLoadingState(prev => ({ ...prev, [questionId]: true }));
    try {
      const response = await apiClient.post<Answer>(`/questions/${questionId}/answer`, { answer_text: answerText });
      const submittedAnswer = response.data;

      // Update passageData to include the new answer
      setPassageData(prevPassageData => {
        if (!prevPassageData) return null;
        const updatedQuestions = prevPassageData.questions.map(q => {
          if (q.id === questionId) {
            return { ...q, answer: submittedAnswer };
          }
          return q;
        });
        return { ...prevPassageData, questions: updatedQuestions };
      });

    } catch (err: any) {
      console.error(`Error submitting answer for question ${questionId}:`, err);
      alert(`Failed to submit answer: ${err.response?.data?.detail || err.message}`); // Simple alert for now
    } finally {
      setQuestionLoadingState(prev => ({ ...prev, [questionId]: false }));
    }
  };

  if (pageLoading) {
    return <div className="container mx-auto px-4 py-8 text-center text-light-secondary-text dark:text-dark-secondary-text">Loading passage details...</div>;
  }
  if (pageError) {
    return <div className="container mx-auto px-4 py-8 text-center text-red-500 dark:text-red-400">{pageError}</div>;
  }
  if (!passageData) {
    return <div className="container mx-auto px-4 py-8 text-center text-light-secondary-text dark:text-dark-secondary-text">Passage data could not be loaded.</div>;
  }

  return (
    <>
      <Head>
        <title>Passage: {passageData.id} - Passage Analyzer</title>
        <meta name="description" content={`Analysis of passage ID ${passageData.id}. Questions and vocabulary insights.`} />
      </Head>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-6">
            <Link href="/submit-passage" legacyBehavior>
              <a className="text-light-primary dark:text-dark-primary hover:underline">&larr; Submit another passage</a>
            </Link>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold mb-2 text-light-text dark:text-dark-text">Passage Analysis</h1>
          <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text mb-6">
            Passage ID: {passageData.id} | Created: {new Date(passageData.created_at).toLocaleDateString()}
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-light-text dark:text-dark-text">Passage Text</h2>
            <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text mb-3">
              Select any single word in the passage below to get its definition.
            </p>
            <PassageViewer text={passageData.text} onWordHighlight={handleWordHighlight} />
          </section>

          {tooltipState.isVisible && tooltipState.word && tooltipState.position && (
            <VocabTooltip
              word={tooltipState.word}
              meaning={tooltipState.meaning}
              position={tooltipState.position}
              onClose={handleCloseTooltip}
              isLoading={tooltipState.isLoading}
              isVisible={tooltipState.isVisible}
              error={tooltipState.error}
            />
          )}

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-light-text dark:text-dark-text">Generated Questions</h2>
            <QuestionList
              questions={passageData.questions}
              onAnswerSubmit={handleAnswerSubmit}
              questionLoadingState={questionLoadingState}
            />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4 text-light-text dark:text-dark-text">Saved Vocabulary</h2>
            {vocabEntries.length > 0 ? (
              <ul className="space-y-3 content-card p-6">
                {vocabEntries.map(entry => (
                  <li key={entry.id} className="border-b border-light-border dark:border-dark-border pb-2 last:border-b-0">
                    <strong className="text-light-text dark:text-dark-text">{entry.word}:</strong>
                    <span className="ml-2 text-light-secondary-text dark:text-dark-secondary-text">
                      {entry.meaning || <em>Meaning not available.</em>}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-light-secondary-text dark:text-dark-secondary-text content-card p-6">
                No vocabulary words saved for this passage yet. Highlight words in the passage above to save them.
              </p>
            )}
          </section>
        </div>
      </div>
    </>
  );
};

export default PassageDetailPage;
