import json
import re

candidates_path = r"c:\Users\LENOVO\Desktop\ARGUS AI\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

def scan_for_honeypots():
    rules_triggered = {
        "salary_min_gt_max": 0,
        "job_duration_impossible": 0,
        "skills_expert_0_duration": 0,
        "education_dates_impossible": 0,
        "any_rule": 0
    }
    
    honeypots = []
    
    with open(candidates_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            cand = json.loads(line)
            cid = cand.get("candidate_id")
            profile = cand.get("profile", {})
            career = cand.get("career_history", [])
            education = cand.get("education", [])
            skills = cand.get("skills", [])
            signals = cand.get("redrob_signals", {})
            
            triggered = []
            
            # Check 1: Salary min > max
            sal = signals.get("expected_salary_range_inr_lpa", {})
            if sal and sal.get("min", 0) > sal.get("max", 0):
                triggered.append("salary_min_gt_max")
                rules_triggered["salary_min_gt_max"] += 1
                
            # Check 2: Job duration impossible
            # Local time is June 14, 2026. Let's assume current date is 2026-06-14.
            for job in career:
                start = job.get("start_date")
                end = job.get("end_date")
                dur = job.get("duration_months", 0)
                if start:
                    try:
                        sy, sm, _ = map(int, start.split('-'))
                        if end:
                            ey, em, _ = map(int, end.split('-'))
                        else:
                            ey, em = 2026, 6 # Current time context
                            
                        elapsed = (ey - sy) * 12 + (em - sm)
                        # Let's allow a margin of 2 months
                        if dur > elapsed + 2:
                            triggered.append("job_duration_impossible")
                            rules_triggered["job_duration_impossible"] += 1
                            break
                    except Exception:
                        pass
                        
            # Check 3: Skills expert/advanced with 0 duration_months
            # The honeypot description says: "expert" proficiency in 10 skills with 0 years used
            # Let's see if we count skills with proficiency 'expert' and duration_months == 0
            expert_0_dur = [s for s in skills if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
            # Let's see if any skills matching this count. Let's check if there are candidates with e.g. >= 5 such skills
            if len(expert_0_dur) >= 5:
                triggered.append("skills_expert_0_duration")
                rules_triggered["skills_expert_0_duration"] += 1
                
            # Check 4: Education dates impossible (start_year > end_year)
            for edu in education:
                sy = edu.get("start_year")
                ey = edu.get("end_year")
                if sy and ey and sy > ey:
                    triggered.append("education_dates_impossible")
                    rules_triggered["education_dates_impossible"] += 1
                    break
                    
            if triggered:
                rules_triggered["any_rule"] += 1
                honeypots.append({
                    "candidate_id": cid,
                    "name": profile.get("anonymized_name"),
                    "title": profile.get("current_title"),
                    "triggered": triggered,
                    "details": {
                        "expert_0_dur_count": len(expert_0_dur),
                        "salary": sal,
                        "career_history": [(j.get("company"), j.get("start_date"), j.get("end_date"), j.get("duration_months")) for j in career]
                    }
                })
                
    print(f"Scanned 100,000 candidates.")
    print(f"Total logical violations found: {len(honeypots)}")
    print("Violations breakdown:")
    for rule, count in rules_triggered.items():
        print(f"  {rule}: {count}")
        
    print("\nFirst 10 logical violation candidates:")
    for h in honeypots[:10]:
        print(json.dumps(h, indent=2))

if __name__ == "__main__":
    scan_for_honeypots()
