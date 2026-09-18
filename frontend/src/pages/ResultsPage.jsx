import { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { searchCandidates, updateJobWeights, getJob, updateCandidateStatus, exportResultsUrl } from "../api/client";
import ResumePreviewModal from "../components/ResumePreviewModal";

const DEFAULT_WEIGHTS = {
  weight_semantic: 0.5,
  weight_skills: 0.2,
  weight_experience: 0.15,
  weight_education: 0.1,
  weight_certifications: 0.05,
};

const WEIGHT_LABELS = {
  weight_semantic: "Semantic Match",
  weight_skills: "Skills Match",
  weight_experience: "Experience",
  weight_education: "Education",
  weight_certifications: "Certifications",
};

const RANK_STYLES = {
  1: "bg-gradient-to-br from-yellow-400 to-amber-500 text-white",
  2: "bg-gradient-to-br from-gray-300 to-gray-400 text-white",
  3: "bg-gradient-to-br from-amber-600 to-amber-700 text-white",
};

const STATUS_OPTIONS = ["Under Review", "Shortlisted", "Rejected"];
const STATUS_COLORS = {
  "Under Review": "bg-gray-100 text-gray-700",
  "Shortlisted": "bg-emerald-100 text-emerald-700",
  "Rejected": "bg-red-100 text-red-700",
};

function ScoreBar({ label, value, colorClass }) {
  return (
    <div className="flex items-center gap-3 text-xs">
      <span className="w-24 text-gray-500 flex-shrink-0">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-1.5 overflow-hidden">
        <div className={colorClass + " h-full rounded-full transition-all"} style={{ width: (value * 100) + "%" }} />
      </div>
      <span className="w-10 text-right text-gray-700 font-medium">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function CandidateCard({ candidate, rank, jobId, onStatusChange }) {
  const [expanded, setExpanded] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const rankClass = RANK_STYLES[rank] || "bg-gray-100 text-gray-600";

  const handleStatusChange = async (event) => {
    const newStatus = event.target.value;
    try {
      await updateCandidateStatus(jobId, candidate.candidate_id, newStatus);
      onStatusChange(candidate.candidate_id, newStatus);
    } catch (err) {
      // silently ignore for now
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className={"flex items-center justify-center w-9 h-9 rounded-full text-sm font-bold flex-shrink-0 " + rankClass}>
            {rank}
          </span>
          <div>
            <p className="font-semibold text-gray-900">{candidate.filename}</p>
            <p className="text-xs text-gray-400 mt-0.5">
              {candidate.matched_skills.length} matched skill{candidate.matched_skills.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">{(candidate.final_score * 100).toFixed(1)}%</p>
          <p className="text-xs text-gray-400">final score</p>
        </div>
      </div>

      <div className="flex items-center justify-between mt-3.5">
        <div className="flex flex-wrap gap-1.5">
          {candidate.matched_skills.map((skill) => (
            <span key={skill} className="bg-teal-50 text-teal-700 text-xs font-medium px-2.5 py-1 rounded-full">
              {skill}
            </span>
          ))}
          {candidate.missing_skills && candidate.missing_skills.map((skill) => (
            <span key={skill} className="bg-gray-100 text-gray-400 text-xs font-medium px-2.5 py-1 rounded-full line-through">
              {skill}
            </span>
          ))}
        </div>
        <select
          value={candidate.status || "Under Review"}
          onChange={handleStatusChange}
          className={"text-xs font-medium px-2.5 py-1 rounded-full border-0 cursor-pointer flex-shrink-0 " + (STATUS_COLORS[candidate.status] || STATUS_COLORS["Under Review"])}
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-teal-600 hover:text-teal-700 font-medium transition-colors"
        >
          {expanded ? "Hide score breakdown" : "Show score breakdown"}
        </button>
        <button
          onClick={() => setShowPreview(true)}
          className="text-xs text-gray-500 hover:text-gray-700 font-medium transition-colors"
        >
          View Resume
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-2.5 pt-4 border-t border-gray-100">
          <ScoreBar label="Semantic" value={candidate.semantic_score} colorClass="bg-teal-500" />
          <ScoreBar label="Skills" value={candidate.skills_score} colorClass="bg-emerald-500" />
          <ScoreBar label="Experience" value={candidate.experience_score} colorClass="bg-amber-500" />
          <ScoreBar label="Education" value={candidate.education_score} colorClass="bg-violet-500" />
          <ScoreBar label="Certifications" value={candidate.certification_score} colorClass="bg-pink-500" />

          {candidate.education.length > 0 && (
            <div className="pt-2 text-xs text-gray-600">
              <span className="font-medium text-gray-500">Education: </span>
              {candidate.education.map((e) => e.degree).join(", ")}
            </div>
          )}
          {candidate.certifications.length > 0 && (
            <div className="text-xs text-gray-600">
              <span className="font-medium text-gray-500">Certifications: </span>
              {candidate.certifications.join(", ")}
            </div>
          )}
        </div>
      )}

      {showPreview && (
        <ResumePreviewModal candidate={candidate} jobId={jobId} onClose={() => setShowPreview(false)} />
      )}
    </div>
  );
}

function ResultsPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [results, setResults] = useState([]);
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [statusFilter, setStatusFilter] = useState("All");
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    getJob(jobId).then((response) => setJob(response.data)).catch(() => {});
  }, [jobId]);

  const runSearch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await searchCandidates(jobId);
      setResults(response.data);
      setHasSearched(true);
    } catch (err) {
      setError("No candidates found, or the search failed. Make sure resumes have been uploaded.");
    } finally {
      setIsLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  const handleStatusChange = (candidateId, newStatus) => {
    setResults((prev) =>
      prev.map((c) => (c.candidate_id === candidateId ? { ...c, status: newStatus } : c))
    );
  };

  const handleWeightChange = (key, value) => {
    setWeights((prev) => ({ ...prev, [key]: parseFloat(value) }));
  };

  const applyWeights = async () => {
    setIsLoading(true);
    try {
      await updateJobWeights(jobId, weights);
      await runSearch();
    } catch (err) {
      setError("Failed to update weights.");
    } finally {
      setIsLoading(false);
    }
  };

  const weightSum = Object.values(weights).reduce((a, b) => a + b, 0);
  const sumIsValid = Math.abs(weightSum - 1) < 0.01;

  const filteredResults = useMemo(() => {
    return results.filter((candidate) => {
      const statusMatches = statusFilter === "All" || candidate.status === statusFilter;
      const scoreMatches = candidate.final_score * 100 >= minScore;
      return statusMatches && scoreMatches;
    });
  }, [results, statusFilter, minScore]);

  return (
    <div>
      <Link to="/" className="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center gap-1 mb-4">
        Back to Dashboard
      </Link>

      {job && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6">
          <div className="flex items-start justify-between">
            <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
            {results.length > 0 && (
              <a                href={exportResultsUrl(jobId)}
                className="text-sm font-medium bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors flex-shrink-0"
              >
                Export CSV
              </a>
            )}
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {job.experience_level && (
              <span className="bg-violet-50 text-violet-700 text-xs font-medium px-2.5 py-1 rounded-full">
                {job.experience_level}
              </span>
            )}
            {job.job_type && (
              <span className="bg-amber-50 text-amber-700 text-xs font-medium px-2.5 py-1 rounded-full">
                {job.job_type}
              </span>
            )}
            {job.work_mode && (
              <span className="bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full">
                {job.work_mode}
              </span>
            )}
          </div>
          {job.required_skills && job.required_skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2.5">
              {job.required_skills.map((skill) => (
                <span key={skill} className="bg-teal-50 text-teal-700 text-xs font-medium px-2.5 py-1 rounded-full">
                  {skill}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 tracking-tight">Ranked Candidates</h2>
              <p className="text-gray-500 mt-1">Sorted by weighted final score, highest first.</p>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white"
            >
              <option value="All">All statuses</option>
              {STATUS_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3 mb-5 bg-white rounded-xl border border-gray-200 px-4 py-3">
            <span className="text-xs text-gray-500 flex-shrink-0">Min score: {minScore}%</span>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="flex-1 accent-teal-600"
            />
          </div>

          {isLoading && (
            <div className="flex items-center gap-2 text-gray-400 text-sm py-8 justify-center">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-teal-500 rounded-full animate-spin" />
              Ranking candidates...
            </div>
          )}
          {error && (
            <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200 mb-4">
              {error}
            </div>
          )}

          {!isLoading && hasSearched && filteredResults.length === 0 && !error && (
            <div className="bg-white rounded-2xl border border-gray-200 p-10 text-center">
              <p className="text-gray-500">No candidates match the current filters.</p>
            </div>
          )}

          <div className="space-y-3">
            {filteredResults.map((candidate, index) => (
              <CandidateCard
                key={candidate.candidate_id}
                candidate={candidate}
                rank={index + 1}
                jobId={jobId}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        </div>

        <div>
          <div className="bg-white rounded-2xl border border-gray-200 p-6 sticky top-24">
            <h2 className="font-semibold text-gray-900 mb-5">Scoring Weights</h2>
            <div className="space-y-5">
              {Object.entries(weights).map(([key, value]) => (
                <div key={key}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-gray-600">{WEIGHT_LABELS[key]}</span>
                    <span className="text-gray-900 font-semibold">{value.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={value}
                    onChange={(e) => handleWeightChange(key, e.target.value)}
                    className="w-full accent-teal-600"
                  />
                </div>
              ))}
            </div>
            <p className={sumIsValid ? "text-xs mt-4 text-gray-400" : "text-xs mt-4 text-amber-600 font-medium"}>
              {"Sum: " + weightSum.toFixed(2) + (sumIsValid ? "" : " (should total 1.0)")}
            </p>
            <button
              onClick={applyWeights}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-teal-500 to-emerald-600 text-white text-sm font-medium py-2.5 rounded-lg mt-5 hover:from-teal-600 hover:to-emerald-700 transition-all disabled:opacity-50 shadow-sm"
            >
              Apply & Re-rank
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;

