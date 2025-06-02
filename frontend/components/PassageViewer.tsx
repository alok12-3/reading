import React from 'react';

interface PassageViewerProps {
  text: string;
  onWordHighlight: (word: string, x: number, y: number) => void;
}

const PassageViewer: React.FC<PassageViewerProps> = ({ text, onWordHighlight }) => {
  const handleMouseUp = (event: React.MouseEvent<HTMLDivElement>) => {
    const selection = window.getSelection();
    if (selection) {
      const selectedText = selection.toString().trim();
      // Basic check for single word (no spaces) and not empty
      if (selectedText && !selectedText.includes(' ') && selectedText.length > 0) {
        // Use event.clientX and event.clientY for mouse position
        // These are relative to the viewport.
        onWordHighlight(selectedText, event.clientX, event.clientY);
      }
    }
  };

  return (
    <div
      onMouseUp={handleMouseUp}
      className="p-4 border rounded-lg shadow-sm
                 bg-light-card dark:bg-dark-card
                 text-light-text dark:text-dark-text
                 border-light-border dark:border-dark-border
                 whitespace-pre-wrap text-lg leading-relaxed cursor-text select-text"
      style={{ lineHeight: '1.8' }} // Example of specific line height for readability
    >
      {text}
    </div>
  );
};

export default PassageViewer;
