import { SearchResponse, RankedCandidate, ScoredCandidate, AnalyticsData } from "../types";

const API_BASE_URL = "http://localhost:8000";

export const apiService = {
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) return false;
      const data = await response.json();
      return data.status === "healthy";
    } catch {
      return false;
    }
  },

  async searchCandidates(jobDescription: string): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ job_description: jobDescription }),
    });
    if (!response.ok) {
      const errorMsg = await response.text();
      throw new Error(errorMsg || "Failed to search candidates.");
    }
    return response.json();
  },

  async getCandidateDetails(candidateId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/candidate/${candidateId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch candidate details for ${candidateId}`);
    }
    return response.json();
  },

  async getRankings(): Promise<RankedCandidate[]> {
    const response = await fetch(`${API_BASE_URL}/api/rankings`);
    if (!response.ok) {
      throw new Error("Failed to fetch rankings");
    }
    return response.json();
  },

  async getAnalytics(): Promise<AnalyticsData> {
    const response = await fetch(`${API_BASE_URL}/api/analytics`);
    if (!response.ok) {
      throw new Error("Failed to fetch analytics");
    }
    return response.json();
  },

  getDownloadUrl(): string {
    return `${API_BASE_URL}/api/submission`;
  }
};
