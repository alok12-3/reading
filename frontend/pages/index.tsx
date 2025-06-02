import Link from 'next/link';
import Head from 'next/head';

const HomePage = () => {
  return (
    <>
      <Head>
        <title>Passage Analyzer - Home</title>
        <meta name="description" content="Welcome to Passage Analyzer. Submit passages, generate questions, and enhance your understanding." />
      </Head>
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-10rem)] text-center px-4"> {/* Adjust min-h as needed based on layout header/footer */}
        <main className="p-8 rounded-lg shadow-xl content-card max-w-xl w-full">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 text-light-text dark:text-dark-text">
            Welcome to Passage Analyzer
          </h1>
          <p className="text-lg md:text-xl mb-8 text-light-secondary-text dark:text-dark-secondary-text">
            Enhance your reading comprehension. Submit text passages, generate insightful questions,
            and build your vocabulary.
          </p>
          <Link href="/submit-passage" legacyBehavior>
            <a className="btn btn-primary text-lg px-8 py-3">
              Get Started
            </a>
          </Link>
        </main>
      </div>
    </>
  );
};

export default HomePage;
