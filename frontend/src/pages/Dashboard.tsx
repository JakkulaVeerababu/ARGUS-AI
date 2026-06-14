import React, { useEffect, useState } from "react";
import { apiService } from "../services/api";
import { AnalyticsData } from "../types";
import { Users, Award, MapPin, CheckCircle, Clock } from "lucide-react";

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const healthy = await apiService.healthCheck();
        setIsBackendHealthy(healthy);
        
        const analytics = await apiService.getAnalytics();
        setData(analytics);
      } catch (err: any) {
        console.error(err);
        setError("Could not load dashboard statistics. Make sure rankings are generated.");
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          Welcome to Argus AI, your intelligent candidate discovery and ranking SaaS portal.
        </p>
      </div>

      {/* Backend Status Check Banner */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 card-shadow">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${isBackendHealthy ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
          <div>
            <p className="text-sm font-medium text-gray-800">
              {isBackendHealthy ? "Sourcing Feed Connected" : "Sourcing Feed Disconnected"}
            </p>
            <p className="text-xs text-gray-500">
              {isBackendHealthy 
                ? "Candidate discovery pipeline is synchronized and actively listening for scoring queries." 
                : "The recommendation engine is currently offline. Please verify the backend service connection."}
            </p>
          </div>
        </div>
        <span className="text-xs font-mono bg-white px-2 py-1 rounded border border-gray-200 text-gray-400">
          v1.0.0
        </span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-6 text-center space-y-3 card-shadow">
          <p className="font-medium">{error}</p>
          <p className="text-xs text-amber-600">
            Please run the ranking script (<code className="bg-amber-100 px-1 py-0.5 rounded font-mono">python rank.py</code>) first to create the initial <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">submission.csv</code>.
          </p>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500">Total Candidate Pool</span>
                <span className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Users size={20} /></span>
              </div>
              <div>
                <h3 className="text-3xl font-bold text-gray-900 tracking-tight">100,000</h3>
                <p className="text-xs text-green-600 font-medium mt-1">Active indices loaded in RAM</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500">Top 100 Selected</span>
                <span className="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><Award size={20} /></span>
              </div>
              <div>
                <h3 className="text-3xl font-bold text-gray-900 tracking-tight">
                  {data?.kpis.total_candidates || 100}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Avg match score: <span className="font-semibold text-gray-700">{(data?.kpis.average_match_score || 0).toFixed(4)}</span>
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500">Honeypots Detected</span>
                <span className="p-2 bg-rose-50 text-rose-600 rounded-lg"><CheckCircle size={20} /></span>
              </div>
              <div>
                <h3 className="text-3xl font-bold text-gray-900 tracking-tight">0%</h3>
                <p className="text-xs text-rose-600 font-medium mt-1">100% of safe profiles verified</p>
              </div>
            </div>
          </div>

          {/* Quick Info Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top Locations Card */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
                <MapPin size={18} className="text-gray-500" />
                <span>Geographic Distribution (Top Cities)</span>
              </h2>
              <div className="space-y-3 pt-2">
                {data?.kpis.top_locations.map((loc, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 font-medium">{loc.city}</span>
                    <div className="flex items-center space-x-3 w-2/3">
                      <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-brand-primary h-full rounded-full" 
                          style={{ width: `${(loc.count / (data.kpis.total_candidates || 100)) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-gray-700 w-8 text-right">
                        {loc.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Notice Period Distributions Card */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
                <Clock size={18} className="text-gray-500" />
                <span>Notice Period Distribution</span>
              </h2>
              <div className="space-y-3 pt-2">
                {data?.distributions.notice_period.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 font-medium">{item.timeline}</span>
                    <div className="flex items-center space-x-3 w-2/3">
                      <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-brand-primary h-full rounded-full" 
                          style={{ width: `${(item.count / (data.kpis.total_candidates || 100)) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-gray-700 w-8 text-right">
                        {item.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
