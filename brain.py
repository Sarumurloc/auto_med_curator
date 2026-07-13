import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv

# --- 定義結構 ---
class Scene(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scene_id: int
    voiceover: str
    visual_prompt: str
    is_highlight: bool

class Metadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    keywords: list[str]
    tags: list[str]
    product_comparison_data: list[dict]

class DiagnosticLogic(BaseModel):
    model_config = ConfigDict(extra='forbid')
    anxiety_trigger: str
    assessment_questions: list[str]
    recommendation_path: str
    affiliate_product_id: str

class CuratorOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    metadata: Metadata
    diagnostic_logic: DiagnosticLogic
    video_scenes: list[Scene]
    seo_article: str

def setup_gemini_client():
    load_dotenv()
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def draft_consultative_script(client, topic: str) -> dict:
    system_instruction = """
    You are a medical IP curator. Your core logic is "Consultative Selling".
    Output in native American English.
    """
    
    schema = CuratorOutput.model_json_schema()
    
    def remove_additional_properties(schema_obj):
        if isinstance(schema_obj, dict):
            if "additionalProperties" in schema_obj:
                del schema_obj["additionalProperties"]
            for value in schema_obj.values():
                remove_additional_properties(value)
        elif isinstance(schema_obj, list):
            for item in schema_obj:
                remove_additional_properties(item)
        return schema_obj

    cleaned_schema = remove_additional_properties(schema)

    # 這裡就是關鍵的 API 呼叫，確保 response 被定義
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Topic: {topic}\nProvide output as strict CuratorOutput JSON.",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=cleaned_schema, 
        )
    )
    return json.loads(response.text)