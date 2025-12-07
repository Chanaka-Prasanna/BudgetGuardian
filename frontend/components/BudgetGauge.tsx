"use client";

import React from "react";

export const BudgetGauge = ({
  total,
  remaining,
  size = "default",
}: {
  total: number;
  remaining: number;
  size?: "small" | "default";
}) => {
  const percentage = Math.max(0, (remaining / total) * 100);

  // Color logic: Green > 50%, Yellow > 20%, Red < 20%
  let color = "bg-emerald-500";
  if (percentage < 50) color = "bg-yellow-500";
  if (percentage < 20) color = "bg-red-500";

  if (size === "small") {
    return (
      <div className="flex items-center gap-3 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
        <div className="flex flex-col items-end">
          <span className="text-sm font-bold text-gray-900 leading-none">
            ${remaining.toFixed(0)}
          </span>
          <span className="text-[10px] text-gray-500 leading-none">
            / ${total}
          </span>
        </div>

        {/* Mini Circular or Bar Gauge */}
        <div className="h-1.5 w-16 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${color}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  }

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
