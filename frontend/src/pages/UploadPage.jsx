import { useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { uploadCandidates } from "../api/client";

function UploadPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const addFiles = useCallback((newFiles) => {
    const validFiles = Array.from(newFiles).filter((file) =>
      file.name.toLowerCase().endsWith(".pdf") || file.name.toLowerCase().endsWith(".docx")
    );
    setFiles((prev) => [...prev, ...validFiles]);
  }, []);

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    addFiles(event.dataTransfer.files);
  };

  const handleFileInput = (event) => {
    addFiles(event.target.files);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError("Please add at least one resume file.");
      return;
    }
    setIsUploading(true);
    setError(null);
    try {
      const response = await uploadCandidates(jobId, files);
      setUploadResult(response.data);
      setFiles([]);
    } catch (err) {
      setError("Upload failed. Please check that the backend server is running.");
    } finally {
      setIsUploading(false);
    }
  };

  const dropZoneClass = isDragging
    ? "border-2 border-dashed rounded-2xl p-12 text-center transition-all border-teal-400 bg-teal-50"
    : "border-2 border-dashed rounded-2xl p-12 text-center transition-all border-gray-300 bg-white hover:border-gray-400";

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Upload Resumes</h1>
        <p className="text-gray-500 mt-1.5">Upload candidate resumes in PDF or DOCX format.</p>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={dropZoneClass}
      >
        <div className="w-12 h-12 rounded-full bg-teal-50 flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">??</span>
        </div>
        <p className="text-gray-600 mb-4">Drag and drop resumes here, or</p>
        <label className="inline-block bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors">
          Browse Files
          <input
            type="file"
            multiple
            accept=".pdf,.docx"
            onChange={handleFileInput}
            className="hidden"
          />
        </label>
        <p className="text-xs text-gray-400 mt-4">PDF or DOCX only</p>
      </div>

      {files.length > 0 && (
        <div className="mt-5 bg-white rounded-xl border border-gray-200 divide-y divide-gray-100 overflow-hidden">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm text-gray-700 truncate flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-500 flex-shrink-0" />
                {file.name}
              </span>
              <button
                onClick={() => removeFile(index)}
                className="text-gray-400 hover:text-red-500 text-sm ml-3 flex-shrink-0 transition-colors"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200 mt-5">
          {error}
        </div>
      )}

      {uploadResult && (
        <div className="mt-5 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3.5">
          <p className="text-emerald-800 text-sm font-medium flex items-center gap-2">
            <span>?</span>
            {uploadResult.created.length} resume(s) uploaded and parsed successfully.
          </p>
          {uploadResult.failed.length > 0 && (
            <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
              {uploadResult.failed.map((failure, i) => (
                <li key={i}>{failure.filename}: {failure.reason}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="flex gap-3 mt-6">
        <button
          onClick={handleUpload}
          disabled={isUploading || files.length === 0}
          className="flex-1 bg-gradient-to-r from-teal-500 to-emerald-600 text-white font-medium py-3 rounded-lg hover:from-teal-600 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {isUploading ? "Uploading & Parsing..." : "Upload Resumes"}
        </button>
        <button
          onClick={() => navigate("/jobs/" + jobId + "/results")}
          className="bg-white text-gray-700 font-medium px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
        >
          View Results
        </button>
      </div>
    </div>
  );
}

export default UploadPage;
