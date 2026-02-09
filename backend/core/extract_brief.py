import os
import json
import sys
import time
import yaml
from typing import List, Optional, Dict, Any, Literal
from pathlib import Path

from pydantic import BaseModel, field_validator
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda

ALLOWED_PRIMARY_METHODOLOGIES = {
    "conjoint",
    "maxdiff",
    "concept_test",
    "discrete_choice",
    "message_test",
    "pricing_study",
    "segmentation",
    "tracking",
    "descriptive",
}

FOUNDATIONAL_SKILLS = {"screening", "rating-scales", "demographics"}

# LangSmith observability
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = "Basics"  # Force override

# Verify LangSmith API key is available
if os.environ.get("LANGCHAIN_TRACING_V2") == "true" and not os.environ.get("LANGCHAIN_API_KEY"):
    print("⚠ Warning: LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is not set. Tracing will not work.")


def load_skills_metadata(skills_dir: Path = Path("skills")) -> List[Dict[str, str]]:
    """
    Load skill metadata from all SKILL.md files in skills directory.
    
    Scans the skills directory for .md files and extracts YAML frontmatter
    containing name and description fields.
    
    Args:
        skills_dir: Path to skills directory (default: ./skills)
    
    Returns:
        List of {name, description, path} dicts for skill discovery
    """
    skills = []
    
    if not skills_dir.exists():
        print(f"Warning: Skills directory not found: {skills_dir}")
        return skills
    
    # Look for any .md files in skills directory (flat structure)
    for skill_path in skills_dir.glob("*.md"):
        try:
            content = skill_path.read_text(encoding="utf-8")
            
            # Extract YAML frontmatter (between --- markers)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])  # Use PyYAML
                    
                    skills.append({
                        "name": metadata.get("name", skill_path.stem),
                        "description": metadata.get("description", ""),
                        "path": str(skill_path)
                    })
        except Exception as e:
            print(f"Warning: Could not load skill from {skill_path}: {e}")
            continue
    
    return skills


class MarketContext(BaseModel):
    """Competitive and category context."""
    client_brand: Optional[str] = None
    competitor_brands: List[str] = []
    category: Optional[str] = None
    market: Optional[str] = None


class StimulusContent(BaseModel):
    """Individual stimulus description from the brief."""
    label: str
    description: Optional[str] = None


class Operational(BaseModel):
    """Practical execution requirements."""
    target_loi_minutes: Optional[int] = None
    fieldwork_mode: Optional[str] = None
    market_specifics: Optional[str] = None
    quality_controls: Optional[List[str]] = None
    constraints: Optional[str] = None


class StimuliDetails(BaseModel):
    stimuli_type: Optional[str] = None
    stimuli_count: Optional[str] = None
    stimuli_format: Optional[str] = None
    stimuli_content: Optional[List[StimulusContent]] = None

    @field_validator("stimuli_type", "stimuli_count", "stimuli_format", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class AttributeLevel(BaseModel):
    """Represents an attribute with its levels for conjoint/attribute testing."""
    attribute_name: str
    level_count: Optional[str] = None
    levels: Optional[List[str]] = None


class QuotaGroup(BaseModel):
    label: str
    min: Optional[int] = None
    max: Optional[int] = None
    proportion: Optional[float] = None


class Quota(BaseModel):
    attribute: str
    type: Literal["hard", "soft"]
    groups: List[QuotaGroup]


class StudyDesign(BaseModel):
    """Study design details (no longer includes study_type - moved to top level)."""
    stimuli_details: Optional[StimuliDetails] = None
    exposure_design: Optional[str] = None
    comparison_intent: Optional[str] = None
    respondent_splitting: Optional[str] = None
    attribute_testing: Optional[List[AttributeLevel]] = None

    @field_validator(
        "exposure_design",
        "comparison_intent",
        "respondent_splitting",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class MeasurementGuidance(BaseModel):
    measurement_priority: Optional[str] = None
    required_outputs: Optional[List[str]] = None
    segmentation_intent: Optional[str] = None
    benchmarking: Optional[str] = None

    @field_validator("measurement_priority", "segmentation_intent", "benchmarking", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class ProblemFrame(BaseModel):
    decision_stage: Optional[
        Literal[
            "discover",
            "define",
            "design",
            "validate",
            "measure",
            "optimize",
            "unknown",
        ]
    ] = "unknown"
    primary_problem: Optional[
        Literal[
            "unknown_needs",
            "idea_selection",
            "tradeoff_optimization",
            "experience_breakdown",
            "launch_risk",
            "performance_tracking",
            "decline_diagnosis",
            "opinion_measurement",
            "other",
            "unknown",
        ]
    ] = "unknown"
    decision_risk_level: Optional[Literal["high", "medium", "low", "unknown"]] = "unknown"


class BriefExtraction(BaseModel):
    """
    Structured extraction from research brief.
    
    Core fields (required):
        objective: Primary research goal
        target_audience: Who the research targets
        key_dimensions: Array of topics/attributes to measure
    
    Study classification (new):
        study_type: Broad category (e.g., "new_product_development")
        primary_methodology: Specific method (e.g., "conjoint")
        secondary_objectives: Supporting elements (e.g., ["usage_attitudes"])
        skills: Skills to load for generation (e.g., ["conjoint", "pricing-study"])
    
    Optional details:
        study_design: How the study is structured
        measurement_guidance: Analysis priorities
        constraints: Practical limitations
    """
    # Core fields (required)
    objective: str
    target_audience: str
    key_dimensions: List[str]
    
    # Market context
    market_context: Optional[MarketContext] = None
    
    # Sample design
    total_sample_size: Optional[int] = None
    
    # Study classification (new top-level fields)
    study_type: Optional[str] = None
    primary_methodology: Optional[str] = None
    secondary_objectives: List[str] = []
    skills: List[str] = []
    
    # Optional details
    study_design: Optional[StudyDesign] = None
    measurement_guidance: Optional[MeasurementGuidance] = None
    problem_frame: Optional[ProblemFrame] = None
    quotas: Optional[List[Quota]] = None
    
    # Operational (replaces top-level constraints)
    operational: Optional[Operational] = None

    @field_validator("objective", "target_audience")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()

    @field_validator("key_dimensions")
    @classmethod
    def validate_key_dimensions(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("must contain at least one item")
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if not cleaned:
            raise ValueError("must contain at least one non-empty string")
        return cleaned
    
    @field_validator("secondary_objectives", "skills")
    @classmethod
    def validate_string_arrays(cls, value: Any) -> List[str]:
        """Ensure arrays are always lists, even if empty."""
        if value is None:
            return []
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if item]

    @field_validator("primary_methodology", mode="before")
    @classmethod
    def normalize_primary_methodology(cls, value: Any) -> str:
        if value is None:
            return "descriptive"
        text = str(value).strip().lower()
        if not text or text not in ALLOWED_PRIMARY_METHODOLOGIES:
            return "descriptive"
        return text
    
    @field_validator("quotas", mode="before")
    @classmethod
    def normalize_quotas(cls, value: Any) -> Optional[List]:
        if value is None:
            return None
        if not isinstance(value, list) or len(value) == 0:
            return None
        return value


def add_foundational_and_dependencies(
    llm_selected_skills: List[str],
    valid_skill_names: set,
    skills_dir: Path = Path("skills")
) -> List[str]:
    """
    Add foundational skills and required dependencies to LLM-selected skills.
    
    This ensures that:
    1. Foundational skills (screening, rating-scales, demographics) are included when needed
    2. Required dependencies from skill metadata are satisfied
    
    Args:
        llm_selected_skills: Skills selected by the LLM
        valid_skill_names: Set of all valid skill names
        skills_dir: Path to skills directory
    
    Returns:
        Complete list of skills with foundations and dependencies
    """
    final_skills = list(llm_selected_skills)  # Start with LLM selections
    
    # 1. Add foundational skills
    for foundation in ["screening", "rating-scales"]:
        if foundation in valid_skill_names and foundation not in final_skills:
            final_skills.append(foundation)
    
    # 2. Add required dependencies by reading skill metadata
    skills_to_check = list(final_skills)
    for skill_name in skills_to_check:
        skill_path = skills_dir / f"{skill_name}.md"
        if not skill_path.exists():
            continue
        
        try:
            content = skill_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    requires = metadata.get("requires", [])
                    
                    for req in requires:
                        if req in valid_skill_names and req not in final_skills:
                            final_skills.append(req)
        except Exception as e:
            print(f"Warning: Could not load requirements for {skill_name}: {e}")
            continue
    
    return final_skills


def strip_task_plan(text) -> str:
    """Strip TASK_PLAN block before JSON, handling both raw strings and AIMessage."""
    if hasattr(text, 'content'):
        text = text.content
    # Find the first { which starts the JSON
    idx = text.find('{')
    if idx > 0:
        text = text[idx:]
    # Find the last } to trim any trailing text
    ridx = text.rfind('}')
    if ridx >= 0:
        text = text[:ridx + 1]
    return text


class BriefExtractor:
    """Model-agnostic brief extractor with streaming support and skills integration."""

    def __init__(self, llm=None, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.0):
        """
        Initialize with any LangChain-compatible LLM.

        Args:
            llm: Pre-configured LLM instance (optional). If provided, model_name is ignored.
            model_name: Model identifier if llm not provided
            temperature: Temperature setting if llm not provided
        """
        if llm is not None:
            self.llm = llm
        else:
            self.llm = init_chat_model(model=model_name, temperature=temperature)

        self.parser = JsonOutputParser(pydantic_object=BriefExtraction)
        
        # Load available skills metadata
        self.available_skills = load_skills_metadata()
        print(f"Loaded {len(self.available_skills)} available skills")
        
        self.prompt = self._load_prompt()
        self.chain = self.prompt | self.llm | RunnableLambda(strip_task_plan) | self.parser

    def _load_prompt(self) -> ChatPromptTemplate:
        """Load prompt template and add parser format instructions + skills list."""
        prompt_path = Path("prompt_template.txt")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        template_text = prompt_path.read_text(encoding="utf-8")
        template_with_format = f"{template_text}\n\n{{format_instructions}}"
        prompt = ChatPromptTemplate.from_template(template_with_format)

        return prompt.partial(
            format_instructions=self.parser.get_format_instructions(),
            available_skills=self._format_skills_for_prompt()
        )
    
    def _format_skills_for_prompt(self) -> str:
        """Format skills as bulleted list for prompt injection."""
        if not self.available_skills:
            return "No skills currently available."
        
        lines = ["Available survey methodology skills:"]
        for skill in self.available_skills:
            lines.append(f"- **{skill['name']}**: {skill['description']}")
        return "\n".join(lines)

    def extract(self, brief_text: str, stream_output: bool = False) -> Optional[dict]:
        """
        Main extraction method.
        
        Uses LLM to select skills based on enhanced metadata descriptions,
        then adds foundational skills and dependencies automatically.
        """
        if stream_output:
            result = self._extract_streaming(brief_text)
        else:
            result = self._extract_non_streaming(brief_text)
        
        # Post-process skills
        if result and "skills" in result:
            valid_skill_names = {s["name"] for s in self.available_skills}
            llm_selected = result["skills"]
            
            # Validate LLM selections
            valid_llm_skills = [
                skill for skill in llm_selected 
                if skill in valid_skill_names
            ]
            
            # Warn about invalid skills
            invalid_skills = set(llm_selected) - set(valid_llm_skills)
            if invalid_skills:
                print(f"Warning: LLM selected invalid skills (removed): {invalid_skills}")
            
            # Add foundational skills and dependencies
            result["skills"] = add_foundational_and_dependencies(
                valid_llm_skills,
                valid_skill_names
            )
            
            print(f"Skills selected: {result['skills']}")
        
        return result

    def _extract_streaming(self, brief_text: str) -> Optional[dict]:
        """Stream partial JSON as generated (works with ANY provider)."""
        print("Extracting fields...\n", flush=True)
        result = None
        seen_keys = set()

        try:
            for chunk in self.chain.stream({"brief": brief_text}):
                result = chunk

                if isinstance(chunk, dict):
                    new_keys = set(chunk.keys()) - seen_keys
                    for key in sorted(new_keys):
                        print(f"✓ {key}", flush=True)
                    seen_keys = set(chunk.keys())

            if result:
                print(f"\n✓ Extraction complete ({len(result.keys())} fields)\n", flush=True)

            return result

        except Exception as e:
            print(f"✗ Extraction error: {e}", flush=True)
            return None

    def _extract_non_streaming(self, brief_text: str) -> Optional[dict]:
        """Non-streaming extraction (works with ANY provider)."""
        try:
            print("Extracting fields...", flush=True)
            result = self.chain.invoke({"brief": brief_text})
            print("✓ Extraction complete\n", flush=True)
            return result
        except Exception as e:
            print(f"✗ Extraction error: {e}", flush=True)
            return None


def format_markdown(result: dict) -> str:
    """Format extraction result as readable markdown."""
    lines: List[str] = ["# Research Brief Summary"]

    objective = str(result.get("objective", "")).strip()
    target_audience = str(result.get("target_audience", "")).strip()
    if objective:
        lines.append(f"- **Objective:** {objective}")
    if target_audience:
        lines.append(f"- **Target Audience:** {target_audience}")

    key_dimensions = [item for item in result.get("key_dimensions", []) if isinstance(item, str) and item.strip()]
    if key_dimensions:
        lines.append("- **Key Dimensions:**")
        lines.extend(f"  - {item}" for item in key_dimensions)
    
    # Market Context (NEW)
    market_context = result.get("market_context") or {}
    if isinstance(market_context, dict):
        mc_lines = []
        if market_context.get("client_brand"):
            mc_lines.append(f"- **Client Brand:** {market_context['client_brand']}")
        if market_context.get("competitor_brands"):
            mc_lines.append(f"- **Competitors:** {', '.join(market_context['competitor_brands'])}")
        if market_context.get("category"):
            mc_lines.append(f"- **Category:** {market_context['category']}")
        if market_context.get("market"):
            mc_lines.append(f"- **Market:** {market_context['market']}")
        if mc_lines:
            lines.append("\n## Market Context")
            lines.extend(mc_lines)
    
    # Study classification
    study_type = result.get("study_type")
    primary_methodology = result.get("primary_methodology")
    secondary_objectives = result.get("secondary_objectives", [])
    skills = result.get("skills", [])
    
    if study_type or primary_methodology:
        lines.append("\n## Study Classification")
        if study_type:
            lines.append(f"- **Study Type:** {study_type}")
        if primary_methodology:
            lines.append(f"- **Primary Methodology:** {primary_methodology}")
        
        # Total Sample Size (NEW)
        total_sample_size = result.get("total_sample_size")
        if total_sample_size:
            lines.append(f"- **Total Sample Size:** n={total_sample_size}")
        
        if secondary_objectives:
            lines.append(f"- **Secondary Objectives:** {', '.join(secondary_objectives)}")
        if skills:
            lines.append(f"- **Skills Required:** {', '.join(skills)}")

    study_design = result.get("study_design") or {}
    if isinstance(study_design, dict):
        study_lines: List[str] = []
        
        # Stimuli details (nested)
        stimuli_details = study_design.get("stimuli_details") or {}
        if isinstance(stimuli_details, dict):
            stimuli_lines: List[str] = []
            for label, key in [
                ("Stimuli Type", "stimuli_type"),
                ("Stimuli Count", "stimuli_count"),
                ("Stimuli Format", "stimuli_format"),
            ]:
                value = stimuli_details.get(key)
                if isinstance(value, str) and value.strip():
                    stimuli_lines.append(f"  - **{label}:** {value.strip()}")
            
            # NEW: Stimuli content
            stimuli_content = stimuli_details.get("stimuli_content")
            if stimuli_content and isinstance(stimuli_content, list):
                stimuli_lines.append("  - **Stimuli Content:**")
                for stimulus in stimuli_content:
                    if isinstance(stimulus, dict):
                        label = stimulus.get("label", "N/A")
                        desc = stimulus.get("description", "")
                        if desc:
                            stimuli_lines.append(f"    - {label}: {desc}")
                        else:
                            stimuli_lines.append(f"    - {label}")
            
            if stimuli_lines:
                study_lines.append("- **Stimuli Details:**")
                study_lines.extend(stimuli_lines)
        
        # Other study design fields
        for label, key in [
            ("Exposure Design", "exposure_design"),
            ("Comparison Intent", "comparison_intent"),
            ("Respondent Splitting", "respondent_splitting"),
        ]:
            value = study_design.get(key)
            if isinstance(value, str) and value.strip():
                study_lines.append(f"- **{label}:** {value.strip()}")
        
        # Handle attribute_testing as structured list
        attribute_testing = study_design.get("attribute_testing")
        if attribute_testing and isinstance(attribute_testing, list):
            study_lines.append(f"- **Attribute Testing:** {len(attribute_testing)} attributes")
            for attr in attribute_testing:
                if isinstance(attr, dict):
                    attr_name = attr.get("attribute_name", "")
                    level_count = attr.get("level_count", "")
                    levels = attr.get("levels", [])
                    
                    level_info = f" ({level_count} levels)" if level_count else ""
                    study_lines.append(f"  - **{attr_name}**{level_info}")
                    
                    if levels and isinstance(levels, list):
                        for level in levels:
                            study_lines.append(f"    - {level}")
        
        if study_lines:
            lines.append("\n## Study Design")
            lines.extend(study_lines)

    measurement_guidance = result.get("measurement_guidance") or {}
    if isinstance(measurement_guidance, dict):
        guidance_lines: List[str] = []
        for label, key in [
            ("Measurement Priority", "measurement_priority"),
            ("Segmentation Intent", "segmentation_intent"),
            ("Benchmarking", "benchmarking"),
        ]:
            value = measurement_guidance.get(key)
            if isinstance(value, str) and value.strip():
                guidance_lines.append(f"- **{label}:** {value.strip()}")
        
        # Handle required_outputs as array (UPDATED)
        value = measurement_guidance.get("required_outputs")
        if isinstance(value, list) and value:
            guidance_lines.append(f"- **Required Outputs:** {', '.join(value)}")
        elif isinstance(value, str) and value.strip():
            guidance_lines.append(f"- **Required Outputs:** {value.strip()}")
        
        if guidance_lines:
            lines.append("\n## Measurement Guidance")
            lines.extend(guidance_lines)

    # Operational Requirements (NEW - replaces constraints)
    operational = result.get("operational") or {}
    if isinstance(operational, dict):
        op_lines = []
        if operational.get("target_loi_minutes"):
            op_lines.append(f"- **Target LOI:** {operational['target_loi_minutes']} minutes")
        if operational.get("fieldwork_mode"):
            op_lines.append(f"- **Fieldwork Mode:** {operational['fieldwork_mode']}")
        if operational.get("market_specifics"):
            op_lines.append(f"- **Market Specifics:** {operational['market_specifics']}")
        if operational.get("quality_controls"):
            op_lines.append(f"- **Quality Controls:** {', '.join(operational['quality_controls'])}")
        if operational.get("constraints"):
            op_lines.append(f"- **Constraints:** {operational['constraints']}")
        if op_lines:
            lines.append("\n## Operational Requirements")
            lines.extend(op_lines)
    
    # Quotas
    quotas = result.get("quotas")
    if quotas and isinstance(quotas, list):
        lines.append("\n## Quotas")
        for quota in quotas:
            if isinstance(quota, dict):
                attr = quota.get("attribute", "")
                qtype = quota.get("type", "")
                lines.append(f"- **{attr}** ({qtype})")
                for group in quota.get("groups", []):
                    if isinstance(group, dict):
                        label = group.get("label", "")
                        parts = []
                        if group.get("min") is not None:
                            parts.append(f"min: {group['min']}")
                        if group.get("max") is not None:
                            parts.append(f"max: {group['max']}")
                        if group.get("proportion") is not None:
                            parts.append(f"{group['proportion']:.0%}")
                        lines.append(f"  - {label}: {', '.join(parts) if parts else 'no targets specified'}")

    return "\n".join(lines).strip()


def get_survey_template_vars(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map extraction result to survey prompt template variables.
    
    Args:
        result: The extraction result dictionary
        
    Returns:
        Dictionary of variables for the survey builder prompt
    """
    return {
        # Existing core fields
        "objective": result.get("objective"),
        "target_audience": result.get("target_audience"),
        "key_dimensions": result.get("key_dimensions"),
        "study_type": result.get("study_type"),
        "primary_methodology": result.get("primary_methodology"),
        "secondary_objectives": result.get("secondary_objectives", []),
        
        # NEW: Market context fields
        "client_brand": (result.get("market_context") or {}).get("client_brand"),
        "competitor_brands": (result.get("market_context") or {}).get("competitor_brands", []),
        "category": (result.get("market_context") or {}).get("category"),
        "market": (result.get("market_context") or {}).get("market"),
        
        # NEW: Total sample size
        "total_sample_size": result.get("total_sample_size"),
        
        # Existing stimuli fields + NEW stimuli_content
        "stimuli_type": ((result.get("study_design") or {}).get("stimuli_details") or {}).get("stimuli_type"),
        "stimuli_count": ((result.get("study_design") or {}).get("stimuli_details") or {}).get("stimuli_count"),
        "stimuli_format": ((result.get("study_design") or {}).get("stimuli_details") or {}).get("stimuli_format"),
        "stimuli_content": ((result.get("study_design") or {}).get("stimuli_details") or {}).get("stimuli_content"),
        
        # Existing design fields
        "exposure_design": (result.get("study_design") or {}).get("exposure_design"),
        "comparison_intent": (result.get("study_design") or {}).get("comparison_intent"),
        "respondent_splitting": (result.get("study_design") or {}).get("respondent_splitting"),
        "attribute_testing": (result.get("study_design") or {}).get("attribute_testing"),
        
        # Existing measurement guidance + NEW benchmarking
        "measurement_priority": (result.get("measurement_guidance") or {}).get("measurement_priority"),
        "required_outputs": (result.get("measurement_guidance") or {}).get("required_outputs"),
        "segmentation_intent": (result.get("measurement_guidance") or {}).get("segmentation_intent"),
        "benchmarking": (result.get("measurement_guidance") or {}).get("benchmarking"),
        
        # NEW: Operational fields (replaces top-level constraints)
        "target_loi_minutes": (result.get("operational") or {}).get("target_loi_minutes"),
        "fieldwork_mode": (result.get("operational") or {}).get("fieldwork_mode"),
        "market_specifics": (result.get("operational") or {}).get("market_specifics"),
        "quality_controls": (result.get("operational") or {}).get("quality_controls"),
        "constraints": (result.get("operational") or {}).get("constraints"),
        
        # Existing quotas
        "quotas": result.get("quotas"),
    }


def stream_text(text: str, delay: float = 0.01):
    """Print text character by character to simulate streaming."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # New line at the end


if __name__ == "__main__":
    brief_text = Path("sample_brief.txt").read_text(encoding="utf-8")

    # Initialize extractor (default: Claude Sonnet 4.5)
    extractor = BriefExtractor()

    # Example for other models:
    # extractor = BriefExtractor(model_name="gpt-4o")
    # or pass a pre-configured LLM:
    # from langchain_openai import ChatOpenAI
    # extractor = BriefExtractor(llm=ChatOpenAI(model="gpt-4o"))

    # Extract with streaming
    result = extractor.extract(brief_text, stream_output=True)

    if result:
        Path("brief_output.json").write_text(
            json.dumps(result, indent=2),
            encoding="utf-8"
        )

        print("\n=== Markdown Output ===")
        markdown_text = format_markdown(result)
        stream_text(markdown_text, delay=0.01)