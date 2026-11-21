import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  User,
  Target,
  Clock,
  BookOpen,
  Sparkles,
  CheckCircle,
  Save,
  Shield,
  GraduationCap
} from "lucide-react";

export default function ProfilePage() {
  const { user, selectedSubject } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [targetGrade, setTargetGrade] = useState("A");
  const [availableHours, setAvailableHours] = useState(2.5);
  const [learningStyle, setLearningStyle] = useState("Interactive & Practical");
  const [academicFocus, setAcademicFocus] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.profile.get()
      .then((data) => {
        setProfileData(data);
        if (data.goal) {
          setTargetGrade(data.goal.target_grade || "A");
          setAvailableHours(data.goal.available_hours_per_day || 2.5);
          setLearningStyle(data.goal.preferred_learning_style || "Interactive & Practical");
          setAcademicFocus(data.goal.academic_focus || "");
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await api.profile.updateGoal({
        target_grade: targetGrade,
        available_hours_per_day: availableHours,
        preferred_learning_style: learningStyle,
        academic_focus: academicFocus,
        subject_id: selectedSubject?.id
      });
      setMessage("Student academic goals and preferences saved successfully!");
    } catch (err) {
      console.error("Save profile goal failed:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
          <GraduationCap className="w-6 h-6 text-indigo-400" />
          Student Academic Profile & Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure learning style preferences, target grades, and daily study availability for autonomous scheduling.
        </p>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Account Info Card */}
      <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <User className="w-4 h-4 text-indigo-400" />
          Student Account Information
        </h3>

        <div className="flex items-center gap-4 pt-2">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-xl text-white shadow-lg"
            style={{ backgroundColor: user?.avatar_color || "#6366f1" }}
          >
            {user?.full_name?.charAt(0) || "U"}
          </div>

          <div>
            <h4 className="text-base font-bold text-white">{user?.full_name}</h4>
            <p className="text-xs text-slate-400 font-mono">{user?.email}</p>
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 mt-1">
              <Shield className="w-3 h-3" />
              Verified College Project Student Account
            </span>
          </div>
        </div>
      </div>

      {/* Academic Goals Form */}
      <form onSubmit={handleSave} className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-5">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-800">
          <Target className="w-4 h-4 text-purple-400" />
          Academic Objectives & Study Time Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Target Semester Grade
            </label>
            <select
              value={targetGrade}
              onChange={(e) => setTargetGrade(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value="A+">A+ (Exceptional Mastery)</option>
              <option value="A">A (Superior Performance)</option>
              <option value="B+">B+ (Above Average)</option>
              <option value="B">B (Solid Competence)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Available Daily Study Time (Hours)
            </label>
            <select
              value={availableHours}
              onChange={(e) => setAvailableHours(parseFloat(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value={1.5}>1.5 Hours / Day</option>
              <option value={2.0}>2.0 Hours / Day</option>
              <option value={2.5}>2.5 Hours / Day</option>
              <option value={3.0}>3.0 Hours / Day</option>
              <option value={4.0}>4.0 Hours / Day</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Preferred Learning Modality
          </label>
          <select
            value={learningStyle}
            onChange={(e) => setLearningStyle(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
          >
            <option value="Interactive & Practical">Interactive & Practical (Code Examples + Quizzes)</option>
            <option value="Concept-First & Analogies">Concept-First & Analogies (Intuitive Mental Models)</option>
            <option value="Rigorous & Architectural">Rigorous & Architectural (Specification Details & Proofs)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Academic Focus & Notes
          </label>
          <textarea
            rows="3"
            value={academicFocus}
            onChange={(e) => setAcademicFocus(e.target.value)}
            placeholder="e.g. Master Object-Oriented Design in Java and prepare for final project evaluation..."
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
          ></textarea>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{saving ? "Saving..." : "Save Preferences"}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
