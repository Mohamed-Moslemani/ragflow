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

    try {
      setStatus("Sending bank and file to backend...");

      // 1) Send bank name to /bankname
      const bankForm = new FormData();
      bankForm.append("bank_name", bank);

      const bankRes = await fetch("http://localhost:8000/bankname", {
        method: "POST",
        body: bankForm,
      });

      if (!bankRes.ok) throw new Error("Failed to set bank name.");
      const bankData = await bankRes.json();

      // 2) Upload file to /documents
      const fileForm = new FormData();
      fileForm.append("file", file);

      const fileRes = await fetch("http://localhost:8000/documents", {
        method: "POST",
        body: fileForm,
      });

      if (!fileRes.ok) throw new Error("Failed to upload file.");
      const fileData = await fileRes.json();
      const uploadedFilename = fileData.filename;

      // 3) Process document
      const processRes = await fetch(
        `http://localhost:8000/documents/${encodeURIComponent(
          uploadedFilename
        )}/process`
      );

      if (!processRes.ok) throw new Error("Failed to process document.");
      const processData = await processRes.json();

      setStatus(
        `Bank: ${bankData.bank_name} | File: ${uploadedFilename} | ${processData.message}`
      );
    } catch (err) {
      console.error(err);
      setStatus(err.message || "Error while uploading or processing file.");
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
            <option value="Bank_of_Beirut">Bank of Beirut</option>
          </select>
        </div>

        {/* File upload */}
        <div>
          <label className="block text-sm font-semibold mb-2 text-gray-700">
            Upload Document
          </label>
          <input
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
            className="w-full border border-gray-300 rounded-md p-2 bg-gray-50"
          />
        </div>

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
