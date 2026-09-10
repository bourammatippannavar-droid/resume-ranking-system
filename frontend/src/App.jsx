import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import JobsListPage from "./pages/JobsListPage";
import CreateJobPage from "./pages/CreateJobPage";
import UploadPage from "./pages/UploadPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-emerald-50">
        <nav className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10 backdrop-blur-sm bg-white/90">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">R</span>
              </div>
              <span className="font-bold text-lg tracking-tight text-gray-900">ResumeRank</span>
            </Link>
            <Link
              to="/create"
              className="text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 px-4 py-2 rounded-lg transition-colors"
            >
              + New Job
            </Link>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-10">
          <Routes>
            <Route path="/" element={<JobsListPage />} />
            <Route path="/create" element={<CreateJobPage />} />
            <Route path="/jobs/:jobId/upload" element={<UploadPage />} />
            <Route path="/jobs/:jobId/results" element={<ResultsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

