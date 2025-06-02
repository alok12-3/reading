import React, { useEffect, useRef, useState } from 'react';

interface VocabTooltipProps {
  word: string | null;
  meaning: string | null;
  position: { x: number; y: number } | null;
  onClose: () => void;
  isLoading: boolean;
  isVisible: boolean;
  error?: string | null;
}

const VocabTooltip: React.FC<VocabTooltipProps> = ({
  word,
  meaning,
  position,
  onClose,
  isLoading,
  isVisible,
  error,
}) => {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);

  useEffect(() => {
    if (position && tooltipRef.current && isVisible) {
      const { innerWidth, innerHeight } = window;
      const tooltipRect = tooltipRef.current.getBoundingClientRect();

      let newX = position.x + 15; // Offset from cursor
      let newY = position.y + 15;

      // Adjust if tooltip goes out of bounds horizontally
      if (newX + tooltipRect.width > innerWidth) {
        newX = position.x - tooltipRect.width - 15;
      }
      // Adjust if tooltip goes out of bounds vertically
      if (newY + tooltipRect.height > innerHeight) {
        newY = position.y - tooltipRect.height - 15;
      }

      // Ensure it doesn't go off screen top/left
      if (newX < 0) newX = 0;
      if (newY < 0) newY = 0;

      setAdjustedPosition({ x: newX, y: newY });
    }
  }, [position, isVisible, word]); // Re-calculate when word changes too, as content affects size

  if (!isVisible || !position || !word) {
    return null;
  }

  return (
    <div
      ref={tooltipRef}
      className="fixed z-50 p-4 rounded-lg shadow-xl
                 bg-light-background dark:bg-dark-card
                 border border-light-border dark:border-dark-border
                 text-light-text dark:text-dark-text
                 max-w-xs w-auto transition-opacity duration-150"
      style={{
        left: `${adjustedPosition?.x ?? 0}px`,
        top: `${adjustedPosition?.y ?? 0}px`,
        opacity: isVisible ? 1 : 0,
        pointerEvents: isVisible ? 'auto' : 'none',
      }}
    >
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-bold text-lg text-light-primary dark:text-dark-primary">{word}</h4>
        <button
          onClick={onClose}
          className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="Close tooltip"
        >
          {/* Simple X icon */}
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {isLoading && <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">Loading meaning...</p>}

      {error && !isLoading && (
        <p className="text-sm text-red-500 dark:text-red-400">Error: {error}</p>
      )}

      {!isLoading && !error && meaning && (
        <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">{meaning}</p>
      )}

      {!isLoading && !error && !meaning && (
         <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">No meaning found or not yet fetched.</p>
      )}
    </div>
  );
};

export default VocabTooltip;
