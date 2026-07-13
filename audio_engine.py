import asyncio
import json
import os
import edge_tts
import argparse
from datetime import datetime

VOICE = "en-US-ChristopherNeural"

async def generate_scene_audio(text: str, output_path: str):
    """呼叫 Edge-TTS 生成單一場景的音軌，並加入簡單的防錯機制"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)
    
    # 驗證機制：如果生成的檔案不到 1KB，通常代表伺服器擋下了請求或網路中斷
    if os.path.exists(output_path) and os.path.getsize(output_path) < 1024:
        raise ValueError("音軌生成失敗 (檔案過小，可能是網路或伺服器阻擋)")
        
    print(f"  └── ✅ 成功產出音軌: {os.path.basename(output_path)}")

async def process_project_audio(project_id: str, date_str: str):
    base_dir = os.path.join("outputs", project_id, date_str)
    json_path = os.path.join(base_dir, "script.json")

    if not os.path.exists(json_path):
        print(f"[Error] 找不到腳本檔案: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[Audio Engine] 開始穩健生成 {project_id} ({date_str}) 的積木音軌...")
    audio_dir = os.path.join(base_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    # 【關鍵修改】：放棄併發，改用安全的 for 迴圈依序等待，避免被免費 API 封鎖
    for scene in data.get("video_scenes", []):
        scene_id = scene["scene_id"]
        text = scene["voiceover"]
        output_path = os.path.join(audio_dir, f"scene_{scene_id}.mp3")
        
        print(f"  ▶ 正在向 Edge-TTS 請求 Scene {scene_id} ...")
        try:
            await generate_scene_audio(text, output_path)
            # 加上 1 秒的友善延遲，保護你的 IP 不被微軟暫時封鎖
            await asyncio.sleep(1)
        except Exception as e:
            print(f"  └── ❌ Scene {scene_id} 生成失敗: {e}")

    print(f"\n[System] 所有音軌任務結束，請檢查 {audio_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-Med-Curator 語音生成引擎")
    parser.add_argument("--project", type=str, default="med_curator", help="指定專案 ID")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y%m%d"), help="指定執行日期")
    args = parser.parse_args()
    
    asyncio.run(process_project_audio(args.project, args.date))