import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createJob } from "../api/client";

const EXPERIENCE_LEVELS = ["Entry-Level", "Mid-Level", "Senior", "Lead"];
const JOB_TYPES = ["Full-time", "Part-time", "Contract"];
const WORK_MODES = ["Remote", "Hybrid", "On-site"];

function CreateJobPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [skillInput, setSkillInput] = useState("");
  const [skills, setSkills] = useState([]);
  const [experienceLevel, setExperienceLevel] = useState("");
  const [jobType, setJobType] = useState("");
  const [workMode, setWorkMode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const addSkill = () => {
    const trimmed = skillInput.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills((prev) => [...prev, trimmed]);
    }
    setSkillInput("");
  };

  const handleSkillKeyDown = (event) => {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      addSkill();
    }
  };

  const removeSkill = (skill) => {
    setSkills((prev) => prev.filter((s) => s !== skill));
  };

  const validate = () => {
    const newErrors = {};
    if (!title.trim()) newErrors.title = "Job title is required.";
    if (!description.trim()) newErrors.description = "Job description is required.";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const response = await createJob({
        title,
        description_raw: description,
        required_skills: skills.length > 0 ? skills : null,
        experience_level: experienceLevel || null,
        job_type: jobType || null,
        work_mode: workMode || null,
      });
      navigate("/jobs/" + response.data.id + "/upload");
    } catch (err) {
      setErrors({ submit: "Failed to create job. Please check that the backend server is running." });
    } finally {
      setIsSubmitting(false);
    }
  };

  const wordCount = description.trim().length > 0 ? description.trim().split(/\s+/).length : 0;

  return (
    <div className="max-w-2xl mx-auto">
      <Link to="/" className="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center gap-1 mb-4">
        Back to Dashboard
      </Link>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Create a Job Posting</h1>
        <p className="text-gray-500 mt-1.5">
          Describe the role and required skills. We will use this to rank uploaded resumes.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-200 p-7 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Senior Backend Engineer"
            className={"w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-shadow " + (errors.title ? "border-red-400" : "border-gray-300")}
          />
          {errors.title && <p className="text-red-500 text-xs mt-1.5">{errors.title}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Key Required Skills</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {skills.map((skill) => (
              <span key={skill} className="bg-teal-50 text-teal-700 text-sm font-medium pl-3 pr-2 py-1 rounded-full flex items-center gap-1.5">
                {skill}
                <button type="button" onClick={() => removeSkill(skill)} className="text-teal-400 hover:text-teal-700">
                  ×
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyDown={handleSkillKeyDown}
            onBlur={addSkill}
            placeholder="Type a skill and press Enter (e.g. Python, React, Docker)"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-shadow"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">Select...</option>
              {EXPERIENCE_LEVELS.map((level) => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Job Type</label>
            <select
              value={jobType}
              onChange={(e) => setJobType(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">Select...</option>
              {JOB_TYPES.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Work Mode</label>
            <select
              value={workMode}
              onChange={(e) => setWorkMode(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">Select...</option>
              {WORK_MODES.map((mode) => (
                <option key={mode} value={mode}>{mode}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Description <span className="text-red-500">*</span>
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the role, required skills, experience level, and qualifications..."
            rows={10}
            className={"w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none transition-shadow " + (errors.description ? "border-red-400" : "border-gray-300")}
          />
          <div className="flex justify-between mt-1.5">
            {errors.description ? (
              <p className="text-red-500 text-xs">{errors.description}</p>
            ) : (
              <span />
            )}
            <p className="text-xs text-gray-400">{wordCount} word{wordCount !== 1 ? "s" : ""}</p>
          </div>
        </div>

        {errors.submit && (
          <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg border border-red-200">
            {errors.submit}
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-gradient-to-r from-teal-500 to-emerald-600 text-white font-medium py-3 rounded-lg hover:from-teal-600 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {isSubmitting ? "Creating..." : "Save Job & Continue"}
          </button>
          <Link
            to="/"
            className="bg-white text-gray-700 font-medium px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors text-center"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

export default CreateJobPage;


