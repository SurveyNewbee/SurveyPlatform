import os
import json
import sys
import time
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, model_validator, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda

# Load environment variables from .env file (Windows env vars take precedence)
load_dotenv()

# LangSmith observability
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = "Basics"  # Force override

# Verify LangSmith API key is available
if os.environ.get("LANGCHAIN_TRACING_V2") == "true" and not os.environ.get("LANGCHAIN_API_KEY"):
    print("⚠ Warning: LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is not set. Tracing will not work.")


def strip_task_plan(text) -> str:
    """Strip TASK_PLAN block before JSON."""
    if hasattr(text, 'content'):
        text = text.content
    idx = text.find('{')
    if idx > 0:
        text = text[idx:]
    ridx = text.rfind('}')
    if ridx >= 0:
        text = text[:ridx + 1]
    return text


class Question(BaseModel):
    question_id: str
    question_text: str
    question_type: str  # single_choice, multiple_choice, scale, matrix, open_ended, numeric_input, stimulus_display
    options: List[str] = []
    rows: Optional[List[str]] = None
    columns: Optional[List[str]] = None
    displays_artefact: Optional[str] = None
    display_logic: Optional[str] = None
    piping: Optional[str] = None
    quota_attribute: Optional[str] = None
    quota_type: Optional[str] = None
    quota_groups: Optional[List[Dict[str, Any]]] = None
    required: bool = True          # NEW
    notes: Optional[str] = None    # NEW

    @field_validator("question_id", "question_text", "question_type")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()

    @model_validator(mode="after")
    def validate_question(self):
        if self.question_type == "matrix":
            if not self.rows or not self.columns:
                raise ValueError("matrix questions must include rows and columns")
            if self.options:
                raise ValueError("matrix questions must have empty options")
        elif self.question_type in ("open_ended", "stimulus_display", "numeric_input"):  # CHANGED: added numeric_input
            if self.options:
                raise ValueError(f"{self.question_type} questions must have empty options")
            if self.question_type == "stimulus_display" and not self.displays_artefact:
                raise ValueError("stimulus_display questions must include displays_artefact field")
        else:
            if not self.options:
                raise ValueError("non-open questions must include options")
        return self


class Section(BaseModel):
    questions: List[Question]

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, value: List[Question]) -> List[Question]:
        if not value:
            raise ValueError("questions must contain at least one question")
        return value


class SubSection(BaseModel):
    subsection_id: str
    subsection_title: str
    purpose: Optional[str] = None  # NEW
    questions: List[Question]

    @field_validator("subsection_id", "subsection_title")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, value: List[Question]) -> List[Question]:
        if not value:
            raise ValueError("questions must contain at least one question")
        return value


class MainSection(BaseModel):
    sub_sections: List[SubSection]

    @field_validator("sub_sections")
    @classmethod
    def validate_sub_sections(cls, value: List[SubSection]) -> List[SubSection]:
        if not value:
            raise ValueError("sub_sections must contain at least one item")
        return value


class DimensionCoverage(BaseModel):
    key_dimension: str
    how_addressed: str
    question_ids: List[str]

    @field_validator("key_dimension", "how_addressed")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()

    @field_validator("question_ids")
    @classmethod
    def validate_question_ids(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("question_ids must contain at least one item")
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if not cleaned:
            raise ValueError("question_ids must contain at least one non-empty string")
        return cleaned


class Artefact(BaseModel):
    artefact_id: str
    artefact_type: str  # e.g., "concept", "stimulus", "image"
    title: str
    content: str

    @field_validator("artefact_id", "artefact_type", "title", "content")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()


class StudyMetadata(BaseModel):
    study_type: str
    description: str
    estimated_loi_minutes: Optional[str] = None  # NEW
    artefacts: List[Artefact] = []

    @field_validator("study_type", "description")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()


class RoutingRule(BaseModel):
    rule_id: str
    condition: str
    action: str

    @field_validator("rule_id", "condition", "action")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()


class Flow(BaseModel):
    summary: str  # CHANGED: was "description"
    routing_rules: List[RoutingRule] = []

    @field_validator("summary")  # CHANGED: was "description"
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value.strip()


class SampleRequirements(BaseModel):
    """NEW: Sample configuration and quotas."""
    total_sample: Optional[int] = None
    target_audience_summary: Optional[str] = None
    qualification_criteria: List[str] = []
    hard_quotas: Optional[Dict[str, Any]] = None
    soft_quotas: Optional[Dict[str, Any]] = None
    exclusions: Optional[List[str]] = None


class ProgrammingSpecifications(BaseModel):
    """NEW: Technical implementation details."""
    estimated_loi_minutes: Optional[str] = None
    loi_breakdown: Optional[Dict[str, str]] = None
    quality_controls: List[str] = []
    mobile_optimization: Optional[str] = None
    progress_indicator: Optional[str] = None
    quota_management: Optional[str] = None
    randomization_notes: Optional[str] = None


class AnalysisPlan(BaseModel):
    """NEW: Analytical approach and deliverables."""
    primary_analyses: List[str] = []
    deliverables: List[str] = []
    strategic_outputs: List[str] = []


class Survey(BaseModel):
    STUDY_METADATA: StudyMetadata
    SAMPLE_REQUIREMENTS: Optional[SampleRequirements] = None  # NEW
    SCREENER: Section
    MAIN_SECTION: MainSection
    DEMOGRAPHICS: Section
    FLOW: Flow
    PROGRAMMING_SPECIFICATIONS: Optional[ProgrammingSpecifications] = None  # NEW
    ANALYSIS_PLAN: Optional[AnalysisPlan] = None  # NEW
    DIMENSION_COVERAGE_SUMMARY: List[DimensionCoverage]

    @field_validator("DIMENSION_COVERAGE_SUMMARY")
    @classmethod
    def validate_dimension_summary(cls, value: List[DimensionCoverage]) -> List[DimensionCoverage]:
        if not value:
            raise ValueError("DIMENSION_COVERAGE_SUMMARY must contain at least one item")
        return value


class SurveyGenerator:
    """Model-agnostic survey generator with skills integration and streaming support."""

    def __init__(
        self, 
        llm=None, 
        model_name: str = "claude-opus-4-5-20251101", 
        temperature: float = 1.0,
        skills_dir: Path = Path("skills")
    ):
        """
        Initialize with any LangChain-compatible LLM.

        Args:
            llm: Pre-configured LLM instance (optional). If provided, model_name is ignored.
            model_name: Model identifier if llm not provided
            temperature: Temperature setting if llm not provided
            skills_dir: Path to skills directory containing .md files
        """
        if llm is not None:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        self.skills_dir = skills_dir
        self.parser = JsonOutputParser(pydantic_object=Survey)
        self.prompt = self._load_prompt()
        self.chain = self.prompt | self.llm | RunnableLambda(strip_task_plan) | self.parser

    def _load_skill_content(self, skill_names: List[str]) -> str:
        """
        Load skill content dynamically based on requested skill names.
        
        This function is called at generation time to load only the skills
        needed for the current survey.
        
        Args:
            skill_names: List of skill names to load
            
        Returns:
            Concatenated skill content with clear separators
        """
        if not skill_names:
            return "No specific skills requested. Use general survey design best practices."
        
        skill_contents = []
        loaded_skills = []
        missing_skills = []
        
        for skill_name in skill_names:
            skill_path = self.skills_dir / f"{skill_name}.md"
            
            if skill_path.exists():
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    skill_contents.append(f"### SKILL: {skill_name}\n\n{content}\n")
                    loaded_skills.append(skill_name)
                except Exception as e:
                    print(f"⚠ Warning: Could not load skill '{skill_name}': {e}")
                    missing_skills.append(skill_name)
            else:
                print(f"⚠ Warning: Skill file not found: {skill_path}")
                missing_skills.append(skill_name)
        
        if loaded_skills:
            print(f"✓ Loaded skills: {', '.join(loaded_skills)}")
        if missing_skills:
            print(f"⚠ Missing skills: {', '.join(missing_skills)}")
        
        if not skill_contents:
            return "No skills were successfully loaded. Use general survey design best practices."
        
        header = f"## METHODOLOGY SKILLS REFERENCE\n\nThe following {len(skill_contents)} skill(s) contain specialized knowledge for this survey:\n\n"
        return header + "\n---\n\n".join(skill_contents)

    def _load_prompt(self) -> ChatPromptTemplate:
        """
        Load prompt template and configure dynamic skill loading.
        
        Uses LangChain's partial() method with callable to defer skill loading
        until generation time, ensuring model-agnostic compatibility.
        """
        prompt_path = Path("survey_prompt_template.txt")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        template_text = prompt_path.read_text(encoding="utf-8")
        
        # Add format_instructions placeholder at the end
        template_with_format = f"{template_text}\n\n{{format_instructions}}"
        
        # Create prompt template with all expected variables
        prompt = ChatPromptTemplate.from_template(template_with_format)

        # Partial with format_instructions (static)
        # Note: skills_content will be provided at generation time via invoke()
        return prompt.partial(
            format_instructions=self.parser.get_format_instructions()
        )

    def generate(self, brief_data: Dict[str, Any], stream_output: bool = False) -> Optional[Dict[str, Any]]:
        """
        Main generation method with automatic fallback.

        Note: Streaming with Anthropic + JsonOutputParser has known issues.
        Will automatically fall back to non-streaming if streaming fails.
        """
        if stream_output:
            try:
                return self._generate_streaming(brief_data)
            except Exception as e:
                print(f"\n⚠ Streaming failed: {str(e)[:80]}", flush=True)
                print("⚠ Falling back to non-streaming mode...\n", flush=True)
                return self._generate_non_streaming(brief_data)
        return self._generate_non_streaming(brief_data)

    def _generate_streaming(self, brief_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Stream partial JSON as generated (works with ANY provider)."""
        print("Generating survey...\n", flush=True)
        result = None
        seen_keys = set()

        template_vars = self._prepare_vars(brief_data)

        try:
            for chunk in self.chain.stream(template_vars):
                result = chunk

                if isinstance(chunk, dict):
                    new_keys = set(chunk.keys()) - seen_keys
                    for key in sorted(new_keys):
                        print(f"✓ {key}", flush=True)
                    seen_keys = set(chunk.keys())

            if result:
                print(f"\n✓ Generation complete ({len(result.keys())} sections)\n", flush=True)

            return result

        except Exception as e:
            print(f"✗ Generation error: {e}", flush=True)
            return None

    def _generate_non_streaming(self, brief_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Non-streaming generation (works with ANY provider)."""
        template_vars = self._prepare_vars(brief_data)

        try:
            print("Generating survey...", flush=True)
            result = self.chain.invoke(template_vars)
            print("✓ Generation complete\n", flush=True)
            return result
        except Exception as e:
            print(f"✗ Generation error: {e}", flush=True)
            return None

    def _prepare_vars(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare template variables from brief data.
        
        Dynamically loads skills based on brief_data["skills"] list.
        Supports V2 schema with market_context, stimuli_content, and operational fields.
        """
        study_design = brief_data.get("study_design") or {}
        measurement_guidance = brief_data.get("measurement_guidance") or {}
        stimuli_details = study_design.get("stimuli_details") or {}
        
        # V2: Extract market_context
        market_context = brief_data.get("market_context") or {}
        
        # V2: Extract operational requirements
        operational = brief_data.get("operational") or {}
        
        # Load skills dynamically based on brief
        skill_names = brief_data.get("skills", [])
        skills_content = self._load_skill_content(skill_names)
        
        # Format attribute_testing array for template
        attribute_testing = study_design.get("attribute_testing")
        if attribute_testing and isinstance(attribute_testing, list):
            attr_lines = []
            for attr in attribute_testing:
                if isinstance(attr, dict):
                    attr_name = attr.get("attribute_name", "")
                    level_count = attr.get("level_count", "")
                    levels = attr.get("levels", [])
                    
                    level_info = f" ({level_count} levels)" if level_count else ""
                    attr_lines.append(f"    * {attr_name}{level_info}")
                    
                    if levels and isinstance(levels, list):
                        for level in levels:
                            attr_lines.append(f"      - {level}")
            
            attribute_testing_str = "\n".join(attr_lines) if attr_lines else "None"
        else:
            attribute_testing_str = attribute_testing or "None"
        
        # Format quotas for prompt
        quotas = brief_data.get("quotas")
        if quotas and isinstance(quotas, list):
            quota_lines = []
            for q in quotas:
                if isinstance(q, dict):
                    groups_str = ", ".join(
                        f"{g['label']} (min: {g.get('min', 'n/a')}, max: {g.get('max', 'n/a')})"
                        for g in q.get("groups", [])
                    )
                    quota_lines.append(f"- {q['attribute']} ({q['type']}): {groups_str}")
            quotas_str = "\n".join(quota_lines) if quota_lines else "None specified"
        else:
            quotas_str = "None specified"
        
        # V2: Format required_outputs list
        required_outputs = measurement_guidance.get("required_outputs")
        if isinstance(required_outputs, list):
            required_outputs_str = "\n".join(f"- {item}" for item in required_outputs) or "Survey results and analysis"
        else:
            required_outputs_str = str(required_outputs) if required_outputs else "Survey results and analysis"
        
        # V2: Format stimuli_content list
        stimuli_content = stimuli_details.get("stimuli_content")
        if isinstance(stimuli_content, list):
            stimuli_lines = []
            for i, stim in enumerate(stimuli_content, 1):
                if isinstance(stim, dict):
                    # Handle both 'stimulus_id' and 'label' keys
                    stim_id = stim.get("stimulus_id") or stim.get("label", f"Stimulus {i}")
                    title = stim.get("title", "")
                    desc = stim.get("description", "")
                    if title:
                        stimuli_lines.append(f"**{stim_id}** - {title}")
                    else:
                        stimuli_lines.append(f"**{stim_id}**")
                    if desc:
                        stimuli_lines.append(f"  {desc}")
            stimuli_content_str = "\n".join(stimuli_lines) if stimuli_lines else "None"
        else:
            stimuli_content_str = "None"
        
        # V2: Format competitor_brands list
        competitor_brands = market_context.get("competitor_brands", [])
        if isinstance(competitor_brands, list) and competitor_brands:
            competitor_brands_str = ", ".join(competitor_brands)
        else:
            competitor_brands_str = "None specified"
        
        # V2: Format quality_controls list
        quality_controls = operational.get("quality_controls")
        if isinstance(quality_controls, list) and quality_controls:
            quality_controls_str = ", ".join(quality_controls)
        else:
            quality_controls_str = "None specified"
        
        return dict(
            # Core study fields
            objective=brief_data.get("objective", ""),
            target_audience=brief_data.get("target_audience", ""),
            key_dimensions=json.dumps(brief_data.get("key_dimensions", [])),
            study_type=brief_data.get("study_type") or "descriptive",
            primary_methodology=brief_data.get("primary_methodology") or "descriptive",
            secondary_objectives=", ".join(brief_data.get("secondary_objectives", [])) or "None",
            
            # V2: Market context fields (matching extract_brief.py MarketContext model)
            client_brand=market_context.get("client_brand") or "Not specified",
            competitor_brands=competitor_brands_str,
            category=market_context.get("category") or "Not specified",
            market=market_context.get("market") or "Not specified",
            
            # Stimuli fields (V2 updated)
            stimuli_type=stimuli_details.get("stimuli_type") or "None",
            stimuli_count=stimuli_details.get("stimuli_count") or "None",
            stimuli_format=stimuli_details.get("stimuli_format") or "None",
            stimuli_content=stimuli_content_str,
            
            # Study design fields
            exposure_design=study_design.get("exposure_design") or "All respondents see same questions",
            comparison_intent=study_design.get("comparison_intent") or "None",
            respondent_splitting=study_design.get("respondent_splitting") or "None",
            attribute_testing=attribute_testing_str,
            
            # Measurement fields (V2 updated)
            measurement_priority=measurement_guidance.get("measurement_priority") or "Standard metrics",
            required_outputs=required_outputs_str,
            segmentation_intent=measurement_guidance.get("segmentation_intent") or "None",
            benchmarking=measurement_guidance.get("benchmarking") or "None",
            
            # V2: Operational fields (matching extract_brief.py Operational model)
            target_loi_minutes=operational.get("target_loi_minutes") or "Not specified",
            fieldwork_mode=operational.get("fieldwork_mode") or "Online",
            market_specifics=operational.get("market_specifics") or "None",
            quality_controls=quality_controls_str,
            constraints=operational.get("constraints") or "None",
            
            # Sample size (V2)
            total_sample_size=brief_data.get("total_sample_size", "Not specified"),
            
            # Other fields
            quotas=quotas_str,
            skills_content=skills_content,  # Dynamic skill content injection
        )


def non_empty_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def render_question_markdown(question: Dict[str, Any]) -> str:
    lines = [
        f"### {question.get('question_id', '').strip()}",
        question.get("question_text", "").strip(),
        f"*Type:* {question.get('question_type', '').strip()}"
    ]

    q_type = question.get("question_type")
    if q_type == "matrix":
        rows = non_empty_str_list(question.get("rows"))
        cols = non_empty_str_list(question.get("columns"))
        if rows:
            lines.append("**Rows:**")
            lines.extend(f"- {row}" for row in rows)
        if cols:
            lines.append("**Columns:**")
            lines.extend(f"- {col}" for col in cols)
    else:
        for option in non_empty_str_list(question.get("options")):
            lines.append(f"- {option}")
    
    # V2: Render notes field if present
    if question.get("notes"):
        lines.append(f"*Notes:* {question['notes']}")

    return "\n".join(lines) + "\n"


def format_markdown(survey: Dict[str, Any]) -> str:
    lines: List[str] = ["# Survey Questionnaire"]

    # V2: Render SAMPLE_REQUIREMENTS if present
    sample_req = survey.get("SAMPLE_REQUIREMENTS")
    if sample_req:
        lines.append("## SAMPLE REQUIREMENTS")
        if sample_req.get("total_sample"):
            lines.append(f"**Total Sample:** {sample_req['total_sample']}")
        if sample_req.get("target_audience_summary"):
            lines.append(f"**Target Audience:** {sample_req['target_audience_summary']}")
        if sample_req.get("qualification_criteria"):
            lines.append("**Qualification Criteria:**")
            for criterion in sample_req['qualification_criteria']:
                lines.append(f"- {criterion}")
        if sample_req.get("hard_quotas"):
            lines.append("**Hard Quotas:**")
            for quota in sample_req['hard_quotas']:
                lines.append(f"- {quota['attribute']}: {', '.join(quota['groups'])}")
        if sample_req.get("soft_quotas"):
            lines.append("**Soft Quotas:**")
            for quota in sample_req['soft_quotas']:
                lines.append(f"- {quota['attribute']}: {', '.join(quota['groups'])}")
        if sample_req.get("exclusions"):
            lines.append("**Exclusions:**")
            for excl in sample_req['exclusions']:
                lines.append(f"- {excl}")
        lines.append("")

    lines.append("## SCREENER")
    for question in survey.get("SCREENER", {}).get("questions", []):
        lines.append(render_question_markdown(question))

    lines.append("## MAIN SECTION")
    for subsection in survey.get("MAIN_SECTION", {}).get("sub_sections", []):
        title = subsection.get("subsection_title", "").strip()
        if title:
            lines.append(f"### {title}")
        for question in subsection.get("questions", []):
            lines.append(render_question_markdown(question))

    lines.append("## DEMOGRAPHICS")
    for question in survey.get("DEMOGRAPHICS", {}).get("questions", []):
        lines.append(render_question_markdown(question))

    # V2: Render PROGRAMMING_SPECIFICATIONS if present
    prog_spec = survey.get("PROGRAMMING_SPECIFICATIONS")
    if prog_spec:
        lines.append("## PROGRAMMING SPECIFICATIONS")
        if prog_spec.get("estimated_loi_minutes"):
            lines.append(f"**Estimated LOI:** {prog_spec['estimated_loi_minutes']} minutes")
        if prog_spec.get("loi_breakdown"):
            lines.append("**LOI Breakdown:**")
            for section, mins in prog_spec['loi_breakdown'].items():
                lines.append(f"- {section}: {mins} minutes")
        if prog_spec.get("quality_controls"):
            lines.append("**Quality Controls:**")
            for qc in prog_spec['quality_controls']:
                lines.append(f"- {qc}")
        if prog_spec.get("mobile_optimization"):
            lines.append(f"**Mobile Optimization:** {prog_spec['mobile_optimization']}")
        if prog_spec.get("progress_indicator"):
            lines.append(f"**Progress Indicator:** {prog_spec['progress_indicator']}")
        if prog_spec.get("quota_management"):
            lines.append(f"**Quota Management:** {prog_spec['quota_management']}")
        if prog_spec.get("randomization_notes"):
            lines.append("**Randomization:**")
            for note in prog_spec['randomization_notes']:
                lines.append(f"- {note}")
        lines.append("")

    # V2: Render ANALYSIS_PLAN if present
    analysis = survey.get("ANALYSIS_PLAN")
    if analysis:
        lines.append("## ANALYSIS PLAN")
        if analysis.get("primary_analyses"):
            lines.append("**Primary Analyses:**")
            for item in analysis['primary_analyses']:
                lines.append(f"- {item}")
        if analysis.get("deliverables"):
            lines.append("**Deliverables:**")
            for item in analysis['deliverables']:
                lines.append(f"- {item}")
        if analysis.get("strategic_outputs"):
            lines.append("**Strategic Outputs:**")
            for item in analysis['strategic_outputs']:
                lines.append(f"- {item}")
        lines.append("")

    lines.append("## DIMENSION COVERAGE SUMMARY")
    for entry in survey.get("DIMENSION_COVERAGE_SUMMARY", []):
        dimension = str(entry.get("key_dimension", "")).strip()
        how = str(entry.get("how_addressed", "")).strip()
        qids = ", ".join(non_empty_str_list(entry.get("question_ids")))
        lines.append(f"- **{dimension}**")
        if how:
            lines.append(f"  - How addressed: {how}")
        if qids:
            lines.append(f"  - Question IDs: {qids}")

    return "\n".join(lines).strip() + "\n"


def stream_text(text: str, delay: float = 0.01):
    """Print text character by character to simulate streaming."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def collect_question_ids(survey: Survey) -> Set[str]:
    ids: Set[str] = set()
    ids.update(q.question_id for q in survey.SCREENER.questions)
    for sub in survey.MAIN_SECTION.sub_sections:
        ids.update(q.question_id for q in sub.questions)
    ids.update(q.question_id for q in survey.DEMOGRAPHICS.questions)
    return ids


if __name__ == "__main__":
    brief_data = json.loads(Path("brief_output.json").read_text(encoding="utf-8"))

    # Initialize generator with default model
    # Skills will be loaded automatically based on brief_data["skills"]
    generator = SurveyGenerator()

    # Example for other providers (model-agnostic):
    # from langchain_anthropic import ChatAnthropic
    # generator = SurveyGenerator(llm=ChatAnthropic(model="claude-sonnet-4"))
    
    # from langchain_openai import ChatOpenAI
    # generator = SurveyGenerator(llm=ChatOpenAI(model="gpt-4o"))

    # Generate without streaming (more reliable for large JSON)
    result = generator.generate(brief_data, stream_output=False)

    if not result:
        print("survey_output.json not written: no survey data was produced.")
        sys.exit(2)

    try:
        survey = Survey.model_validate(result)
    except ValidationError as exc:
        print("Validation error while parsing survey JSON:")
        print(exc)
        print("survey_output.json not written due to validation failure.")
        sys.exit(2)

    question_ids = collect_question_ids(survey)
    referenced_ids: Set[str] = set()
    for entry in survey.DIMENSION_COVERAGE_SUMMARY:
        referenced_ids.update(entry.question_ids)

    missing_ids = sorted(qid for qid in referenced_ids if qid not in question_ids)

    if missing_ids:
        print("Validation error: DIMENSION_COVERAGE_SUMMARY contains missing question_ids.")
        print(f"Total emitted question_ids: {len(question_ids)}")
        print(f"Total referenced question_ids: {len(referenced_ids)}")
        print("Missing question_ids:")
        for qid in missing_ids:
            print(f"- {qid}")
        print("survey_output.json not written due to missing question_ids.")
        sys.exit(2)

    Path("survey_output.json").write_text(
        json.dumps(survey.model_dump(), indent=2),
        encoding="utf-8"
    )
    print("Saved survey_output.json")

    print("\n=== Markdown Output ===")
    markdown_text = format_markdown(survey.model_dump())
    markdown_delay = float(os.getenv("MARKDOWN_STREAM_DELAY", "0.01"))
    stream_text(markdown_text, delay=markdown_delay)