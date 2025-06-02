import React, { ReactNode } from 'react';
import Link from 'next/link';
import ThemeSwitcher from './ThemeSwitcher'; // Assuming ThemeSwitcher is in the same directory

type LayoutProps = {
  children: ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen bg-light-background dark:bg-dark-background transition-colors duration-300">
      <header className="py-4 px-6 shadow-md bg-light-card dark:bg-dark-card">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="/" legacyBehavior>
            <a className="text-2xl font-bold text-light-primary dark:text-dark-primary hover:no-underline">
              Passage Analyzer
            </a>
          </Link>
          <nav className="flex items-center space-x-4">
            <Link href="/" legacyBehavior>
              <a className="text-light-text dark:text-dark-text hover:text-light-primary dark:hover:text-dark-primary transition-colors">
                Home
              </a>
            </Link>
            <Link href="/passages/new" legacyBehavior>
              <a className="text-light-text dark:text-dark-text hover:text-light-primary dark:hover:text-dark-primary transition-colors">
                New Passage
              </a>
            </Link>
            {/* Add more navigation links as needed */}
            <ThemeSwitcher />
          </nav>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      <footer className="py-6 text-center bg-light-card dark:bg-dark-card border-t border-light-border dark:border-dark-border">
        <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">
          &copy; {new Date().getFullYear()} Passage Analyzer. All rights reserved.
        </p>
        {/* Add any other footer content here */}
      </footer>
    </div>
  );
};

export default Layout;
