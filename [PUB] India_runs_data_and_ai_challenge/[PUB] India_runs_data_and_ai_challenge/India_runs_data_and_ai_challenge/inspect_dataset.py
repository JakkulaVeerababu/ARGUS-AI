import json
import gzip
import os
import time

candidates_path = r"c:\Users\LENOVO\Desktop\ARGUS AI\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

def inspect_dataset():
    start_time = time.time()
    total_count = 0
    anomalies = []
    titles = {}
    countries = {}
    years_exp = []
    
    # Let's inspect the first 10,000 candidates to get a quick sample
    print("Reading and analyzing candidates...")
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total_count += 1
            if total_count > 100000:
                break
                
            candidate = json.loads(line)
            profile = candidate.get("profile", {})
            title = profile.get("current_title", "")
            country = profile.get("country", "")
            years = profile.get("years_of_experience", 0)
            
            titles[title] = titles.get(title, 0) + 1
            countries[country] = countries.get(country, 0) + 1
            years_exp.append(years)
            
            # Check for potential honeypot/anomaly conditions:
            # 1. Expert proficiency in many skills with 0 duration_months
            skills = candidate.get("skills", [])
            expert_skills_0_duration = [s for s in skills if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", 0) == 0]
            
            # 2. Impossible career history durations vs dates
            impossible_dates = False
            career_history = candidate.get("career_history", [])
            for job in career_history:
                start = job.get("start_date")
                end = job.get("end_date")
                dur = job.get("duration_months", 0)
                # Parse start and end date if they exist
                if start and end:
                    try:
                        sy, sm, sd = map(int, start.split('-'))
                        ey, em, ed = map(int, end.split('-'))
                        actual_months = (ey - sy) * 12 + (em - sm)
                        if abs(actual_months - dur) > 12: # more than a year discrepancy
                            impossible_dates = True
                    except Exception:
                        pass
            
            # 3. Check for specific impossible experience
            # 8 years of experience at a company founded 3 years ago
            # Since we don't have company foundation dates directly, let's see if the company name contains clues,
            # or if the duration_months is e.g. 96 (8 years) but the start date is e.g. 2023 (which is 3 years ago relative to 2026)
            # Let's check if the job start_date is within the last 3 years (e.g., since 2023) but listed duration is > 36 months (3 years)
            company_date_mismatch = False
            for job in career_history:
                start = job.get("start_date")
                dur = job.get("duration_months", 0)
                if start:
                    try:
                        sy = int(start.split('-')[0])
                        # If started in 2023 or later, but duration is > 36 months, or if started in 2024 but duration is > 24 months, etc.
                        # Since the current year is 2026:
                        # 2026 - sy is the maximum possible years.
                        max_possible_months = (2026 - sy + 1) * 12 # add buffer
                        if dur > max_possible_months:
                            company_date_mismatch = True
                    except Exception:
                        pass

            if len(expert_skills_0_duration) >= 5 or impossible_dates or company_date_mismatch:
                anomalies.append({
                    "id": candidate.get("candidate_id"),
                    "name": profile.get("anonymized_name"),
                    "title": title,
                    "years": years,
                    "num_expert_0_dur": len(expert_skills_0_duration),
                    "impossible_dates": impossible_dates,
                    "company_date_mismatch": company_date_mismatch,
                    "skills": [s.get("name") for s in expert_skills_0_duration]
                })

    end_time = time.time()
    print(f"Read {total_count} lines in {end_time - start_time:.2f} seconds.")
    print(f"Total anomalies found in sample: {len(anomalies)}")
    print("\nSample Anomalies:")
    for a in anomalies[:10]:
        print(a)
        
    print("\nTop titles:")
    sorted_titles = sorted(titles.items(), key=lambda x: x[1], reverse=True)
    for t, c in sorted_titles[:15]:
        print(f"  {t}: {c}")
        
    print("\nTop countries:")
    sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
    for c, count in sorted_countries[:10]:
        print(f"  {c}: {count}")

if __name__ == "__main__":
    inspect_dataset()
