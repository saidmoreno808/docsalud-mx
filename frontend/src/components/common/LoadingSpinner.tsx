import { Loader2 } from "lucide-react";

interface Props {
  message?: string;
  size?: "sm" | "md" | "lg";
}

const sizes = { sm: "h-4 w-4", md: "h-8 w-8", lg: "h-12 w-12" };

export default function LoadingSpinner({ message, size = "md" }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <Loader2 className={`${sizes[size]} animate-spin text-medical-primary`} />
      {message && <p className="text-sm text-slate-500">{message}</p>}
    </div>
  );
}
