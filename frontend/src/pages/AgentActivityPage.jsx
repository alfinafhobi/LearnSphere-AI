import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import WorkflowVisualizer from "../components/WorkflowVisualizer";
import {
  Bot,
  Play,
  RotateCw,
  Clock,
  CheckCircle,
  Eye,
  Calendar,
  MessageSquare,
  HelpCircle,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  ArrowRight
} from "lucide-react";

export default function AgentActivityPage() {
  const { selectedSubject } = useAuth();
  const [agentStatuses, setAgentStatuses] = useState([]);
  const [logs, setLogs] = useState([]);
  const [selectedAgentFilter, setSelectedAgentFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [runningWorkflow, setRunningWorkflow] = useState(false);
  const [expandedLogId, setExpandedLogId] = useState(null);
  const [workflowBanner, setWorkflowBanner] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statuses, activityLogs] = await Promise.all([
        api.agents.getStatus(),
        api.agents.getActivity(selectedAgentFilter === "all" ? undefined : selectedAgentFilter)
      ]);
      setAgentStatuses(statuses);
      setLogs(activityLogs);
    } catch (err) {
      console.error("Failed to load agent activity:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedAgentFilter]);

  const handleRunWorkflow = async () => {
    if (!selectedSubject) return;
    setRunningWorkflow(true);
    setWorkflowBanner(null);
    try {
      const res = await api.agents.runWorkflow(selectedSubject.id, "diagnostic_to_plan");
      setWorkflowBanner(res);
      await loadData();
    } catch (err) {
      console.error("Workflow run failed:", err);
    } finally {
      setRunningWorkflow(false);
    }
  };

  const getCycleBadge = (cycle) => {
    const cycleColors = {
      Observe: "bg-blue-500/15 text-blue-400 border-blue-500/30",
      Analyze: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
      Plan: "bg-purple-500/15 text-purple-400 border-purple-500/30",
      Act: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
      Evaluate: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
      Adapt: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    };
    return cycleColors[cycle] || "bg-slate-800 text-slate-300 border-slate-700";
  };

  return (
    <div className="space-y-6 pb-16 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            Real Multi-Agent Orchestration
          </span>
          <h1 className="text-2xl font-bold text-white mt-1 flex items-center gap-2">
            <Bot className="w-6 h-6 text-emerald-400" />
            Autonomous Agent Activity & Trace Logs
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real recorded multi-agent executions, reasoning steps, tool invocations, and adaptive replanning decisions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Refresh Logs"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleRunWorkflow}
            disabled={runningWorkflow}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${runningWorkflow ? "animate-spin" : ""}`} />
            <span>{runningWorkflow ? "Orchestrating Graph..." : "Execute Demonstration Cycle"}</span>
          </button>
        </div>
      </div>

      {/* Workflow Run Result Toast Banner */}
      {workflowBanner && (
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>
              <strong>LangGraph Execution Finished:</strong> {workflowBanner.message} State reached:{" "}
              <code className="text-white bg-slate-900 px-1 py-0.5 rounded font-mono">{workflowBanner.workflow_step}</code>
            </span>
          </div>
          <button onClick={() => setWorkflowBanner(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Visualizer */}
      <WorkflowVisualizer currentStage="Evaluate" />

      {/* 5 Specialized Agents Status Cards */}
      <div>
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
          Active Specialized Agents (Live System Architecture)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3.5">
          {agentStatuses.map((ag, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl flex flex-col justify-between space-y-3 relative overflow-hidden"
            >
              <div className="flex items-center justify-between">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${getCycleBadge(ag.state_cycle)}`}>
                  {ag.state_cycle}
                </span>
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-100 line-clamp-1">{ag.name}</h3>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {ag.role}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 text-[10px]">
                <span className="text-slate-500 block">Latest Action:</span>
                <span className="text-indigo-300 font-medium line-clamp-1">{ag.last_action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Execution Logs Table / Stream */}
      <div className="p-6 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              Recorded Agent Execution History
            </h2>
            <p className="text-xs text-slate-400">Verifiable trace logs stored in database</p>
          </div>

          {/* Filter by agent */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Filter Agent:</span>
            <select
              value={selectedAgentFilter}
              onChange={(e) => setSelectedAgentFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-300 focus:outline-none"
            >
              <option value="all">All 5 Agents</option>
              <option value="Assessment">Assessment Agent</option>
              <option value="Planner">Planner Agent</option>
              <option value="Tutor">Tutor Agent</option>
              <option value="Quiz">Quiz Agent</option>
              <option value="Progress">Progress Agent</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-xs text-slate-400">
            <div className="inline-block animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mb-2"></div>
            <p>Loading agent traces...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No agent activities recorded yet. Run a diagnostic test or click "Execute Demonstration Cycle".
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => {
              const isExpanded = expandedLogId === log.id;
              let inputData = null;
              let outputData = null;
              try {
                if (log.input_data_json) inputData = JSON.parse(log.input_data_json);
                if (log.output_data_json) outputData = JSON.parse(log.output_data_json);
              } catch {}

              return (
                <div
                  key={log.id}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-2 text-xs"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <span className={`px-2 py-0.5 rounded font-mono font-semibold text-[10px] border ${getCycleBadge(log.state_cycle)}`}>
                        {log.state_cycle}
                      </span>
                      <strong className="text-slate-200 font-semibold">{log.agent_name}</strong>
                    </div>

                    <div className="flex items-center gap-2 text-slate-500 font-mono text-[11px]">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  {/* Action & Decision summary */}
                  <div>
                    <h3 className="font-semibold text-indigo-300 text-xs">{log.action}</h3>
                    <p className="text-slate-300 mt-1 leading-relaxed">{log.reasoning}</p>
                    {log.decision && (
                      <p className="text-emerald-400 font-mono text-[11px] mt-1">
                        <strong>Decision:</strong> {log.decision}
                      </p>
                    )}
                  </div>

                  {/* Toggle JSON details */}
                  {(inputData || outputData) && (
                    <div className="pt-2">
                      <button
                        onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                        className="text-[11px] text-slate-400 hover:text-indigo-300 flex items-center gap-1 font-mono transition"
                      >
                        <span>{isExpanded ? "Hide Execution Payloads" : "Inspect Agent Input/Output State"}</span>
                        {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                      </button>

                      {isExpanded && (
                        <div className="mt-2.5 grid grid-cols-1 md:grid-cols-2 gap-3 p-3 rounded-lg bg-black/60 border border-slate-800 font-mono text-[11px]">
                          <div>
                            <span className="text-slate-500 block mb-1">State Input:</span>
                            <pre className="text-slate-400 overflow-x-auto leading-relaxed">
                              {JSON.stringify(inputData, null, 2)}
                            </pre>
                          </div>
                          <div>
                            <span className="text-slate-500 block mb-1">State Output / Decision:</span>
                            <pre className="text-emerald-400 overflow-x-auto leading-relaxed">
                              {JSON.stringify(outputData, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
