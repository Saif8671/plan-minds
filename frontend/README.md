# Planner App - Frontend

This is the frontend for the AI-powered Planner App, built with React, Vite, and Tailwind CSS.

## Tech Stack
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** Tailwind CSS + Glassmorphism aesthetics
- **Routing:** React Router
- **Formatting:** Prettier (with tailwindcss plugin) & ESLint

## Getting Started

### Prerequisites
Make sure you have Node.js and npm installed.

### Installation
1. Clone the repository and navigate to this frontend directory.
2. Install dependencies:
   ```bash
   npm install
   ```

### Running Locally
To start the development server:
```bash
npm run dev
```
The app will be available at `http://localhost:5173`.

### Code Formatting
This project adheres to a strict 2-space indentation, single quotes, and automatic Tailwind class sorting standard.
To format the codebase:
```bash
npx prettier --write "src/**/*.{ts,tsx,css}"
```

## Component Architecture
- **AuthContext:** Manages user sessions and JWT tokens.
- **FloatingAssistant:** The AI-powered chat interface available globally across the app for scheduling and interacting with routines.
- **AlarmManager:** A global component handling background alarms and notifications for scheduled tasks.
