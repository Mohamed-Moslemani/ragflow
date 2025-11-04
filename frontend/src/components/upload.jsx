import { useState } from "react";

export default function UploadForm() {
  const [bank, setBank] = useState("BankMed");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setStatus("Please upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("bank", bank);
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setStatus(`Uploaded ${data.filename} (${data.size} bytes) to ${data.bank}`);
    } catch (err) {
      console.error(err);
      setStatus("Error uploading file.");
    }
  };

  return (
    <div className="max-w-lg mx-auto mt-10 p-8 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold text-purple-700 mb-4 text-center">
        Upload Banking Document
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Bank selector */}
        <div>
          <label className="block text-sm font-semibold mb-2 text-gray-700">
            Select Bank
          </label>
          <select
            value={bank}
            onChange={(e) => setBank(e.target.value)}
            className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
          >
            <option value="BankMed">BankMed</option>
            <option value="Bank of Beirut">Bank of Beirut</option>
          </select>
        </div>

        {/* File upload */}
        <div>
          <label className="block text-sm font-semibold mb-2 text-gray-700">
            Upload Document
          </label>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full border border-gray-300 rounded-md p-2 bg-gray-50"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          className="w-full bg-purple-700 text-white py-2 rounded-md hover:bg-purple-800 transition"
        >
          Submit
        </button>
      </form>

      {status && (
        <p className="mt-4 text-center text-sm text-gray-600">{status}</p>
      )}
    </div>
  );
}
