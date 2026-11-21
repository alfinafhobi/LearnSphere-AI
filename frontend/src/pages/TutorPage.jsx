import React, { useState, useEffect, useRef } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  MessageSquareText,
  Send,
  Sparkles,
  Bot,
  User,
  Code,
  Copy,
  Check,
  HelpCircle,
  Lightbulb,
  ArrowRight
} from "lucide-react";

export default function TutorPage() {
  const { selectedSubject } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [difficulty, setDifficulty] = useState("Intermediate");
  const [selectedTopic, setSelectedSubjectTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedCodeIndex, setCopiedCodeIndex] = useState(null);

  const messagesEndRef = useRef(null);

  const loadHistory = async () => {
    if (!selectedSubject) return;
    try {
      const history = await api.tutor.getHistory(selectedSubject.id);
      if (history.length > 0) {
        setMessages(history);
      } else {
        // Initial friendly greeting from Tutor Agent
        setMessages([
          {
            id: 0,
            role: "assistant",
            content: `Hello! I'm your Intelligent AI Tutor for **${selectedSubject.name}**. I adapt explanations to your proficiency level (${difficulty}), provide step-by-step breakdowns, and share practical code snippets. What topic would you like to master today?`,
            step_by_step_points: [
              "Ask for high-level analogies or deep architectural explanations.",
              "Request code examples and debugging tips.",
              "Inquire about exam-focused question patterns."
            ],
            suggested_questions: [
              "Explain Object-Oriented Programming with a real-world analogy",
              "What is the difference between method overloading and overriding?",
              "How does exception handling work under the hood in Java?"
            ]
          }
        ]);
      }
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [selectedSubject]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await api.tutor.chat({
        subject_id: selectedSubject.id,
        topic_name: selectedTopic || selectedSubject.name,
        message: text,
        difficulty_level: difficulty
      });

      const assistantMsg = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.reply,
        step_by_step_points: response.step_by_step_points,
        code_example: response.code_example,
        recommended_next_topic: response.recommended_next_topic,
        suggested_questions: response.suggested_questions,
        agent_reasoning: response.agent_reasoning,
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Tutor message failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: "I apologize, but I encountered an error formulating the explanation. Please try again or rephrase your question."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeIndex(index);
    setTimeout(() => setCopiedCodeIndex(null), 2000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] max-w-5xl mx-auto space-y-4 pb-4">
      {/* Tutor Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-3 flex-shrink-0">
        <div>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
            Agent 3: Intelligent AI Tutor
          </span>
          <h1 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
            <MessageSquareText className="w-5 h-5 text-indigo-400" />
            Socratic Learning Chat
          </h1>
        </div>

        {/* Difficulty & Topic Config */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span className="text-slate-500 font-medium">Difficulty:</span>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="bg-transparent text-indigo-400 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="Beginner" className="bg-slate-900">Beginner (Simple & Intuitive)</option>
              <option value="Intermediate" className="bg-slate-900">Intermediate (Balanced Practical)</option>
              <option value="Advanced" className="bg-slate-900">Advanced (In-depth Internals)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Chat Messages Stream */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m, idx) => {
          const isAssistant = m.role === "assistant";

          return (
            <div
              key={m.id || idx}
              className={`flex items-start gap-3.5 ${isAssistant ? "justify-start" : "justify-end"}`}
            >
              {isAssistant && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white flex-shrink-0 shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4 sm:p-5 text-sm space-y-3 ${
                  isAssistant
                    ? "bg-[#0f172a] border border-slate-800 text-slate-200 shadow-xl"
                    : "bg-indigo-600 text-white rounded-tr-none shadow-md"
                }`}
              >
                {/* Agent reasoning tag */}
                {isAssistant && m.agent_reasoning && (
                  <div className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 inline-block mb-1">
                    [Tutor Agent Reasoning]: {m.agent_reasoning}
                  </div>
                )}

                {/* Main Content */}
                <div className="leading-relaxed whitespace-pre-wrap">{m.content}</div>

                {/* Step-by-Step Points if available */}
                {m.step_by_step_points && m.step_by_step_points.length > 0 && (
                  <div className="mt-3 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <span className="text-xs font-bold text-indigo-300 flex items-center gap-1.5 mb-1">
                      <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                      Key Step-by-Step Takeaways:
                    </span>
                    <ol className="list-decimal list-inside space-y-1 text-xs text-slate-300">
                      {m.step_by_step_points.map((pt, pIdx) => (
                        <li key={pIdx} className="leading-relaxed">{pt}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* Code Example block with copy button */}
                {m.code_example && (
                  <div className="mt-3 rounded-xl overflow-hidden border border-slate-700 bg-black/60">
                    <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-800 text-[11px] font-mono text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <Code className="w-3.5 h-3.5 text-indigo-400" />
                        Code Demonstration
                      </span>
                      <button
                        onClick={() => handleCopyCode(m.code_example, idx)}
                        className="flex items-center gap-1 text-slate-400 hover:text-white"
                      >
                        {copiedCodeIndex === idx ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="p-3.5 text-xs font-mono text-emerald-300 overflow-x-auto leading-relaxed">
                      <code>{m.code_example}</code>
                    </pre>
                  </div>
                )}

                {/* Recommended next topic tag */}
                {m.recommended_next_topic && (
                  <div className="pt-2 flex items-center gap-2 text-xs text-indigo-400">
                    <span className="text-slate-500">Recommended Next Step:</span>
                    <span className="font-semibold underline decoration-indigo-500/50">
                      {m.recommended_next_topic}
                    </span>
                  </div>
                )}

                {/* Suggested follow-up chips */}
                {m.suggested_questions && m.suggested_questions.length > 0 && (
                  <div className="pt-3 border-t border-slate-800 space-y-1.5">
                    <span className="text-[11px] font-medium text-slate-400">Suggested Follow-ups:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.suggested_questions.map((sq, sIdx) => (
                        <button
                          key={sIdx}
                          type="button"
                          onClick={() => handleSend(sq)}
                          className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 transition text-left"
                        >
                          {sq} →
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {!isAssistant && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300 flex-shrink-0 shadow-md">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/30 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
            </div>
            <span>Tutor Agent is formulating tailored explanation...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="pt-2 flex-shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3 p-2 rounded-2xl bg-[#0f172a] border border-slate-800 shadow-2xl focus-within:border-indigo-500 transition"
        >
          <input
            type="text"
            placeholder={`Ask a question on ${selectedSubject?.name || "your curriculum"}...`}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={loading}
            className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
          />

          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-40 shadow-md shadow-indigo-600/30"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
