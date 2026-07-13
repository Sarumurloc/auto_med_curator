import json
import os
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_placeholder_image(scene_id: int, prompt_text: str, output_path: str):
    """
    使用 Pillow 生成一張 1920x1080 的極簡佔位圖 (Storyboard Card)，
    將大腦構思的 visual_prompt 寫在圖片正中央，供後續影片合成對位使用。
    """
    # 建立一張 1920x1080 的白底畫布 (符合白板動畫底色)
    width, height = 1920, 1080
    image = Image.new('RGB', (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    
    # 準備繪製文字 (若無預設字體，Pillow 會使用極簡的預設點陣字)
    # 這裡我們將長句子自動斷行，避免超出螢幕邊界
    wrapped_text = textwrap.fill(f"Scene {scene_id} Visual Prompt:\n\n{prompt_text}", width=50)
    
    # 粗略計算文字置中的位置並繪製 (使用深灰色字體)
    draw.text((100, height // 3), wrapped_text, fill=(50, 50, 50), align="left", spacing=20)
    
    image.save(output_path)
    print(f"  └── 成功產出佔位圖: {os.path.basename(output_path)}")

def process_project_images(project_id: str, date_str: str):
    """讀取專案 JSON 並批次生成所有場景的佔位圖片"""
    base_dir = os.path.join("outputs", project_id, date_str)
    json_path = os.path.join(base_dir, "script.json")

    if not os.path.exists(json_path):
        print(f"[Error] 找不到腳本檔案: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[Image Engine] 開始批次生成 {project_id} ({date_str}) 的視覺佔位圖...")

    # 建立圖片專屬的子資料夾
    image_dir = os.path.join(base_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    # 遍歷所有 Scene 並生成圖片
    for scene in data.get("video_scenes", []):
        scene_id = scene["scene_id"]
        prompt_text = scene["visual_prompt"]
        output_path = os.path.join(image_dir, f"scene_{scene_id}.png")
        
        create_placeholder_image(scene_id, prompt_text, output_path)

    print(f"\n[System] ✅ 所有佔位圖已成功封裝至：{image_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-Med-Curator 視覺生成引擎 (佔位符版)")
    parser.add_argument("--project", type=str, default="med_curator", help="指定專案 ID")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y%m%d"), help="指定執行日期")
    args = parser.parse_args()
    
    process_project_images(args.project, args.date)