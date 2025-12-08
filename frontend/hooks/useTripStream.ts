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
  foundPlaces: any[];
  researchedPlaces: any[];
  workflowStage: string;
  isLoading: boolean;
  threadId: string | null;
  isPaused: boolean;
};

export function useTripStream() {
  const [state, setState] = useState<StreamState>({
    messages: [],
    totalBudget: 0,
    remainingBudget: 0,
    itinerary: [],
    foundPlaces: [],
    researchedPlaces: [],
    workflowStage: "initial",
    isLoading: false,
    threadId: null,
    isPaused: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const processStream = async (response: Response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    if (!response.body) throw new Error("No response body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");

        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.replace("data: ", "").trim();
            if (jsonStr === "[DONE]") {
              return;
            }

            try {
              const payload = JSON.parse(jsonStr);
              if (payload.type === "error") {
                console.error("Server error:", payload.data);
                setState((prev) => ({
                  ...prev,
                  messages: [
                    ...prev.messages,
                    { role: "error", content: `Error: ${payload.data}` },
                  ],
                }));
              } else {
                handleEvent(payload);
              }
            } catch (e) {
              console.error("Failed to parse chunk", jsonStr, e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Stream processing error:", error);
      throw error;
    }
  };

  const startStream = async (
    query: string,
    budget: number,
    location: string,
    description: string = ""
  ) => {
    setState({
      messages: [],
      totalBudget: budget,
      remainingBudget: budget,
      itinerary: [],
      foundPlaces: [],
      researchedPlaces: [],
      workflowStage: "search",
      isLoading: true,
      threadId: null,
      isPaused: false,
    });

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("http://localhost:8000/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, budget, location, description }),
        signal: abortControllerRef.current.signal,
      });
      await processStream(response);
    } catch (err: any) {
      if (err.name !== "AbortError") console.error("Stream error:", err);
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const resumeStream = async (
    selectedPlaces: string[],
    action: string = "research",
    message: string = ""
  ) => {
    if (!state.threadId) return;

    setState((prev) => ({ ...prev, isLoading: true, isPaused: false }));
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("http://localhost:8000/api/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: state.threadId,
          selected_places: selectedPlaces,
          action: action,
          message: message,
        }),
        signal: abortControllerRef.current.signal,
      });
      await processStream(response);
    } catch (err: any) {
      if (err.name !== "AbortError") console.error("Resume error:", err);
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const handleEvent = (payload: any) => {
    setState((prev) => {
      if (payload.type === "meta") {
        return { ...prev, threadId: payload.thread_id };
      }
      if (payload.type === "message") {
        // Check if message already exists to prevent duplicates
        const isDuplicate = prev.messages.some(
          (msg) => msg.role === payload.data.role && msg.content === payload.data.content
        );
        if (isDuplicate) {
          return prev; // Skip duplicate messages
        }
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
      if (payload.type === "map_update") {
        return {
          ...prev,
          foundPlaces: payload.data,
        };
      }
      if (payload.type === "research_update") {
        return {
          ...prev,
          researchedPlaces: payload.data,
        };
      }
      if (payload.type === "workflow_stage") {
        return {
          ...prev,
          workflowStage: payload.data,
        };
      }
      if (payload.type === "status" && payload.data === "paused") {
        return {
          ...prev,
          isPaused: true,
        };
      }
      if (payload.type === "error") {
        return {
          ...prev,
          messages: [
            ...prev.messages,
            { role: "error", content: `❌ Error: ${payload.data}` },
          ],
        };
      }
      return prev;
    });
  };

  const stopStream = () => abortControllerRef.current?.abort();

  return { ...state, startStream, resumeStream, stopStream };
}
