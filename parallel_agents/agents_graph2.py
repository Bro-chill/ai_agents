from typing import Optional, Dict, Any, List, Annotated
from pydantic import BaseModel, Field
from dataclasses import dataclass
from langgraph.graph import StateGraph, START, END
from typing import Literal, Dict, Any
import asyncio
from datetime import datetime
import inspect

# Import Agents
from agents.info_gathering_agent import RawScriptData
from agents.cost_analysis_agent import CostBreakdown
from agents.props_extraction_agent import PropsBreakdown
from agents.location_analysis_agent import LocationBreakdown
from agents.character_analysis_agent import CharacterBreakdown
from agents.scene_breakdown_agent import SceneBreakdown
from agents.timeline_agent import TimelineBreakdown

# Import agents result
from agents.info_gathering_agent import extract_script_data
from agents.cost_analysis_agent import analyze_costs
from agents.props_extraction_agent import analyze_props
from agents.location_analysis_agent import analyze_locations
from agents.character_analysis_agent import analyze_characters
from agents.scene_breakdown_agent import analyze_scenes
from agents.timeline_agent import analyze_timeline

# Custom reducers for handling concurrent updates
def merge_metadata(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Merge metadata dictionaries"""
    if not left:
        return right
    if not right:
        return left
    return {**left, **right}

def merge_analyses_complete(left: Dict[str, bool], right: Dict[str, bool]) -> Dict[str, bool]:
    """Merge analyses completion status"""
    if not left:
        return right
    if not right:
        return left
    return {**left, **right}

def merge_errors(left: List[str], right: List[str]) -> List[str]:
    """Merge error lists"""
    if not left:
        return right
    if not right:
        return left
    return left + right

def merge_strings(left: Optional[str], right: Optional[str]) -> Optional[str]:
    """Merge strings - take the most recent non-None value"""
    if right is not None:
        return right
    return left

def merge_bools(left: bool, right: bool) -> bool:
    """Merge booleans - use OR logic"""
    return left or right

# State/Output type
class ScriptAnalysisState(BaseModel):
    """State for script analysis workflow"""
    # Input - this should only be set once at the beginning
    script_content: str = Field(description="Original script content")
    
    # Current workflow state - use Annotated to handle concurrent updates
    current_agent: Annotated[Optional[str], merge_strings] = Field(default=None, description="Currently running agent")
    task_complete: Annotated[bool, merge_bools] = Field(default=False, description="Whether analysis is complete")
    
    # Phase 1: Raw data extraction - only set once by info_gathering
    raw_data: Optional[RawScriptData] = Field(default=None, description="Extracted raw script data")
    extraction_complete: bool = Field(default=False, description="Whether extraction is complete")
    
    # Phase 2: Analysis results - each set by individual nodes
    cost_analysis: Optional[CostBreakdown] = Field(default=None, description="Cost analysis results")
    props_analysis: Optional[PropsBreakdown] = Field(default=None, description="Props analysis results")
    location_analysis: Optional[LocationBreakdown] = Field(default=None, description="Location analysis results")
    character_analysis: Optional[CharacterBreakdown] = Field(default=None, description="Character analysis results")
    scene_analysis: Optional[SceneBreakdown] = Field(default=None, description="Scene analysis results")
    timeline_analysis: Optional[TimelineBreakdown] = Field(default=None, description="Timeline analysis results")
    
    # Analysis completion tracking - use custom reducer
    analyses_complete: Annotated[Dict[str, bool], merge_analyses_complete] = Field(
        default_factory=lambda: {
            "cost": False,
            "props": False,
            "location": False,
            "character": False,
            "scene": False,
            "timeline": False
        },
        description="Track completion of each analysis type"
    )
    
    # Metadata - use custom reducer
    processing_metadata: Annotated[Dict[str, Any], merge_metadata] = Field(
        default_factory=dict, 
        description="Processing information"
    )
    
    # Errors - use custom reducer
    errors: Annotated[List[str], merge_errors] = Field(
        default_factory=list, 
        description="Any errors encountered"
    )

# Dependencies
@dataclass
class ScriptAnalysisDeps:
    """Dependencies for script analysis agents"""
    script_content: str
    max_retries: int = 3
    timeout_seconds: int = 300

# Helper functions
def extract_result(result: Any) -> Any:
    """Helper function to extract actual result from agent response"""
    if hasattr(result, 'output'):
        return result.output
    elif hasattr(result, 'data'):
        return result.data
    else:
        return result

async def safe_call_agent(agent_func, *args, **kwargs):
    """Safely call an agent function, ensuring it runs asynchronously"""
    try:
        # Check if function is already a coroutine function
        if inspect.iscoroutinefunction(agent_func):
            return await agent_func(*args, **kwargs)
        
        # Check if it's a callable that might return a coroutine
        elif callable(agent_func):
            result = agent_func(*args, **kwargs)
            
            # If the result is a coroutine, await it
            if inspect.iscoroutine(result):
                return await result
            
            # If it's not a coroutine, it's a blocking call - run in thread
            else:
                # We need to call the function again in the thread
                return await asyncio.to_thread(agent_func, *args, **kwargs)
        
        else:
            # Fallback: run in thread
            return await asyncio.to_thread(agent_func, *args, **kwargs)
            
    except Exception as e:
        print(f"Error in safe_call_agent: {str(e)}")
        raise e

# Node functions
async def run_info_gathering(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run the info gathering agent to extract raw data."""
    print("🔍 Phase 1: Extracting raw data from script...")
    start_time = datetime.now()
    
    try:
        # Extract raw data using the info gathering agent
        raw_data = await safe_call_agent(extract_script_data, state.script_content)
        
        extraction_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Data extraction completed in {extraction_time:.2f} seconds")
        if raw_data:
            print(f"   - Characters found: {len(raw_data.characters) if hasattr(raw_data, 'characters') else 0}")
            print(f"   - Locations found: {len(raw_data.locations) if hasattr(raw_data, 'locations') else 0}")
            print(f"   - Language detected: {getattr(raw_data, 'language_detected', 'Unknown')}")
        
        # Return only the fields this node should update
        return {
            "current_agent": "info_gathering",
            "raw_data": raw_data,
            "extraction_complete": True,
            "processing_metadata": {
                "extraction_time_seconds": extraction_time,
                "extraction_timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        error_msg = f"Error in info gathering: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "info_gathering",
            "errors": [error_msg],
            "extraction_complete": False
        }

async def run_cost_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run cost analysis."""
    print("💰 Running cost analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for cost analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_costs, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Cost analysis completed")
        
        return {
            "current_agent": "cost_analysis",
            "cost_analysis": actual_result,
            "analyses_complete": {"cost": True}
        }
        
    except Exception as e:
        error_msg = f"Error in cost analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "cost_analysis",
            "errors": [error_msg]
        }

async def run_props_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run props analysis."""
    print("🎭 Running props analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for props analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_props, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Props analysis completed")
        
        return {
            "current_agent": "props_analysis",
            "props_analysis": actual_result,
            "analyses_complete": {"props": True}
        }
        
    except Exception as e:
        error_msg = f"Error in props analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "props_analysis",
            "errors": [error_msg]
        }

async def run_location_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run location analysis."""
    print("📍 Running location analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for location analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_locations, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Location analysis completed")
        
        return {
            "current_agent": "location_analysis",
            "location_analysis": actual_result,
            "analyses_complete": {"location": True}
        }
        
    except Exception as e:
        error_msg = f"Error in location analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "location_analysis",
            "errors": [error_msg]
        }

async def run_character_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run character analysis."""
    print("👥 Running character analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for character analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_characters, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Character analysis completed")
        
        return {
            "current_agent": "character_analysis",
            "character_analysis": actual_result,
            "analyses_complete": {"character": True}
        }
        
    except Exception as e:
        error_msg = f"Error in character analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "character_analysis",
            "errors": [error_msg]
        }

async def run_scene_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run scene analysis."""
    print("🎬 Running scene analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for scene analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_scenes, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Scene analysis completed")
        
        return {
            "current_agent": "scene_analysis",
            "scene_analysis": actual_result,
            "analyses_complete": {"scene": True}
        }
        
    except Exception as e:
        error_msg = f"Error in scene analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "scene_analysis",
            "errors": [error_msg]
        }

async def run_timeline_analysis(state: ScriptAnalysisState) -> Dict[str, Any]:
    """Run timeline analysis."""
    print("⏰ Running timeline analysis...")
    
    if not state.raw_data:
        error_msg = "No raw data available for timeline analysis"
        print(f"❌ {error_msg}")
        return {
            "errors": [error_msg]
        }
    
    try:
        result = await safe_call_agent(analyze_timeline, state.raw_data)
        actual_result = extract_result(result)
        
        print("✅ Timeline analysis completed")
        
        return {
            "current_agent": "timeline_analysis",
            "timeline_analysis": actual_result,
            "analyses_complete": {"timeline": True}
        }
        
    except Exception as e:
        error_msg = f"Error in timeline analysis: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "current_agent": "timeline_analysis",
            "errors": [error_msg]
        }
# Define graph
def create_script_analysis_workflow():
    """Create and return the script analysis workflow."""
    # Create the graph
    workflow = StateGraph(ScriptAnalysisState)
    
    # Add nodes to the graph - using unique names to avoid conflicts
    workflow.add_node("info_gathering", run_info_gathering)
    workflow.add_node("cost_node", run_cost_analysis)
    workflow.add_node("props_node", run_props_analysis)
    workflow.add_node("location_node", run_location_analysis)
    workflow.add_node("character_node", run_character_analysis)
    workflow.add_node("scene_node", run_scene_analysis)
    workflow.add_node("timeline_node", run_timeline_analysis)
    
    # Add edges - info_gathering runs first, then all analyses run in parallel
    workflow.add_edge(START, "info_gathering")
    workflow.add_edge("info_gathering", "cost_node")
    workflow.add_edge("info_gathering", "props_node")
    workflow.add_edge("info_gathering", "location_node")
    workflow.add_edge("info_gathering", "character_node")
    workflow.add_edge("info_gathering", "scene_node")
    workflow.add_edge("info_gathering", "timeline_node")
    workflow.add_edge("cost_node", END)
    workflow.add_edge("props_node", END)
    workflow.add_edge("location_node", END)
    workflow.add_edge("character_node", END)
    workflow.add_edge("scene_node", END)
    workflow.add_edge("timeline_node", END)
    
    # Compile the graph
    return workflow.compile()

# Create the compiled graph for LangGraph Studio
analyze_script_workflow = create_script_analysis_workflow()


async def run_analyze_script_workflow(script_content: str) -> ScriptAnalysisState:
    """Run the complete script analysis workflow."""
    print("🎬 Starting Script Analysis Workflow")
    print("=" * 50)
    
    # Initialize state
    initial_state = ScriptAnalysisState(
        script_content=script_content,
        processing_metadata={
            "workflow_start_time": datetime.now().isoformat()
        }
    )
    
    # Execute the workflow
    try:
        final_state = await analyze_script_workflow.ainvoke(initial_state)
        
        print("\n" + "=" * 50)
        print("🎉 Script Analysis Workflow Completed!")
        
        # Calculate summary statistics
        successful_analyses = sum(1 for completed in final_state.analyses_complete.values() if completed)
        failed_analyses = len(final_state.analyses_complete) - successful_analyses
        
        # Calculate total time
        start_time_str = final_state.processing_metadata.get("workflow_start_time")
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
            total_time = (datetime.now() - start_time).total_seconds()
        else:
            total_time = final_state.processing_metadata.get("extraction_time_seconds", 0)
        
        print(f"📊 Summary:")
        print(f"   - Total processing time: {total_time:.2f} seconds")
        print(f"   - Successful analyses: {successful_analyses}")
        print(f"   - Failed analyses: {failed_analyses}")
        print(f"   - Extraction completed: {final_state.extraction_complete}")
        print(f"   - Task completed: {final_state.task_complete}")
        
        if final_state.errors:
            print(f"⚠️  Errors encountered: {len(final_state.errors)}")
            for error in final_state.errors:
                print(f"   - {error}")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        raise


async def main():
    """Main function to demonstrate the workflow."""
    
    sample_script = """
    INT. COFFEE SHOP - DAY
    
    SARAH, 25, sits at a corner table with her laptop. She nervously checks her phone.
    
    SARAH
    (into phone)
    I can't do this anymore, Mom. The pressure is killing me.
    
    The BARISTA, 20s, approaches with a steaming cup.
    
    BARISTA
    One large coffee, extra shot.
    
    SARAH
    Thanks.
    
    Sarah's phone BUZZES. She looks at the screen - "BOSS CALLING"
    
    SARAH (CONT'D)
    (answering)
    Hello, Mr. Peterson?
    
    CUT TO:
    
    EXT. CITY STREET - DAY
    
    MIKE, 30, walks briskly down the sidewalk, talking on his phone.
    
    MIKE
    The deal fell through. We need a backup plan.
    
    A BLACK SUV pulls up beside him. Two MEN in suits get out.
    
    MIKE (CONT'D)
    (panicked)
    I have to go.
    
    Mike hangs up and starts running.
    """
    
    # Run script analysis
    result = await run_analyze_script_workflow(sample_script)
    
    # Display detailed results
    print("\n" + "=" * 60)
    print("📋 DETAILED RESULTS")
    print("=" * 60)
    
    if result.cost_analysis:
        print(f"\n💰 COST ANALYSIS:")
        print(f"   Budget Range: {getattr(result.cost_analysis, 'estimated_budget_range', 'N/A')}")
        print(f"   Shoot Days: {getattr(result.cost_analysis, 'estimated_shoot_days', 'N/A')}")
        print(f"   Crew Size: {getattr(result.cost_analysis, 'crew_size_recommendation', 'N/A')}")
    
    if result.character_analysis:
        print(f"\n👥 CHARACTER ANALYSIS:")
        main_chars = getattr(result.character_analysis, 'main_characters', {})
        supporting_chars = getattr(result.character_analysis, 'supporting_characters', {})
        print(f"   Main Characters: {list(main_chars.keys()) if main_chars else 'N/A'}")
        print(f"   Supporting Characters: {list(supporting_chars.keys()) if supporting_chars else 'N/A'}")
    
    if result.location_analysis:
        print(f"\n📍 LOCATION ANALYSIS:")
        locations_by_type = getattr(result.location_analysis, 'locations_by_type', {})
        for loc_type, locations in locations_by_type.items():
            print(f"   {loc_type}: {locations}")
    
    if result.props_analysis:
        print(f"\n🎭 PROPS ANALYSIS:")
        props_by_category = getattr(result.props_analysis, 'props_by_category', {})
        for category, props in props_by_category.items():
            if props:  # Only show non-empty categories
                print(f"   {category}: {props}")
    
    if result.timeline_analysis:
        print(f"\n⏰ TIMELINE ANALYSIS:")
        schedule = getattr(result.timeline_analysis, 'shooting_schedule_estimate', 'N/A')
        print(f"   Shooting Schedule: {schedule}")


if __name__ == "__main__":
    asyncio.run(main())