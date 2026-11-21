import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import StatCard from "../components/StatCard";
import {
  BarChart3,
  TrendingUp,
  Award,
  AlertTriangle,
  Brain,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle2
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  Legend
} from "recharts";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const { selectedSubject } = useAuth();

  useEffect(() => {
    api.analytics.getOverview()
      .then(setAnalytics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const barColors = ["#6366f1", "#0ea5e9", "#10b981", "#8b5cf6", "#f59e0b"];

  return (
    <div className="space-y-6 pb-16 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30">
            Progress Intelligence & Mastery Analytics
          </span>
          <h1 className="text-2xl font-bold text-white mt-1 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            Performance & Mastery Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Visualizing cognitive mastery progression, topic distributions, and historical trajectory.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Overall Average"
          value={`${analytics?.average_quiz_score || 0}%`}
          subtitle="Cumulative across all quizzes"
          icon={TrendingUp}
          color="indigo"
        />
        <StatCard
          title="Quizzes Taken"
          value={analytics?.total_quizzes_taken || 0}
          subtitle="Evaluated by Quiz Agent"
          icon={Award}
          color="emerald"
        />
        <StatCard
          title="Diagnostics Completed"
          value={analytics?.completed_assessments || 0}
          subtitle="Baseline knowledge benchmarks"
          icon={Calendar}
          color="purple"
        />
        <StatCard
          title="Tasks Completed"
          value={`${analytics?.tasks_completed || 0} / ${analytics?.total_tasks || 0}`}
          subtitle={`${analytics?.completion_rate || 0}% completion efficiency`}
          icon={CheckCircle2}
          color="amber"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Area Chart */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              Quiz Performance Over Time
            </h2>
            <p className="text-xs text-slate-400">Score percentage progress across recent attempts</p>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics?.performance_trends || []}>
                <defs>
                  <linearGradient id="scoreGrad2" x1="0" y1="0" x2="0" y2="1">
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
                <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#scoreGrad2)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Subject-Wise Performance Bar Chart */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-400" />
              Subject-Wise Mastery Comparison
            </h2>
            <p className="text-xs text-slate-400">Average benchmark score per curriculum subject</p>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.subject_breakdown || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="code" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                />
                <Bar dataKey="average_score" radius={[6, 6, 0, 0]}>
                  {(analytics?.subject_breakdown || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={barColors[index % barColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Weak & Strong Topics Comparison Tables */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weak Topics */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              Weak Areas & Misconceptions
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/15 text-rose-400">
              Needs Study
            </span>
          </div>

          {analytics?.weak_topics && analytics.weak_topics.length > 0 ? (
            <div className="space-y-2.5">
              {analytics.weak_topics.map((w, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <h4 className="font-semibold text-slate-200">{w.topic_name}</h4>
                    <span className="text-[10px] text-slate-400">Evaluated in {w.attempts} attempts</span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono font-bold text-rose-400">{w.score_percentage}%</span>
                    <span className="block text-[10px] text-slate-500">{w.proficiency}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-4 text-center">No critical weak topics identified yet.</p>
          )}
        </div>

        {/* Strong Topics */}
        <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4" />
              Mastered Topics
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400">
              Validated
            </span>
          </div>

          {analytics?.strong_topics && analytics.strong_topics.length > 0 ? (
            <div className="space-y-2.5">
              {analytics.strong_topics.map((s, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <h4 className="font-semibold text-slate-200">{s.topic_name}</h4>
                    <span className="text-[10px] text-slate-400">High retention score</span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono font-bold text-emerald-400">{s.score_percentage}%</span>
                    <span className="block text-[10px] text-slate-500">{s.proficiency}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-4 text-center">Take quizzes to demonstrate advanced mastery.</p>
          )}
        </div>
      </div>
    </div>
  );
}
