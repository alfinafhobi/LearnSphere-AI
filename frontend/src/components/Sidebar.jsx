import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  ClipboardCheck,
  CalendarCheck2,
  MessageSquareText,
  FileQuestion,
  BarChart3,
  Bot,
  User,
  Sparkles
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/subjects", label: "Subjects & Topics", icon: BookOpen },
  { to: "/assessment", label: "Diagnostic Test", icon: ClipboardCheck },
  { to: "/planner", label: "Study Planner", icon: CalendarCheck2 },
  { to: "/tutor", label: "AI Tutor Chat", icon: MessageSquareText },
  { to: "/quiz", label: "Quizzes & Practice", icon: FileQuestion },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/agents", label: "Agent Activity", icon: Bot, highlight: true },
  { to: "/profile", label: "Student Profile", icon: User },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800/80 min-h-[calc(100vh-61px)] p-4 flex flex-col justify-between select-none">
      <div className="space-y-6">
        <div className="px-3">
          <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
            Platform Navigation
          </p>
        </div>

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm shadow-indigo-500/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  } ${item.highlight ? "relative" : ""}`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
                {item.highlight && (
                  <span className="ml-auto flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Multi-Agent status capsule banner */}
      <div className="p-3.5 rounded-xl bg-gradient-to-br from-indigo-950/60 to-purple-950/60 border border-indigo-500/20">
        <div className="flex items-center gap-2 mb-1.5">
          <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" style={{ animationDuration: "8s" }} />
          <span className="text-xs font-semibold text-slate-200">LangGraph Multi-Agent</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed mb-2.5">
          5 autonomous agents continuously observing, planning, tutoring, and adapting.
        </p>
        <div className="flex items-center gap-1.5">
          <div className="flex -space-x-1">
            <span className="w-4 h-4 rounded-full bg-blue-500 border border-slate-900 inline-block text-[9px] text-center font-bold text-white leading-4">A</span>
            <span className="w-4 h-4 rounded-full bg-purple-500 border border-slate-900 inline-block text-[9px] text-center font-bold text-white leading-4">P</span>
            <span className="w-4 h-4 rounded-full bg-emerald-500 border border-slate-900 inline-block text-[9px] text-center font-bold text-white leading-4">T</span>
            <span className="w-4 h-4 rounded-full bg-amber-500 border border-slate-900 inline-block text-[9px] text-center font-bold text-white leading-4">Q</span>
            <span className="w-4 h-4 rounded-full bg-rose-500 border border-slate-900 inline-block text-[9px] text-center font-bold text-white leading-4">M</span>
          </div>
          <span className="text-[10px] text-indigo-300 font-mono">Real State Graph</span>
        </div>
      </div>
    </aside>
  );
}
