import React, { useRef, useState } from "react";
import { apiService } from "../services/api";
import { ScoredCandidate } from "../types";
import {
  Search as SearchIcon,
  FileText,
  Cpu,
  CheckCircle2,
  ChevronRight,
  X,
  Briefcase,
  MapPin,
  Calendar,
  Code2,
  TrendingUp,
  User,
  Building2,
  Sparkles,
} from "lucide-react";

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
  const [selectedCandidate, setSelectedCandidate] =
    useState<ScoredCandidate | null>(null);
  const [detailedProfile, setDetailedProfile] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  const handleSearch = async () => {
    if (!jd.trim()) return;
    setLoading(true);
    setError(null);
    setSelectedCandidate(null);
    setDetailedProfile(null);
    setCandidates([]);
    try {
      const response = await apiService.searchCandidates(jd);
      if (response.success) {
        setCandidates(response.results);
      } else {
        setError("Failed to obtain ranking list.");
      }
    } catch (err: any) {
      console.error(err);
      setError(
        err.message ||
          "An error occurred during search. Please verify the connection to the recommendation service."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCandidate = async (cand: ScoredCandidate) => {
    // Toggle off if clicking same candidate
    if (selectedCandidate?.candidate_id === cand.candidate_id) {
      setSelectedCandidate(null);
      setDetailedProfile(null);
      return;
    }

    setSelectedCandidate(cand);
    setDetailedProfile(null);
    setDetailLoading(true);

    // Immediately scroll the drawer into view
    setTimeout(() => {
      drawerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 50);

    try {
      const details = await apiService.getCandidateDetails(cand.candidate_id);
      setDetailedProfile(details);
    } catch (err) {
      console.error("Could not load full profile:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 1.1) return "text-emerald-600 bg-emerald-50 border-emerald-200";
    if (score >= 0.9) return "text-blue-600 bg-blue-50 border-blue-200";
    if (score >= 0.7) return "text-amber-600 bg-amber-50 border-amber-200";
    return "text-gray-500 bg-gray-50 border-gray-200";
  };

  const getMultiplierColor = (val: number) => {
    if (val > 1.05) return "text-emerald-600 font-bold";
    if (val < 0.95) return "text-red-500 font-bold";
    return "text-gray-500";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">
          Search Engine
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Paste a Job Description to trigger the real-time hybrid retrieval and
          cross-encoder ranking pipeline.
        </p>
      </div>

      {/* Top section: JD input + Results list side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: JD Input */}
        <div className="lg:col-span-5 space-y-3">
          <div className="bg-white p-5 rounded-xl border border-gray-200 card-shadow space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">
                Job Description Input
              </span>
              <button
                onClick={() => setJd(SAMPLE_JD)}
                className="text-xs text-brand-primary font-medium hover:underline focus:outline-none"
              >
                Insert Sample
              </button>
            </div>

            <textarea
              className="w-full h-72 p-4 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-mono resize-none"
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
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Running Pipeline...</span>
                </>
              ) : (
                <>
                  <SearchIcon size={15} />
                  <span>Execute Ranking Pipeline</span>
                </>
              )}
            </button>
          </div>

          {/* Tip box */}
          {candidates.length === 0 && !loading && !error && (
            <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-700 space-y-1">
              <p className="font-semibold">How it works</p>
              <p>
                1. Paste or load a JD above and click{" "}
                <span className="font-mono">Execute Ranking Pipeline</span>.
              </p>
              <p>
                2. Results appear on the right — click any candidate to view
                the full profile below.
              </p>
            </div>
          )}
        </div>

        {/* Right: Results List */}
        <div className="lg:col-span-7 space-y-3">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 text-sm p-4 rounded-xl card-shadow flex items-start space-x-3">
              <X size={16} className="mt-0.5 flex-shrink-0 text-red-500" />
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="bg-white border border-gray-200 rounded-xl card-shadow p-10 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-500">
                Running hybrid retrieval + cross-encoder ranking...
              </p>
              <p className="text-xs text-gray-400">
                This may take 10–30 seconds on first run.
              </p>
            </div>
          )}

          {candidates.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 card-shadow overflow-hidden">
              {/* Table Header */}
              <div className="px-5 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                  <Cpu size={15} className="text-blue-500" />
                  <span>
                    Top {candidates.length} Real-time Recommendations
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  {selectedCandidate && (
                    <span className="text-[10px] text-brand-primary font-medium">
                      1 selected ↓
                    </span>
                  )}
                  <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                    Calibrated Relevance
                  </span>
                </div>
              </div>

              {/* Candidate list */}
              <div className="divide-y divide-gray-50 max-h-[440px] overflow-y-auto">
                {candidates.map((cand, idx) => {
                  const isSelected =
                    selectedCandidate?.candidate_id === cand.candidate_id;
                  const scoreClass = getScoreColor(cand.final_score);

                  return (
                    <div
                      key={cand.candidate_id}
                      onClick={() => handleSelectCandidate(cand)}
                      className={`px-4 py-3 flex items-center justify-between transition-all cursor-pointer group ${
                        isSelected
                          ? "bg-blue-50 border-l-[3px] border-brand-primary"
                          : "hover:bg-gray-50/80 border-l-[3px] border-transparent"
                      }`}
                    >
                      {/* Rank badge + info */}
                      <div className="flex items-center space-x-3">
                        <span
                          className={`text-xs font-bold w-6 text-center shrink-0 ${isSelected ? "text-brand-primary" : "text-gray-400"}`}
                        >
                          {idx + 1}
                        </span>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span
                              className={`font-semibold text-sm ${isSelected ? "text-brand-primary" : "text-gray-900"}`}
                            >
                              {cand.candidate_name}
                            </span>
                            <span className="text-[10px] text-gray-400 font-mono hidden sm:inline">
                              ({cand.candidate_id})
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {cand.current_title} •{" "}
                            {cand.years_of_experience.toFixed(1)} yrs exp
                          </p>
                          <p className="text-[11px] text-gray-400">
                            {cand.location}
                          </p>
                        </div>
                      </div>

                      {/* Score + chevron */}
                      <div className="flex items-center space-x-3 shrink-0 ml-2">
                        <div className="text-right">
                          <div
                            className={`text-sm font-bold px-2 py-0.5 rounded border ${scoreClass}`}
                          >
                            {cand.final_score.toFixed(4)}
                          </div>
                          <div className="text-[10px] text-gray-400 mt-0.5">
                            Raw: {cand.cross_encoder_score.toFixed(2)}
                          </div>
                        </div>
                        <ChevronRight
                          size={14}
                          className={`transition-all ${isSelected ? "text-brand-primary rotate-90" : "text-gray-300 group-hover:text-gray-500"}`}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Empty placeholder when no search run yet */}
          {candidates.length === 0 && !loading && !error && (
            <div className="h-80 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center text-center p-8 bg-gray-50/30">
              <FileText size={40} className="text-gray-300 mb-3" />
              <h3 className="text-sm font-semibold text-gray-700">
                No active ranking query
              </h3>
              <p className="text-xs text-gray-400 max-w-sm mt-1">
                Paste or load a job description on the left to see
                recommendations.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ─── CANDIDATE DETAIL DRAWER ─── */}
      {/* This always renders below the grid so we can scroll/ref to it */}
      <div ref={drawerRef}>
        {selectedCandidate ? (
          <div className="bg-white border border-gray-200 rounded-xl card-shadow overflow-hidden animate-fade-in">
            {/* Drawer Top Bar */}
            <div className="bg-gradient-to-r from-slate-800 to-blue-900 px-6 py-5 text-white flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center shrink-0">
                  <User size={18} />
                </div>
                <div>
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-bold">
                      {selectedCandidate.candidate_name}
                    </h2>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getScoreColor(selectedCandidate.final_score)}`}
                    >
                      Score: {selectedCandidate.final_score.toFixed(6)}
                    </span>
                  </div>
                  <p className="text-sm text-blue-200 mt-0.5">
                    {selectedCandidate.current_title} •{" "}
                    {selectedCandidate.location}
                  </p>
                  <p className="text-[11px] text-blue-300 font-mono mt-0.5">
                    ID: {selectedCandidate.candidate_id}
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedCandidate(null);
                  setDetailedProfile(null);
                }}
                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                title="Close panel"
              >
                <X size={16} />
              </button>
            </div>

            {/* Quick stats row */}
            <div className="grid grid-cols-2 md:grid-cols-4 border-b border-gray-100 divide-x divide-gray-100">
              {[
                {
                  icon: <Briefcase size={14} />,
                  label: "Experience",
                  val: `${selectedCandidate.years_of_experience.toFixed(1)} years`,
                },
                {
                  icon: <MapPin size={14} />,
                  label: "Location",
                  val: selectedCandidate.location?.split(",")[0] || "—",
                },
                {
                  icon: <TrendingUp size={14} />,
                  label: "Final Score",
                  val: selectedCandidate.final_score.toFixed(4),
                },
                {
                  icon: <Code2 size={14} />,
                  label: "Raw CE Score",
                  val: selectedCandidate.cross_encoder_score.toFixed(2),
                },
              ].map(({ icon, label, val }) => (
                <div key={label} className="px-5 py-3 bg-gray-50/50">
                  <div className="flex items-center space-x-1.5 text-gray-400 text-[10px] font-medium uppercase tracking-wider mb-1">
                    {icon}
                    <span>{label}</span>
                  </div>
                  <p className="text-sm font-bold text-gray-800">{val}</p>
                </div>
              ))}
            </div>

            {/* Main detail content */}
            <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Multipliers panel */}
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center space-x-1.5">
                  <Sparkles size={12} className="text-amber-500" />
                  <span>Business Multipliers</span>
                </h3>
                <div className="space-y-2 text-xs">
                  {Object.entries(selectedCandidate.multipliers).map(
                    ([key, val]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between"
                      >
                        <span className="text-gray-500 capitalize">
                          {key.replace(/_/g, " ")}
                        </span>
                        <div className="flex items-center space-x-2">
                          {/* Mini bar */}
                          <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${val > 1.05 ? "bg-emerald-500" : val < 0.95 ? "bg-red-400" : "bg-gray-300"}`}
                              style={{
                                width: `${Math.min(100, ((val - 0.5) / 0.8) * 100)}%`,
                              }}
                            />
                          </div>
                          <span className={`font-mono w-10 text-right ${getMultiplierColor(val)}`}>
                            ×{val.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* AI Reasoning panel - spans 2 cols */}
              <div className="md:col-span-2 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center space-x-1.5">
                  <CheckCircle2 size={12} className="text-emerald-500" />
                  <span>Deterministic Explanatory Reasoning</span>
                </h3>
                <div className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100 text-sm text-gray-700 leading-relaxed italic">
                  &ldquo;
                  {selectedCandidate.reasoning || "No reasoning generated."}
                  &rdquo;
                </div>
              </div>
            </div>

            {/* Extended profile section (loaded async) */}
            {detailLoading ? (
              <div className="px-6 pb-6 flex items-center space-x-3 text-sm text-gray-500">
                <div className="w-5 h-5 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
                <span>Loading full candidate profile...</span>
              </div>
            ) : (
              detailedProfile && (
                <div className="border-t border-gray-100 px-6 pb-6 pt-5 space-y-6">
                  {/* Skills */}
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
                      Technical Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {detailedProfile.skills?.map((s: any, idx: number) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 bg-white border border-gray-200 rounded-lg text-xs font-medium text-gray-700"
                        >
                          {s.name}
                          <span className="text-gray-400 font-normal ml-1">
                            ({s.proficiency})
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Work History */}
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center space-x-1.5">
                        <Building2 size={12} />
                        <span>Work History</span>
                      </h4>
                      <div className="space-y-3">
                        {detailedProfile.career_history
                          ?.slice(0, 4)
                          .map((job: any, idx: number) => (
                            <div
                              key={idx}
                              className="text-xs border-l-2 border-brand-primary/30 pl-3"
                            >
                              <p className="font-semibold text-gray-800">
                                {job.title}
                              </p>
                              <p className="text-gray-500 mt-0.5">
                                {job.company} • {job.start_date} →{" "}
                                {job.end_date || "Present"}
                              </p>
                            </div>
                          ))}
                      </div>
                    </div>

                    {/* Redrob Signals */}
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
                        Redrob System Signals
                      </h4>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        {[
                          {
                            label: "Notice Period",
                            val: `${detailedProfile.redrob_signals?.notice_period_days} days`,
                          },
                          {
                            label: "GitHub Score",
                            val:
                              detailedProfile.redrob_signals
                                ?.github_activity_score >= 0
                                ? `${detailedProfile.redrob_signals.github_activity_score}/100`
                                : "N/A",
                          },
                          {
                            label: "Recruiter Response",
                            val: `${Math.round(detailedProfile.redrob_signals?.recruiter_response_rate * 100)}%`,
                          },
                          {
                            label: "Profile Match Quality",
                            val: `${Math.round(detailedProfile.redrob_signals?.profile_completeness_score)}%`,
                          },
                        ].map(({ label, val }) => (
                          <div
                            key={label}
                            className="p-3 bg-gray-50 rounded-lg border border-gray-100"
                          >
                            <span className="text-gray-400 block text-[10px] font-medium uppercase tracking-wider mb-1">
                              {label}
                            </span>
                            <span className="font-bold text-gray-900 text-sm">
                              {val}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          /* Subtle hint shown when results are loaded but nothing is selected */
          candidates.length > 0 && (
            <div className="border border-dashed border-gray-200 rounded-xl px-6 py-5 text-center text-gray-400 bg-gray-50/30 flex items-center justify-center space-x-3">
              <ChevronRight size={16} className="text-gray-300" />
              <p className="text-sm">
                Click any candidate above to view their full profile here.
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
};
