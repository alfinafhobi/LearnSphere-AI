import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  FileQuestion,
  Sparkles,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  AlertTriangle,
  History,
  TrendingDown,
  TrendingUp,
  Award
} from "lucide-react";

export default function QuizPage() {
  const { selectedSubject } = useAuth();
  const [topics, setTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [difficulty, setDifficulty] = useState("Medium");
  const [questionCount, setQuestionCount] = useState(5);
  const [quizData, setQuizData] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [evalResult, setEvalResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (selectedSubject) {
      api.subjects.getOne(selectedSubject.id)
        .then((s) => {
          setTopics(s.topics || []);
          if (s.topics?.length > 0) setSelectedTopicId(s.topics[0].id);
        })
        .catch(console.error);

      loadQuizHistory();
    }
  }, [selectedSubject]);

  const loadQuizHistory = async () => {
    if (!selectedSubject) return;
    try {
      const data = await api.quiz.getHistory(selectedSubject.id);
      setHistory(data);
    } catch (err) {
      console.error("Failed to load quiz history:", err);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!selectedSubject) return;
    setLoading(true);
    setEvalResult(null);
    setSelectedAnswers({});
    try {
      const selectedT = topics.find((t) => t.id === parseInt(selectedTopicId));
      const data = await api.quiz.generate({
        subject_id: selectedSubject.id,
        topic_id: selectedTopicId ? parseInt(selectedTopicId) : undefined,
        topic_name: selectedT?.name,
        difficulty,
        question_count: questionCount
      });
      setQuizData(data);
    } catch (err) {
      console.error("Quiz generation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId, optionKey) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!quizData) return;
    setSubmitting(true);
    try {
      const answersPayload = Object.entries(selectedAnswers).map(([qId, opt]) => ({
        question_id: parseInt(qId),
        selected_option: opt
      }));

      const res = await api.quiz.submit(quizData.quiz_id, answersPayload);
      setEvalResult(res);
      loadQuizHistory();
    } catch (err) {
      console.error("Quiz submission failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
            Agent 4: Quiz Generation & Evaluation
          </span>
          <h1 className="text-2xl font-bold text-white mt-1 flex items-center gap-2">
            <FileQuestion className="w-6 h-6 text-amber-400" />
            Adaptive Practice Quizzes
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Subject: <span className="text-amber-400 font-semibold">{selectedSubject?.name}</span>.
            Evaluates mastery without exposing solutions until submission. Results feed the Progress Agent.
          </p>
        </div>
      </div>

      {/* Quiz Config Bar */}
      <div className="p-5 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Configure Topic & Difficulty
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Topic Select */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Select Topic</label>
            <select
              value={selectedTopicId}
              onChange={(e) => setSelectedTopicId(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-amber-500"
            >
              {topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Difficulty Tier</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-amber-500"
            >
              <option value="Easy">Easy (Foundational)</option>
              <option value="Medium">Medium (Practical Standard)</option>
              <option value="Hard">Hard (Deep & Architectural)</option>
            </select>
          </div>

          {/* Question Count */}
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Questions</label>
            <select
              value={questionCount}
              onChange={(e) => setQuestionCount(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-amber-500"
            >
              <option value={5}>5 Questions</option>
              <option value={8}>8 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={handleGenerateQuiz}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-amber-600/30 transition disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{loading ? "Agent Generating..." : "Generate Practice Quiz"}</span>
          </button>
        </div>
      </div>

      {/* Quiz Questions Section */}
      {quizData && !evalResult && (
        <div className="space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="text-base font-bold text-white">{quizData.title}</h2>
            <span className="text-xs text-slate-400 font-mono">
              {Object.keys(selectedAnswers).length}/{quizData.questions?.length} answered
            </span>
          </div>

          <div className="space-y-4">
            {quizData.questions?.map((q, idx) => (
              <div key={q.id} className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-slate-500">
                    Question 0{idx + 1}
                  </span>
                  {q.key_concept && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      Concept: {q.key_concept}
                    </span>
                  )}
                </div>

                <p className="text-sm font-semibold text-slate-100">{q.question_text}</p>

                <div className="space-y-2 pt-2">
                  {q.options?.map((opt, optIdx) => {
                    const optKey = opt.charAt(0);
                    const isSelected = selectedAnswers[q.id] === optKey;

                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => handleSelectOption(q.id, optKey)}
                        className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition flex items-center justify-between ${
                          isSelected
                            ? "bg-amber-600/20 border-amber-500 text-white"
                            : "bg-slate-900/80 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <span>{opt}</span>
                        <span className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                          isSelected ? "border-amber-400 bg-amber-500 text-white" : "border-slate-700"
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
              onClick={handleSubmitQuiz}
              disabled={submitting || Object.keys(selectedAnswers).length === 0}
              className="py-3 px-6 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center gap-2 shadow-xl shadow-emerald-600/30 transition disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <span className="inline-block animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
                  <span>Agent Evaluating Quiz...</span>
                </>
              ) : (
                <>
                  <span>Submit Quiz for Evaluation</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Quiz Result & Detailed Review */}
      {evalResult && (
        <div className="space-y-6">
          <div className="p-8 rounded-3xl bg-gradient-to-br from-[#0f172a] to-slate-900 border border-slate-800 shadow-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <span className={`text-xs font-mono uppercase tracking-wider font-semibold ${
                  evalResult.passed ? "text-emerald-400" : "text-rose-400"
                }`}>
                  {evalResult.passed ? "Quiz Passed" : "Quiz Needs Review"}
                </span>
                <h2 className="text-2xl font-bold text-white mt-1">Performance Evaluation</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Evaluated by Quiz Agent and coordinated with Progress Monitoring Agent.
                </p>
              </div>

              <div className="text-right">
                <div className={`text-3xl font-extrabold ${evalResult.passed ? "text-emerald-400" : "text-rose-400"}`}>
                  {evalResult.percentage}%
                </div>
                <div className="text-xs text-slate-400">
                  {evalResult.score} of {evalResult.total_questions} correct
                </div>
              </div>
            </div>

            {/* Adaptive Replanning Notification */}
            {evalResult.plan_revision_triggered && (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-bold">Autonomous Adaptation Triggered:</strong>
                  <span>{evalResult.adaptive_recommendation}</span>
                </div>
              </div>
            )}

            {/* Questions Review with explanations */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Question-by-Question Review & Explanations
              </h3>

              {evalResult.questions_review?.map((rev, idx) => (
                <div
                  key={idx}
                  className={`p-5 rounded-2xl border space-y-3 ${
                    rev.is_correct
                      ? "bg-emerald-500/5 border-emerald-500/20"
                      : "bg-rose-500/5 border-rose-500/20"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      Question 0{idx + 1}
                    </span>
                    <span className={`text-xs font-semibold flex items-center gap-1 ${
                      rev.is_correct ? "text-emerald-400" : "text-rose-400"
                    }`}>
                      {rev.is_correct ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                      <span>{rev.is_correct ? "Correct" : `Incorrect (You chose ${rev.selected_option})`}</span>
                    </span>
                  </div>

                  <p className="text-xs sm:text-sm font-semibold text-slate-200">
                    {rev.question_text}
                  </p>

                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1">
                    <div className="text-slate-300">
                      <strong className="text-indigo-400">Correct Answer:</strong> {rev.correct_option}
                    </div>
                    <div className="text-slate-400 leading-relaxed">
                      <strong className="text-indigo-400">Explanation:</strong> {rev.explanation}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Action buttons */}
            <div className="flex justify-between items-center pt-4 border-t border-slate-800">
              <button
                onClick={handleGenerateQuiz}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retry Another Quiz</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Past Quiz Attempts History */}
      {history.length > 0 && (
        <div className="p-5 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <History className="w-4 h-4 text-indigo-400" />
            Previous Quiz Attempts
          </h3>

          <div className="divide-y divide-slate-800/80">
            {history.slice(0, 5).map((att) => (
              <div key={att.id} className="py-2.5 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-slate-200">{att.quiz_title}</span>
                  <span className="text-slate-500 text-[10px] ml-2">
                    {new Date(att.completed_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`font-mono font-bold ${
                    att.percentage >= 60 ? "text-emerald-400" : "text-rose-400"
                  }`}>
                    {att.percentage}%
                  </span>
                  <span className="text-slate-500 font-mono">
                    ({att.score}/{att.total_questions})
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
