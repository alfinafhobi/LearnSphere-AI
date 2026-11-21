import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  CalendarCheck2,
  Clock,
  Target,
  Sparkles,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  ShieldCheck,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Sliders,
  Check,
  X,
  BookOpen,
  ExternalLink,
  GraduationCap,
  Layers,
  Compass
} from "lucide-react";

export default function StudyPlannerPage() {
  const { selectedSubject } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [availableHours, setAvailableHours] = useState(2.5);
  const [learningGoal, setLearningGoal] = useState("Master weak topics and ace college semester exams");
  const [regenerating, setRegenerating] = useState(false);
  const [message, setMessage] = useState("");
  // Track expanded learning resource sections per task
  const [expandedResources, setExpandedResources] = useState({});

  const loadPlan = async () => {
    if (!selectedSubject) return;
    try {
      setLoading(true);
      const data = await api.studyPlans.getCurrent(selectedSubject.id);
      setPlan(data);
      if (data.available_hours) setAvailableHours(data.available_hours);

      // Auto-expand resources for High priority tasks so students immediately see materials for weak areas
      const initialExpanded = {};
      (data.tasks || []).forEach((t) => {
        if (t.priority === "High") {
          initialExpanded[t.id] = true;
        }
      });
      setExpandedResources(initialExpanded);
    } catch (err) {
      console.error("Failed to load study plan:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, [selectedSubject]);

  const handleToggleTask = async (taskId) => {
    try {
      await api.studyPlans.toggleTask(taskId);
      loadPlan();
    } catch (err) {
      console.error("Task toggle failed:", err);
    }
  };

  const toggleResourceExpand = (e, taskId) => {
    e.stopPropagation();
    setExpandedResources((prev) => ({
      ...prev,
      [taskId]: !prev[taskId],
    }));
  };

  const handleRegenerate = async () => {
    if (!selectedSubject) return;
    setRegenerating(true);
    setMessage("");
    try {
      const data = await api.studyPlans.generate(selectedSubject.id, availableHours, learningGoal);
      setPlan(data);
      setMessage("Study plan and AI-recommended learning resources refreshed by Study Planner Agent.");
      // Auto-expand high priority tasks
      const initialExpanded = {};
      (data.tasks || []).forEach((t) => {
        if (t.priority === "High") {
          initialExpanded[t.id] = true;
        }
      });
      setExpandedResources(initialExpanded);
    } catch (err) {
      console.error("Regeneration failed:", err);
    } finally {
      setRegenerating(false);
    }
  };

  const handleHumanApproval = async (approved) => {
    if (!plan) return;
    try {
      await api.studyPlans.approveRevision(plan.id, approved);
      loadPlan();
      setMessage(approved ? "Adaptive timetable approved and activated!" : "Revision proposal dismissed.");
    } catch (err) {
      console.error("Approval action failed:", err);
    }
  };

  const getResourceTypeColor = (type) => {
    switch (type) {
      case "Official Documentation":
        return "bg-blue-500/15 text-blue-400 border-blue-500/30";
      case "Interactive Tutorial":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "Beginner Guide":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "Technical Blog":
      case "Technical Article":
        return "bg-purple-500/15 text-purple-400 border-purple-500/30";
      case "Interactive Visualization":
        return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
      default:
        return "bg-indigo-500/15 text-indigo-400 border-indigo-500/30";
    }
  };

  // Group tasks by day
  const tasksByDay = (plan?.tasks || []).reduce((acc, task) => {
    const day = task.day_of_week || "Monday";
    if (!acc[day]) acc[day] = [];
    acc[day].push(task);
    return acc;
  }, {});

  const daysOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  return (
    <div className="space-y-6 pb-16 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 border border-purple-500/30">
            Agent 2: Personalized Study Planner
          </span>
          <h1 className="text-2xl font-bold text-white mt-1 flex items-center gap-2">
            <CalendarCheck2 className="w-6 h-6 text-purple-400" />
            Adaptive Study Schedule & Learning Resources
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Subject: <span className="text-purple-400 font-semibold">{selectedSubject?.name}</span>.
            Autonomous schedule with AI-curated tutorials, official documentation, and technical articles.
          </p>
        </div>

        {/* Available Hours quick tuner */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <select
              value={availableHours}
              onChange={(e) => setAvailableHours(parseFloat(e.target.value))}
              className="bg-transparent text-white font-semibold focus:outline-none cursor-pointer"
            >
              <option value={1.5} className="bg-slate-900">1.5 hrs/day</option>
              <option value={2.0} className="bg-slate-900">2.0 hrs/day</option>
              <option value={2.5} className="bg-slate-900">2.5 hrs/day</option>
              <option value={3.0} className="bg-slate-900">3.0 hrs/day</option>
              <option value={4.0} className="bg-slate-900">4.0 hrs/day</option>
            </select>
          </div>

          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-purple-600/30 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? "animate-spin" : ""}`} />
            <span>Regenerate Plan</span>
          </button>
        </div>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Human Approval Required Banner for Major Adaptive Changes */}
      {plan?.status === "Pending_Approval" && plan.pending_revision && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-950/60 via-purple-950/60 to-slate-900 border-2 border-amber-500/50 shadow-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-amber-400" />
              <h3 className="text-sm font-bold text-white">
                Human-in-the-Loop Review: Adaptive Plan Revision Proposed
              </h3>
            </div>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold">
              Action Required
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            The <strong>Progress Monitoring Agent</strong> identified repeated difficulty in:{" "}
            <span className="text-amber-300 font-semibold">{plan.pending_revision.focus_topics?.join(", ") || "OOP Concepts"}</span>.
            The Study Planner Agent has re-balanced your timetable to allocate intensified 45-60 min blocks to these areas with curated beginner-friendly resources.
          </p>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => handleHumanApproval(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md shadow-emerald-600/30 transition"
            >
              <Check className="w-4 h-4" />
              <span>Approve & Apply New Timetable</span>
            </button>

            <button
              onClick={() => handleHumanApproval(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-2 border border-slate-700 transition"
            >
              <X className="w-4 h-4" />
              <span>Dismiss & Keep Current</span>
            </button>
          </div>
        </div>
      )}

      {/* Overview Cards: Objectives & Focus Topics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Weekly Objectives */}
        <div className="md:col-span-2 p-5 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-3">
          <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
            <Target className="w-4 h-4" />
            Weekly Academic Objectives
          </h3>
          <ul className="space-y-2">
            {plan?.weekly_objectives?.map((obj, i) => (
              <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5 flex-shrink-0"></span>
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Priority Focus Topics */}
        <div className="p-5 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-3">
          <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-4 h-4" />
            Priority Focus Modules
          </h3>
          <div className="space-y-2">
            {plan?.focus_topics && plan.focus_topics.length > 0 ? (
              plan.focus_topics.map((t, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 flex items-center justify-between">
                  <span>{t}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold font-mono">
                    High Priority
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">General comprehensive mastery schedule</p>
            )}
          </div>
          <p className="text-[11px] text-slate-500">
            Schedule revisions applied: <span className="font-mono text-purple-300">{plan?.adaptation_count || 0} times</span>
          </p>
        </div>
      </div>

      {/* Daily Tasks Schedule Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>Daily Timetable & Tasks</span>
            <span className="text-xs text-slate-400 font-normal">
              ({plan?.tasks?.filter((t) => t.is_completed).length || 0} of {plan?.tasks?.length || 0} completed)
            </span>
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {daysOrder.map((day) => {
            const dayTasks = tasksByDay[day] || [];
            if (dayTasks.length === 0) return null;

            return (
              <div key={day} className="p-4 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <h4 className="text-xs font-bold text-slate-200 tracking-wide uppercase font-mono">{day}</h4>
                  <span className="text-[10px] text-slate-400">
                    {dayTasks.reduce((sum, t) => sum + t.estimated_minutes, 0)} mins total
                  </span>
                </div>

                <div className="space-y-3">
                  {dayTasks.map((task) => {
                    const isExpanded = !!expandedResources[task.id];
                    const resourcesCount = task.resources?.length || 0;

                    return (
                      <div
                        key={task.id}
                        onClick={() => handleToggleTask(task.id)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition ${
                          task.is_completed
                            ? "bg-slate-900/40 border-slate-800/60 opacity-60"
                            : "bg-slate-900 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        {/* Task Header */}
                        <div className="flex items-start gap-2.5">
                          <input
                            type="checkbox"
                            readOnly
                            checked={task.is_completed}
                            className="mt-0.5 rounded border-slate-700 text-purple-600 focus:ring-0 cursor-pointer"
                          />
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <span className={`text-xs font-semibold ${task.is_completed ? "line-through text-slate-500" : "text-slate-200"}`}>
                                {task.title}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold ${
                                task.priority === "High" ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" : "bg-slate-800 text-slate-400"
                              }`}>
                                {task.priority} Priority
                              </span>
                              <span className="text-[10px] text-slate-400 font-mono">
                                {task.estimated_minutes} min
                              </span>
                              {task.topic_name && (
                                <span className="text-[10px] text-indigo-400 font-medium">
                                  • {task.topic_name}
                                </span>
                              )}
                            </div>
                            {task.description && (
                              <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                                {task.description}
                              </p>
                            )}
                          </div>
                        </div>

                        {/* AI-Recommended Learning Resources Expandable Section */}
                        {resourcesCount > 0 && (
                          <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                            <button
                              type="button"
                              onClick={(e) => toggleResourceExpand(e, task.id)}
                              className="w-full flex items-center justify-between text-left group"
                            >
                              <div className="flex items-center gap-2">
                                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                                <span className="text-xs font-semibold text-indigo-300 group-hover:text-indigo-200 transition">
                                  Recommended Learning Resources
                                </span>
                                <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 font-mono font-bold border border-indigo-500/30">
                                  {resourcesCount} verified
                                </span>
                              </div>
                              <span className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 group-hover:text-white transition">
                                {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                              </span>
                            </button>

                            {/* Resource Cards List */}
                            {isExpanded && (
                              <div className="mt-2.5 space-y-2">
                                <div className="text-[10px] text-slate-400 flex items-center justify-between px-1">
                                  <span>Curated by Study Planner Agent for {task.topic_name || "this topic"}:</span>
                                  {task.priority === "High" && (
                                    <span className="text-amber-400 font-semibold">
                                      Beginner-friendly tutorials prioritized
                                    </span>
                                  )}
                                </div>

                                {task.resources.map((res, rIdx) => (
                                  <div
                                    key={rIdx}
                                    onClick={(e) => e.stopPropagation()}
                                    className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-indigo-500/40 transition flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                                  >
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[10px] font-mono text-slate-400">
                                          {rIdx + 1}.
                                        </span>
                                        <h5 className="text-xs font-semibold text-slate-200 truncate" title={res.title}>
                                          {res.title}
                                        </h5>
                                      </div>
                                      <div className="flex flex-wrap items-center gap-1.5 ml-4">
                                        <span className="text-[10px] text-slate-400 font-medium">
                                          {res.platform}
                                        </span>
                                        <span className="text-slate-600 text-[10px]">•</span>
                                        <span className={`text-[10px] px-1.5 py-0.2 rounded border font-mono ${getResourceTypeColor(res.resource_type)}`}>
                                          {res.resource_type}
                                        </span>
                                      </div>
                                    </div>

                                    {/* Direct Clickable Learn Now Link */}
                                    <a
                                      href={res.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                      className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-[11px] font-semibold transition flex-shrink-0 shadow-sm"
                                    >
                                      <span>Learn Now</span>
                                      <ExternalLink className="w-3 h-3" />
                                    </a>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
