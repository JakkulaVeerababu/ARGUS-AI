import React, { useEffect, useState } from "react";
import { apiService } from "../services/api";
import { RankedCandidate } from "../types";
import { Award, Download, Search, Calendar, Briefcase, Eye } from "lucide-react";

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
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [detailProfile, setDetailProfile] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

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
        result = result.filter((c) => c.notice_period > 15 && c.notice_period <= 30);
      } else if (noticeFilter === "standard") {
        result = result.filter((c) => c.notice_period > 30 && c.notice_period <= 60);
      } else if (noticeFilter === "long") {
        result = result.filter((c) => c.notice_period > 60);
      }
    }

    if (expFilter !== "all") {
      if (expFilter === "mid") {
        result = result.filter((c) => c.experience < 5);
      } else if (expFilter === "senior") {
        result = result.filter((c) => c.experience >= 5 && c.experience <= 9);
      } else if (expFilter === "lead") {
        result = result.filter((c) => c.experience > 9);
      }
    }

    setFiltered(result);
  }, [searchQuery, noticeFilter, expFilter, candidates]);

  const handleSelectCandidate = async (cand: RankedCandidate) => {
    setSelectedCandidate(cand);
    setDetailLoading(true);
    setDetailProfile(null);
    try {
      const details = await apiService.getCandidateDetails(cand.candidate_id);
      setDetailProfile(details);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">Top 100 Rankings</h1>
          <p className="text-sm text-gray-500 mt-1">
            Displaying the final safe candidate recommendations generated for the Job Description.
          </p>
        </div>
        
        <div>
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
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-6 text-center space-y-3 card-shadow">
          <p className="font-medium">{error}</p>
          <p className="text-xs text-amber-600">
            Please execute the ranking script (<code className="bg-amber-100 px-1 py-0.5 rounded font-mono">python rank.py</code>) first to create the rankings report.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Table Panel */}
          <div className="lg:col-span-2 space-y-4">
            
            {/* Filters Bar */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 card-shadow flex flex-col md:flex-row gap-4 items-center">
              <div className="relative w-full md:w-1/2">
                <Search className="absolute left-3 top-2.5 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Filter by name, title, or ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 w-full border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-brand-primary bg-gray-50 focus:bg-white transition-colors"
                />
              </div>

              <div className="flex w-full md:w-1/2 gap-4">
                <select
                  value={expFilter}
                  onChange={(e) => setExpFilter(e.target.value)}
                  className="w-1/2 p-2 border border-gray-200 rounded-lg text-xs bg-gray-50 focus:outline-none text-gray-700"
                >
                  <option value="all">Experience (All)</option>
                  <option value="mid">{"< 5 Years"}</option>
                  <option value="senior">5 - 9 Years (Target)</option>
                  <option value="lead">{"> 9 Years"}</option>
                </select>

                <select
                  value={noticeFilter}
                  onChange={(e) => setNoticeFilter(e.target.value)}
                  className="w-1/2 p-2 border border-gray-200 rounded-lg text-xs bg-gray-50 focus:outline-none text-gray-700"
                >
                  <option value="all">Notice Period (All)</option>
                  <option value="immediate">Immediate ({"<= 15d"})</option>
                  <option value="short">Short ({"<= 30d"})</option>
                  <option value="standard">Standard ({"<= 60d"})</option>
                  <option value="long">Long ({"> 60d"})</option>
                </select>
              </div>
            </div>

            {/* List */}
            <div className="bg-white rounded-xl border border-gray-200 card-shadow overflow-hidden">
              <div className="max-h-[500px] overflow-y-auto">
                <table className="w-full border-collapse text-left text-sm text-gray-600">
                  <thead className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-3 text-center w-16">Rank</th>
                      <th className="px-6 py-3">Candidate</th>
                      <th className="px-6 py-3">Fit Metrics</th>
                      <th className="px-6 py-3 text-right">Score</th>
                      <th className="px-6 py-3 w-10"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filtered.map((c) => (
                      <tr 
                        key={c.candidate_id}
                        onClick={() => handleSelectCandidate(c)}
                        className={`hover:bg-gray-50/50 transition-colors cursor-pointer ${selectedCandidate?.candidate_id === c.candidate_id ? "bg-blue-50/30" : ""}`}
                      >
                        <td className="px-6 py-4 text-center font-bold text-gray-800">
                          {c.rank}
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-gray-900 text-sm">{c.name}</div>
                          <div className="text-xs text-gray-500">{c.title}</div>
                        </td>
                        <td className="px-6 py-4 space-y-1">
                          <div className="flex items-center space-x-1.5 text-xs text-gray-500">
                            <Briefcase size={12} />
                            <span>{c.experience.toFixed(1)} yrs exp</span>
                          </div>
                          <div className="flex items-center space-x-1.5 text-xs text-gray-500">
                            <Calendar size={12} />
                            <span>{c.notice_period}d notice</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right font-bold text-brand-primary">
                          {c.score.toFixed(4)}
                        </td>
                        <td className="px-6 py-4 text-gray-400">
                          <Eye size={14} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filtered.length === 0 && (
                  <div className="p-8 text-center text-gray-400 text-xs">
                    No candidates match the filter parameters.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Details Sidebar Panel */}
          <div className="lg:col-span-1">
            {selectedCandidate ? (
              <div className="bg-white border border-gray-200 rounded-xl p-6 card-shadow space-y-6 sticky top-8 animate-fade-in">
                <div className="border-b border-gray-100 pb-4">
                  <div className="flex items-center space-x-2">
                    <span className="p-1 bg-blue-50 text-blue-600 rounded"><Award size={16} /></span>
                    <h2 className="text-lg font-bold text-gray-900">{selectedCandidate.name}</h2>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{selectedCandidate.title}</p>
                  <p className="text-[10px] text-gray-400 font-mono mt-1">ID: {selectedCandidate.candidate_id}</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Match Explanation</h3>
                    <p className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg border border-gray-100 leading-relaxed italic mt-1.5">
                      "{selectedCandidate.reasoning}"
                    </p>
                  </div>

                  <div className="border-t border-gray-100 pt-4 space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Candidate Summary</h3>
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                      <div className="p-2 bg-gray-50/50 rounded">
                        <span className="text-gray-400 block text-[10px]">Location</span>
                        <span className="font-semibold text-gray-800">{selectedCandidate.location.split(",")[0]}</span>
                      </div>
                      <div className="p-2 bg-gray-50/50 rounded">
                        <span className="text-gray-400 block text-[10px]">Notice Period</span>
                        <span className="font-semibold text-gray-800">{selectedCandidate.notice_period} Days</span>
                      </div>
                      <div className="p-2 bg-gray-50/50 rounded">
                        <span className="text-gray-400 block text-[10px]">GitHub Index</span>
                        <span className="font-semibold text-gray-800">
                          {selectedCandidate.github_score >= 0 ? `${selectedCandidate.github_score}/100` : "N/A"}
                        </span>
                      </div>
                      <div className="p-2 bg-gray-50/50 rounded">
                        <span className="text-gray-400 block text-[10px]">Platform Response</span>
                        <span className="font-semibold text-gray-800">{Math.round(selectedCandidate.response_rate * 100)}%</span>
                      </div>
                    </div>
                  </div>

                  {detailLoading ? (
                    <div className="flex justify-center py-4">
                      <div className="w-5 h-5 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : (
                    detailProfile && (
                      <div className="border-t border-gray-100 pt-4 space-y-2">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Top Skills</h3>
                        <div className="flex flex-wrap gap-1.5">
                          {detailProfile.skills?.slice(0, 5).map((s: any, idx: number) => (
                            <span key={idx} className="px-2 py-0.5 bg-gray-50 border border-gray-200 text-gray-600 text-[10px] rounded">
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
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center text-gray-400 bg-gray-50/30 sticky top-8">
                <span className="block text-xs">Select a candidate from the rankings list to view detailed profile mapping and explainability.</span>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
};
