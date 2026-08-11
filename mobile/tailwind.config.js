/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  presets: [require("nativewind/preset")],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#1677FF',
        secondary: '#7A3EF3',
        accent: '#17C6A3',
        background: '#F8FAFC',
        dark: '#0F172A',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
      },
      fontFamily: {
        sans: ['System'], // Will change to Inter later
      }
    },
  },
  plugins: [],
}
