import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import SubjectsPage from "./pages/SubjectsPage";
import AssessmentPage from "./pages/AssessmentPage";
import StudyPlannerPage from "./pages/StudyPlannerPage";
import TutorPage from "./pages/TutorPage";
import QuizPage from "./pages/QuizPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AgentActivityPage from "./pages/AgentActivityPage";
import ProfilePage from "./pages/ProfilePage";

function ProtectedLayout({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-mono">Initializing LearnSphere AI...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-6 sm:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          
          <Route
            path="/"
            element={
              <ProtectedLayout>
                <DashboardPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/subjects"
            element={
              <ProtectedLayout>
                <SubjectsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/assessment"
            element={
              <ProtectedLayout>
                <AssessmentPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/planner"
            element={
              <ProtectedLayout>
                <StudyPlannerPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/tutor"
            element={
              <ProtectedLayout>
                <TutorPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/quiz"
            element={
              <ProtectedLayout>
                <QuizPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedLayout>
                <AnalyticsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/agents"
            element={
              <ProtectedLayout>
                <AgentActivityPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedLayout>
                <ProfilePage />
              </ProtectedLayout>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
