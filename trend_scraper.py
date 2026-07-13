import requests
import xml.etree.ElementTree as ET

def fetch_health_trends(limit: int = 5) -> list:
    """
    透過輕量級 requests 爬取北美權威醫療 RSS，擷取最新健康趨勢。
    這裡以紐約時報 (NYT) Health 版塊為例，因其涵蓋北美大眾最關心的減重、睡眠、焦慮等熱點。
    """
    rss_url = "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"
    print(f"[Scraper] 啟動趨勢天線，正在從 RSS 獲取最新醫療健康趨勢...\n")
    
    try:
        # 1. 發送請求 (加入 User-Agent 避免被防火牆擋下)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status() # 檢查連線狀態
        
        # 2. 使用內建的 XML 解析器 (零外部依賴)
        root = ET.fromstring(response.content)
        
        trends = []
        # 3. 遍歷 RSS 中的 item 節點，抓取前 N 筆最新話題
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text
            
            # 確保 description 節點存在
            desc_node = item.find('description')
            description = desc_node.text if desc_node is not None else "無摘要"
            
            trends.append({
                "title": title,
                "summary": description
            })
            
        return trends
        
    except requests.exceptions.RequestException as e:
        print(f"[Error] 網路連線錯誤: {e}")
        return []
    except ET.ParseError as e:
        print(f"[Error] XML 解析錯誤: {e}")
        return []

if __name__ == "__main__":
    # === 本地測試區塊 ===
    print("--- 啟動 Auto-Med-Curator 趨勢天線測試 ---")
    latest_trends = fetch_health_trends(limit=3)
    
    if latest_trends:
        print("=== 📡 成功攔截今日北美醫療熱點 ===\n")
        for i, trend in enumerate(latest_trends, 1):
            print(f"熱點 {i}: {trend['title']}")
            print(f"摘要: {trend['summary']}\n")
            print("-" * 40)
    else:
        print("[System] 抓取失敗，請檢查網路狀態。")