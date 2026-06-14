import React, { useEffect, useState } from "react";
import { apiService } from "../services/api";
import { AnalyticsData } from "../types";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import { BarChart3, PieChart as PieIcon, Info } from "lucide-react";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const res = await apiService.getAnalytics();
        setData(res);
      } catch (err) {
        console.error(err);
        setError("Could not load analytics. Make sure submission rankings are generated.");
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-gray-900 font-sans">Analytics & Distributions</h1>
        <p className="text-sm text-gray-500 mt-1">
          Detailed metrics and visual distributions for the top 100 ranked candidates.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-brand-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-6 text-center space-y-3 card-shadow">
          <p className="font-medium">{error}</p>
          <p className="text-xs text-amber-600">
            Please run the ranking script (<code className="bg-amber-100 px-1 py-0.5 rounded font-mono">python rank.py</code>) first to create the analytics dataset.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          
          {/* Main Visualizations Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Experience Distribution */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                <BarChart3 size={16} className="text-blue-500" />
                <span>Experience Level Distribution</span>
              </div>
              <div className="h-64 pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.distributions.experience} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="range" tickLine={false} axisLine={false} style={{ fontSize: 11, fill: "#64748b" }} />
                    <YAxis tickLine={false} axisLine={false} style={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip cursor={{ fill: "#f8fafc" }} contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
                    <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-gray-400 flex items-center space-x-1.5 bg-gray-50 p-2.5 rounded border border-gray-100">
                <Info size={14} className="text-blue-500" />
                <span>Ideally matches candidates with 5-9 years of industry experience.</span>
              </p>
            </div>

            {/* Notice Periods Chart */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4">
              <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                <BarChart3 size={16} className="text-emerald-500" />
                <span>Notice Period Breakdown</span>
              </div>
              <div className="h-64 pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.distributions.notice_period} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="timeline" tickLine={false} axisLine={false} style={{ fontSize: 11, fill: "#64748b" }} />
                    <YAxis tickLine={false} axisLine={false} style={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip cursor={{ fill: "#f8fafc" }} contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
                    <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-gray-400 flex items-center space-x-1.5 bg-gray-50 p-2.5 rounded border border-gray-100">
                <Info size={14} className="text-emerald-500" />
                <span>Shorter notice periods (&lt; 30 days) receive scoring multipliers.</span>
              </p>
            </div>

            {/* Top Locations Pie Chart */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 card-shadow space-y-4 lg:col-span-2">
              <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                <PieIcon size={16} className="text-amber-500" />
                <span>Top Regional Hubs (Candidate Locations)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center pt-2">
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data?.distributions.locations}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {data?.distributions.locations.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-gray-800">Target Cities Summary</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {data?.distributions.locations.map((loc, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs p-2 bg-gray-50 border border-gray-100 rounded">
                        <div className="flex items-center space-x-2">
                          <span 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: COLORS[idx % COLORS.length] }} 
                          />
                          <span className="font-medium text-gray-700">{loc.name}</span>
                        </div>
                        <span className="font-bold text-gray-900">{loc.value} candidates</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>
          
        </div>
      )}
    </div>
  );
};
