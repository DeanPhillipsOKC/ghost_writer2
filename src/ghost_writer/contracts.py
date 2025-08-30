from typing import Dict, List, Literal
from pydantic import BaseModel


class CharacterCard(BaseModel):
    id: str
    name: str
    role: Literal["protagonist", "deuteragonist", "antagonist", "supporting"]
    voice: str
    look: str
    desires: str
    flaws: str
    first_appearance_chapter: int

class ContinuityFact(BaseModel):
    id: str
    text: str
    tags: List[str] = []

class StoryBible(BaseModel):
    title: str
    logline: str
    tone: str
    themes: List[str]
    world_rules: str
    locations: List[str]
    characters: Dict[str, CharacterCard] # key = character id
    continuity: List[ContinuityFact]
    prose_style: str
    art_style: str