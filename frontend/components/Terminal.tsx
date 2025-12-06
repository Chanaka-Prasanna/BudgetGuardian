"use client";
import React, { useEffect, useRef } from "react";

export const Terminal = ({
  logs,
}: {
  logs: { role: string; content: string }[];
}) => {
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="bg-slate-900 rounded-lg p-4 font-mono text-xs h-96 overflow-y-auto border border-slate-700 shadow-inner">
      <div className="text-green-400 mb-2">➜ system_init... OK</div>
      <div className="text-green-400 mb-2">➜ connecting_agent... OK</div>

      {logs.map((log, i) => (
        <div
          key={i}
          className={`mb-2 ${
            log.role === "ai"
              ? "text-blue-300"
              : log.role === "tool"
              ? "text-yellow-300"
              : "text-gray-400"
          }`}
        >
          <span className="opacity-50">[{log.role.toUpperCase()}]</span>{" "}
          {log.content}
        </div>
      ))}

      {/* Invisible element to scroll to */}
      <div ref={endRef} />
    </div>
  );
};
