# reason_graph/schemas.py

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# --- Pydantic Schemas Mirroring Zod Schemas from original JS ---

class SearchQuery(BaseModel):
    """Represents a single search query within the research plan."""
    query: str = Field(description="The specific search query string.")
    rationale: str = Field(description="The reasoning behind why this query is important.")
    source: Literal['web', 'academic', 'x', 'all'] = Field(description="The source type(s) to search.")
    priority: int = Field(description="Priority of the query (e.g., 2-4, lower means higher priority).")

class RequiredAnalysis(BaseModel):
    """Represents a required analysis step in the research plan."""
    type: str = Field(description="The type of analysis to perform (e.g., 'SWOT', 'Comparative', 'Sentiment').")
    description: str = Field(description="A brief description of what the analysis should cover.")
    importance: int = Field(description="Importance score (e.g., 1-5, higher means more important).")

class ResearchPlan(BaseModel):
    """The overall research plan generated by the LLM."""
    search_queries: List[SearchQuery] = Field(
        description="List of targeted search queries.",
    )
    required_analyses: List[RequiredAnalysis] = Field(
        description="List of key analyses to perform on the search results.",
    )

class SearchResultItem(BaseModel):
    """Represents a single item returned from a search API."""
    source: Literal['web', 'academic', 'x'] = Field(description="The type of source the result came from.")
    title: str = Field(description="The title of the search result.")
    url: str = Field(description="The URL of the search result.")
    content: str = Field(description="The content snippet or summary of the result.")
    tweetId: Optional[str] = Field(default=None, description="The ID of the tweet, if the source is 'x'.")

class SearchStepResult(BaseModel):
    """Holds the results obtained from executing a single search step."""
    type: Literal['web', 'academic', 'x'] = Field(description="The type of search performed for this step.")
    query: SearchQuery = Field(description="The original SearchQuery object that prompted this search.")
    results: List[SearchResultItem] = Field(description="The list of results found for this search step.")

class AnalysisFinding(BaseModel):
    """Represents a single finding from an analysis step."""
    insight: str = Field(description="The core insight or finding discovered.")
    evidence: List[str] = Field(description="List of supporting evidence (e.g., brief quotes, source references).")
    confidence: float = Field(description="Confidence score in the finding (0.0 to 1.0).")

class AnalysisResult(BaseModel):
    """The structured output of a single analysis performed by the LLM."""
    findings: List[AnalysisFinding] = Field(description="List of key findings from the analysis.")
    implications: List[str] = Field(description="Potential implications of the findings.")
    limitations: List[str] = Field(description="Limitations noted during this specific analysis.")

class Limitation(BaseModel):
    """Describes a limitation identified during the gap analysis phase."""
    type: str = Field(description="The type of limitation (e.g., 'Source Bias', 'Data Scarcity').")
    description: str = Field(description="Detailed description of the limitation.")
    severity: int = Field(description="Severity score (e.g., 2-10, higher means more severe).")
    potential_solutions: List[str] = Field(description="Suggested ways to mitigate or address the limitation.")

class KnowledgeGap(BaseModel):
    """Describes a knowledge gap identified during the gap analysis phase."""
    topic: str = Field(description="The specific topic or area where knowledge is lacking.")
    reason: str = Field(description="The reason why this gap exists or is significant.")
    additional_queries: List[str] = Field(description="Specific queries suggested to help fill this gap.")

class RecommendedFollowup(BaseModel):
    """Describes a recommended follow-up action from the gap analysis."""
    action: str = Field(description="The suggested follow-up action.")
    rationale: str = Field(description="The reasoning behind recommending this action.")
    priority: int = Field(description="Priority score for the follow-up action (e.g., 2-10).")

class GapAnalysisResult(BaseModel):
    """The structured output of the gap analysis phase."""
    limitations: List[Limitation] = Field(description="List of identified limitations in the research.")
    knowledge_gaps: List[KnowledgeGap] = Field(description="List of identified knowledge gaps.")
    recommended_followup: List[RecommendedFollowup] = Field(description="List of recommended follow-up actions.")

class KeyFinding(BaseModel):
    """Represents a key finding in the final synthesis report."""
    finding: str = Field(description="The synthesized key finding or conclusion.")
    confidence: float = Field(description="Overall confidence in this finding (0.0 to 1.0).")
    supporting_evidence: List[str] = Field(description="List of key pieces of evidence supporting the finding (e.g., references to specific search results or analyses).")

class FinalSynthesisResult(BaseModel):
    """The structured output of the final synthesis phase (only in 'advanced' depth)."""
    key_findings: List[KeyFinding] = Field(description="List of synthesized key findings from all research.")
    remaining_uncertainties: List[str] = Field(description="List of questions or uncertainties that remain after the research.")


# --- Helper Schemas for Graph State and Streaming ---

class StepInfo(BaseModel):
    """Helper schema to store planned step information in the state."""
    id: str = Field(description="Unique ID for the step.")
    type: str = Field(description="Type of step ('web', 'academic', 'x', 'analysis').")
    details: Dict[str, Any] = Field(description="Holds the original query or analysis object details.")


class StreamUpdateData(BaseModel):
    """Data payload for a single streaming update message."""
    id: str = Field(description="Unique ID for the step or phase this update refers to.")
    type: str = Field(description="Type of the step or phase ('plan', 'web', 'academic', 'x', 'analysis', 'progress', 'error').")
    status: Literal['running', 'completed'] = Field(description="Current status of the step/phase.")
    title: str = Field(description="Display title for the update.")
    message: str = Field(description="Descriptive message about the current status or result.")
    timestamp: float = Field(description="Timestamp when the update was generated (epoch time).")
    overwrite: Optional[bool] = Field(default=False, description="Whether this update should replace a previous one with the same ID in the UI.")
    # Optional fields depending on the update type and status
    plan: Optional[ResearchPlan] = Field(default=None, description="The research plan (used in 'plan completed' update).")
    totalSteps: Optional[int] = Field(default=None, description="Total number of steps planned for the research.")
    query: Optional[str] = Field(default=None, description="The query string for search steps.")
    results: Optional[List[SearchResultItem]] = Field(default=None, description="Search results (used in 'search completed' updates).")
    analysisType: Optional[str] = Field(default=None, description="The type of analysis being performed or completed.")
    # Use Dict for findings in stream update for simplicity, full Pydantic models are in state
    findings: Optional[List[Dict]] = Field(default=None, description="Analysis findings (simplified for streaming).")
    gaps: Optional[List[KnowledgeGap]] = Field(default=None, description="Identified knowledge gaps.")
    recommendations: Optional[List[RecommendedFollowup]] = Field(default=None, description="Follow-up recommendations.")
    uncertainties: Optional[List[str]] = Field(default=None, description="Remaining uncertainties from final synthesis.")
    completedSteps: Optional[int] = Field(default=None, description="Number of steps completed so far.")
    isComplete: Optional[bool] = Field(default=None, description="Flag indicating if the entire research process is complete.")

class StreamUpdate(BaseModel):
    """Wrapper for the streaming update message, matching the original JS structure."""
    type: Literal['research_update'] = Field(default='research_update')
    data: StreamUpdateData = Field(description="The actual data payload for the update.")