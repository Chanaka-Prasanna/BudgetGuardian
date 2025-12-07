import React from "react";
import ReactMarkdown from "react-markdown";

interface ResearchPanelProps {
    messages: { role: string; content: string }[];
}

export function ResearchPanel({ messages }: ResearchPanelProps) {
    // Extract research reports
    const reports = React.useMemo(() => {
        return messages
            .filter(m => m.content.includes("### Research Report:"))
            .map(m => m.content);
    }, [messages]);

    if (reports.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <span className="text-4xl mb-2">🧐</span>
                <p>No research notes yet.</p>
                <p className="text-sm">Select places and click "Research Selected".</p>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6 overflow-y-auto h-full bg-white">
            <h2 className="text-xl font-bold text-gray-800 border-b pb-4">Research Findings</h2>
            {reports.map((report, i) => (
                <div key={i} className="prose prose-sm max-w-none bg-yellow-50 p-6 rounded-xl border border-yellow-100">
                    {/* We render the raw markdown content which contains the report */}
                    <pre className="whitespace-pre-wrap font-sans text-gray-700">{report}</pre>
                </div>
            ))}
        </div>
    );
}
