import React, { useState } from 'react';
import Head from 'next/head';
import PassageInput from '@/components/PassageInput'; // Using path alias
// import apiClient from '@/lib/api'; // To be used later for API calls

const SubmitPassagePage = () => {
  const [passageText, setPassageText] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // const [error, setError] = useState<string | null>(null);
  // const [submittedPassage, setSubmittedPassage] = useState<any | null>(null); // Replace 'any' with actual Passage type

  const handlePassageChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPassageText(event.target.value);
  };

  const handleSubmit = async () => {
    if (!passageText.trim()) {
      // setError('Passage text cannot be empty.');
      alert('Passage text cannot be empty.'); // Simple alert for now
      return;
    }
    setIsLoading(true);
    // setError(null);
    // setSubmittedPassage(null);

    try {
      // TODO: API call logic will be added in a later subtask
      // const response = await apiClient.post('/passages/', { text: passageText });
      // setSubmittedPassage(response.data);
      console.log('Submitting passage:', passageText);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Passage submitted (simulated). API integration pending.');
      // router.push(`/passage/${response.data.id}`); // Navigate after successful submission
    } catch (err) {
      console.error('Failed to submit passage:', err);
      // setError('Failed to submit passage. Please try again.');
      alert('Failed to submit passage (simulated).');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Submit Passage - Passage Analyzer</title>
        <meta name="description" content="Submit a new passage to generate comprehension questions and vocabulary." />
      </Head>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-center text-light-text dark:text-dark-text">
            Submit Your Passage
          </h1>

          <div className="mb-6 content-card p-6">
            <PassageInput
              value={passageText}
              onChange={handlePassageChange}
              placeholder="Enter your text passage here. The longer and more detailed, the better the questions and vocabulary analysis will be."
              rows={15}
              disabled={isLoading}
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={handleSubmit}
              disabled={isLoading || !passageText.trim()}
              className="btn btn-primary text-lg px-8 py-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Processing...' : 'Generate Analysis'}
              {/* Text changed from "Generate Questions" to "Generate Analysis" as it's more encompassing */}
            </button>
          </div>

          {/* {error && (
            <div className="mt-6 p-4 text-center text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200 rounded-lg">
              {error}
            </div>
          )} */}

          {/* Placeholder for displaying submitted passage info or results later */}
          {/* {submittedPassage && (
            <div className="mt-8 content-card p-6">
              <h2 className="text-2xl font-semibold mb-4">Passage Submitted!</h2>
              <p>ID: {submittedPassage.id}</p>
              <Link href={`/passage/${submittedPassage.id}`}>
                <a className="text-blue-500 hover:underline">View Passage Analysis</a>
              </Link>
            </div>
          )} */}
        </div>
      </div>
    </>
  );
};

export default SubmitPassagePage;
