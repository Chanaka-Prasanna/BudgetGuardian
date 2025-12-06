"use client";
import React, { useState } from "react";
import { useTripStream } from "@/hooks/useTripStream";
import { BudgetGauge } from "@/components/BudgetGauge";
import { Terminal } from "@/components/Terminal";

export default function Dashboard() {
  const {
    startStream,
    messages,
    remainingBudget,
    totalBudget,
    itinerary,
    isLoading,
  } = useTripStream();

  const [input, setInput] = useState("Plan a 3-day luxury trip to Paris");
  const [budget, setBudget] = useState(3000);
  const [location, setLocation] = useState("Paris");

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <header className="max-w-6xl mx-auto mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          🛡️ BudgetGuardian{" "}
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
            PROTOTYPE
          </span>
        </h1>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT COL: Controls & Terminal */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Location
                </label>
                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition"
                  placeholder="e.g. New York"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Total Budget ($)
                </label>
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition"
                  placeholder="e.g. 3000"
                />
              </div>
            </div>
            <div className="flex gap-4">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 p-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition"
                placeholder="Where do you want to go?"
              />
              <button
                onClick={() => startStream(input, budget, location)}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 transition-colors"
              >
                {isLoading ? "Thinking..." : "Launch Agent"}
              </button>
            </div>
          </div>

          <Terminal logs={messages} />
        </div>

        {/* RIGHT COL: State Visualization */}
        <div className="space-y-6">
          <BudgetGauge
            total={totalBudget || budget}
            remaining={totalBudget ? remainingBudget : budget}
          />

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm min-h-[300px]">
            <h3 className="text-gray-500 text-sm font-medium uppercase mb-4">
              Confirmed Itinerary
            </h3>
            {itinerary.length === 0 ? (
              <div className="text-center text-gray-400 py-10 text-sm">
                No bookings confirmed yet.
                <br />
                Waiting for agent transactions...
              </div>
            ) : (
              <ul className="space-y-3">
                {itinerary.map((item, i) => (
                  <li
                    key={i}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {item.name}
                      </div>
                      <div className="text-xs text-gray-500 capitalize">
                        {item.type}
                      </div>
                    </div>
                    <div className="font-mono text-red-600 font-medium">
                      -${item.cost}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
