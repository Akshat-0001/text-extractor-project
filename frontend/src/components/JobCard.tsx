import { Link } from "react-router-dom";
import { Job } from "../api";

interface JobCardProps {
  job: Job;
  onUpdate: () => void;
}

export default function JobCard({ job }: JobCardProps) {
  return (
    <Link to={`/jobs/${job.id}`} style={{ textDecoration: "none", color: "inherit" }}>
      <div className="card" style={{ cursor: "pointer", transition: "transform 0.2s" }}>
        <h3 style={{ marginBottom: "10px", fontSize: "18px" }}>{job.filename}</h3>
        
        <div style={{ marginBottom: "10px" }}>
          <span className={`status-badge status-${job.status}`}>{job.status}</span>
          {job.finalized === 1 && (
            <span className="status-badge" style={{ marginLeft: "8px", background: "#6f42c1", color: "white" }}>
              Finalized
            </span>
          )}
        </div>

        {job.title && (
          <p style={{ fontSize: "14px", color: "#666", marginBottom: "5px" }}>
            <strong>Title:</strong> {job.title}
          </p>
        )}

        {job.category && (
          <p style={{ fontSize: "14px", color: "#666", marginBottom: "5px" }}>
            <strong>Category:</strong> {job.category}
          </p>
        )}

        <p style={{ fontSize: "12px", color: "#999", marginTop: "10px" }}>
          {new Date(job.created_at).toLocaleString()}
        </p>
      </div>
    </Link>
  );
}
