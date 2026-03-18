import { Routes, Route } from "react-router-dom";
import { useState } from "react";
import { Search as SearchIcon } from "lucide-react";
import MainLayout from "@/components/layout/MainLayout";
import StatsCards from "@/components/dashboard/StatsCards";
import RecentDocuments from "@/components/dashboard/RecentDocuments";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import RiskChart from "@/components/dashboard/RiskChart";
import DocumentUploader from "@/components/upload/DocumentUploader";
import PatientList from "@/components/patients/PatientList";
import PatientDetail from "@/components/patients/PatientDetail";
import ChatInterface from "@/components/chat/ChatInterface";
import { useSearchDocuments } from "@/hooks/useSearch";
import { docTypeLabel, formatConfidence, truncate } from "@/utils/formatters";

function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500">
          System overview
        </p>
      </div>
      <StatsCards />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RecentDocuments documents={[]} />
        <AlertsPanel />
      </div>
      <RiskChart />
    </div>
  );
}

function SearchPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading } = useSearchDocuments(query);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Search</h1>
        <p className="text-sm text-slate-500">
          Semantic search over clinical records
        </p>
      </div>

      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search clinical documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-lg border border-slate-300 py-3 pl-10 pr-4 text-sm focus:border-medical-primary focus:outline-none focus:ring-1 focus:ring-medical-primary"
        />
      </div>

      {isLoading && query.length >= 2 && (
        <p className="text-sm text-slate-400">Searching...</p>
      )}

      {data?.results && data.results.length > 0 && (
        <div className="space-y-3">
          {data.results.map((r, i) => (
            <div key={i} className="card">
              <div className="flex items-center justify-between">
                <span className="badge bg-slate-100 text-slate-600">
                  {docTypeLabel(r.document_type)}
                </span>
                <span className="text-xs text-slate-400">
                  Relevance: {formatConfidence(r.similarity_score)}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-700">
                {truncate(r.chunk_text, 300)}
              </p>
              {r.patient_name && (
                <p className="mt-1 text-xs text-slate-400">
                  Patient: {r.patient_name}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {data?.results && data.results.length === 0 && query.length >= 2 && (
        <p className="py-8 text-center text-sm text-slate-400">
          No results for "{query}"
        </p>
      )}
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/upload" element={<DocumentUploader />} />
        <Route path="/patients" element={<PatientList />} />
        <Route path="/patients/:id" element={<PatientDetail />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/chat" element={<ChatInterface />} />
      </Route>
    </Routes>
  );
}
