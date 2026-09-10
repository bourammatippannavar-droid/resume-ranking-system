import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { searchCandidates, updateJobWeights } from "../api/client";

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

function CandidateCard({ candidate, rank }) {
  const [expanded, setExpanded] = useState(false);
  const rankClass = RANK_STYLES[rank] || "bg-gray-100 text-gray-600";

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

      {candidate.matched_skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3.5">
          {candidate.matched_skills.map((skill) => (
            <span key={skill} className="bg-teal-50 text-teal-700 text-xs font-medium px-2.5 py-1 rounded-full">
              {skill}
            </span>
          ))}
        </div>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-teal-600 hover:text-teal-700 mt-4 font-medium transition-colors"
      >
        {expanded ? "Hide score breakdown" : "Show score breakdown"}
      </button>

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
    </div>
  );
}

function ResultsPage() {
  const { jobId } = useParams();
  const [results, setResults] = useState([]);
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Ranked Candidates</h1>
          <p className="text-gray-500 mt-1.5">Sorted by weighted final score, highest first.</p>
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

        {!isLoading && hasSearched && results.length === 0 && !error && (
          <div className="bg-white rounded-2xl border border-gray-200 p-10 text-center">
            <p className="text-gray-500">No candidates to rank yet.</p>
          </div>
        )}

        <div className="space-y-3">
          {results.map((candidate, index) => (
            <CandidateCard key={candidate.candidate_id} candidate={candidate} rank={index + 1} />
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
  );
}

export default ResultsPage;
