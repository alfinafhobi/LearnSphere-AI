import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  BookOpen,
  Plus,
  CheckCircle2,
  Layers,
  ArrowRight,
  Code,
  Database,
  Cpu,
  Radio,
  Brain,
  Network,
  Coffee,
  X
} from "lucide-react";

const ICON_MAP = {
  Coffee: Coffee,
  Code: Code,
  Database: Database,
  Cpu: Cpu,
  Radio: Radio,
  Brain: Brain,
  Network: Network,
  Layers: Layers
};

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customName, setCustomName] = useState("");
  const [customCode, setCustomCode] = useState("");
  const [customDescription, setCustomDescription] = useState("");
  const [customTopics, setCustomTopics] = useState("");
  const [error, setError] = useState("");

  const { selectedSubject, selectSubject } = useAuth();

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const data = await api.subjects.getAll();
      setSubjects(data);
    } catch (err) {
      console.error("Failed to load subjects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubjects();
  }, []);

  const handleCreateCustomSubject = async (e) => {
    e.preventDefault();
    setError("");
    const topicList = customTopics.split(",").map((t) => t.trim()).filter(Boolean);
    if (topicList.length === 0) {
      setError("Please provide at least one topic (comma-separated).");
      return;
    }

    try {
      const newSubj = await api.subjects.createCustom({
        name: customName,
        code: customCode || "CUSTOM",
        description: customDescription,
        topics: topicList
      });
      setIsModalOpen(false);
      setCustomName("");
      setCustomCode("");
      setCustomDescription("");
      setCustomTopics("");
      loadSubjects();
      selectSubject(newSubj);
    } catch (err) {
      setError(err.message || "Failed to create custom subject");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <BookOpen className="w-6 h-6 text-indigo-400" />
            Curriculum & Subject Selection
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Choose your active subject for diagnostic evaluation, personalized study planning, and AI tutoring.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-indigo-600/30"
        >
          <Plus className="w-4 h-4" />
          <span>Add Custom Subject</span>
        </button>
      </div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects.map((sub) => {
          const Icon = ICON_MAP[sub.icon] || BookOpen;
          const isSelected = selectedSubject?.id === sub.id;

          return (
            <div
              key={sub.id}
              className={`p-6 rounded-2xl border transition-all flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-900 border-indigo-500/80 ring-2 ring-indigo-500/30 shadow-xl shadow-indigo-500/10"
                  : "bg-[#0f172a] border-slate-800 hover:border-slate-700 hover:scale-[1.01]"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {sub.code}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-1.5">{sub.name}</h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2 mb-4">
                  {sub.description}
                </p>

                {/* Topics Preview */}
                <div className="space-y-1.5 pt-3 border-t border-slate-800/80 mb-5">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
                    Core Topics ({sub.topics?.length || 0})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {sub.topics?.map((t) => (
                      <span
                        key={t.id}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60"
                      >
                        {t.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <button
                  onClick={() => selectSubject(sub)}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition ${
                    isSelected
                      ? "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300"
                      : "bg-slate-800 hover:bg-indigo-600 text-white"
                  }`}
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Active Focus Subject</span>
                    </>
                  ) : (
                    <>
                      <span>Select as Focus Subject</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Custom Subject Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#111827] border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-lg font-bold text-white mb-1">Add Custom Curriculum</h2>
            <p className="text-xs text-slate-400 mb-4">
              Define your custom college subject and topics for autonomous agent planning.
            </p>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleCreateCustomSubject} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Subject Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Cloud Computing & Microservices"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Subject Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CS-CLOUD"
                  value={customCode}
                  onChange={(e) => setCustomCode(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 uppercase font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  rows="2"
                  placeholder="Key subject objectives and goals..."
                  value={customDescription}
                  onChange={(e) => setCustomDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
                ></textarea>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Topics (comma-separated)
                </label>
                <textarea
                  rows="3"
                  required
                  placeholder="e.g. Virtualization, Containers & Docker, Kubernetes Orchestration, Serverless Architecture, Cloud Security"
                  value={customTopics}
                  onChange={(e) => setCustomTopics(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 font-mono text-xs"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
                >
                  Save Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
