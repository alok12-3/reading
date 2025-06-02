"use client"; // Required for Next.js 13+ App Router or if using hooks like useState/useEffect at top level

import { useState, useEffect } from 'react';

const ThemeSwitcher = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Effect to check localStorage and set initial theme
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    } else if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
    } else if (prefersDark) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark'); // Save preference if relying on prefers-color-scheme
    } else {
      // Default to light if no preference or saved theme
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDarkMode(!isDarkMode);
  };

  return (
    <button
      onClick={toggleTheme}
      className="px-3 py-2 rounded-md text-sm font-medium transition-colors
                 bg-gray-200 hover:bg-gray-300
                 dark:bg-gray-700 dark:hover:bg-gray-600
                 text-light-text dark:text-dark-text"
      aria-label="Toggle theme"
    >
      {isDarkMode ? (
        // Sun icon (example, replace with actual SVG or icon component)
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm0 15a1 1 0 01-1-1v-1a1 1 0 112 0v1a1 1 0 01-1 1zm6.09-10.09a1 1 0 01.29.71.994.994 0 01-.29.71l-.71.71a1 1 0 01-1.41-1.41l.71-.71a1 1 0 011.41 0zm-12.18 0a1 1 0 011.41 0l.71.71a1 1 0 01-1.41 1.41l-.71-.71a1 1 0 010-1.41zM10 5a5 5 0 100 10 5 5 0 000-10zm0 8a3 3 0 110-6 3 3 0 010 6zM20 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM2 10a1 1 0 011-1h1a1 1 0 110 2H3a1 1 0 01-1-1zm14.09 6.09a1 1 0 010-1.41l.71-.71a1 1 0 111.41 1.41l-.71.71a1 1 0 01-.7.29.994.994 0 01-.71-.29zM3.91 3.91a1 1 0 010 1.41l-.71.71a1 1 0 01-1.41-1.41l.71-.71a1 1 0 011.41 0z"/>
        </svg>
      ) : (
        // Moon icon (example)
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
        </svg>
      )}
    </button>
  );
};

export default ThemeSwitcher;
