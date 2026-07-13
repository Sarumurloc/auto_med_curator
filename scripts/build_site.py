import json
import os

def build():
    print("[Build] 開始編譯靜態網頁...")
    
    # 1. 動態尋找最新的 Agent 產出
    base_dir = os.path.join("outputs", "med_curator")
    if not os.path.exists(base_dir):
        print(f"[Build Error] 找不到目錄 {base_dir}，請確認 Agent 是否成功執行。")
        return
        
    # 取得最新日期的資料夾
    folders = sorted(os.listdir(base_dir), reverse=True)
    if not folders:
        print("[Build Error] 找不到任何日期的資料夾。")
        return
        
    latest_folder = folders[0]
    json_path = os.path.join(base_dir, latest_folder, "script.json")
    print(f"[Build] 成功鎖定最新資料庫：{json_path}")
    
    # 2. 讀取 Agent 產出的 JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get("metadata", {})
    diagnostic = data.get("diagnostic_logic", {})
    
    # 3. 讀取 HTML 模版
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        print(f"[Build Error] 找不到模版檔案 {template_path}")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 4. 執行字串替換 (將大腦數據注入前端)
    html_output = template.replace('{{ title }}', metadata.get('title', 'Medical Curation'))
    
    # 處理 list 結構的 keywords
    keywords = metadata.get('keywords', [])
    if isinstance(keywords, list):
        html_output = html_output.replace('{{ keywords }}', ', '.join(keywords))
    else:
        html_output = html_output.replace('{{ keywords }}', str(keywords))
        
    html_output = html_output.replace('{{ anxiety_trigger }}', diagnostic.get('anxiety_trigger', '無資料'))
    html_output = html_output.replace('{{ recommendation_path }}', diagnostic.get('recommendation_path', '無資料'))
    html_output = html_output.replace('{{ affiliate_product_id }}', diagnostic.get('affiliate_product_id', ''))
    
    # 5. 建立公開資料夾並輸出
    os.makedirs('public', exist_ok=True)
    with open(os.path.join('public', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print("[Build] 網頁編譯完成，已輸出至 public/index.html")

if __name__ == "__main__":
    build()