import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getJobs, Job } from "../api";
import JobCard from "../components/JobCard";

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("desc");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
  }, [search, status, sort]);

  async function loadJobs() {
    setLoading(true);
    try {
      const data = await getJobs(search || undefined, status || undefined, sort);
      setJobs(data);
    } catch (error) {
      console.error("Failed to load jobs:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Document Processing</h1>
        <div className="nav">
          <Link to="/upload" className="btn btn-primary">
            Upload Documents
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="filters">
          <input
            type="text"
            placeholder="Search by filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="card">Loading...</div>
      ) : jobs.length === 0 ? (
        <div className="card">No jobs found</div>
      ) : (
        <div className="job-grid">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onUpdate={loadJobs} />
          ))}
        </div>
      )}
    </div>
  );
}
