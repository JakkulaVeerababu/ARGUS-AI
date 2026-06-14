export interface Multipliers {
  experience: number;
  role: number;
  location: number;
  engagement: number;
  github: number;
  notice: number;
  profile_quality: number;
}

export interface RankedCandidate {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
  name: string;
  title: string;
  experience: number;
  location: string;
  github_score: number;
  response_rate: number;
  notice_period: number;
}

export interface ScoredCandidate {
  candidate_id: string;
  candidate_name: string;
  current_title: string;
  years_of_experience: number;
  location: string;
  cross_encoder_score: number;
  sigmoid_ce_score: number;
  multipliers: Multipliers;
  final_score: number;
  reasoning?: string;
}

export interface SearchResponse {
  success: boolean;
  results: ScoredCandidate[];
}

export interface AnalyticsData {
  kpis: {
    total_candidates: number;
    average_match_score: number;
    top_locations: { city: string; count: number }[];
  };
  distributions: {
    experience: { range: string; count: number }[];
    notice_period: { timeline: string; count: number }[];
    locations: { name: string; value: number }[];
  };
}
