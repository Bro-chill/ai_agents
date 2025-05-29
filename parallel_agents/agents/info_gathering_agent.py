# from pydantic_ai import Agent, RunContext
# from pydantic import BaseModel, Field
# from typing import Any, List, Dict, Optional, Union
# from dataclasses import dataclass
# import json
# import sys
# import os
# import re
# from datetime import datetime

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils import get_model

# model = get_model()

# # Dependencies type
# @dataclass
# class ScriptContext:
#     """Enhanced context for script analysis state"""
#     current_scene: Optional[str] = None
#     current_page: Optional[int] = None
#     characters_identified: List[str] = None
#     language: Optional[str] = None
#     script_title: Optional[str] = None
#     total_pages: Optional[int] = None
#     scene_count: int = 0
#     analysis_timestamp: Optional[datetime] = None
    
#     def __post_init__(self):
#         if self.characters_identified is None:
#             self.characters_identified = []
#         if self.analysis_timestamp is None:
#             self.analysis_timestamp = datetime.now()

# # State/Output type
# class CharacterInfo(BaseModel):
#     """Raw character data extracted from script"""
#     name: str = Field(description='Character name')
#     dialogue_lines: List[str] = Field(description='All dialogue lines for this character')
#     action_descriptions: List[str] = Field(description='Action lines involving this character')
#     first_appearance_page: Optional[int] = Field(description='Page of first appearance')
#     total_lines: int = Field(description='Total number of dialogue lines')

# class LocationInfo(BaseModel):
#     """Raw location data extracted from script"""
#     location_name: str = Field(description='Location name from scene header')
#     time_of_day: str = Field(description='Time setting (DAY/NIGHT/etc.)')
#     scene_description: str = Field(description='Full scene description text')
#     action_lines: List[str] = Field(description='All action lines in this location')
#     transitions: List[str] = Field(description='Scene transitions (CUT TO, FADE, etc.)')

# class TechnicalInfo(BaseModel):
#     """Raw technical elements extracted from script"""
#     camera_directions: List[str] = Field(description='All camera direction mentions')
#     lighting_mentions: List[str] = Field(description='Lighting-related text')
#     sound_mentions: List[str] = Field(description='Sound/audio mentions')
#     special_effects_mentions: List[str] = Field(description='VFX/special effects mentions')
#     technical_notes: List[str] = Field(description='Other technical directions')

# class PropsInfo(BaseModel):
#     """Raw props and costume data extracted from script"""
#     props_mentioned: List[str] = Field(description='All props mentioned in script')
#     costume_mentions: List[str] = Field(description='Costume/wardrobe mentions')
#     makeup_mentions: List[str] = Field(description='Makeup/prosthetics mentions')
#     set_pieces: List[str] = Field(description='Set pieces and decoration mentions')
#     vehicles: List[str] = Field(description='Vehicles mentioned')

# class SceneInfo(BaseModel):
#     """Raw scene structure data"""
#     scene_number: Optional[str] = Field(description='Scene number if present')
#     scene_header: str = Field(description='Full scene header text')
#     page_start: Optional[int] = Field(description='Starting page number')
#     page_end: Optional[int] = Field(description='Ending page number')
#     word_count: int = Field(description='Total word count')
#     dialogue_percentage: float = Field(description='Percentage of content that is dialogue')

# class RawScriptData(BaseModel):
#     """Complete raw data extracted from script - input for analysis agents"""
#     # Core extracted data
#     characters: List[CharacterInfo] = Field(description='All character data')
#     locations: List[LocationInfo] = Field(description='All location data')
#     technical_elements: TechnicalInfo = Field(description='Technical elements found')
#     props_elements: PropsInfo = Field(description='Props and costume elements')
#     scene_structure: SceneInfo = Field(description='Scene structure information')
    
#     # Raw text sections
#     full_script_text: str = Field(description='Complete script text')
#     dialogue_only: str = Field(description='All dialogue extracted')
#     action_only: str = Field(description='All action lines extracted')
    
#     # Metadata
#     language_detected: str = Field(description='Primary language detected')
#     script_format: str = Field(description='Script format type detected')
#     total_pages: Optional[int] = Field(description='Total page count')
#     extraction_timestamp: str = Field(description='When extraction was performed')

# # Tools
# def extract_characters_tool(ctx: RunContext[ScriptContext], script_content: str) -> str:
#     """Extract all character information from script"""
#     # Pattern for character names (usually in caps before dialogue)
#     character_pattern = r'^([A-Z][A-Z\s]+)(?:\s*\([^)]+\))?\s*$'
#     dialogue_pattern = r'^([A-Z][A-Z\s]+)(?:\s*\([^)]+\))?\s*\n(.+?)(?=\n[A-Z][A-Z\s]+|\n\n|\Z)'
    
#     lines = script_content.split('\n')
#     characters_data = {}
    
#     current_character = None
#     current_dialogue = []
    
#     for i, line in enumerate(lines):
#         line = line.strip()
#         if line and re.match(character_pattern, line):
#             # Save previous character's dialogue
#             if current_character and current_dialogue:
#                 if current_character not in characters_data:
#                     characters_data[current_character] = []
#                 characters_data[current_character].extend(current_dialogue)
            
#             # Start new character
#             current_character = re.sub(r'\s*\([^)]+\)', '', line).strip()
#             current_dialogue = []
#         elif current_character and line and not line.isupper():
#             # This is dialogue for current character
#             current_dialogue.append(line)
    
#     # Don't forget the last character
#     if current_character and current_dialogue:
#         if current_character not in characters_data:
#             characters_data[current_character] = []
#         characters_data[current_character].extend(current_dialogue)
    
#     ctx.deps.characters_identified = list(characters_data.keys())
#     return f"Extracted {len(characters_data)} characters with dialogue data"

# def extract_locations_tool(ctx: RunContext[ScriptContext], script_content: str) -> str:
#     """Extract all location and scene information"""
#     # Scene header patterns
#     scene_patterns = [
#         r'(INT\.|EXT\.)\s+(.+?)\s+-\s+(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING)',
#         r'(\d+\.?\s*)?(INT\.|EXT\.)\s+(.+?)\s+-\s+(DAY|NIGHT|DAWN|DUSK)',
#         r'(INTERIOR|EXTERIOR|INT|EXT)[\.\s]+(.+?)[\s\-]+(DAY|NIGHT)'
#     ]
    
#     locations_found = []
#     for pattern in scene_patterns:
#         matches = re.finditer(pattern, script_content, re.IGNORECASE | re.MULTILINE)
#         for match in matches:
#             locations_found.append({
#                 'header': match.group(0),
#                 'location': match.groups()[-2].strip(),
#                 'time': match.groups()[-1].strip(),
#                 'position': match.start()
#             })
    
#     return f"Extracted {len(locations_found)} scene locations"

# def extract_technical_elements_tool(ctx: RunContext[ScriptContext], script_content: str) -> str:
#     """Extract technical production elements"""
#     technical_patterns = {
#         'camera': [r'(CLOSE UP|MEDIUM SHOT|WIDE SHOT|PAN|TILT|ZOOM|DOLLY|TRACKING|POV|ANGLE)',
#                   r'(CU|MS|WS|ECU|EWS|MCU)'],
#         'lighting': [r'(FADE IN|FADE OUT|DIM|BRIGHT|SPOTLIGHT|SHADOW)',
#                     r'(LIGHTING|ILLUMINATED|DARK|BRIGHT)'],
#         'sound': [r'(SFX|SOUND|AUDIO|MUSIC|VOICE OVER|V\.O\.|O\.S\.)',
#                  r'(SILENCE|QUIET|LOUD|WHISPER|SHOUT)'],
#         'effects': [r'(VFX|CGI|SPECIAL EFFECT|EXPLOSION|FIRE|SMOKE)',
#                    r'(GREEN SCREEN|PRACTICAL EFFECT)']
#     }
    
#     found_elements = {}
#     for category, patterns in technical_patterns.items():
#         found_elements[category] = []
#         for pattern in patterns:
#             matches = re.findall(pattern, script_content, re.IGNORECASE)
#             found_elements[category].extend(matches)
    
#     total_found = sum(len(elements) for elements in found_elements.values())
#     return f"Extracted {total_found} technical elements across {len(found_elements)} categories"

# def extract_props_tool(ctx: RunContext[ScriptContext], script_content: str) -> str:
#     """Extract props, costumes, and physical elements"""
#     # Common prop/costume keywords
#     prop_patterns = [
#         r'\b(gun|weapon|sword|knife|phone|car|computer|book|glass|bottle|bag|briefcase)\b',
#         r'\b(costume|dress|suit|uniform|hat|glasses|jewelry|watch|shoes)\b',
#         r'\b(makeup|prosthetic|wig|mask|scar|tattoo)\b'
#     ]
    
#     props_found = []
#     for pattern in prop_patterns:
#         matches = re.findall(pattern, script_content, re.IGNORECASE)
#         props_found.extend(matches)
    
#     return f"Extracted {len(set(props_found))} unique props/costume elements"

# def detect_language_tool(ctx: RunContext[ScriptContext], text_sample: str) -> str:
#     """Detect primary language of script"""
#     malay_indicators = ['yang', 'dan', 'dengan', 'untuk', 'adalah', 'ini', 'itu', 'saya', 'kamu', 'dia']
#     english_indicators = ['the', 'and', 'with', 'for', 'is', 'this', 'that', 'you', 'he', 'she']
    
#     text_lower = text_sample.lower()
#     malay_count = sum(1 for word in malay_indicators if word in text_lower)
#     english_count = sum(1 for word in english_indicators if word in text_lower)
    
#     if malay_count > english_count:
#         ctx.deps.language = "Malay/Bahasa Malaysia"
#         return "Language detected: Malay/Bahasa Malaysia"
#     else:
#         ctx.deps.language = "English"
#         return "Language detected: English"

# # Prompt
# system_prompt = """
#     You are a script data extraction specialist. Your job is to extract and structure ALL raw data from the script without analysis or interpretation.

#     EXTRACTION TASKS:
#     1. **Character Data**: Extract all character names, their dialogue lines, and action descriptions
#     2. **Location Data**: Extract scene headers, locations, time settings, and scene descriptions  
#     3. **Technical Elements**: Find all camera directions, lighting notes, sound cues, and technical directions
#     4. **Props/Costumes**: Identify all mentioned props, costumes, makeup, set pieces, and vehicles
#     5. **Scene Structure**: Extract scene numbers, page counts, and structural elements
#     6. **Text Separation**: Separate dialogue from action lines

#     IMPORTANT:
#     - Extract everything mentioned, don't filter or analyze
#     - Preserve original text and context
#     - Don't make assumptions or interpretations
#     - Focus on completeness and accuracy
#     - Maintain character names exactly as written
#     - Include page references when available

#     Your output will be used by specialized analysis agents, so thoroughness is critical.
#     """

# # Agent
# info_gathering_agent = Agent(
#     model,
#     output_type=RawScriptData,
#     system_prompt=system_prompt
#     ,
#     deps_type=ScriptContext,
#     tools=[
#         extract_characters_tool,
#         extract_locations_tool, 
#         extract_technical_elements_tool,
#         extract_props_tool,
#         detect_language_tool
#     ],
#     retries=2
# )

# # Main extraction function
# async def extract_script_data(script_content: str, context: Optional[ScriptContext] = None) -> RawScriptData:
#     """
#     Extract all raw data from script content
    
#     Args:
#         script_content: Raw script text
#         context: Optional context for multi-page scripts
    
#     Returns:
#         RawScriptData: Structured raw data for analysis agents
#     """
#     if context is None:
#         context = ScriptContext()
    
#     try:
#         result = await info_gathering_agent.run(script_content, deps=context)
#         return result.output
#     except Exception as e:
#         print(f"Data extraction error: {e}")
#         raise

from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Optional
from dataclasses import dataclass
import sys
import os
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

# Dependencies/Context
@dataclass
class ScriptContext:
    """Simple context for script analysis"""
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()

# State/Output
class RawScriptData(BaseModel):
    """Simplified raw data extracted from script"""
    characters: List[str] = Field(description='List of character names found in script')
    locations: List[str] = Field(description='List of locations/scene headers found')
    dialogue_lines: List[str] = Field(description='Sample dialogue lines')
    action_lines: List[str] = Field(description='Sample action/description lines')
    language_detected: str = Field(description='Primary language detected')
    script_length: int = Field(description='Total character count')
    estimated_pages: int = Field(description='Estimated page count')
    scene_count: int = Field(description='Number of scenes detected')

# Prompt
system_prompt = """
You are a script analysis expert. Extract key information from the provided script.

Extract and return:
1. Character names (anyone who speaks)
2. Locations (INT./EXT. scene headers)
3. A few sample dialogue lines
4. A few sample action lines
5. Primary language (English/Malay)
6. Basic script statistics

Be thorough but concise. Focus on accuracy over completeness.
"""

# Agent
info_gathering_agent = Agent(
    model,
    output_type=RawScriptData,
    system_prompt=system_prompt,
    deps_type=ScriptContext,
    retries=2
)

# Function (to extract data and pass to state)
async def extract_script_data(script_content: str) -> RawScriptData:
    """Extract raw data from script content"""
    context = ScriptContext()
    
    try:
        # Limit script content to avoid token limits
        limited_content = script_content[:8000] if len(script_content) > 8000 else script_content
        
        result = await info_gathering_agent.run(limited_content, deps=context)
        return result.output
        
    except Exception as e:
        print(f"Pydantic AI extraction failed: {e}")
        # Fallback to manual extraction
        return _manual_extract_script_data(script_content)

def _manual_extract_script_data(script_content: str) -> RawScriptData:
    """Fallback manual extraction using regex"""
    lines = script_content.split('\n')
    
    characters = set()
    locations = []
    dialogue_lines = []
    action_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract locations (scene headers)
        if re.match(r'^(INT\.|EXT\.)', line, re.IGNORECASE):
            locations.append(line)
        
        # Extract character names (all caps, not scene headers)
        elif (line.isupper() and 
              len(line.split()) <= 3 and 
              not line.startswith(('INT.', 'EXT.', 'FADE', 'CUT', 'DISSOLVE')) and
              not re.match(r'^[A-Z\s]+(DAY|NIGHT)', line)):
            
            clean_name = re.sub(r'\s*\([^)]*\)', '', line).strip()
            if clean_name and len(clean_name) > 1:
                characters.add(clean_name)
        
        # Collect sample dialogue and action lines
        elif not line.isupper() and len(dialogue_lines) < 5:
            if any(char in line.lower() for char in ['said', 'says', '"', "'"]):
                dialogue_lines.append(line[:100])  # Limit length
            elif len(action_lines) < 5:
                action_lines.append(line[:100])
    
    # Detect language
    text_lower = script_content.lower()
    malay_words = ['yang', 'dan', 'dengan', 'untuk', 'adalah', 'ini', 'itu', 'saya']
    english_words = ['the', 'and', 'with', 'for', 'is', 'this', 'that', 'you']
    
    malay_count = sum(1 for word in malay_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    language = "Malay" if malay_count > english_count else "English"
    
    return RawScriptData(
        characters=list(characters),
        locations=locations,
        dialogue_lines=dialogue_lines,
        action_lines=action_lines,
        language_detected=language,
        script_length=len(script_content),
        estimated_pages=max(1, len(script_content) // 250),
        scene_count=len(locations)
    )