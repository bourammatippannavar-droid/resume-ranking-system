import { getCandidateFileUrl } from "../api/client";

function ResumePreviewModal({ candidate, jobId, onClose }) {
  if (!candidate) return null;

  const fileUrl = getCandidateFileUrl(jobId, candidate.candidate_id);
  const isPdf = candidate.filename.toLowerCase().endsWith(".pdf");

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-3xl h-[85vh] flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">{candidate.filename}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 text-xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-hidden bg-gray-50">
          {isPdf ? (
            <iframe
              src={fileUrl}
              title={candidate.filename}
              className="w-full h-full border-0"
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              <p className="text-gray-500 text-sm">
                DOCX files cannot be previewed inline. Download to view.
              </p>
              <a                href={fileUrl}
                download={candidate.filename}
                className="bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
              >
                Download {candidate.filename}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResumePreviewModal;

