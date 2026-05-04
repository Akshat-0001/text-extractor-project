const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Job {
  id: number;
  filename: string;
  status: string;
  progress: string;
  created_at: string;
  updated_at: string;
  error_message?: string;
  title?: string;
  category?: string;
  summary?: string;
  keywords?: string[];
  finalized: number;
}

export interface ProgressEvent {
  job_id: number;
  status: string;
  progress: string;
  message: string;
}

export async function uploadFiles(files: FileList): Promise<Job[]> {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }
  
  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) throw new Error("Upload failed");
  return response.json();
}

export async function getJobs(search?: string, status?: string, sort?: string): Promise<Job[]> {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);
  if (sort) params.append("sort", sort);
  
  const response = await fetch(`${API_BASE}/jobs?${params}`);
  if (!response.ok) throw new Error("Failed to fetch jobs");
  return response.json();
}

export async function getJob(id: number): Promise<Job> {
  const response = await fetch(`${API_BASE}/jobs/${id}`);
  if (!response.ok) throw new Error("Failed to fetch job");
  return response.json();
}

export async function retryJob(id: number): Promise<Job> {
  const response = await fetch(`${API_BASE}/jobs/${id}/retry`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to retry job");
  return response.json();
}

export async function updateJob(id: number, data: Partial<Job>): Promise<Job> {
  const response = await fetch(`${API_BASE}/jobs/${id}/result`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to update job");
  return response.json();
}

export async function finalizeJob(id: number): Promise<Job> {
  const response = await fetch(`${API_BASE}/jobs/${id}/finalize`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to finalize job");
  return response.json();
}

export function subscribeToProgress(jobId: number, onEvent: (event: ProgressEvent) => void): EventSource {
  const eventSource = new EventSource(`${API_BASE}/jobs/${jobId}/progress`);
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onEvent(data);
  };
  
  return eventSource;
}

export function downloadExport(jobId: number, format: "json" | "csv") {
  window.open(`${API_BASE}/jobs/${jobId}/export?format=${format}`, "_blank");
}
