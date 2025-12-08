"use client";
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { useTripStream } from "@/hooks/useTripStream";
import { MapComponent } from "@/components/MapComponent";
import Link from "next/link";

export default function PlanYourTrip() {
  const {
    startStream,
    resumeStream,
    messages,
    remainingBudget,
    totalBudget,
    itinerary,
    isLoading,
    foundPlaces,
    researchedPlaces,
    workflowStage,
    isPaused,
  } = useTripStream();

  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState(5000);
  const [description, setDescription] = useState("");

  // HITL State - text-based selection
  const [selectedPlaceInput, setSelectedPlaceInput] = useState("");
  
  // Track if trip has started to hide input controls
  const [tripStarted, setTripStarted] = useState(false);

  const handleStart = () => {
    if (!location || !budget) {
      alert("Please enter location and budget");
      return;
    }
    const query = description || `Find interesting places in ${location}`;
    startStream(query, budget, location, description);
    setTripStarted(true);
  };

  const handleNewTrip = () => {
    setTripStarted(false);
    setLocation("");
    setBudget(5000);
    setDescription("");
    setSelectedPlaceInput("");
  };

  const handleSelectPlaces = () => {
    if (!selectedPlaceInput.trim()) {
      alert("Please enter place numbers (comma-separated)");
      return;
    }

    // Parse user input - convert numbers to place IDs
    const inputs = selectedPlaceInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const placeIds: string[] = [];

    inputs.forEach((input) => {
      // Check if it's a number (index)
      const num = parseInt(input);
      if (!isNaN(num) && num > 0 && num <= (foundPlaces?.length || 0)) {
        // Convert 1-based index to 0-based and get place ID
        const place = foundPlaces[num - 1];
        if (place) placeIds.push(place.id);
      } else {
        // Try to find by name
        const place = foundPlaces?.find((p) =>
          p.name.toLowerCase().includes(input.toLowerCase())
        );
        if (place) placeIds.push(place.id);
      }
    });

    if (placeIds.length === 0) {
      alert("No valid places found. Please check the numbers.");
      return;
    }

    resumeStream(placeIds, "research");
    setSelectedPlaceInput("");
  };

  const handleChooseLocations = () => {
    if (!selectedPlaceInput.trim()) {
      alert("Please enter a location number for your itinerary");
      return;
    }

    // Parse user input - accept only ONE location number
    const input = selectedPlaceInput.trim();
    const num = parseInt(input);
    
    if (isNaN(num) || num < 1 || num > researchedPlaces.length) {
      alert(`Please enter a valid location number between 1 and ${researchedPlaces.length}`);
      return;
    }

    // Get the single selected place
    const place = researchedPlaces[num - 1];
    if (!place) {
      alert("Location not found. Please check the number.");
      return;
    }

    // Send only ONE place ID for itinerary
    resumeStream([place.id], "plan_itinerary");
    setSelectedPlaceInput("");
  };

  const handleAdjustItinerary = () => {
    if (!selectedPlaceInput.trim()) {
      alert("Please describe what adjustments you'd like to make");
      return;
    }

    resumeStream([], "adjust_itinerary", selectedPlaceInput);
    setSelectedPlaceInput("");
  };

  const handleFinalizeItinerary = () => {
    resumeStream([], "finalize_itinerary", "Looks perfect!");
    setSelectedPlaceInput("");
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col font-sans overflow-hidden">
      {/* HEADER */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center shrink-0">
        <Link href="/" className="text-xl font-bold text-gray-900 flex items-center gap-2 hover:opacity-80 transition-opacity">
          🛡️ BudgetGuardian{" "}
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
            AI Travel Planner
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-700">
            <span className="text-xs text-gray-500">Stage: </span>
            <span className="font-semibold text-blue-600">
              {workflowStage || "Ready"}
            </span>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT - SPLIT VIEW */}
      <main className="flex-1 flex overflow-hidden">
        {/* LEFT PANEL: AGENT & CONTROLS (40%) */}
        <div className="w-[40%] flex flex-col border-r border-gray-200 bg-white relative">
          {/* CONTROLS - Hide after trip starts */}
          {!tripStarted ? (
            <div className="p-6 border-b border-gray-100 space-y-4">
              <div className="space-y-3">
                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"
                  placeholder="📍 Enter location (e.g., Paris, Tokyo)"
                />
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"
                  placeholder="💰 Enter budget (USD)"
                />
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder:text-gray-400"
                  placeholder="✨ Describe what you're looking for (hotels, temples, restaurants, etc.)"
                  rows={3}
                />
              </div>
              <button
                onClick={handleStart}
                disabled={isLoading || !location}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg text-sm font-bold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition-all"
              >
                {isLoading ? "🔍 Searching..." : "🚀 Start Planning"}
              </button>
            </div>
          ) : (
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="text-sm">
                <div className="font-semibold text-gray-800">
                  📍 {location}
                </div>
              </div>
              <button
                onClick={handleNewTrip}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
              >
                🔄 New Trip
              </button>
            </div>
          )}

          {/* CHAT / MESSAGES */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50 pb-[22rem]">
            {messages.length === 0 && isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                  <p className="mt-4 text-gray-600 text-sm font-medium">Searching for places...</p>
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                <div className="text-center">
                  <div className="text-4xl mb-2">💬</div>
                  <p>Enter your trip details above to get started</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-lg ${
                      msg.role === "human"
                        ? "bg-blue-100 ml-8"
                        : msg.role === "error"
                        ? "bg-red-100"
                        : "bg-white shadow-sm"
                    }`}
                  >
                    <div className="text-xs text-gray-500 mb-1 font-semibold">
                      {msg.role === "human"
                        ? "You"
                        : msg.role === "error"
                        ? "Error"
                        : "Assistant"}
                    </div>
                    <div className="prose-content text-sm text-gray-900">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-center gap-2 text-gray-500 text-sm p-3">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    <span>Processing...</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ACTION BAR (HITL) - Fixed Position */}
          {workflowStage === "select_locations" && isPaused && (
            <div className="absolute bottom-0 left-0 right-0 p-3 bg-blue-50 border-t border-blue-100 space-y-2 shadow-lg max-h-80 overflow-y-auto">
              <div className="text-sm text-blue-900 font-medium">
                ✅ Found {foundPlaces?.length || 0} places
              </div>

              {/* Places List */}
              {foundPlaces && foundPlaces.length > 0 && (
                <div className="max-h-40 overflow-y-auto bg-white rounded p-2 text-xs border border-blue-200">
                  {foundPlaces.map((place, idx) => (
                    <div key={place.id} className="py-1 flex gap-2">
                      <span className="font-bold text-blue-600">
                        {idx + 1}.
                      </span>
                      <span className="text-gray-700">{place.name}</span>
                      <span className="text-gray-400 text-xs">
                        ({place.type})
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="text-xs text-blue-700">
                Enter place numbers to research (comma-separated):
              </div>
              <input
                type="text"
                value={selectedPlaceInput}
                onChange={(e) => setSelectedPlaceInput(e.target.value)}
                className="w-full p-2 border border-blue-200 rounded-lg bg-white text-gray-900 text-sm placeholder:text-gray-400"
                placeholder="e.g., 1, 3, 5, 7"
                onKeyPress={(e) => e.key === "Enter" && handleSelectPlaces()}
              />
              <button
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-700 transition-colors disabled:opacity-50"
                onClick={handleSelectPlaces}
                disabled={isLoading}
              >
                {isLoading ? "Processing..." : "Research Selected Places →"}
              </button>
            </div>
          )}

          {workflowStage === "choose_locations" &&
            isPaused &&
            researchedPlaces.length > 0 && (
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-green-50 border-t border-green-100 space-y-2 shadow-lg max-h-80 overflow-y-auto">
                <div className="text-sm text-green-900 font-medium">
                  ✅ Research completed for {researchedPlaces.length} places
                </div>

                {/* Researched Places List */}
                <div className="max-h-40 overflow-y-auto bg-white rounded p-2 text-xs border border-green-200">
                  {researchedPlaces.map((place, idx) => (
                    <div key={place.id} className="py-1 flex gap-2">
                      <span className="font-bold text-green-600">
                        {idx + 1}.
                      </span>
                      <span className="text-gray-700">{place.name}</span>
                      <span className="text-gray-400 text-xs">
                        ({place.type})
                      </span>
                    </div>
                  ))}
                </div>

                <div className="text-xs text-green-700">
                  Select ONE location number for your itinerary:
                </div>
                <input
                  type="text"
                  value={selectedPlaceInput}
                  onChange={(e) => setSelectedPlaceInput(e.target.value)}
                  className="w-full p-2 border border-green-200 rounded-lg bg-white text-gray-900 text-sm placeholder:text-gray-400"
                  placeholder="e.g., 1"
                  onKeyPress={(e) =>
                    e.key === "Enter" && handleChooseLocations()
                  }
                />
                <button
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-green-700 transition-colors disabled:opacity-50"
                  onClick={handleChooseLocations}
                  disabled={isLoading}
                >
                  {isLoading ? "Planning..." : "Create Itinerary →"}
                </button>
              </div>
            )}

          {workflowStage === "review_itinerary" && isPaused && (
            <div className="absolute bottom-0 left-0 right-0 p-3 bg-purple-50 border-t border-purple-100 space-y-2 shadow-lg max-h-80 overflow-y-auto">
              <div className="text-sm text-purple-900 font-medium">
                ✅ Initial itinerary created! Review and adjust if needed
              </div>

              <div className="text-xs text-purple-700">
                Request adjustments (e.g., "Add more activities", "Change hotel
                to budget option", "Extend to 3 days"):
              </div>
              <textarea
                value={selectedPlaceInput}
                onChange={(e) => setSelectedPlaceInput(e.target.value)}
                className="w-full p-2 border border-purple-200 rounded-lg bg-white text-gray-900 text-sm placeholder:text-gray-400 resize-none"
                placeholder="Describe changes you'd like..."
                rows={3}
                onKeyPress={(e) =>
                  e.key === "Enter" &&
                  !e.shiftKey &&
                  handleAdjustItinerary()
                }
              />
              <div className="flex gap-2">
                <button
                  className="flex-1 bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-purple-700 transition-colors disabled:opacity-50"
                  onClick={handleAdjustItinerary}
                  disabled={isLoading || !selectedPlaceInput.trim()}
                >
                  {isLoading ? "Adjusting..." : "Adjust Itinerary"}
                </button>
                <button
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-green-700 transition-colors disabled:opacity-50"
                  onClick={handleFinalizeItinerary}
                  disabled={isLoading}
                >
                  {isLoading ? "Finalizing..." : "Looks Perfect! ✓"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT PANEL: Map View (60%) */}
        <div className="flex-1 bg-gray-100 relative flex flex-col">
          {/* Map Content */}
          <div className="flex-1 relative overflow-hidden">
            <MapComponent places={foundPlaces || []} />
            {/* Floating Itinerary Overlay */}
            {itinerary.length > 0 && (
              <div className="absolute top-4 right-4 w-80 bg-white/90 backdrop-blur shadow-xl rounded-xl p-4 border border-gray-200 z-10">
                <h3 className="font-bold text-gray-800 mb-2">
                  Current Itinerary
                </h3>
                <ul className="space-y-2 text-sm">
                  {itinerary.map((item, i) => (
                    <li key={i} className="text-gray-700">
                      • {item.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

