import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "@/services/api";

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, patientId }: { file: File; patientId?: string }) =>
      api.uploadDocument(file, patientId),
    onSuccess: () => {
      toast.success("Documento subido correctamente");
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}

export function useProcessingStatus(documentId: string | null) {
  return useQuery({
    queryKey: ["processing-status", documentId],
    queryFn: () => api.getProcessingStatus(documentId!),
    enabled: !!documentId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") return false;
      return 2000;
    },
  });
}
