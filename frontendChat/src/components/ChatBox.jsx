import { useState, useRef, useEffect } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [database, setDatabase] = useState("Bank_of_Beirut");
  const chatEndRef = useRef(null);

  const sendMessage = async () => { 
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(
        `http://localhost:8000/chat/${encodeURIComponent(input)}?bank_name=${database}`
      );
      const data = await res.json();

      const botMessage = {
        sender: "bot",
        text: data.response || "No response from server.",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Could not reach backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-purple-50 to-white p-4">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-2xl p-6 flex flex-col h-[85vh] border border-purple-100">
        {/* Header */}
        <div className="flex items-center justify-between mb-10 border-b pb-3 border-gray-200">
          <h1 className="text-2xl font-bold text-purple-800 tracking-tight">
            Bank RAG Assistant  
          </h1>
          <select
            value={database}
            onChange={(e) => setDatabase(e.target.value)}
            className="border border-gray-300 rounded-lg mx-6 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 bg-gray-50"
          >
            <option value="Bank_of_Beirut">Bank of Beirut</option>
            <option value="BankMed">BankMed</option>
          </select>
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto rounded-xl p-4 space-y-3 bg-gray-50 border border-gray-100 shadow-inner">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-3 rounded-2xl max-w-[75%] break-words ${
                msg.sender === "user"
                  ? "ml-auto bg-purple-600 text-white shadow-md"
                  : "mr-auto bg-white border border-gray-200 text-gray-800 shadow-sm"
              }`}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="mr-auto bg-purple-100 text-purple-700 px-3 py-2 rounded-xl w-fit text-sm animate-pulse">
              Thinking...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="flex items-center mt-4">
          <textarea
            className="flex-1 border border-gray-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-gray-50 resize-none"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your bank policy, card, or FAQs..."
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className={`ml-3 px-5 py-2.5 rounded-lg text-white font-semibold transition-all shadow-md ${
              loading
                ? "bg-purple-400 cursor-not-allowed"
                : "bg-purple-700 hover:bg-purple-800"
            }`}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
