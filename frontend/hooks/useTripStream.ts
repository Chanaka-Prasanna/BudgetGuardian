import { useState, useRef } from "react";

type ItineraryItem = {
  name: string;
  cost: number;
  type: string;
  status: string;
};

type StreamState = {
  messages: { role: string; content: string }[];
  totalBudget: number;
  remainingBudget: number;
  itinerary: ItineraryItem[];
  isLoading: boolean;
};

export function useTripStream() {
  const [state, setState] = useState<StreamState>({
    messages: [],
    totalBudget: 0,
    remainingBudget: 0,
    itinerary: [],
    isLoading: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = async (
    query: string,
    budget: number,
    location: string
  ) => {
    // 1. Reset State
    setState({
      messages: [],
      totalBudget: budget,
      remainingBudget: budget,
      itinerary: [],
      isLoading: true,
    });

    abortControllerRef.current = new AbortController();

    try {
      // 2. Initiate Stream (Using fetch instead of EventSource to support POST)
      const response = await fetch("http://localhost:8000/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, budget, location }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.body) throw new Error("No response body");

      // 3. Read the Stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // SSE sends messages like "data: {...}\n\n"
        const lines = chunk.split("\n\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.replace("data: ", "").trim();
            if (jsonStr === "[DONE]") break;

            try {
              const payload = JSON.parse(jsonStr);
              handleEvent(payload);
            } catch (e) {
              console.error("Failed to parse chunk", e);
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") console.error("Stream error:", err);
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const handleEvent = (payload: any) => {
    setState((prev) => {
      // Logic to merge updates
      if (payload.type === "message") {
        return { ...prev, messages: [...prev.messages, payload.data] };
      }
      if (payload.type === "ledger_update") {
        return {
          ...prev,
          remainingBudget: payload.data.remaining,
          totalBudget: payload.data.total,
          itinerary: payload.data.itinerary,
        };
      }
      return prev;
    });
  };

  const stopStream = () => abortControllerRef.current?.abort();

  return { ...state, startStream, stopStream };
}
