interface ProgressBarProps {
  status: string;
  progress: string;
}

const PROGRESS_MAP: Record<string, number> = {
  document_received: 10,
  parsing_started: 25,
  parsing_completed: 40,
  extraction_started: 55,
  extraction_completed: 70,
  storing_result: 85,
  job_completed: 100,
};

export default function ProgressBar({ progress }: ProgressBarProps) {
  const percentage = PROGRESS_MAP[progress] || 0;

  return (
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${percentage}%` }} />
    </div>
  );
}
