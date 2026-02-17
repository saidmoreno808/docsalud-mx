import { useMutation, useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";
import type { ClassifyRequest } from "@/types";

export function useSearchDocuments(
  query: string,
  params: { patient_id?: string; top_k?: number } = {},
) {
  return useQuery({
    queryKey: ["search", query, params],
    queryFn: () => api.searchDocuments({ q: query, ...params }),
    enabled: query.length >= 2,
  });
}

export function useClassifyText() {
  return useMutation({
    mutationFn: (data: ClassifyRequest) => api.classifyText(data),
  });
}
