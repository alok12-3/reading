import React from 'react';

interface PassageInputProps {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  rows?: number;
  disabled?: boolean;
}

const PassageInput: React.FC<PassageInputProps> = ({
  value,
  onChange,
  placeholder = "Paste or type your passage here...",
  rows = 10,
  disabled = false,
}) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      rows={rows}
      disabled={disabled}
      className={`
        w-full p-4 border rounded-lg shadow-sm
        text-base leading-relaxed
        bg-light-background dark:bg-dark-background
        text-light-text dark:text-dark-text
        border-light-border dark:border-dark-border
        focus:ring-2 focus:ring-light-primary dark:focus:ring-dark-primary
        focus:border-transparent outline-none transition-shadow duration-150 ease-in-out
        resize-y
        ${disabled ? 'opacity-70 cursor-not-allowed' : ''}
      `}
      aria-label="Passage Input Text Area"
    />
  );
};

export default PassageInput;
