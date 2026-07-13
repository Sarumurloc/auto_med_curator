import json
import os

def build():
    print("[Build] 開始編譯靜態網頁...")
    
    # 1. 讀取 Agent 產出的 JSON
    with open('data/script.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get("metadata", {})
    diagnostic = data.get("diagnostic_logic", {})
    
    # 2. 讀取 HTML 模版
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 3. 執行字串替換 (將大腦數據注入前端)
    html_output = template.replace('{{ title }}', metadata.get('title', 'Medical Curation'))
    html_output = template.replace('{{ keywords }}', ', '.join(metadata.get('keywords', [])))
    html_output = template.replace('{{ anxiety_trigger }}', diagnostic.get('anxiety_trigger', ''))
    html_output = template.replace('{{ recommendation_path }}', diagnostic.get('recommendation_path', ''))
    html_output = template.replace('{{ affiliate_product_id }}', diagnostic.get('affiliate_product_id', ''))
    
    # 4. 建立公開資料夾並輸出
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print("[Build] 網頁編譯完成，已輸出至 public/index.html")

if __name__ == "__main__":
    build()