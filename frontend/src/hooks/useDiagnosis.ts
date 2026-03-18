import { useMutation } from '@tanstack/react-query';
import { diagnosePatient } from '@/services/api';
import type { DiagnosticResult } from '@/components/DiagnosticPanel/types';

export const useDiagnosis = (patientId: string) => {
  return useMutation<DiagnosticResult, Error>({
    mutationFn: () => diagnosePatient(patientId),
  });
};
