import React, { useState } from "react";
import { apiService } from "../services/api";
import { ScoredCandidate } from "../types";
import { Search as SearchIcon, FileText, Cpu, CheckCircle2, ChevronRight, Download } from "lucide-react";

const SAMPLE_JD = `AI Engineer / Machine Learning Engineer
Location: Noida, Gurgaon, or Bangalore.
Experience: 5-8 years.
Must Have Skills: Python, PyTorch, SentenceTransformers, Vector Databases (FAISS, Qdrant, Milvus), BM25, Information Retrieval.
Good to Have Skills: FastAPI, React, Docker, CI/CD pipelines.
Role involves: Building search and retrieval frameworks, ranking algorithms, semantic vector representation, optimizing latency and accuracy.`;

export const Search: React.FC = () => {
  const [jd, setJd] = useState("");
  const [candidates, setCandidates] = useState<ScoredCandidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<ScoredCandidate | null>(null);
  const [detailedProfile, setDetailedProfile] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const handleSearch = async () => {
    if (!jd.trim()) return;
    setLoading(true);
    setError(null);
    setSelectedCandidate(null);
    setDetailedProfile(null);
    try {
      const response = await apiService.searchCandidates(jd);
      if (response.success) {
        setCandidates(response.results);
      } else {
        setError("Failed to obtain ranking list.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred during search. Make sure FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCandidate = async (cand: ScoredCandidate) => {
    setSelectedCandidate(cand);
    setDetailLoading(true);
    setDetailedProfile(null);
    try {
      const details = await apiService.getCandidateDetails(cand.candidate_id);
      setDetailedProfile(details);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">Search Engine</h1>
        <p className="text-sm text-gray-500 mt-1">
          Paste a Job Description to trigger the real-time hybrid retrieval and cross-encoder ranking pipeline.
        </p>
      </div>

      {/* Grid: Search Input + Results panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left: Search Input Box */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Job Description Input</span>
              <button 
                onClick={() => setJd(SAMPLE_JD)}
                className="text-xs text-brand-primary font-medium hover:underline focus:outline-none"
              >
                Insert Sample
              </button>
            </div>
            
            <textarea
              className="w-full h-80 p-4 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-mono resize-none"
              placeholder="Paste Job Description specifications here..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />

            <button
              onClick={handleSearch}
              disabled={loading || !jd.trim()}
              className="w-full py-3 bg-brand-primary hover:bg-brand-hover text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center space-x-2 cursor-pointer disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <SearchIcon size={16} />
                  <span>Execute Ranking Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right: Results List */}
        <div className="lg:col-span-7 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 text-sm p-4 rounded-lg card-shadow">
              {error}
            </div>
          )}

          {candidates.length > 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 card-shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                  <Cpu size={16} className="text-blue-500" />
                  <span>Real-time Top {candidates.length} Recommendations</span>
                </div>
                <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                  Sigmoid Score Scaled
                </span>
              </div>
              <div className="divide-y divide-gray-100 max-h-[460px] overflow-y-auto">
                {candidates.map((cand, idx) => (
                  <div 
                    key={cand.candidate_id}
                    onClick={() => handleSelectCandidate(cand)}
                    className={`p-4 flex items-center justify-between hover:bg-blue-50/30 transition-colors cursor-pointer ${selectedCandidate?.candidate_id === cand.candidate_id ? "bg-blue-50/50" : ""}`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-sm text-gray-900">{cand.candidate_name}</span>
                        <span className="text-xs text-gray-500 font-mono">({cand.candidate_id})</span>
                      </div>
                      <p className="text-xs text-gray-600 font-medium">{cand.current_title} • {cand.years_of_experience.toFixed(1)} yrs exp</p>
                      <p className="text-[11px] text-gray-400">{cand.location}</p>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-sm font-bold text-brand-primary">
                          {cand.final_score.toFixed(4)}
                        </div>
                        <div className="text-[10px] text-gray-400">
                          CE: {cand.cross_encoder_score.toFixed(2)}
                        </div>
                      </div>
                      <ChevronRight size={16} className="text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            !loading && (
              <div className="h-96 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center text-center p-8 bg-gray-50/30">
                <FileText size={48} className="text-gray-300 mb-3" />
                <h3 className="text-sm font-semibold text-gray-700">No active ranking query</h3>
                <p className="text-xs text-gray-400 max-w-sm mt-1">
                  Paste or load a job description on the left to see recommendations.
                </p>
              </div>
            )
          )}
        </div>
      </div>

      {/* Expanded Candidate Details Drawer panel */}
      {selectedCandidate && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 card-shadow space-y-6 animate-fade-in">
          <div className="border-b border-gray-100 pb-4 flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-bold text-gray-900">{selectedCandidate.candidate_name}</h2>
                <span className="text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-full">
                  Score: {selectedCandidate.final_score.toFixed(6)}
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-1">{selectedCandidate.current_title} • {selectedCandidate.location}</p>
            </div>
            
            <div className="text-right">
              <span className="text-xs text-gray-400 block font-mono">ID: {selectedCandidate.candidate_id}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Multipliers Breakdown */}
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500">Business Multipliers</h3>
              <div className="space-y-1.5 text-xs">
                {Object.entries(selectedCandidate.multipliers).map(([key, val]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-600 capitalize">{key.replace("_", " ")}</span>
                    <span className={`font-semibold ${val < 1.0 ? "text-amber-600" : val > 1.0 ? "text-green-600" : "text-gray-800"}`}>
                      x{val.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Fact-based Reasoning */}
            <div className="md:col-span-2 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center space-x-1">
                <CheckCircle2 size={14} className="text-emerald-500" />
                <span>Deterministic Explanatory Reasoning</span>
              </h3>
              <div className="bg-emerald-50/30 p-4 rounded-lg border border-emerald-100 text-sm text-gray-700 leading-relaxed italic">
                "{selectedCandidate.reasoning || "No reasoning generated."}"
              </div>
            </div>
          </div>

          {/* Full Parsed profile info if loaded */}
          {detailLoading ? (
            <div className="flex justify-center py-6">
              <div className="w-6 h-6 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            detailedProfile && (
              <div className="space-y-4 border-t border-gray-100 pt-6">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Technical Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {detailedProfile.skills?.map((s: any, idx: number) => (
                      <span key={idx} className="px-2.5 py-1 bg-white border border-gray-200 rounded text-xs font-medium text-gray-700">
                        {s.name} <span className="text-gray-400 font-normal">({s.proficiency})</span>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Work History</h4>
                    <div className="space-y-3">
                      {detailedProfile.career_history?.slice(0, 3).map((job: any, idx: number) => (
                        <div key={idx} className="text-xs border-l-2 border-gray-200 pl-3">
                          <p className="font-semibold text-gray-800">{job.title}</p>
                          <p className="text-gray-500">{job.company} • {job.start_date} to {job.end_date || "Present"}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Redrob System Signals</h4>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="p-3 bg-gray-50 rounded">
                        <span className="text-gray-400 block">Notice Period</span>
                        <span className="font-bold text-gray-800">{detailedProfile.redrob_signals?.notice_period_days} days</span>
                      </div>
                      <div className="p-3 bg-gray-50 rounded">
                        <span className="text-gray-400 block">GitHub Score</span>
                        <span className="font-bold text-gray-800">
                          {detailedProfile.redrob_signals?.github_activity_score >= 0 
                            ? `${detailedProfile.redrob_signals.github_activity_score}/100` 
                            : "N/A"}
                        </span>
                      </div>
                      <div className="p-3 bg-gray-50 rounded">
                        <span className="text-gray-400 block">Recruiter Response</span>
                        <span className="font-bold text-gray-800">
                          {Math.round(detailedProfile.redrob_signals?.recruiter_response_rate * 100)}%
                        </span>
                      </div>
                      <div className="p-3 bg-gray-50 rounded">
                        <span className="text-gray-400 block">Profile Match Quality</span>
                        <span className="font-bold text-gray-800">
                          {Math.round(detailedProfile.redrob_signals?.profile_completeness_score)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};
