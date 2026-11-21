import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import StatCard from "../components/StatCard";
import WorkflowVisualizer from "../components/WorkflowVisualizer";
import {
  Trophy,
  Flame,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  BookOpen,
  CalendarCheck,
  Brain,
  TrendingUp,
  RotateCcw
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function DashboardPage() {
  const { user, selectedSubject } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewData, planData] = await Promise.all([
        api.analytics.getOverview(),
        api.studyPlans.getCurrent(selectedSubject?.id).catch(() => null)
      ]);
      setAnalytics(overviewData);
      setStudyPlan(planData);
    } catch (err) {
      console.error("Dashboard data load failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [selectedSubject]);

  const handleToggleTask = async (taskId) => {
    try {
      await api.studyPlans.toggleTask(taskId);
      loadDashboardData();
    } catch (err) {
      console.error("Task toggle failed:", err);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-900/60 via-purple-900/40 to-slate-900 border border-indigo-500/30 shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Academic System Active</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {user?.full_name?.split(" ")[0] || "Student"}! 🎓
          </h1>
          <p className="text-sm text-slate-300 mt-2 leading-relaxed">
            Your 5 AI agents are actively monitoring your progress in{" "}
            <span className="text-indigo-400 font-semibold">{selectedSubject?.name}</span>.
            Weak areas are automatically prioritized in your personalized study timetable.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-5">
            <Link
              to="/assessment"
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition"
            >
              <span>Take Diagnostic Test</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              to="/planner"
              className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold transition"
            >
              View Daily Timetable
            </Link>
            <Link
              to="/tutor"
              className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold transition flex items-center gap-1.5"
            >
              <Brain className="w-3.5 h-3.5 text-indigo-400" />
              <span>Ask AI Tutor</span>
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Average Quiz Score"
          value={`${analytics?.average_quiz_score || 0}%`}
          subtitle="Calculated across all evaluated quizzes"
          icon={Trophy}
          color="indigo"
          trend="+12% this week"
        />
        <StatCard
          title="Study Streak"
          value={`${analytics?.study_streak_days || 3} Days`}
          subtitle="Consecutive daily learning activity"
          icon={Flame}
          color="amber"
        />
        <StatCard
          title="Task Completion Rate"
          value={`${analytics?.completion_rate || 0}%`}
          subtitle={`${analytics?.tasks_completed || 0} of ${analytics?.total_tasks || 0} tasks done`}
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Identified Knowledge Gaps"
          value={analytics?.weak_topics?.length || 0}
          subtitle="Weak topics prioritized by planner"
          icon={AlertTriangle}
          color={analytics?.weak_topics?.length > 0 ? "rose" : "emerald"}
        />
      </div>

      {/* Workflow Cycle Visualizer */}
      <WorkflowVisualizer currentStage="Plan" />

      {/* Main Grid: Performance Chart & Immediate Next Steps */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Performance Trends Chart (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-indigo-400" />
                Performance Mastery Trajectory
              </h2>
              <p className="text-xs text-slate-400">Quiz scores tracked over time</p>
            </div>
            <Link to="/analytics" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
              View Detailed Analytics →
            </Link>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics?.performance_trends || []}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                  itemStyle={{ color: "#818cf8" }}
                />
                <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#scoreGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Weak Topics & Adaptive Recommendations (1 col) */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Adaptive Focus Areas
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                AI Detected
              </span>
            </div>

            {analytics?.weak_topics && analytics.weak_topics.length > 0 ? (
              <div className="space-y-3">
                {analytics.weak_topics.slice(0, 3).map((w, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-slate-200">{w.topic_name}</h3>
                      <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-rose-500/15 text-rose-400">
                        {w.proficiency} ({w.score_percentage}%)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">Study Planner increased daily practice allocation.</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
                <p className="text-xs font-medium text-slate-300">No critical weak topics!</p>
                <p className="text-[11px] text-slate-500 mt-1">All assessed concepts meet the mastery threshold.</p>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <Link
              to="/quiz"
              className="w-full py-2.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold flex items-center justify-center gap-2 transition"
            >
              <span>Practice Targeted Quiz</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Upcoming Study Activities & Agent Live Decisions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Tasks */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <CalendarCheck className="w-4 h-4 text-indigo-400" />
              Today's Recommended Study Tasks
            </h2>
            <Link to="/planner" className="text-xs text-indigo-400 hover:text-indigo-300">
              Full Schedule →
            </Link>
          </div>

          {studyPlan?.tasks && studyPlan.tasks.length > 0 ? (
            <div className="space-y-2.5">
              {studyPlan.tasks.slice(0, 4).map((t) => (
                <div
                  key={t.id}
                  onClick={() => handleToggleTask(t.id)}
                  className={`p-3.5 rounded-xl border flex items-start gap-3 cursor-pointer transition ${
                    t.is_completed
                      ? "bg-slate-900/40 border-slate-800/60 opacity-60"
                      : "bg-slate-900 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <input
                    type="checkbox"
                    readOnly
                    checked={t.is_completed}
                    className="mt-0.5 rounded border-slate-700 text-indigo-600 focus:ring-0 cursor-pointer"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className={`text-xs font-semibold ${t.is_completed ? "line-through text-slate-500" : "text-slate-200"}`}>
                        {t.title}
                      </h3>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                        t.priority === "High" ? "bg-rose-500/15 text-rose-400" : "bg-slate-800 text-slate-400"
                      }`}>
                        {t.estimated_minutes} min
                      </span>
                    </div>
                    {t.description && (
                      <p className="text-[11px] text-slate-400 mt-1 leading-snug">{t.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500 text-xs">
              No tasks currently pending. Visit the Study Planner to generate a timetable.
            </div>
          )}
        </div>

        {/* Live Multi-Agent Decision Feed */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Brain className="w-4 h-4 text-emerald-400" />
              Autonomous Agent Decision Log
            </h2>
            <Link to="/agents" className="text-xs text-indigo-400 hover:text-indigo-300">
              Live Agent Stream →
            </Link>
          </div>

          <div className="space-y-3">
            {analytics?.recent_agent_decisions && analytics.recent_agent_decisions.length > 0 ? (
              analytics.recent_agent_decisions.map((dec, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono flex items-start gap-2.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 mt-1 flex-shrink-0"></span>
                  <span className="leading-relaxed">{dec}</span>
                </div>
              ))
            ) : (
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
                [Learning Assessment Agent] Initialized diagnostic monitoring baseline for Java Programming.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
