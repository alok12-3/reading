/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enable dark mode using a class
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}', // If using App Router
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Example: using Inter as default sans-serif
      },
      colors: {
        // Light theme colors
        light: {
          primary: '#0070f3', // Example primary color
          background: '#ffffff',
          text: '#1a202c', // Dark gray for text
          'secondary-text': '#4a5568', // Medium gray
          border: '#e2e8f0', // Light gray for borders
          card: '#f7fafc', // Very light gray for card backgrounds
        },
        // Dark theme colors
        dark: {
          primary: '#38bdf8', // Example primary color for dark mode (lighter blue)
          background: '#1a202c', // Dark gray, almost black
          text: '#f7fafc', // Very light gray, almost white
          'secondary-text': '#a0aec0', // Lighter gray for secondary text
          border: '#2d3748', // Medium-dark gray for borders
          card: '#2d3748', // Medium-dark gray for card backgrounds
        },
      },
      // Example: Spacing, keyframes, or other theme extensions can go here
      // backgroundImage: {
      //   'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      //   'gradient-conic':
      //     'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      // },
    },
  },
  plugins: [],
};
