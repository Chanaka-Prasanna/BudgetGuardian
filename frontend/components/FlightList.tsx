import React from "react";

interface Flight {
    flightNum: string;
    airline: string;
    route: string;
    price: number;
    time: string;
}

interface FlightListProps {
    messages: { role: string; content: string }[];
}

export function FlightList({ messages }: FlightListProps) {
    // Parse flights from messages
    const flights: Flight[] = React.useMemo(() => {
        const foundFlights: Flight[] = [];
        const flightRegex = /- Flight: (.*?) \((.*?)\)\n\s+Route: (.*?) -> (.*?)\n\s+Price: \$(\d+)\n\s+Time: (.*?)$/gm;

        messages.forEach((msg) => {
            if (msg.role === "ai" || msg.role === "model") { // Check role
                const lines = msg.content.split('\n');
                let currentFlight: Partial<Flight> = {};

                // Simple line-by-line parser since regex across newlines can be tricky with different line endings
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (line.startsWith("- Flight:")) {
                        const match = line.match(/- Flight: (.*?) \((.*?)\)/);
                        if (match) {
                            currentFlight = { flightNum: match[1], airline: match[2] };
                        }
                    } else if (line.startsWith("Route:")) {
                        currentFlight.route = line.replace("Route:", "").trim();
                    } else if (line.startsWith("Price:")) {
                        const priceStr = line.replace("Price: $", "").trim();
                        currentFlight.price = parseInt(priceStr);
                    } else if (line.startsWith("Time:")) {
                        currentFlight.time = line.replace("Time:", "").trim();
                        // Push if complete
                        if (currentFlight.flightNum && currentFlight.price) {
                            foundFlights.push(currentFlight as Flight);
                            currentFlight = {};
                        }
                    }
                }
            }
        });
        return foundFlights;
    }, [messages]);

    if (flights.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <span className="text-4xl mb-2">✈️</span>
                <p>No flights found yet.</p>
                <p className="text-sm">Ask the agent to "find flights".</p>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-4 overflow-y-auto h-full bg-gray-50">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                Available Flights <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">{flights.length}</span>
            </h2>
            <div className="grid gap-4">
                {flights.map((flight, i) => (
                    <div key={i} className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex justify-between items-center">
                        <div className="flex items-center gap-4">
                            <div className="h-12 w-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 font-bold text-lg">
                                {flight.airline.substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-900">{flight.airline} <span className="text-gray-400 font-normal text-sm">#{flight.flightNum}</span></h3>
                                <p className="text-sm text-gray-600">{flight.route}</p>
                                <p className="text-xs text-gray-400 mt-1">Departs: {flight.time}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="block text-2xl font-bold text-gray-900">${flight.price}</span>
                            <button className="mt-2 bg-black text-white text-xs px-3 py-1.5 rounded hover:bg-gray-800">
                                Book
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
