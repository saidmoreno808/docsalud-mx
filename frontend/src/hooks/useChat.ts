import { create } from "zustand";
import { useMutation } from "@tanstack/react-query";
import * as api from "@/services/api";
import type { ChatMessage, QueryType } from "@/types";

interface ChatStore {
  messages: ChatMessage[];
  selectedPatientId: string | null;
  addMessage: (msg: ChatMessage) => void;
  clearMessages: () => void;
  setPatientId: (id: string | null) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  selectedPatientId: null,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  clearMessages: () => set({ messages: [] }),
  setPatientId: (id) => set({ selectedPatientId: id }),
}));

export function useQueryMutation() {
  const { addMessage, selectedPatientId } = useChatStore();

  return useMutation({
    mutationFn: ({
      question,
      queryType,
    }: {
      question: string;
      queryType: QueryType;
    }) =>
      api.queryDocuments({
        question,
        patient_id: selectedPatientId,
        query_type: queryType,
      }),
    onMutate: ({ question }) => {
      addMessage({
        id: crypto.randomUUID(),
        role: "user",
        content: question,
        timestamp: new Date(),
      });
    },
    onSuccess: (data) => {
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
        timestamp: new Date(),
      });
    },
    onError: () => {
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Lo siento, ocurrio un error al procesar tu consulta.",
        timestamp: new Date(),
      });
    },
  });
}
