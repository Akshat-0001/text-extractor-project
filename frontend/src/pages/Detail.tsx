import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { getJob, updateJob, finalizeJob, retryJob, subscribeToProgress, downloadExport, Job, ProgressEvent } from "../api";
import ProgressBar from "../components/ProgressBar";

export default function Detail() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [summary, setSummary] = useState("");
  const [keywords, setKeywords] = useState("");

  useEffect(() => {
    if (id) {
      loadJob();
      const eventSource = subscribeToProgress(parseInt(id), handleProgressEvent);
      return () => eventSource.close();
    }
  }, [id]);

  async function loadJob() {
    try {
      const data = await getJob(parseInt(id!));
      setJob(data);
      setTitle(data.title || "");
      setCategory(data.category || "");
      setSummary(data.summary || "");
      setKeywords(data.keywords?.join(", ") || "");
    } catch (error) {
      console.error("Failed to load job:", error);
    } finally {
      setLoading(false);
    }
  }

  function handleProgressEvent(event: ProgressEvent) {
    setJob((prev) => {
      if (!prev) return prev;
      return { ...prev, status: event.status, progress: event.progress };
    });
    if (event.status === "completed" || event.status === "failed") {
      loadJob();
    }
  }

  async function handleSave() {
    if (!job) return;
    
    try {
      const keywordArray = keywords.split(",").map((k) => k.trim()).filter((k) => k);
      await updateJob(job.id, { title, category, summary, keywords: keywordArray });
      setEditing(false);
      loadJob();
    } catch (error) {
      console.error("Failed to update job:", error);
    }
  }

  async function handleFinalize() {
    if (!job) return;
    
    try {
      await finalizeJob(job.id);
      loadJob();
    } catch (error) {
      console.error("Failed to finalize job:", error);
    }
  }

  async function handleRetry() {
    if (!job) return;
    
    try {
      await retryJob(job.id);
      loadJob();
    } catch (error) {
      console.error("Failed to retry job:", error);
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="card">Loading...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container">
        <div className="card">Job not found</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Job Details</h1>
        <div className="nav">
          <Link to="/dashboard" className="btn btn-secondary">
            Back to Dashboard
          </Link>
        </div>
      </div>

      <div className="card">
        <h2>{job.filename}</h2>
        <div style={{ marginTop: "10px" }}>
          <span className={`status-badge status-${job.status}`}>{job.status}</span>
          {job.finalized === 1 && (
            <span className="status-badge" style={{ marginLeft: "10px", background: "#6f42c1", color: "white" }}>
              Finalized
            </span>
          )}
        </div>
        
        {job.status === "processing" && (
          <div style={{ marginTop: "15px" }}>
            <ProgressBar status={job.status} progress={job.progress} />
            <p style={{ marginTop: "5px", fontSize: "14px", color: "#666" }}>{job.progress}</p>
          </div>
        )}

        {job.error_message && (
          <div className="error" style={{ marginTop: "15px" }}>
            {job.error_message}
          </div>
        )}
      </div>

      {job.status === "completed" && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h3>Extracted Data</h3>
            {!editing && job.finalized === 0 && (
              <button className="btn btn-primary" onClick={() => setEditing(true)}>
                Edit
              </button>
            )}
          </div>

          <div className="detail-grid">
            <div className="form-group">
              <label>Title</label>
              {editing ? (
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
              ) : (
                <p>{job.title}</p>
              )}
            </div>

            <div className="form-group">
              <label>Category</label>
              {editing ? (
                <input type="text" value={category} onChange={(e) => setCategory(e.target.value)} />
              ) : (
                <p>{job.category}</p>
              )}
            </div>

            <div className="form-group">
              <label>Summary</label>
              {editing ? (
                <textarea value={summary} onChange={(e) => setSummary(e.target.value)} />
              ) : (
                <p>{job.summary}</p>
              )}
            </div>

            <div className="form-group">
              <label>Keywords</label>
              {editing ? (
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="Comma-separated keywords"
                />
              ) : (
                <div className="keywords">
                  {job.keywords?.map((kw, i) => (
                    <span key={i} className="keyword-tag">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {editing && (
            <div className="actions" style={{ marginTop: "20px" }}>
              <button className="btn btn-success" onClick={handleSave}>
                Save Changes
              </button>
              <button className="btn btn-secondary" onClick={() => setEditing(false)}>
                Cancel
              </button>
            </div>
          )}

          {!editing && job.finalized === 0 && (
            <div className="actions" style={{ marginTop: "20px" }}>
              <button className="btn btn-success" onClick={handleFinalize}>
                Finalize
              </button>
            </div>
          )}

          {job.finalized === 1 && (
            <div className="actions" style={{ marginTop: "20px" }}>
              <button className="btn btn-primary" onClick={() => downloadExport(job.id, "json")}>
                Export JSON
              </button>
              <button className="btn btn-primary" onClick={() => downloadExport(job.id, "csv")}>
                Export CSV
              </button>
            </div>
          )}
        </div>
      )}

      {job.status === "failed" && (
        <div className="card">
          <button className="btn btn-danger" onClick={handleRetry}>
            Retry Job
          </button>
        </div>
      )}
    </div>
  );
}
