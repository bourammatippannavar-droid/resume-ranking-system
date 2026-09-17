import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const createJob = (jobData) => client.post("/jobs/", jobData);

export const listJobs = () => client.get("/jobs/");

export const getJob = (jobId) => client.get("/jobs/" + jobId);

export const updateJob = (jobId, jobData) => client.put("/jobs/" + jobId, jobData);

export const deleteJob = (jobId) => client.delete("/jobs/" + jobId);

export const updateJobWeights = (jobId, weights) =>
  client.put("/jobs/" + jobId + "/weights", weights);

export const uploadCandidates = (jobId, files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  return client.post("/jobs/" + jobId + "/candidates", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });
};

export const listCandidates = (jobId) => client.get("/jobs/" + jobId + "/candidates");

export const deleteCandidate = (jobId, candidateId) =>
  client.delete("/jobs/" + jobId + "/candidates/" + candidateId);

export const updateCandidateNotes = (jobId, candidateId, notes) =>
  client.put("/jobs/" + jobId + "/candidates/" + candidateId + "/notes", { notes });

export const updateCandidateStatus = (jobId, candidateId, status) =>
  client.put("/jobs/" + jobId + "/candidates/" + candidateId + "/status", { status });

export const getCandidateDetail = (jobId, candidateId) =>
  client.get("/jobs/" + jobId + "/candidates/" + candidateId);

export const searchCandidates = (jobId) =>
  client.post("/jobs/" + jobId + "/search", null, { timeout: 60000 });

export const exportResultsUrl = (jobId) =>
  API_BASE_URL + "/jobs/" + jobId + "/export";

export default client;
