import { AlertTriangle } from "lucide-react";

interface EmptyStateProps {
  message: string;
}

function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="flex min-h-[120px] items-center justify-center text-center">
      <div>
        <AlertTriangle
          size={28}
          className="mx-auto text-slate-300"
        />

        <p className="mt-3 text-sm text-slate-500">
          {message}
        </p>
      </div>
    </div>
  );
}

export default EmptyState;