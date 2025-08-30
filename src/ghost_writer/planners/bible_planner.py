import json, os
from typing import Optional
from pydantic import ValidationError
from dotenv import load_dotenv
from openai import OpenAI
from ..contracts import StoryBible

load_dotenv()
_client = OpenAI()
_MODEL = os.getenv("OPENAI_MODEL_PLANNER", "gpt-4o-mini")


def _chat(messages, model: Optional[str] = None, response_format: Optional[dict] = None) -> str:
    r = _client.chat.completions.create(
        model=model or _MODEL,
        messages=messages,
        temperature=0.2,
        response_format=response_format,  # e.g., {"type": "json_object"}
    )
    return r.choices[0].message.content or ""


def generate_story_bible(pitch: str) -> StoryBible:
    system = ("You are a head writer creating a compact Story Bible.  It must be internally consistent, "
              "grounded, and suitable for a novel-length work.  Use only the specified keys.")
    user = (
        "Create a Story Bible JSON object with these exact keys:\n"
        "{"
        '  "title": str,'
        '  "logline": str,'
        '  "tone": str,'
        '  "themes": str[],'
        '  "world_rules": str,'
        '  "locations": str[],'
        '  "characters": { "<id>": { "id": str, "name": str, "role": "protagonist|deuteragonist|antagonist|supporting", '
        '"voice": str, "look": str, "desires": str, "flaws": str, "first_appearance_chapter": int } },'
        '  "continuity": [ { "id": str, "text": str, "tags": str[] } ],'
        '  "prose_style": str,'
        '  "art_style": str'
        "}\n\n"
        f'Pitch:\n"""{pitch}"""'
        "\nReturn only the JSON object.  No commentary."
    )
    raw = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    try:
        return StoryBible.model_validate_json(raw)
    except (json.JSONDecodeError, ValidationError) as e:
        schema = StoryBible.model_json_schema()
        repair = (
            "Repair this JSON to strictly match the schema.  Return only valid JSON.\n\n"
            f"Schema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Error:\n{e}\n\n"
            f"Bad JSON:\n{raw}"
        )
        fixed = _chat(
            [{"role": "system", "content": "You fix JSON to match schemas exactly."},
             {"role": "user", "content": repair}],
            response_format={"type": "json_object"},
        )
        return StoryBible.model_validate_json(fixed)


# Backward-compatible alias if other code imports plan_bible
def plan_bible(pitch: str) -> StoryBible:
    return generate_story_bible(pitch)


__all__ = ["generate_story_bible", "plan_bible"]
