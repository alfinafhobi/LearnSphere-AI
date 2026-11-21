import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Sparkles, Brain, LogOut, ChevronDown, BookOpen, Activity } from "lucide-react";
import { api } from "../api/client";

export default function Navbar() {
  const { user, logout, selectedSubject, selectSubject } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.subjects.getAll().then(setSubjects).catch(console.error);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-[#0f172a]/90 backdrop-blur-md border-b border-slate-800 px-6 py-3.5 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                LearnSphere
              </span>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-wide">Autonomous Academic Multi-Agent System</p>
          </div>
        </Link>
      </div>

      {/* Center: Active Subject Switcher */}
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 text-sm text-slate-200 transition"
        >
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <span className="font-medium">{selectedSubject?.name || "Select Subject"}</span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        </button>

        {dropdownOpen && (
          <div className="absolute left-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl py-1.5 z-50">
            <div className="px-3 py-1.5 text-[11px] uppercase font-semibold text-slate-400 border-b border-slate-800">
              Active Curriculum
            </div>
            {subjects.map((sub) => (
              <button
                key={sub.id}
                onClick={() => {
                  selectSubject(sub);
                  setDropdownOpen(false);
                }}
                className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between hover:bg-indigo-600/10 transition ${
                  selectedSubject?.id === sub.id ? "text-indigo-400 font-semibold bg-indigo-500/10" : "text-slate-300"
                }`}
              >
                <span>{sub.name}</span>
                <span className="text-[10px] text-slate-500 font-mono">{sub.code}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right User & Agent Live Status */}
      <div className="flex items-center gap-4">
        {/* Agent live badge */}
        <Link
          to="/agents"
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 transition"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>5 Agents Active</span>
        </Link>

        {/* User profile capsule */}
        {user ? (
          <div className="flex items-center gap-3">
            <Link to="/profile" className="flex items-center gap-2.5 group">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs text-white shadow"
                style={{ backgroundColor: user.avatar_color || "#6366f1" }}
              >
                {user.full_name?.charAt(0) || "U"}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition">
                  {user.full_name}
                </p>
                <p className="text-[10px] text-slate-400 font-mono truncate max-w-[120px]">{user.email}</p>
              </div>
            </Link>
            <button
              onClick={() => {
                logout();
                navigate("/auth");
              }}
              title="Sign Out"
              className="p-2 rounded-lg bg-slate-800/60 hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-slate-700/60 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            to="/auth"
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md transition"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
