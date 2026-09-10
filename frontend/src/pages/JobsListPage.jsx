import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { listJobs } from "../api/client";

function JobsListPage() {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    listJobs()
      .then((response) => setJobs(response.data))
      .catch(() => setError("Failed to load jobs. Is the backend running?"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Job Postings</h1>
        <p className="text-gray-500 mt-1.5">Select a job to view ranked candidates, or create a new posting.</p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-gray-400 text-sm py-8 justify-center">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-teal-500 rounded-full animate-spin" />
          Loading jobs...
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {!isLoading && !error && jobs.length === 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-teal-50 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">+</span>
          </div>
          <p className="text-gray-600 font-medium mb-1">No jobs yet</p>
          <p className="text-gray-400 text-sm mb-4">Create your first job posting to start ranking candidates.</p>
          <Link
            to="/create"
            className="inline-block bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Create a Job
          </Link>
        </div>
      )}

      <div className="space-y-3">
        {jobs.map((job) => (
          <Link
            key={job.id}
            to={"/jobs/" + job.id + "/results"}
            className="group block bg-white rounded-xl border border-gray-200 p-5 hover:border-teal-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors">
                  {job.title}
                </p>
                <p className="text-sm text-gray-500 mt-0.5 truncate">
                  {job.description_raw}
                </p>
              </div>
              <span className="text-xs text-gray-400 flex-shrink-0 whitespace-nowrap">
                {new Date(job.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default JobsListPage;
