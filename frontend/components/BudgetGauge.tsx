"use client";

import React from "react";

export const BudgetGauge = ({
  total,
  remaining,
}: {
  total: number;
  remaining: number;
}) => {
  const percentage = Math.max(0, (remaining / total) * 100);

  // Color logic: Green > 50%, Yellow > 20%, Red < 20%
  let color = "bg-emerald-500";
  if (percentage < 50) color = "bg-yellow-500";
  if (percentage < 20) color = "bg-red-500";

  return (
    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-gray-500 text-sm font-medium uppercase">
        Live Ledger
      </h3>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900">
          ${remaining.toFixed(0)}
        </span>
        <span className="text-sm text-gray-400">/ ${total}</span>
      </div>

      {/* Tailwind Progress Bar */}
      <div className="mt-4 h-2 w-full bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-right text-gray-400">
        {percentage.toFixed(0)}% funds remaining
      </p>
    </div>
  );
};
