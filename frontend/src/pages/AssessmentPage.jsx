import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  ClipboardCheck,
  CheckCircle,
  XCircle,
  Clock,
  Sparkles,
  ArrowRight,
  RotateCcw,
  AlertTriangle,
  Award,
  Layers,
  ChevronRight
} from "lucide-react";

export default function AssessmentPage() {
  const { selectedSubject } = useAuth();
  const navigate = useNavigate();

  const [assessmentData, setAssessmentData] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submittedResult, setSubmittedResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(600); // 10 minutes
  const [isTimerActive, setIsTimerActive] = useState(true);

  // Fetch or initialize diagnostic test
  const initializeDiagnostic = async () => {
    if (!selectedSubject) return;
    setLoading(true);
    setSubmittedResult(null);
    setSelectedAnswers({});
    setTimerSeconds(600);
    try {
      const data = await api.assessment.start(selectedSubject.id);
      setAssessmentData(data);
    } catch (err) {
      console.error("Diagnostic start failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initializeDiagnostic();
  }, [selectedSubject]);

  // Optional countdown timer
  useEffect(() => {
    if (!isTimerActive || !assessmentData || submittedResult) return;
    const interval = setInterval(() => {
      setTimerSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [isTimerActive, assessmentData, submittedResult]);

  const handleSelectOption = (questionId, optionKey) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  const handleSubmit = async () => {
    if (!assessmentData) return;
    setEvaluating(true);
    try {
      const answersPayload = Object.entries(selectedAnswers).map(([qId, opt]) => ({
        question_id: parseInt(qId),
        selected_option: opt
      }));

      const result = await api.assessment.submit(assessmentData.assessment_id, answersPayload);
      setSubmittedResult(result);
    } catch (err) {
      console.error("Diagnostic submission failed:", err);
    } finally {
      setEvaluating(false);
    }
  };

  const formatTimer = (sec) => {
    const mins = Math.floor(sec / 60);
    const s = sec % 60;
    return `${mins}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="space-y-6 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
              Agent 1: Learning Assessment
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1 flex items-center gap-2">
            <ClipboardCheck className="w-6 h-6 text-indigo-400" />
            Diagnostic Knowledge Assessment
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Subject: <span className="text-indigo-400 font-semibold">{selectedSubject?.name}</span>.
            Identifies knowledge gaps and informs the Study Planner Agent.
          </p>
        </div>

        {assessmentData && !submittedResult && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>{formatTimer(timerSeconds)}</span>
            </div>
            <button
              onClick={() => setIsTimerActive(!isTimerActive)}
              className="text-[11px] text-slate-400 hover:text-slate-200 underline"
            >
              {isTimerActive ? "Pause" : "Resume"}
            </button>
          </div>
        )}
      </div>

      {loading && (
        <div className="py-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-3"></div>
          <p className="text-xs text-slate-400">Assessment Agent is generating diagnostic questions...</p>
        </div>
      )}

      {/* Questions Section */}
      {!loading && assessmentData && !submittedResult && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-xs text-indigo-300 flex items-center justify-between">
            <span>Answer all questions to the best of your ability. Wrong answers reveal focal topics for your study plan.</span>
            <span className="font-mono">{Object.keys(selectedAnswers).length}/{assessmentData.questions?.length} answered</span>
          </div>

          <div className="space-y-4">
            {assessmentData.questions?.map((q, idx) => (
              <div key={q.id} className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider">
                    Question 0{idx + 1}
                  </span>
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-800 text-indigo-400 border border-slate-700">
                    Topic: {q.topic_name}
                  </span>
                </div>

                <h3 className="text-sm sm:text-base font-semibold text-slate-100 leading-snug">
                  {q.question_text}
                </h3>

                <div className="space-y-2 pt-2">
                  {q.options?.map((opt, optIdx) => {
                    const optKey = opt.charAt(0); // A, B, C, D
                    const isSelected = selectedAnswers[q.id] === optKey;

                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => handleSelectOption(q.id, optKey)}
                        className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition flex items-center justify-between ${
                          isSelected
                            ? "bg-indigo-600/20 border-indigo-500 text-white shadow-sm"
                            : "bg-slate-900/80 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:border-slate-700"
                        }`}
                      >
                        <span>{opt}</span>
                        <span className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                          isSelected ? "border-indigo-400 bg-indigo-500 text-white" : "border-slate-700"
                        }`}>
                          {isSelected && "✓"}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <button
              onClick={handleSubmit}
              disabled={evaluating || Object.keys(selectedAnswers).length === 0}
              className="py-3 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-2 shadow-xl shadow-indigo-600/30 transition disabled:opacity-50"
            >
              {evaluating ? (
                <>
                  <span className="inline-block animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
                  <span>Assessment Agent Evaluating...</span>
                </>
              ) : (
                <>
                  <span>Submit Diagnostic for Gap Analysis</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Submitted Result & Diagnostic Gap Analysis */}
      {submittedResult && (
        <div className="space-y-6">
          <div className="p-8 rounded-3xl bg-gradient-to-br from-[#0f172a] to-slate-900 border border-slate-800 shadow-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-semibold">
                  Diagnostic Evaluation Complete
                </span>
                <h2 className="text-2xl font-bold text-white mt-1">Knowledge Profile & Gap Report</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Learning Assessment Agent has finalized topic proficiency levels.
                </p>
              </div>

              <div className="text-right">
                <div className="text-3xl font-extrabold text-white">
                  {submittedResult.percentage}%
                </div>
                <div className="text-xs text-slate-400">
                  {submittedResult.score} of {submittedResult.total_questions} correct
                </div>
              </div>
            </div>

            {/* Topic Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Weak Topics */}
              <div className="p-5 rounded-2xl bg-rose-500/5 border border-rose-500/20">
                <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5 mb-3">
                  <AlertTriangle className="w-4 h-4" />
                  Identified Weak Areas (Priority Focus)
                </h4>
                {submittedResult.weak_topics?.length > 0 ? (
                  <ul className="space-y-2">
                    {submittedResult.weak_topics.map((t, i) => (
                      <li key={i} className="text-xs text-slate-200 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                        <span className="font-semibold">{t}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 ml-auto">
                          Beginner
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400">No critical weaknesses detected!</p>
                )}
              </div>

              {/* Strong Topics */}
              <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
                <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 mb-3">
                  <Award className="w-4 h-4" />
                  Demonstrated Strengths
                </h4>
                {submittedResult.strong_topics?.length > 0 ? (
                  <ul className="space-y-2">
                    {submittedResult.strong_topics.map((t, i) => (
                      <li key={i} className="text-xs text-slate-200 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        <span className="font-semibold">{t}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 ml-auto">
                          Advanced
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400">Consistent effort needed to reach advanced mastery.</p>
                )}
              </div>
            </div>

            {/* AI Recommendation Banner */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <h5 className="text-xs font-semibold text-indigo-400 mb-1 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Assessment Agent Next-Step Recommendation:
              </h5>
              <p className="text-xs text-slate-300 leading-relaxed">
                {submittedResult.recommendations}
              </p>
            </div>

            {/* Action buttons */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-800">
              <button
                onClick={initializeDiagnostic}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-2 transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retake Diagnostic</span>
              </button>

              <button
                onClick={() => navigate("/planner")}
                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition"
              >
                <span>View Personalized Study Plan</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
