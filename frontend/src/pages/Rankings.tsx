import React, { useEffect, useRef, useState } from "react";
import { apiService } from "../services/api";
import { RankedCandidate } from "../types";
import {
  Award,
  Download,
  Search,
  Calendar,
  Briefcase,
  MapPin,
  Code2,
  TrendingUp,
  X,
  ChevronRight,
  Star,
} from "lucide-react";

export const Rankings: React.FC = () => {
  const [candidates, setCandidates] = useState<RankedCandidate[]>([]);
  const [filtered, setFiltered] = useState<RankedCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter States
  const [searchQuery, setSearchQuery] = useState("");
  const [noticeFilter, setNoticeFilter] = useState("all");
  const [expFilter, setExpFilter] = useState("all");

  // Detail panel state
  const [selectedCandidate, setSelectedCandidate] =
    useState<RankedCandidate | null>(null);
  const [detailProfile, setDetailProfile] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const detailPanelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchRankings() {
      try {
        const data = await apiService.getRankings();
        setCandidates(data);
        setFiltered(data);
      } catch (err: any) {
        console.error(err);
        setError("Rankings file not found. Make sure rankings are generated.");
      } finally {
        setLoading(false);
      }
    }
    fetchRankings();
  }, []);

  // Filter logic
  useEffect(() => {
    let result = [...candidates];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.title.toLowerCase().includes(q) ||
          c.candidate_id.toLowerCase().includes(q)
      );
    }

    if (noticeFilter !== "all") {
      if (noticeFilter === "immediate") {
        result = result.filter((c) => c.notice_period <= 15);
      } else if (noticeFilter === "short") {
        result = result.filter(
          (c) => c.notice_period > 15 && c.notice_period <= 30
        );
      } else if (noticeFilter === "standard") {
        result = result.filter(
          (c) => c.notice_period > 30 && c.notice_period <= 60
        );
      } else if (noticeFilter === "long") {
        result = result.filter((c) => c.notice_period > 60);
      }
    }

    if (expFilter !== "all") {
      if (expFilter === "mid") {
        result = result.filter((c) => c.experience < 5);
      } else if (expFilter === "senior") {
        result = result.filter(
          (c) => c.experience >= 5 && c.experience <= 9
        );
      } else if (expFilter === "lead") {
        result = result.filter((c) => c.experience > 9);
      }
    }

    setFiltered(result);
  }, [searchQuery, noticeFilter, expFilter, candidates]);

  const handleSelectCandidate = async (cand: RankedCandidate) => {
    // If clicking the same candidate again, deselect
    if (selectedCandidate?.candidate_id === cand.candidate_id) {
      setSelectedCandidate(null);
      setDetailProfile(null);
      return;
    }

    setSelectedCandidate(cand);
    setDetailProfile(null);
    setDetailLoading(true);

    // Scroll detail panel into view on mobile
    setTimeout(() => {
      detailPanelRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);

    try {
      const details = await apiService.getCandidateDetails(cand.candidate_id);
      setDetailProfile(details);
    } catch (err) {
      console.error("Could not load full candidate profile:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return "text-yellow-500 font-black text-lg";
    if (rank === 2) return "text-gray-400 font-black text-base";
    if (rank === 3) return "text-amber-600 font-black text-base";
    return "text-gray-600 font-bold text-sm";
  };

  const getRankIcon = (rank: number) => {
    if (rank <= 3)
      return <Star size={10} className="inline mr-0.5 fill-current" />;
    return null;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">
            Top 100 Rankings
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Final AI-ranked candidate recommendations. Click any row to view
            full profile details.
          </p>
        </div>

        <a
          href={apiService.getDownloadUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-2 px-4 py-2.5 bg-brand-primary hover:bg-brand-hover text-white text-sm font-medium rounded-lg transition-colors card-shadow cursor-pointer"
        >
          <Download size={16} />
          <span>Download submission.csv</span>
        </a>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-6 text-center space-y-3 card-shadow">
          <p className="font-medium">{error}</p>
          <p className="text-xs text-amber-600">
            Please execute the ranking script (
            <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">
              python rank.py
            </code>
            ) first to create the rankings report.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Table Panel */}
          <div className="lg:col-span-2 space-y-3">
            {/* Filters Bar */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 card-shadow flex flex-col md:flex-row gap-3 items-center">
              <div className="relative w-full md:flex-1">
                <Search
                  className="absolute left-3 top-2.5 text-gray-400"
                  size={15}
                />
                <input
                  type="text"
                  placeholder="Search by name, title, or candidate ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 w-full border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-brand-primary bg-gray-50 focus:bg-white transition-colors"
                />
              </div>

              <div className="flex w-full md:w-auto gap-2">
                <select
                  value={expFilter}
                  onChange={(e) => setExpFilter(e.target.value)}
                  className="flex-1 md:w-40 p-2 border border-gray-200 rounded-lg text-xs bg-gray-50 focus:outline-none text-gray-700"
                >
                  <option value="all">Experience (All)</option>
                  <option value="mid">{"< 5 Years"}</option>
                  <option value="senior">5–9 Years (Target)</option>
                  <option value="lead">{"> 9 Years"}</option>
                </select>

                <select
                  value={noticeFilter}
                  onChange={(e) => setNoticeFilter(e.target.value)}
                  className="flex-1 md:w-40 p-2 border border-gray-200 rounded-lg text-xs bg-gray-50 focus:outline-none text-gray-700"
                >
                  <option value="all">Notice Period (All)</option>
                  <option value="immediate">Immediate ({"≤ 15d"})</option>
                  <option value="short">Short ({"≤ 30d"})</option>
                  <option value="standard">Standard ({"≤ 60d"})</option>
                  <option value="long">Long ({"> 60d"})</option>
                </select>
              </div>
            </div>

            {/* Results count */}
            <p className="text-xs text-gray-400 px-1">
              Showing{" "}
              <span className="font-semibold text-gray-600">
                {filtered.length}
              </span>{" "}
              of{" "}
              <span className="font-semibold text-gray-600">
                {candidates.length}
              </span>{" "}
              candidates
              {selectedCandidate && (
                <span className="ml-2 text-brand-primary">
                  · 1 selected (click again to deselect)
                </span>
              )}
            </p>

            {/* Table */}
            <div className="bg-white rounded-xl border border-gray-200 card-shadow overflow-hidden">
              <div className="max-h-[520px] overflow-y-auto">
                <table className="w-full border-collapse text-left text-sm text-gray-600">
                  <thead className="bg-gray-50 border-b border-gray-100 text-[11px] font-bold text-gray-400 uppercase tracking-wider sticky top-0 z-10">
                    <tr>
                      <th className="px-5 py-3 text-center w-14">#</th>
                      <th className="px-5 py-3">Candidate</th>
                      <th className="px-5 py-3 hidden md:table-cell">
                        Signals
                      </th>
                      <th className="px-5 py-3 text-right">Score</th>
                      <th className="px-5 py-3 w-8"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {filtered.map((c) => {
                      const isSelected =
                        selectedCandidate?.candidate_id === c.candidate_id;
                      return (
                        <tr
                          key={c.candidate_id}
                          onClick={() => handleSelectCandidate(c)}
                          className={`transition-all cursor-pointer ${
                            isSelected
                              ? "bg-blue-50 border-l-2 border-brand-primary"
                              : "hover:bg-gray-50 border-l-2 border-transparent"
                          }`}
                        >
                          <td className="px-5 py-3.5 text-center">
                            <span className={getRankStyle(c.rank)}>
                              {getRankIcon(c.rank)}
                              {c.rank}
                            </span>
                          </td>
                          <td className="px-5 py-3.5">
                            <div
                              className={`font-semibold text-sm ${isSelected ? "text-brand-primary" : "text-gray-900"}`}
                            >
                              {c.name}
                            </div>
                            <div className="text-xs text-gray-500 mt-0.5">
                              {c.title}
                            </div>
                            <div className="text-[10px] text-gray-400 font-mono mt-0.5">
                              {c.candidate_id}
                            </div>
                          </td>
                          <td className="px-5 py-3.5 hidden md:table-cell">
                            <div className="flex items-center space-x-1 text-xs text-gray-500 mb-1">
                              <Briefcase size={11} />
                              <span>{c.experience.toFixed(1)} yrs</span>
                            </div>
                            <div className="flex items-center space-x-1 text-xs text-gray-500 mb-1">
                              <Calendar size={11} />
                              <span>{c.notice_period}d notice</span>
                            </div>
                            <div className="flex items-center space-x-1 text-xs text-gray-500">
                              <MapPin size={11} />
                              <span>{c.location?.split(",")[0]}</span>
                            </div>
                          </td>
                          <td className="px-5 py-3.5 text-right">
                            <span
                              className={`font-bold text-sm ${isSelected ? "text-brand-primary" : "text-gray-700"}`}
                            >
                              {c.score.toFixed(4)}
                            </span>
                          </td>
                          <td className="px-3 py-3.5">
                            <ChevronRight
                              size={14}
                              className={`transition-transform ${isSelected ? "text-brand-primary rotate-90" : "text-gray-300"}`}
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {filtered.length === 0 && (
                  <div className="p-10 text-center text-gray-400 text-xs">
                    No candidates match the selected filters.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Details Sidebar Panel */}
          <div ref={detailPanelRef} className="lg:col-span-1">
            {selectedCandidate ? (
              <div className="bg-white border border-gray-200 rounded-xl card-shadow overflow-hidden animate-fade-in sticky top-4">
                {/* Panel Header */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-5 text-white">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <Award size={16} className="text-white" />
                      </div>
                      <div>
                        <p className="text-[10px] text-blue-200 font-mono uppercase tracking-wider">
                          Rank #{selectedCandidate.rank}
                        </p>
                        <h2 className="text-base font-bold leading-tight">
                          {selectedCandidate.name}
                        </h2>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedCandidate(null);
                        setDetailProfile(null);
                      }}
                      className="p-1 hover:bg-white/20 rounded transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </div>
                  <p className="text-xs text-blue-100 mt-2">
                    {selectedCandidate.title}
                  </p>
                  <p className="text-[10px] text-blue-200 font-mono mt-1">
                    {selectedCandidate.candidate_id}
                  </p>
                </div>

                {/* Score Banner */}
                <div className="px-5 py-3 bg-blue-50 border-b border-blue-100 flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 text-xs text-blue-700">
                    <TrendingUp size={13} />
                    <span className="font-medium">Match Score</span>
                  </div>
                  <span className="text-lg font-black text-blue-700">
                    {selectedCandidate.score.toFixed(4)}
                  </span>
                </div>

                {/* Quick Stats Grid */}
                <div className="p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex items-center space-x-1 text-gray-400 mb-1">
                        <Briefcase size={11} />
                        <span className="text-[10px] uppercase tracking-wider font-medium">
                          Experience
                        </span>
                      </div>
                      <p className="font-bold text-gray-900 text-sm">
                        {selectedCandidate.experience.toFixed(1)} yrs
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex items-center space-x-1 text-gray-400 mb-1">
                        <Calendar size={11} />
                        <span className="text-[10px] uppercase tracking-wider font-medium">
                          Notice
                        </span>
                      </div>
                      <p className="font-bold text-gray-900 text-sm">
                        {selectedCandidate.notice_period}d
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex items-center space-x-1 text-gray-400 mb-1">
                        <Code2 size={11} />
                        <span className="text-[10px] uppercase tracking-wider font-medium">
                          GitHub
                        </span>
                      </div>
                      <p className="font-bold text-gray-900 text-sm">
                        {selectedCandidate.github_score >= 0
                          ? `${selectedCandidate.github_score}/100`
                          : "N/A"}
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex items-center space-x-1 text-gray-400 mb-1">
                        <MapPin size={11} />
                        <span className="text-[10px] uppercase tracking-wider font-medium">
                          Location
                        </span>
                      </div>
                      <p
                        className="font-bold text-gray-900 text-xs truncate"
                        title={selectedCandidate.location}
                      >
                        {selectedCandidate.location?.split(",")[0]}
                      </p>
                    </div>
                  </div>

                  {/* Reasoning */}
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-2">
                      AI Match Explanation
                    </h3>
                    <p className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg border border-gray-100 leading-relaxed italic">
                      &ldquo;{selectedCandidate.reasoning}&rdquo;
                    </p>
                  </div>

                  {/* Additional Details (loaded async) */}
                  {detailLoading ? (
                    <div className="flex items-center justify-center py-4 space-x-2">
                      <div className="w-4 h-4 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
                      <span className="text-xs text-gray-400">
                        Loading full profile...
                      </span>
                    </div>
                  ) : (
                    detailProfile && (
                      <div className="border-t border-gray-100 pt-4">
                        <h3 className="text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-2">
                          Top Skills
                        </h3>
                        <div className="flex flex-wrap gap-1.5">
                          {detailProfile.skills
                            ?.slice(0, 8)
                            .map((s: any, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-blue-50 border border-blue-100 text-blue-700 text-[10px] font-medium rounded"
                              >
                                {s.name}
                              </span>
                            ))}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-10 text-center text-gray-400 bg-gray-50/30 sticky top-4">
                <Award size={32} className="mx-auto mb-3 text-gray-300" />
                <p className="text-sm font-medium text-gray-500">
                  Select a candidate
                </p>
                <p className="text-xs text-gray-400 mt-1 max-w-[180px] mx-auto">
                  Click any row in the rankings table to view their full
                  profile.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
