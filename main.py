import argparse
import json
import os
from datetime import datetime
from trend_scraper import fetch_health_trends
from brain import draft_consultative_script, setup_gemini_client

def save_assets(project_id: str, script_data: dict, date_str: str):
    output_dir = os.path.join("outputs", project_id, date_str)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "script.json"), 'w', encoding='utf-8') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=4)
    with open(os.path.join(output_dir, "article.md"), 'w', encoding='utf-8') as f:
        f.write(script_data["seo_article"])
    print(f"\n[System] ✅ 數位資產已成功封裝至：{output_dir}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=str, default="med_curator")
    args = parser.parse_args()
    
    trends = fetch_health_trends(limit=1)
    if not trends: return

    print(f"[System] 正在分析主題: {trends[0]['title']}...")
    client = setup_gemini_client()
    script_data = draft_consultative_script(client, trends[0]['title'])
    save_assets(args.project, script_data, datetime.now().strftime("%Y%m%d"))

if __name__ == "__main__":
    main()