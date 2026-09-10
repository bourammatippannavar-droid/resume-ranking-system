import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const createJob = (title, descriptionRaw) =>
  client.post("/jobs/", { title, description_raw: descriptionRaw });

export const listJobs = () => client.get("/jobs/");

export const getJob = (jobId) => client.get("/jobs/" + jobId);

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

export const searchCandidates = (jobId) =>
  client.post("/jobs/" + jobId + "/search", null, { timeout: 60000 });

export default client;
