import { AlertCircle, RefreshCw } from "lucide-react";

export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="error-message" role="alert">
      <AlertCircle size={18} aria-hidden="true" />
      <span>{error.message || error}</span>
      {onRetry && (
        <button className="icon-button" type="button" onClick={onRetry} aria-label="Try again">
          <RefreshCw size={16} />
        </button>
      )}
    </div>
  );
}