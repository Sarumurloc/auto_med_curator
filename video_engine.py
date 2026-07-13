import json
import os
import argparse
from datetime import datetime
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def process_project_videos(project_id: str, date_str: str):
    """
    讀取積木資產，自動對齊時間軸，並雙軌輸出長片與短片。
    """
    base_dir = os.path.join("outputs", project_id, date_str)
    json_path = os.path.join(base_dir, "script.json")
    audio_dir = os.path.join(base_dir, "audio")
    image_dir = os.path.join(base_dir, "images")
    video_dir = os.path.join(base_dir, "videos")
    
    if not os.path.exists(json_path):
        print(f"[Error] 找不到腳本檔案: {json_path}")
        return

    os.makedirs(video_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[Video Engine] 啟動自動化組裝線 | 專案：{project_id} ({date_str})")

    full_video_clips = []
    highlight_video_clips = []

    # 1. 遍歷每一個積木場景，進行音影合成
    for scene in data.get("video_scenes", []):
        scene_id = scene["scene_id"]
        is_highlight = scene["is_highlight"]
        
        audio_path = os.path.join(audio_dir, f"scene_{scene_id}.mp3")
        image_path = os.path.join(image_dir, f"scene_{scene_id}.png")
        
        if not (os.path.exists(audio_path) and os.path.exists(image_path)):
            print(f"  └── [警告] 缺少 Scene {scene_id} 的素材，跳過此場景。")
            continue

        # 讀取音軌
        audio_clip = AudioFileClip(audio_path)
        # 讀取圖片，並將圖片的顯示長度強制設定為「與音軌等長」
        image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
        # 將音軌綁定到圖片上
        video_clip = image_clip.set_audio(audio_clip)
        
        full_video_clips.append(video_clip)
        
        # 2. 如果是高光時刻，順便複製一份丟進短片陣列
        if is_highlight:
            highlight_video_clips.append(video_clip)
            print(f"  └── Scene {scene_id} 已標記為高光，加入短片陣列。")

    print("\n[Video Engine] 素材讀取完畢，開始渲染影片 (這可能需要幾分鐘)...")

    # 3. 渲染完整長片
    if full_video_clips:
        print("  ▶ 正在渲染：完整白板動畫 (Full Video)")
        final_full_video = concatenate_videoclips(full_video_clips, method="compose")
        full_output_path = os.path.join(video_dir, "full_video.mp4")
        # 設定 fps=24 確保最低資源消耗
        final_full_video.write_videofile(full_output_path, fps=24, logger=None)
        print(f"  ✅ 完整長片已儲存: {full_output_path}")

    # 4. 渲染引流短片
    if highlight_video_clips:
        print("\n  ▶ 正在渲染：15秒引流短片 (Shorts)")
        final_shorts_video = concatenate_videoclips(highlight_video_clips, method="compose")
        shorts_output_path = os.path.join(video_dir, "shorts_video.mp4")
        final_shorts_video.write_videofile(shorts_output_path, fps=24, logger=None)
        print(f"  ✅ 引流短片已儲存: {shorts_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-Med-Curator 影片渲染引擎")
    parser.add_argument("--project", type=str, default="med_curator", help="指定專案 ID")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y%m%d"), help="指定執行日期")
    args = parser.parse_args()
    
    process_project_videos(args.project, args.date)