import React from "react";

export default function StatCard({ title, value, subtitle, icon: Icon, color = "indigo", trend }) {
  const colorMap = {
    indigo: "from-indigo-500/20 to-indigo-600/5 text-indigo-400 border-indigo-500/30",
    emerald: "from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/30",
    purple: "from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/30",
    amber: "from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/30",
    rose: "from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/30",
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${colorMap[color] || colorMap.indigo} border backdrop-blur-sm relative overflow-hidden transition-all hover:scale-[1.01]`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-700/50 shadow-inner">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
        {trend && (
          <span className="text-xs font-semibold text-emerald-400">
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
    </div>
  );
}
