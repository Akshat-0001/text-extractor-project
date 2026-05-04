import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { uploadFiles } from "../api";

export default function Upload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!files || files.length === 0) {
      setError("Please select at least one file");
      return;
    }

    setUploading(true);
    setError("");

    try {
      await uploadFiles(files);
      navigate("/dashboard");
    } catch (err) {
      setError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Upload Documents</h1>
        <div className="nav">
          <Link to="/dashboard" className="btn btn-secondary">
            Back to Dashboard
          </Link>
        </div>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}

          <div className="form-group">
            <label>Select Documents</label>
            <input
              type="file"
              multiple
              onChange={(e) => setFiles(e.target.files)}
              disabled={uploading}
            />
          </div>

          {files && files.length > 0 && (
            <div style={{ marginBottom: "15px" }}>
              <strong>Selected files:</strong>
              <ul style={{ marginTop: "5px", paddingLeft: "20px" }}>
                {Array.from(files).map((file, i) => (
                  <li key={i}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
      </div>
    </div>
  );
}
