import React from "react";
import { Eye, Search, Calendar, MessageSquare, CheckCircle, RefreshCw } from "lucide-react";

const STAGES = [
  { id: "Observe", label: "Observe", agent: "Learning Assessment", desc: "Diagnostic testing & knowledge scan", icon: Eye, color: "text-blue-400 border-blue-500/40 bg-blue-500/10" },
  { id: "Analyze", label: "Analyze", agent: "Learning Assessment", desc: "Gap analysis & proficiency classification", icon: Search, color: "text-cyan-400 border-cyan-500/40 bg-cyan-500/10" },
  { id: "Plan", label: "Plan", agent: "Study Planner", desc: "Dynamic schedule & weighted allocation", icon: Calendar, color: "text-purple-400 border-purple-500/40 bg-purple-500/10" },
  { id: "Act", label: "Act", agent: "AI Tutor & Quizzes", desc: "Socratic explanation & question generation", icon: MessageSquare, color: "text-indigo-400 border-indigo-500/40 bg-indigo-500/10" },
  { id: "Evaluate", label: "Evaluate", agent: "Quiz & Evaluation", desc: "Score calculation & misconception diagnosis", icon: CheckCircle, color: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" },
  { id: "Adapt", label: "Adapt", agent: "Progress Monitoring", desc: "Trigger study-plan revision & human approval", icon: RefreshCw, color: "text-amber-400 border-amber-500/40 bg-amber-500/10" },
];

export default function WorkflowVisualizer({ currentStage = "Act" }) {
  return (
    <div className="p-5 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">The Autonomous Agentic AI Cycle</h4>
          <p className="text-xs text-slate-400">Continuous closed-loop multi-agent orchestration via LangGraph</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-xs text-emerald-400 font-mono font-medium">Observe → Analyze → Plan → Act → Evaluate → Adapt</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
        {STAGES.map((s, idx) => {
          const Icon = s.icon;
          const isActive = s.id.toLowerCase() === currentStage.toLowerCase();
          return (
            <div
              key={s.id}
              className={`p-3 rounded-xl border transition-all ${
                isActive
                  ? `${s.color} ring-2 ring-indigo-500/50 scale-[1.02]`
                  : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500">
                  0{idx + 1}
                </span>
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
              </div>
              <h5 className={`text-xs font-bold mb-0.5 ${isActive ? "text-white" : "text-slate-200"}`}>
                {s.label}
              </h5>
              <p className="text-[11px] font-semibold text-indigo-400 truncate">{s.agent}</p>
              <p className="text-[10px] text-slate-500 mt-1 leading-tight">{s.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
