"""
Post-generation validator for survey_output.json.

Runs between generate_survey.py and render_survey.py to enforce structural rules,
apply auto-fixes, and flag warnings/errors before final rendering.

Architecture:
    generate_survey.py → survey_output.json → validate_survey.py → survey_output_validated.json → render_survey.py

Outputs:
    - survey_output_validated.json: patched survey (identical to input if no fixes applied)
    - validation_log.json: detailed log of all checks, fixes, warnings, and errors
"""

import json
import sys
import copy
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Represents a single validation check result."""
    check_id: str
    check_name: str
    severity: str  # "auto_fix", "warning", "error", "advisory"
    question_id: Optional[str]
    section: Optional[str]
    message: str
    action_taken: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class SurveyValidator:
    """Validates and patches survey_output.json using rules from skills and brief."""

    def __init__(self, survey: dict, brief: dict):
        self.survey = copy.deepcopy(survey)  # deep copy so we can mutate for fixes
        self.brief = brief
        self.results: List[ValidationResult] = []
        self.skills = brief.get("skills", [])
        
    def validate(self) -> Tuple[dict, List[ValidationResult]]:
        """Run all applicable validators, return patched survey + results."""
        self._run_core_validators()
        self._run_sequence_validators()
        self._run_methodology_validators()
        self._run_optional_section_validators()
        self._run_quality_advisories()
        return self.survey, self.results
    
    def _run_core_validators(self):
        """Run all core structural validators."""
        self._check_stimulus_display_artefacts()  # CORE_001
        self._check_question_type_field_compatibility()  # CORE_002
        self._check_options_arrays()  # CORE_003
        self._check_question_id_uniqueness()  # CORE_004
        self._check_screener_prefer_not_to_say()  # CORE_005
        self._check_demographics_placement()  # CORE_006
        self._check_routing_rule_references()  # CORE_007
        self._check_scale_format()  # CORE_008
        self._check_quota_alignment()  # CORE_009
        self._check_matrix_consistency()  # CORE_010
        self._check_ranking_format()  # CORE_011

    # ========================================================================
    # CORE_001: stimulus_display_has_artefact
    # ========================================================================
    def _check_stimulus_display_artefacts(self):
        """Ensure stimulus_display questions have valid displays_artefact."""
        artefacts = self.survey.get("STUDY_METADATA", {}).get("artefacts", [])
        artefact_ids = {a["artefact_id"] for a in artefacts}
        
        if not artefacts:
            # If no artefacts exist, flag any stimulus_display as error
            for section_name in ["SCREENER", "DEMOGRAPHICS"]:
                section = self.survey.get(section_name, {})
                for q in section.get("questions", []):
                    if q.get("question_type") == "stimulus_display":
                        self.results.append(ValidationResult(
                            check_id="CORE_001",
                            check_name="stimulus_display_has_artefact",
                            severity="error",
                            question_id=q.get("question_id"),
                            section=section_name,
                            message="stimulus_display question found but no artefacts defined in STUDY_METADATA",
                            action_taken=None
                        ))
            
            main = self.survey.get("MAIN_SECTION", {})
            for subsec in main.get("sub_sections", []):
                for q in subsec.get("questions", []):
                    if q.get("question_type") == "stimulus_display":
                        self.results.append(ValidationResult(
                            check_id="CORE_001",
                            check_name="stimulus_display_has_artefact",
                            severity="error",
                            question_id=q.get("question_id"),
                            section=subsec.get("subsection_id"),
                            message="stimulus_display question found but no artefacts defined in STUDY_METADATA",
                            action_taken=None
                        ))
            return
        
        # Check SCREENER and DEMOGRAPHICS sections
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                if q.get("question_type") == "stimulus_display":
                    if not q.get("displays_artefact") or q.get("displays_artefact") not in artefact_ids:
                        # Can't auto-infer in these sections, mark as error
                        self.results.append(ValidationResult(
                            check_id="CORE_001",
                            check_name="stimulus_display_has_artefact",
                            severity="error",
                            question_id=q.get("question_id"),
                            section=section_name,
                            message=f"stimulus_display question missing or invalid displays_artefact (available: {sorted(artefact_ids)})",
                            action_taken=None
                        ))
        
        # Check MAIN_SECTION subsections (can infer from position)
        main = self.survey.get("MAIN_SECTION", {})
        subsections = main.get("sub_sections", [])
        
        for idx, subsec in enumerate(subsections):
            subsec_id = subsec.get("subsection_id")
            for q in subsec.get("questions", []):
                if q.get("question_type") == "stimulus_display":
                    current_artefact = q.get("displays_artefact")
                    
                    if not current_artefact or current_artefact not in artefact_ids:
                        # Try to infer from subsection position
                        if idx < len(artefacts):
                            inferred_id = artefacts[idx]["artefact_id"]
                            q["displays_artefact"] = inferred_id
                            self.results.append(ValidationResult(
                                check_id="CORE_001",
                                check_name="stimulus_display_has_artefact",
                                severity="auto_fix",
                                question_id=q.get("question_id"),
                                section=subsec_id,
                                message=f"stimulus_display question missing displays_artefact, inferred {inferred_id} from subsection position",
                                action_taken=f"Set displays_artefact to {inferred_id}"
                            ))
                        else:
                            # Can't infer, not enough artefacts
                            self.results.append(ValidationResult(
                                check_id="CORE_001",
                                check_name="stimulus_display_has_artefact",
                                severity="error",
                                question_id=q.get("question_id"),
                                section=subsec_id,
                                message=f"stimulus_display question missing displays_artefact and cannot infer (subsection {idx+1} has no corresponding artefact)",
                                action_taken=None
                            ))

    # ========================================================================
    # CORE_002: question_type_field_compatibility
    # ========================================================================
    def _check_question_type_field_compatibility(self):
        """Validate field values match question_type requirements."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                self._validate_question_fields(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                self._validate_question_fields(q, subsec.get("subsection_id"))

    def _validate_question_fields(self, q: dict, section: str):
        """Validate individual question field compatibility."""
        qtype = q.get("question_type")
        qid = q.get("question_id")
        options = q.get("options", [])
        rows = q.get("rows")
        columns = q.get("columns")
        
        if qtype == "stimulus_display":
            if options:
                q["options"] = []
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="stimulus_display must have empty options",
                    action_taken="Cleared options array"
                ))
            if rows is not None or columns is not None:
                if rows is not None:
                    q["rows"] = None
                if columns is not None:
                    q["columns"] = None
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="stimulus_display must have null rows/columns",
                    action_taken="Set rows and columns to null"
                ))
        
        elif qtype == "matrix":
            if not rows or not columns:
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="error",
                    question_id=qid,
                    section=section,
                    message="matrix questions must have non-empty rows AND columns",
                    action_taken=None
                ))
            if options:
                q["options"] = []
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="matrix questions must have empty options",
                    action_taken="Cleared options array"
                ))
        
        elif qtype == "open_ended":
            if options:
                q["options"] = []
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="open_ended questions must have empty options",
                    action_taken="Cleared options array"
                ))
        
        elif qtype in ["single_choice", "multiple_choice"]:
            if not options or len(options) < 2:
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="error",
                    question_id=qid,
                    section=section,
                    message=f"{qtype} questions must have at least 2 options (found {len(options)})",
                    action_taken=None
                ))
        
        elif qtype == "scale":
            if not options or len(options) < 3:
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="error",
                    question_id=qid,
                    section=section,
                    message=f"scale questions must have at least 3 options (found {len(options)})",
                    action_taken=None
                ))
        
        elif qtype == "ranking":
            # Ranking questions must have options (items to rank)
            if not options or len(options) < 2:
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="error",
                    question_id=qid,
                    section=section,
                    message=f"ranking questions must have at least 2 options to rank (found {len(options)})",
                    action_taken=None
                ))
            
            # Ranking questions should have 3-7 items (cognitive load limit)
            if len(options) > 7:
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="warning",
                    question_id=qid,
                    section=section,
                    message=f"ranking questions with more than 7 items ({len(options)} found) create high cognitive load - consider reducing or using rated importance instead",
                    action_taken=None
                ))
            
            # Ranking questions must NOT have rows/columns (those are for matrix)
            if rows is not None or columns is not None:
                if rows is not None:
                    q["rows"] = None
                if columns is not None:
                    q["columns"] = None
                self.results.append(ValidationResult(
                    check_id="CORE_002",
                    check_name="question_type_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="ranking questions must have null rows/columns",
                    action_taken="Set rows and columns to null"
                ))

    # ========================================================================
    # CORE_003: options_array_validity
    # ========================================================================
    def _check_options_arrays(self):
        """Check for empty strings and duplicates in options."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                self._validate_options(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                self._validate_options(q, subsec.get("subsection_id"))

    def _validate_options(self, q: dict, section: str):
        """Validate and clean options array."""
        options = q.get("options", [])
        if not options:
            return
        
        qid = q.get("question_id")
        original_len = len(options)
        
        # Remove empty strings
        options = [opt for opt in options if opt and opt.strip()]
        
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for opt in options:
            if opt not in seen:
                seen.add(opt)
                deduped.append(opt)
        
        if len(deduped) < original_len:
            q["options"] = deduped
            removed = original_len - len(deduped)
            self.results.append(ValidationResult(
                check_id="CORE_003",
                check_name="options_array_validity",
                severity="auto_fix",
                question_id=qid,
                section=section,
                message=f"Removed {removed} empty or duplicate option(s)",
                action_taken=f"Cleaned options from {original_len} to {len(deduped)} items"
            ))

    # ========================================================================
    # CORE_004: question_id_uniqueness
    # ========================================================================
    def _check_question_id_uniqueness(self):
        """Ensure all question_ids are unique across the survey."""
        seen_ids = {}
        duplicates = []
        
        # Check all sections
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                qid = q.get("question_id")
                if qid in seen_ids:
                    duplicates.append((qid, seen_ids[qid], section_name))
                else:
                    seen_ids[qid] = section_name
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            for q in subsec.get("questions", []):
                qid = q.get("question_id")
                if qid in seen_ids:
                    duplicates.append((qid, seen_ids[qid], subsec_id))
                else:
                    seen_ids[qid] = subsec_id
        
        for qid, first_section, second_section in duplicates:
            self.results.append(ValidationResult(
                check_id="CORE_004",
                check_name="question_id_uniqueness",
                severity="error",
                question_id=qid,
                section=second_section,
                message=f"Duplicate question_id found in {first_section} and {second_section}",
                action_taken=None
            ))

    # ========================================================================
    # CORE_005: screener_prefer_not_to_say
    # ========================================================================
    def _check_screener_prefer_not_to_say(self):
        """Ensure screener questions have 'Prefer not to say' option."""
        screener = self.survey.get("SCREENER", {})
        
        for q in screener.get("questions", []):
            qid = q.get("question_id")
            options = q.get("options", [])
            
            if not options:
                continue  # Skip open-ended screeners
            
            # Check for prefer not to say variants (case-insensitive)
            has_pnts = any(
                re.search(r"prefer\s+not\s+to\s+say", opt, re.IGNORECASE) 
                for opt in options
            )
            
            if not has_pnts:
                options.append("Prefer not to say")
                q["options"] = options
                self.results.append(ValidationResult(
                    check_id="CORE_005",
                    check_name="screener_prefer_not_to_say",
                    severity="auto_fix",
                    question_id=qid,
                    section="SCREENER",
                    message="Missing 'Prefer not to say' option",
                    action_taken="Appended 'Prefer not to say' to options"
                ))

    # ========================================================================
    # CORE_006: demographics_placement
    # ========================================================================
    def _check_demographics_placement(self):
        """Validate DEMOGRAPHICS section exists and is correctly placed."""
        if "DEMOGRAPHICS" not in self.survey:
            self.results.append(ValidationResult(
                check_id="CORE_006",
                check_name="demographics_placement",
                severity="warning",
                question_id=None,
                section=None,
                message="DEMOGRAPHICS section missing from survey",
                action_taken=None
            ))
            return
        
        # Check that DEMOGRAPHICS comes after MAIN_SECTION (by checking key order)
        keys = list(self.survey.keys())
        if "MAIN_SECTION" in keys and "DEMOGRAPHICS" in keys:
            main_idx = keys.index("MAIN_SECTION")
            demo_idx = keys.index("DEMOGRAPHICS")
            
            if demo_idx < main_idx:
                self.results.append(ValidationResult(
                    check_id="CORE_006",
                    check_name="demographics_placement",
                    severity="error",
                    question_id=None,
                    section="DEMOGRAPHICS",
                    message="DEMOGRAPHICS section appears before MAIN_SECTION (should be last section before FLOW)",
                    action_taken=None
                ))

    # ========================================================================
    # CORE_007: routing_rule_references
    # ========================================================================
    def _check_routing_rule_references(self):
        """Ensure routing rules reference valid questions and sections."""
        flow = self.survey.get("FLOW", {})
        routing_rules = flow.get("routing_rules", [])
        
        # Build index of all question IDs and sections
        all_question_ids = set()
        all_sections = {"SCREENER", "DEMOGRAPHICS", "MAIN_SECTION"}
        all_subsections = set()
        
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                all_question_ids.add(q.get("question_id"))
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            all_subsections.add(subsec_id)
            for q in subsec.get("questions", []):
                all_question_ids.add(q.get("question_id"))
        
        # Check each routing rule
        for rule in routing_rules:
            rule_id = rule.get("rule_id")
            condition = rule.get("condition", "")
            action = rule.get("action", "")
            
            # Extract question IDs from condition (pattern: SECTION_Q# or MS#_Q#)
            referenced_qids = re.findall(r'\b[A-Z]+_Q\d+\b|\bMS\d+_Q\d+\b', condition)
            
            for qid in referenced_qids:
                if qid not in all_question_ids:
                    self.results.append(ValidationResult(
                        check_id="CORE_007",
                        check_name="routing_rule_references",
                        severity="error",
                        question_id=None,
                        section="FLOW",
                        message=f"Routing rule {rule_id} references non-existent question {qid}",
                        action_taken=None
                    ))
            
            # Extract section references from action (pattern: MS#, SCREENER, DEMOGRAPHICS)
            referenced_sections = re.findall(r'\b(?:MS\d+|SCREENER|DEMOGRAPHICS|MAIN_SECTION)\b', action)
            
            for section_ref in referenced_sections:
                if section_ref.startswith("MS") and section_ref not in all_subsections:
                    self.results.append(ValidationResult(
                        check_id="CORE_007",
                        check_name="routing_rule_references",
                        severity="error",
                        question_id=None,
                        section="FLOW",
                        message=f"Routing rule {rule_id} references non-existent subsection {section_ref}",
                        action_taken=None
                    ))

    # ========================================================================
    # CORE_008: scale_format
    # ========================================================================
    def _check_scale_format(self):
        """Validate scale questions have balanced endpoints and appropriate counts."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                if q.get("question_type") == "scale":
                    self._validate_scale(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                if q.get("question_type") == "scale":
                    self._validate_scale(q, subsec.get("subsection_id"))

    def _validate_scale(self, q: dict, section: str):
        """Validate individual scale question."""
        qid = q.get("question_id")
        options = q.get("options", [])
        
        if not options:
            return
        
        # Check scale length (warn if not 5 or 7)
        if len(options) not in [5, 7]:
            self.results.append(ValidationResult(
                check_id="CORE_008",
                check_name="scale_format",
                severity="warning",
                question_id=qid,
                section=section,
                message=f"Scale has {len(options)} points (standard practice is 5 or 7)",
                action_taken=None
            ))
        
        # Check for balanced endpoints (simple heuristic: first should contain negative, last positive)
        if len(options) >= 2:
            first = options[0].lower()
            last = options[-1].lower()
            
            # Negative indicators
            negative_words = ["not", "no", "never", "unlikely", "disagree", "poor", "low"]
            # Positive indicators  
            positive_words = ["very", "extremely", "always", "likely", "agree", "excellent", "high"]
            
            first_is_negative = any(word in first for word in negative_words)
            last_is_positive = any(word in last for word in positive_words)
            
            if not (first_is_negative and last_is_positive):
                self.results.append(ValidationResult(
                    check_id="CORE_008",
                    check_name="scale_format",
                    severity="warning",
                    question_id=qid,
                    section=section,
                    message=f"Scale endpoints may not be balanced ('{options[0]}' → '{options[-1]}')",
                    action_taken=None
                ))

    # ========================================================================
    # CORE_009: quota_alignment
    # ========================================================================
    def _check_quota_alignment(self):
        """Ensure quota attributes in screener match brief quotas."""
        brief_quotas = {q["attribute"]: q for q in self.brief.get("quotas", [])}
        
        screener = self.survey.get("SCREENER", {})
        screener_quota_attrs = set()
        
        for q in screener.get("questions", []):
            qid = q.get("question_id")
            quota_attr = q.get("quota_attribute")
            quota_type = q.get("quota_type")
            
            if quota_attr:
                screener_quota_attrs.add(quota_attr)
                
                # Normalize quota_groups format from strings to objects (regardless of brief match)
                quota_groups = q.get("quota_groups")
                if quota_groups and isinstance(quota_groups, list) and len(quota_groups) > 0:
                    # Check if it's an array of strings (needs normalization)
                    if isinstance(quota_groups[0], str):
                        normalized_groups = []
                        
                        # Build a mapping of all brief quota groups (from all quota attributes)
                        all_brief_groups = {}
                        for brief_quota in brief_quotas.values():
                            for g in brief_quota.get("groups", []):
                                label = g["label"]
                                # Store with original label
                                all_brief_groups[label] = g
                                
                                # Handle regional quotas that might be prefixed
                                if brief_quota["attribute"] == "australia_regions":
                                    # Map both "Australia - Sydney" and "Australia - Other Australia"
                                    if "Other" in label:
                                        all_brief_groups[f"Australia - Other"] = g
                                    else:
                                        all_brief_groups[f"Australia - {label}"] = g
                                elif brief_quota["attribute"] == "new_zealand_regions":
                                    # Map both "New Zealand - Auckland" and "New Zealand - Other New Zealand"
                                    if "Other" in label:
                                        all_brief_groups[f"New Zealand - Other"] = g
                                    else:
                                        all_brief_groups[f"New Zealand - {label}"] = g
                        
                        # Try to match each group label to brief data
                        for group_label in quota_groups:
                            if group_label in all_brief_groups:
                                brief_group = all_brief_groups[group_label]
                                normalized_groups.append({
                                    "label": group_label,
                                    "min": brief_group.get("min"),
                                    "max": brief_group.get("max")
                                })
                            else:
                                # Group not found in brief, use label-only format
                                normalized_groups.append({"label": group_label})
                        
                        q["quota_groups"] = normalized_groups
                        self.results.append(ValidationResult(
                            check_id="CORE_009",
                            check_name="quota_alignment",
                            severity="auto_fix",
                            question_id=qid,
                            section="SCREENER",
                            message=f"Normalized quota_groups from string array to object array",
                            action_taken=f"Transformed {len(normalized_groups)} group(s) to object format with label/min/max"
                        ))
                
                # Check if quota exists in brief
                if quota_attr not in brief_quotas:
                    self.results.append(ValidationResult(
                        check_id="CORE_009",
                        check_name="quota_alignment",
                        severity="warning",
                        question_id=qid,
                        section="SCREENER",
                        message=f"Quota attribute '{quota_attr}' not found in brief quotas",
                        action_taken=None
                    ))
                else:
                    # Check if quota_type matches
                    expected_type = brief_quotas[quota_attr]["type"]
                    if quota_type != expected_type:
                        q["quota_type"] = expected_type
                        self.results.append(ValidationResult(
                            check_id="CORE_009",
                            check_name="quota_alignment",
                            severity="auto_fix",
                            question_id=qid,
                            section="SCREENER",
                            message=f"Quota type mismatch: survey has '{quota_type}', brief has '{expected_type}'",
                            action_taken=f"Updated quota_type to '{expected_type}'"
                        ))
        
        # Check for brief quotas missing from screener
        for attr in brief_quotas:
            if attr not in screener_quota_attrs:
                self.results.append(ValidationResult(
                    check_id="CORE_009",
                    check_name="quota_alignment",
                    severity="warning",
                    question_id=None,
                    section="SCREENER",
                    message=f"Brief quota '{attr}' has no corresponding screener question with quota_attribute",
                    action_taken=None
                ))

    # ========================================================================
    # CORE_010: matrix_consistency
    # ========================================================================
    def _check_matrix_consistency(self):
        """Validate matrix questions have sufficient rows/columns and consistent labels."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                if q.get("question_type") == "matrix":
                    self._validate_matrix(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                if q.get("question_type") == "matrix":
                    self._validate_matrix(q, subsec.get("subsection_id"))

    def _validate_matrix(self, q: dict, section: str):
        """Validate individual matrix question."""
        qid = q.get("question_id")
        rows = q.get("rows", [])
        columns = q.get("columns", [])
        
        # Check minimum counts
        if not rows or len(rows) < 2:
            self.results.append(ValidationResult(
                check_id="CORE_010",
                check_name="matrix_consistency",
                severity="error",
                question_id=qid,
                section=section,
                message=f"Matrix must have at least 2 rows (found {len(rows) if rows else 0})",
                action_taken=None
            ))
        
        if not columns or len(columns) < 2:
            self.results.append(ValidationResult(
                check_id="CORE_010",
                check_name="matrix_consistency",
                severity="error",
                question_id=qid,
                section=section,
                message=f"Matrix must have at least 2 columns (found {len(columns) if columns else 0})",
                action_taken=None
            ))
        
        # Check column label consistency (all short or all long)
        if columns and len(columns) >= 2:
            word_counts = [len(col.split()) for col in columns]
            min_words = min(word_counts)
            max_words = max(word_counts)
            
            # Flag if mixing single words with multi-word phrases
            if min_words == 1 and max_words >= 4:
                self.results.append(ValidationResult(
                    check_id="CORE_010",
                    check_name="matrix_consistency",
                    severity="warning",
                    question_id=qid,
                    section=section,
                    message=f"Matrix column labels have inconsistent length (range: {min_words}-{max_words} words)",
                    action_taken=None
                ))

    # ========================================================================
    # CORE_011: ranking_format
    # ========================================================================
    def _check_ranking_format(self):
        """Validate ranking questions have proper format and instructions."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                if q.get("question_type") == "ranking":
                    self._validate_ranking(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                if q.get("question_type") == "ranking":
                    self._validate_ranking(q, subsec.get("subsection_id"))

    def _validate_ranking(self, q: dict, section: str):
        """Validate individual ranking question."""
        qid = q.get("question_id")
        qtext = q.get("question_text", "")
        options = q.get("options", [])
        
        # Check 1: Question text should mention "rank" or "order"
        ranking_instruction_keywords = ["rank", "ranking", "order", "prioritize", "arrange"]
        has_instruction = any(kw in qtext.lower() for kw in ranking_instruction_keywords)
        
        if not has_instruction:
            self.results.append(ValidationResult(
                check_id="CORE_011",
                check_name="ranking_format",
                severity="warning",
                question_id=qid,
                section=section,
                message="Ranking question text should include clear instruction (e.g., 'Please rank...', 'Place in order...')",
                action_taken=None
            ))
        
        # Check 2: Question should specify ranking scale
        has_scale_reference = any(phrase in qtext.lower() for phrase in [
            "from 1", "1 to", "most to least", "least to most", 
            "highest to lowest", "drag", "arrange", "most valuable", "least valuable"
        ])
        
        if not has_scale_reference:
            self.results.append(ValidationResult(
                check_id="CORE_011",
                check_name="ranking_format",
                severity="warning",
                question_id=qid,
                section=section,
                message="Ranking question should specify scale (e.g., 'rank from 1 to 4' or 'most to least valuable')",
                action_taken=None
            ))
        
        # Check 3: Option text should be concise (easier to rank)
        for idx, opt in enumerate(options):
            word_count = len(opt.split())
            if word_count > 20:
                self.results.append(ValidationResult(
                    check_id="CORE_011",
                    check_name="ranking_format",
                    severity="warning",
                    question_id=qid,
                    section=section,
                    message=f"Ranking option {idx+1} is very long ({word_count} words) - consider shortening for easier comparison",
                    action_taken=None
                ))
        
        # Check 4: Warn about full vs partial ranking
        if len(options) > 5:
            self.results.append(ValidationResult(
                check_id="CORE_011",
                check_name="ranking_format",
                severity="advisory",
                question_id=qid,
                section=section,
                message=f"Ranking {len(options)} items may create respondent fatigue. Consider: (a) reducing items, (b) using partial ranking ('select and rank top 3'), or (c) using rated importance scale instead",
                action_taken=None
            ))

    # ========================================================================
    # SEQUENCE VALIDATORS
    # ========================================================================
    
    def _run_sequence_validators(self):
        """Run all sequence/ordering validators."""
        self._check_stimulus_before_evaluation()  # SEQ_001
        self._check_unaided_before_aided()  # SEQ_002
        self._check_comprehension_before_persuasion()  # SEQ_003
        self._check_open_end_diagnostics_after_closed()  # SEQ_004
    
    def _text_contains_any(self, text: str, keywords: list) -> bool:
        """Check if text contains any of the keywords (case-insensitive, word-boundary aware)."""
        text_lower = text.lower()
        for kw in keywords:
            # Use word boundaries for single words, substring match for phrases
            if ' ' in kw:
                # Multi-word phrase - exact substring match
                if kw.lower() in text_lower:
                    return True
            else:
                # Single word - word boundary match to avoid "use" matching "because"
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    return True
        return False
    
    # ========================================================================
    # Helper methods for stimulus exposure validators
    # ========================================================================
    def _get_artefacts(self) -> list:
        """Get all artefacts from STUDY_METADATA."""
        return self.survey.get("STUDY_METADATA", {}).get("artefacts", [])
    
    def _get_stimulus_questions(self) -> dict:
        """Map artefact_id to subsection_id for all stimulus_display questions."""
        artefact_to_subsection = {}
        main = self.survey.get("MAIN_SECTION", {})
        
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("section_id")
            for q in subsec.get("questions", []):
                if q.get("question_type") == "stimulus_display":
                    artefact_id = q.get("displays_artefact")
                    if artefact_id:
                        artefact_to_subsection[artefact_id] = subsec_id
        
        return artefact_to_subsection
    
    def _get_evaluation_subsections(self) -> list:
        """Get subsections that contain stimulus_display questions."""
        main = self.survey.get("MAIN_SECTION", {})
        eval_subsections = []
        
        for subsec in main.get("sub_sections", []):
            has_stimulus = any(
                q.get("question_type") == "stimulus_display"
                for q in subsec.get("questions", [])
            )
            if has_stimulus:
                eval_subsections.append(subsec)
        
        return eval_subsections
    
    def _subsection_has_pattern(self, subsection: dict, keywords: list) -> bool:
        """Check if any question in subsection matches keyword pattern."""
        for q in subsection.get("questions", []):
            qtext = q.get("question_text", "")
            if self._text_contains_any(qtext, keywords):
                return True
        return False
    
    def _check_subsection_consistency(self, subsections: list, check_id: str, check_name: str) -> None:
        """Check if subsections have consistent structure (question counts and types)."""
        if len(subsections) <= 1:
            return
        
        question_counts = [len(s.get("questions", [])) for s in subsections]
        question_types = [
            [q.get("question_type") for q in s.get("questions", [])]
            for s in subsections
        ]
        
        if len(set(question_counts)) > 1:
            self.results.append(ValidationResult(
                check_id=check_id,
                check_name=check_name,
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message=f"Evaluation subsections have inconsistent question counts: {question_counts}",
                action_taken=None
            ))
        
        if len(set(tuple(qt) for qt in question_types)) > 1:
            self.results.append(ValidationResult(
                check_id=check_id,
                check_name=check_name,
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message="Evaluation subsections have inconsistent question type sequences",
                action_taken=None
            ))
    
    # ========================================================================
    # Helper methods for tracking/measurement validators
    # ========================================================================
    TIME_REFERENCE_KEYWORDS = [
        "past week", "past month", "past 3 months", "past 6 months",
        "past year", "last 7 days", "last 30 days", "last 12 months",
        "per week", "per month", "in the past",
        "last", "recently", "within the"  # More flexible patterns
    ]
    
    USAGE_KEYWORDS = [
        "purchase", "purchased", "purchasing",  # Verb forms
        "buy", "bought", "buying",
        "use", "used", "using",
        "tried", "trying"
    ]
    
    def _find_questions_matching(self, keywords_a: list, keywords_b: list = None) -> list:
        """Find all questions whose text matches keywords_a AND optionally keywords_b.
        Returns list of (question, section_id, position) tuples."""
        matching = []
        position = 0
        
        # Search in all sections
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                # Handle subsections
                for subsec in section.get("sub_sections", []):
                    subsec_id = subsec.get("section_id")
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "")
                        if self._text_contains_any(qtext, keywords_a):
                            if keywords_b is None or self._text_contains_any(qtext, keywords_b):
                                matching.append((q, subsec_id, position))
                        position += 1
            else:
                # Handle flat sections
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "")
                    if self._text_contains_any(qtext, keywords_a):
                        if keywords_b is None or self._text_contains_any(qtext, keywords_b):
                            matching.append((q, section_key, position))
                    position += 1
        
        return matching
    
    def _get_question_position(self, question_id: str) -> int:
        """Get the global position of a question across all sections for ordering checks."""
        position = 0
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        if q.get("question_id") == question_id:
                            return position
                        position += 1
            else:
                for q in section.get("questions", []):
                    if q.get("question_id") == question_id:
                        return position
                    position += 1
        
        return -1  # Not found

    # ========================================================================
    # Helper methods for satisfaction/feedback validators
    # ========================================================================
    def _count_total_questions(self) -> int:
        """Count all questions across all sections."""
        total = 0
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    total += len(subsec.get("questions", []))
            else:
                total += len(section.get("questions", []))
        
        return total
    
    def _get_all_scale_point_counts(self) -> list:
        """Get the option count for every scale question in the survey."""
        scale_types = ["rating_scale", "likert_scale"]
        point_counts = []
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        if q.get("question_type") in scale_types:
                            options = q.get("options", [])
                            if options:
                                point_counts.append(len(options))
            else:
                for q in section.get("questions", []):
                    if q.get("question_type") in scale_types:
                        options = q.get("options", [])
                        if options:
                            point_counts.append(len(options))
        
        return point_counts
    
    def _check_scale_consistency(self) -> bool:
        """Return True if all scale questions use the same number of points."""
        point_counts = self._get_all_scale_point_counts()
        
        if not point_counts:
            return True
        
        # All point counts should be the same
        return len(set(point_counts)) == 1

    # ========================================================================
    # SEQ_001: stimulus_before_evaluation
    # ========================================================================
    def _check_stimulus_before_evaluation(self):
        """Ensure stimulus_display questions appear first in their subsections."""
        main = self.survey.get("MAIN_SECTION", {})
        
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            questions = subsec.get("questions", [])
            
            if not questions:
                continue
            
            # Find all stimulus_display questions
            stimulus_indices = [
                (idx, q) for idx, q in enumerate(questions) 
                if q.get("question_type") == "stimulus_display"
            ]
            
            if not stimulus_indices:
                continue  # No stimulus in this subsection
            
            # Check if any stimulus is not at position 0
            for idx, q in stimulus_indices:
                if idx != 0:
                    # Auto-fix: move to position 0
                    qid = q.get("question_id")
                    questions.remove(q)
                    questions.insert(0, q)
                    
                    self.results.append(ValidationResult(
                        check_id="SEQ_001",
                        check_name="stimulus_before_evaluation",
                        severity="auto_fix",
                        question_id=qid,
                        section=subsec_id,
                        message=f"stimulus_display question at position {idx+1}, should be first",
                        action_taken=f"Moved {qid} to position 1 in subsection"
                    ))
                    # Only move one stimulus per subsection to position 0
                    break

    # ========================================================================
    # SEQ_002: unaided_before_aided
    # ========================================================================
    def _check_unaided_before_aided(self):
        """Ensure unaided awareness questions appear before aided ones."""
        unaided_keywords = [
            "without prompting", "top of mind", "first come to mind", 
            "think of", "can you name", "what brands"
        ]
        aided_keywords = [
            "which of the following", "from this list", "select from", 
            "have you heard of"
        ]
        
        # Check in MAIN_SECTION subsections
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            questions = subsec.get("questions", [])
            
            unaided_positions = []
            aided_positions = []
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                qid = q.get("question_id")
                
                if self._text_contains_any(qtext, unaided_keywords):
                    unaided_positions.append((idx, qid))
                
                # Aided detection: keywords + has option list
                if self._text_contains_any(qtext, aided_keywords) and q.get("options"):
                    aided_positions.append((idx, qid))
            
            # Check if any aided appears before any unaided
            if aided_positions and unaided_positions:
                first_aided_idx = aided_positions[0][0]
                first_unaided_idx = unaided_positions[0][0]
                
                if first_aided_idx < first_unaided_idx:
                    self.results.append(ValidationResult(
                        check_id="SEQ_002",
                        check_name="unaided_before_aided",
                        severity="warning",
                        question_id=aided_positions[0][1],
                        section=subsec_id,
                        message=f"Aided awareness question at position {first_aided_idx+1} appears before unaided at position {first_unaided_idx+1}",
                        action_taken=None
                    ))

    # ========================================================================
    # SEQ_003: comprehension_before_persuasion
    # ========================================================================
    def _check_comprehension_before_persuasion(self):
        """Ensure comprehension questions appear before persuasion questions."""
        comprehension_keywords = [
            "main message", "key takeaway", "what is this about", 
            "what does this communicate", "in your own words"
        ]
        persuasion_keywords = [
            "how likely", "purchase intent", "would you buy", 
            "how persuasive", "how convincing"
        ]
        
        # Check in MAIN_SECTION subsections
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            questions = subsec.get("questions", [])
            
            comprehension_positions = []
            persuasion_positions = []
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                qid = q.get("question_id")
                
                if self._text_contains_any(qtext, comprehension_keywords):
                    comprehension_positions.append((idx, qid))
                
                if self._text_contains_any(qtext, persuasion_keywords):
                    persuasion_positions.append((idx, qid))
            
            # Check if any persuasion appears before any comprehension
            if persuasion_positions and comprehension_positions:
                first_persuasion_idx = persuasion_positions[0][0]
                first_comprehension_idx = comprehension_positions[0][0]
                
                if first_persuasion_idx < first_comprehension_idx:
                    self.results.append(ValidationResult(
                        check_id="SEQ_003",
                        check_name="comprehension_before_persuasion",
                        severity="warning",
                        question_id=persuasion_positions[0][1],
                        section=subsec_id,
                        message=f"Persuasion question at position {first_persuasion_idx+1} appears before comprehension at position {first_comprehension_idx+1}",
                        action_taken=None
                    ))

    # ========================================================================
    # SEQ_004: open_end_diagnostics_after_closed
    # ========================================================================
    def _check_open_end_diagnostics_after_closed(self):
        """Ensure open-ended diagnostics appear after closed-ended ratings."""
        diagnostic_keywords = [
            "like most", "like least", "improve", "change", "why did you"
        ]
        
        # Check in MAIN_SECTION subsections
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            questions = subsec.get("questions", [])
            
            first_scale_idx = None
            diagnostic_open_ends = []
            
            for idx, q in enumerate(questions):
                qtype = q.get("question_type")
                qtext = q.get("question_text", "")
                qid = q.get("question_id")
                
                # Track first scale question
                if qtype == "scale" and first_scale_idx is None:
                    first_scale_idx = idx
                
                # Track open-ended diagnostics
                if qtype == "open_ended" and self._text_contains_any(qtext, diagnostic_keywords):
                    diagnostic_open_ends.append((idx, qid))
            
            # Check if any diagnostic open-end appears before first scale
            if first_scale_idx is not None:
                for oe_idx, oe_qid in diagnostic_open_ends:
                    if oe_idx < first_scale_idx:
                        self.results.append(ValidationResult(
                            check_id="SEQ_004",
                            check_name="open_end_diagnostics_after_closed",
                            severity="warning",
                            question_id=oe_qid,
                            section=subsec_id,
                            message=f"Open-ended diagnostic at position {oe_idx+1} appears before scale ratings at position {first_scale_idx+1}",
                            action_taken=None
                        ))

    # ========================================================================
    # METHODOLOGY VALIDATORS
    # ========================================================================
    
    def _run_methodology_validators(self):
        """Run validators only for skills present in the brief."""
        skills = self.brief.get("skills", [])
        
        if "pricing-study" in skills:
            self._check_van_westendorp()  # METH_001
        if "concept-test" in skills:
            self._check_concept_test()  # METH_002
        if "conjoint" in skills:
            self._check_conjoint()  # METH_003
        if "maxdiff" in skills:
            self._check_maxdiff()  # METH_004
        if "nps-csat" in skills:
            self._check_nps_csat()  # METH_005
        if "ad-testing" in skills:
            self._check_ad_testing()  # METH_006
        if "message-test" in skills:
            self._check_message_test()  # METH_007
        if "claims-testing" in skills:
            self._check_claims_testing()  # METH_008
        if "naming-testing" in skills:
            self._check_naming_testing()  # METH_009
        if "pack-testing" in skills:
            self._check_pack_testing()  # METH_010
        if "brand-tracking" in skills:
            self._check_brand_tracking()  # METH_011
        if "market-share-tracking" in skills:
            self._check_market_share_tracking()  # METH_012
        if "market-share-benchmarking" in skills:
            self._check_market_share_benchmarking()  # METH_013
        if "penetration-frequency-loyalty" in skills:
            self._check_penetration_frequency_loyalty()  # METH_014
        if "awareness-trial-usage" in skills:
            self._check_awareness_trial_usage()  # METH_015
        if "market-sizing" in skills:
            self._check_market_sizing()  # METH_016
        if "customer-lifecycle" in skills:
            self._check_customer_lifecycle()  # METH_017
        if "churn-retention" in skills:
            self._check_churn_retention()  # METH_018
        if "employee-engagement" in skills:
            self._check_employee_engagement()  # METH_019
        if "voc-programs" in skills:
            self._check_voc_programs()  # METH_020
        if "usability-testing" in skills:
            self._check_usability_testing()  # METH_021
        if "brand-positioning" in skills:
            self._check_brand_positioning()  # METH_022
        if "brand-architecture" in skills:
            self._check_brand_architecture()  # METH_023
        if "go-to-market-validation" in skills:
            self._check_go_to_market_validation()  # METH_024
        if "segmentation" in skills:
            self._check_segmentation()  # METH_025

    # ========================================================================
    # METH_001: van_westendorp
    # ========================================================================
    def _check_van_westendorp(self):
        """Validate Van Westendorp Price Sensitivity Meter questions."""
        # Keywords for each price point
        too_cheap_keywords = ["too cheap", "so inexpensive", "question its quality", "question the quality"]
        bargain_keywords = ["bargain", "great value", "good value"]
        expensive_keywords = ["expensive", "getting expensive", "but still worth", "still worth considering"]
        too_expensive_keywords = ["too expensive", "would not consider", "not consider buying"]
        
        # Collect all Van Westendorp questions across all subsections
        vw_questions = []  # List of (subsec_id, idx, q, price_type)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("subsection_id")
            for idx, q in enumerate(subsec.get("questions", [])):
                qtext = q.get("question_text", "")
                qid = q.get("question_id")
                
                price_type = None
                if self._text_contains_any(qtext, too_cheap_keywords):
                    price_type = "too_cheap"
                elif self._text_contains_any(qtext, bargain_keywords):
                    price_type = "bargain"
                elif self._text_contains_any(qtext, expensive_keywords) and not self._text_contains_any(qtext, too_expensive_keywords):
                    price_type = "expensive"
                elif self._text_contains_any(qtext, too_expensive_keywords):
                    price_type = "too_expensive"
                
                if price_type:
                    vw_questions.append((subsec_id, idx, q, price_type))
        
        if not vw_questions:
            return  # No Van Westendorp questions found
        
        # Check 1: All 4 price points must exist
        found_types = {vw[3] for vw in vw_questions}
        required_types = {"too_cheap", "bargain", "expensive", "too_expensive"}
        missing_types = required_types - found_types
        
        if missing_types:
            self.results.append(ValidationResult(
                check_id="METH_001",
                check_name="van_westendorp",
                severity="error",
                question_id=None,
                section="MAIN_SECTION",
                message=f"Van Westendorp incomplete: missing {', '.join(sorted(missing_types))} price point(s)",
                action_taken=None
            ))
            return  # Can't validate further if incomplete
        
        # Check 2 & 3: All 4 must be in same subsection and in correct order
        subsec_groups = {}
        for subsec_id, idx, q, price_type in vw_questions:
            if subsec_id not in subsec_groups:
                subsec_groups[subsec_id] = []
            subsec_groups[subsec_id].append((idx, q, price_type))
        
        if len(subsec_groups) > 1:
            self.results.append(ValidationResult(
                check_id="METH_001",
                check_name="van_westendorp",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message=f"Van Westendorp questions split across {len(subsec_groups)} subsections (should be in same subsection)",
                action_taken=None
            ))
        
        # Check order within each subsection
        for subsec_id, questions_in_subsec in subsec_groups.items():
            if len(questions_in_subsec) < 4:
                continue  # Already flagged as incomplete
            
            # Sort by index to get current order
            questions_in_subsec.sort(key=lambda x: x[0])
            current_order = [q[2] for q in questions_in_subsec]
            correct_order = ["too_cheap", "bargain", "expensive", "too_expensive"]
            
            if current_order != correct_order:
                # Auto-fix: reorder them
                subsec_obj = None
                main = self.survey.get("MAIN_SECTION", {})
                for subsec in main.get("sub_sections", []):
                    if subsec.get("subsection_id") == subsec_id:
                        subsec_obj = subsec
                        break
                
                if subsec_obj:
                    questions_list = subsec_obj.get("questions", [])
                    # Remove all VW questions
                    vw_q_objects = [q[1] for q in questions_in_subsec]
                    for vw_q in vw_q_objects:
                        questions_list.remove(vw_q)
                    
                    # Re-insert in correct order at the position of the first one
                    first_position = min(q[0] for q in questions_in_subsec)
                    ordered_vw_qs = []
                    for price_type in correct_order:
                        for q_tuple in questions_in_subsec:
                            if q_tuple[2] == price_type:
                                ordered_vw_qs.append(q_tuple[1])
                                break
                    
                    for i, vw_q in enumerate(ordered_vw_qs):
                        questions_list.insert(first_position + i, vw_q)
                    
                    self.results.append(ValidationResult(
                        check_id="METH_001",
                        check_name="van_westendorp",
                        severity="auto_fix",
                        question_id=None,
                        section=subsec_id,
                        message=f"Van Westendorp questions out of order (was {current_order})",
                        action_taken="Reordered to: too_cheap → bargain → expensive → too_expensive"
                    ))
            
            # Check 4: All should be open_ended
            for idx, q, price_type in questions_in_subsec:
                if q.get("question_type") != "open_ended":
                    self.results.append(ValidationResult(
                        check_id="METH_001",
                        check_name="van_westendorp",
                        severity="warning",
                        question_id=q.get("question_id"),
                        section=subsec_id,
                        message=f"Van Westendorp '{price_type}' question should be open_ended for price entry (found {q.get('question_type')})",
                        action_taken=None
                    ))
        
        # Check 5: Validation constraint in FLOW
        flow = self.survey.get("FLOW", {})
        flow_desc = flow.get("description", "").lower()
        routing_rules = flow.get("routing_rules", [])
        
        has_validation = (
            "price" in flow_desc and "validation" in flow_desc
        ) or any(
            "price" in rule.get("condition", "").lower() and 
            any(op in rule.get("condition", "") for op in ["<", ">"])
            for rule in routing_rules
        )
        
        if not has_validation:
            self.results.append(ValidationResult(
                check_id="METH_001",
                check_name="van_westendorp",
                severity="warning",
                question_id=None,
                section="FLOW",
                message="Van Westendorp price ordering validation not specified in routing rules — fieldwork platform must enforce Too Cheap < Bargain < Expensive < Too Expensive",
                action_taken=None
            ))

    # ========================================================================
    # METH_002: concept_test
    # ========================================================================
    def _check_concept_test(self):
        """Validate concept test design."""
        artefacts = self.survey.get("STUDY_METADATA", {}).get("artefacts", [])
        
        # Only validate concept-related artefacts
        concept_artefacts = [
            a for a in artefacts 
            if a.get("artefact_type", "").lower() in [
                "concept", "product_description", "product_concept"
            ]
        ]
        
        if not concept_artefacts:
            return  # No concept artefacts to validate
        
        main = self.survey.get("MAIN_SECTION", {})
        subsections = main.get("sub_sections", [])
        
        # Find concept evaluation subsections (those with stimulus_display)
        concept_subsections = []
        artefact_usage = {a["artefact_id"]: 0 for a in concept_artefacts}
        
        for subsec in subsections:
            has_stimulus = any(
                q.get("question_type") == "stimulus_display" 
                for q in subsec.get("questions", [])
            )
            if has_stimulus:
                concept_subsections.append(subsec)
                # Track artefact usage
                for q in subsec.get("questions", []):
                    if q.get("question_type") == "stimulus_display":
                        artefact_id = q.get("displays_artefact")
                        if artefact_id in artefact_usage:
                            artefact_usage[artefact_id] += 1
        
        # Check 1: Number of concept subsections should match concept artefacts
        if len(concept_subsections) != len(concept_artefacts):
            self.results.append(ValidationResult(
                check_id="METH_002",
                check_name="concept_test",
                severity="error",
                question_id=None,
                section="MAIN_SECTION",
                message=f"Concept subsection count ({len(concept_subsections)}) does not match concept artefact count ({len(concept_artefacts)})",
                action_taken=None
            ))
        
        # Check 2: Every artefact must be referenced exactly once
        for artefact_id, usage_count in artefact_usage.items():
            if usage_count == 0:
                self.results.append(ValidationResult(
                    check_id="METH_002",
                    check_name="concept_test",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
            elif usage_count > 1:
                self.results.append(ValidationResult(
                    check_id="METH_002",
                    check_name="concept_test",
                    severity="warning",
                    question_id=None,
                    section="MAIN_SECTION",
                    message=f"Artefact '{artefact_id}' referenced by {usage_count} stimulus_display questions (typically should be 1)",
                    action_taken=None
                ))
        
        # Check 3: Consistent structure across concept subsections
        if len(concept_subsections) > 1:
            question_counts = [len(subsec.get("questions", [])) for subsec in concept_subsections]
            question_types = [
                [q.get("question_type") for q in subsec.get("questions", [])]
                for subsec in concept_subsections
            ]
            
            if len(set(question_counts)) > 1:
                self.results.append(ValidationResult(
                    check_id="METH_002",
                    check_name="concept_test",
                    severity="warning",
                    question_id=None,
                    section="MAIN_SECTION",
                    message=f"Concept subsections have inconsistent question counts: {question_counts}",
                    action_taken=None
                ))
            
            # Check if all subsections have same question type sequence
            if len(set(tuple(qt) for qt in question_types)) > 1:
                self.results.append(ValidationResult(
                    check_id="METH_002",
                    check_name="concept_test",
                    severity="warning",
                    question_id=None,
                    section="MAIN_SECTION",
                    message="Concept subsections have inconsistent question type sequences",
                    action_taken=None
                ))
        
        # Check 4: Rotation/randomisation in FLOW for 2+ concepts
        if len(concept_artefacts) >= 2:
            flow = self.survey.get("FLOW", {})
            flow_desc = flow.get("summary", "").lower()  # Use 'summary' field
            routing_rules = flow.get("routing_rules", [])
            
            has_rotation = (
                "rotation" in flow_desc or "randomiz" in flow_desc or 
                "random" in flow_desc or "order bias" in flow_desc
            ) or any(
                "rotation" in rule.get("action", "").lower() or 
                "random" in rule.get("action", "").lower()
                for rule in routing_rules
            )
            
            if not has_rotation:
                self.results.append(ValidationResult(
                    check_id="METH_002",
                    check_name="concept_test",
                    severity="warning",
                    question_id=None,
                    section="FLOW",
                    message="Multiple concepts detected but no rotation/randomisation mentioned in FLOW — concept order should be randomized to control for order bias",
                    action_taken=None
                ))
        
        # Check 5: Sequential monadic maximum 4 concepts
        if len(concept_artefacts) > 4:
            self.results.append(ValidationResult(
                check_id="METH_002",
                check_name="concept_test",
                severity="warning",
                question_id=None,
                section="STUDY_METADATA",
                message=f"Sequential monadic designs typically test a maximum of 4 concepts (found {len(concept_artefacts)}). Consider monadic design with separate cells.",
                action_taken=None
            ))
        
        # Check 6: Comparative preference question
        comparative_keywords = [
            "prefer overall", "which concept", "which one do you prefer", 
            "preferred concept", "most prefer",
            "rank", "ranking", "order of preference"  # Add ranking keywords
        ]
        has_comparative = False
        
        for subsec in subsections:
            for q in subsec.get("questions", []):
                qtext = q.get("question_text", "")
                if self._text_contains_any(qtext, comparative_keywords):
                    has_comparative = True
                    break
            if has_comparative:
                break
        
        if len(concept_artefacts) >= 2 and not has_comparative:
            self.results.append(ValidationResult(
                check_id="METH_002",
                check_name="concept_test",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message="Multiple concepts tested but no comparative preference question found (expected question asking 'which concept do you prefer overall?')",
                action_taken=None
            ))

    # ========================================================================
    # METH_003: conjoint
    # ========================================================================
    def _check_conjoint(self):
        """Validate conjoint analysis design."""
        study_design = self.brief.get("study_design", {})
        attribute_testing = study_design.get("attribute_testing")
        
        if not attribute_testing:
            self.results.append(ValidationResult(
                check_id="METH_003",
                check_name="conjoint",
                severity="warning",
                question_id=None,
                section="brief",
                message="Conjoint skill selected but study_design.attribute_testing not defined in brief",
                action_taken=None
            ))
            return
        
        # Check 1: 4-8 attributes
        attributes = attribute_testing.get("attributes", [])
        if len(attributes) < 4 or len(attributes) > 8:
            self.results.append(ValidationResult(
                check_id="METH_003",
                check_name="conjoint",
                severity="warning",
                question_id=None,
                section="brief",
                message=f"Conjoint typically uses 4-8 attributes (found {len(attributes)})",
                action_taken=None
            ))
        
        # Check 2: One attribute should be price
        has_price = any("price" in attr.lower() for attr in attributes)
        if not has_price:
            self.results.append(ValidationResult(
                check_id="METH_003",
                check_name="conjoint",
                severity="warning",
                question_id=None,
                section="brief",
                message="Conjoint analysis typically includes price as an attribute",
                action_taken=None
            ))
        
        # Check 3: Each attribute should have 3-5 levels
        attribute_levels = attribute_testing.get("levels", {})
        for attr in attributes:
            levels = attribute_levels.get(attr, [])
            if len(levels) < 2:
                self.results.append(ValidationResult(
                    check_id="METH_003",
                    check_name="conjoint",
                    severity="warning",
                    question_id=None,
                    section="brief",
                    message=f"Attribute '{attr}' has fewer than 2 levels (found {len(levels)})",
                    action_taken=None
                ))
            elif len(levels) > 7:
                self.results.append(ValidationResult(
                    check_id="METH_003",
                    check_name="conjoint",
                    severity="warning",
                    question_id=None,
                    section="brief",
                    message=f"Attribute '{attr}' has more than 7 levels (found {len(levels)}) — may increase cognitive load",
                    action_taken=None
                ))
        
        # Check 4: "None" option mentioned
        survey_str = json.dumps(self.survey).lower()
        has_none = "none of these" in survey_str or "none of the above" in survey_str
        
        if not has_none:
            self.results.append(ValidationResult(
                check_id="METH_003",
                check_name="conjoint",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message="Conjoint analysis typically includes a 'none of these' option in choice tasks",
                action_taken=None
            ))
        
        # Check 5: Primary methodology should be conjoint
        primary_method = self.brief.get("primary_methodology")
        if primary_method != "conjoint":
            self.results.append(ValidationResult(
                check_id="METH_003",
                check_name="conjoint",
                severity="warning",
                question_id=None,
                section="brief",
                message=f"Conjoint skill selected but primary_methodology is '{primary_method}' (should be 'conjoint')",
                action_taken=None
            ))

    # ========================================================================
    # METH_004: maxdiff
    # ========================================================================
    def _check_maxdiff(self):
        """Validate MaxDiff design."""
        # Find MaxDiff tasks
        maxdiff_questions = []
        main = self.survey.get("MAIN_SECTION", {})
        
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                qtext = q.get("question_text", "").lower()
                # Detect MaxDiff by keywords
                has_most_least = ("most" in qtext and "least" in qtext) or \
                                 ("best" in qtext and "worst" in qtext) or \
                                 ("most important" in qtext and "least important" in qtext)
                
                if has_most_least:
                    maxdiff_questions.append(q)
        
        if not maxdiff_questions:
            return  # No MaxDiff tasks found
        
        # Check 1: Items per task should be 4-5
        for q in maxdiff_questions:
            options = q.get("options", [])
            qid = q.get("question_id")
            
            if len(options) < 4 or len(options) > 5:
                self.results.append(ValidationResult(
                    check_id="METH_004",
                    check_name="maxdiff",
                    severity="warning",
                    question_id=qid,
                    section="MAIN_SECTION",
                    message=f"MaxDiff task has {len(options)} items (optimal is 4-5 items per task)",
                    action_taken=None
                ))
        
        # Check 2: Total tasks should be 8-12
        if len(maxdiff_questions) < 8 or len(maxdiff_questions) > 12:
            self.results.append(ValidationResult(
                check_id="METH_004",
                check_name="maxdiff",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message=f"MaxDiff typically uses 8-12 tasks (found {len(maxdiff_questions)})",
                action_taken=None
            ))
        
        # Check 3: Primary methodology should be maxdiff
        primary_method = self.brief.get("primary_methodology")
        if primary_method != "maxdiff":
            self.results.append(ValidationResult(
                check_id="METH_004",
                check_name="maxdiff",
                severity="warning",
                question_id=None,
                section="brief",
                message=f"MaxDiff skill selected but primary_methodology is '{primary_method}' (should be 'maxdiff')",
                action_taken=None
            ))

    # ========================================================================
    # METH_005: nps_csat
    # ========================================================================
    def _check_nps_csat(self):
        """Validate NPS and CSAT questions."""
        main = self.survey.get("MAIN_SECTION", {})
        
        # Find NPS questions
        nps_questions = []
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                qtext = q.get("question_text", "").lower()
                # NPS keywords
                if "recommend" in qtext and ("friend" in qtext or "colleague" in qtext or "someone you know" in qtext):
                    nps_questions.append((subsec.get("subsection_id"), q))
        
        # Check NPS questions
        for subsec_id, nps_q in nps_questions:
            qid = nps_q.get("question_id")
            options = nps_q.get("options", [])
            
            # Check 1: Must use 0-10 scale (11 points)
            if len(options) != 11:
                self.results.append(ValidationResult(
                    check_id="METH_005",
                    check_name="nps_csat",
                    severity="error",
                    question_id=qid,
                    section=subsec_id,
                    message=f"NPS question must use 0-10 scale (11 points), found {len(options)} options",
                    action_taken=None
                ))
            else:
                # Check endpoints
                first_option = str(options[0]).lower()
                last_option = str(options[-1]).lower()
                
                has_zero_start = "0" in first_option or "not at all" in first_option
                has_ten_end = "10" in last_option or "extremely" in last_option
                
                if not (has_zero_start and has_ten_end):
                    self.results.append(ValidationResult(
                        check_id="METH_005",
                        check_name="nps_csat",
                        severity="warning",
                        question_id=qid,
                        section=subsec_id,
                        message="NPS scale should have endpoints '0 - Not at all likely' and '10 - Extremely likely'",
                        action_taken=None
                    ))
            
            # Check 2: Must have follow-up open-ended
            subsec_questions = None
            for subsec in main.get("sub_sections", []):
                if subsec.get("subsection_id") == subsec_id:
                    subsec_questions = subsec.get("questions", [])
                    break
            
            if subsec_questions:
                nps_idx = subsec_questions.index(nps_q)
                has_followup = False
                
                # Check next 2 questions for open-ended follow-up
                for i in range(nps_idx + 1, min(nps_idx + 3, len(subsec_questions))):
                    next_q = subsec_questions[i]
                    next_qtext = next_q.get("question_text", "").lower()
                    
                    if next_q.get("question_type") == "open_ended" and \
                       ("why" in next_qtext or "reason" in next_qtext or "primary reason" in next_qtext):
                        has_followup = True
                        break
                
                if not has_followup:
                    self.results.append(ValidationResult(
                        check_id="METH_005",
                        check_name="nps_csat",
                        severity="warning",
                        question_id=qid,
                        section=subsec_id,
                        message="NPS question should be followed by open-ended question asking 'why' or 'reason for score'",
                        action_taken=None
                    ))
        
        # Find CSAT questions
        csat_questions = []
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                qtext = q.get("question_text", "").lower()
                qtype = q.get("question_type", "")
                # CSAT must be a scale question (not multiple_choice)
                if ("how satisfied" in qtext or "satisfaction" in qtext) and qtype == "scale":
                    csat_questions.append((subsec.get("subsection_id"), q))
        
        # Check 3: CSAT should use 5-point scale
        for subsec_id, csat_q in csat_questions:
            qid = csat_q.get("question_id")
            options = csat_q.get("options", [])
            
            if len(options) != 5:
                self.results.append(ValidationResult(
                    check_id="METH_005",
                    check_name="nps_csat",
                    severity="warning",
                    question_id=qid,
                    section=subsec_id,
                    message=f"CSAT questions typically use 5-point satisfaction scale (found {len(options)} options)",
                    action_taken=None
                ))
        
        # Check 4: NPS/CSAT positioning (after main content, before demographics)
        if nps_questions or csat_questions:
            # Check if any NPS/CSAT appears in demographics (bad)
            demo_section = self.survey.get("DEMOGRAPHICS", {})
            for q in demo_section.get("questions", []):
                qtext = q.get("question_text", "").lower()
                if ("recommend" in qtext and "friend" in qtext) or "satisfied" in qtext:
                    self.results.append(ValidationResult(
                        check_id="METH_005",
                        check_name="nps_csat",
                        severity="warning",
                        question_id=q.get("question_id"),
                        section="DEMOGRAPHICS",
                        message="NPS/CSAT questions should appear before demographics section, not within it",
                        action_taken=None
                    ))
    
    # ========================================================================
    # METH_011: brand_tracking
    # ========================================================================
    def _check_brand_tracking(self):
        """Validate brand tracking design."""
        awareness_keywords = ["aware of", "heard of", "familiar with", "know of"]
        consideration_keywords = ["consider", "would you consider", "preference", "prefer"]
        usage_keywords = ["used", "purchased", "bought", "tried"]
        
        # Check 1: Must include awareness measure (error if missing)
        awareness_questions = self._find_questions_matching(awareness_keywords)
        if not awareness_questions:
            self.results.append(ValidationResult(
                check_id="METH_011",
                check_name="brand_tracking",
                severity="error",
                question_id=None,
                section=None,
                message="Brand tracking must include an awareness measure (expected question with 'aware of', 'heard of', 'familiar with', or 'know of')",
                action_taken=None
            ))
        
        # Check 2: Must include consideration/preference measure
        consideration_questions = self._find_questions_matching(consideration_keywords)
        if not consideration_questions:
            self.results.append(ValidationResult(
                check_id="METH_011",
                check_name="brand_tracking",
                severity="warning",
                question_id=None,
                section=None,
                message="Brand tracking should include a consideration/preference measure (expected question with 'consider', 'would you consider', 'preference', or 'prefer')",
                action_taken=None
            ))
        
        # Check 3: Must include usage/purchase measure
        usage_questions = self._find_questions_matching(usage_keywords)
        if not usage_questions:
            self.results.append(ValidationResult(
                check_id="METH_011",
                check_name="brand_tracking",
                severity="warning",
                question_id=None,
                section=None,
                message="Brand tracking should include a usage/purchase measure (expected question with 'used', 'purchased', 'bought', or 'tried')",
                action_taken=None
            ))
        
        # Check 4: Awareness funnel order (awareness → consideration → usage)
        if awareness_questions and consideration_questions:
            first_awareness_pos = awareness_questions[0][2]
            first_consideration_pos = consideration_questions[0][2]
            
            if first_consideration_pos < first_awareness_pos:
                self.results.append(ValidationResult(
                    check_id="METH_011",
                    check_name="brand_tracking",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Awareness funnel out of order: consideration question appears before awareness question — awareness should be measured first",
                    action_taken=None
                ))
        
        if consideration_questions and usage_questions:
            first_consideration_pos = consideration_questions[0][2]
            first_usage_pos = usage_questions[0][2]
            
            if first_usage_pos < first_consideration_pos:
                self.results.append(ValidationResult(
                    check_id="METH_011",
                    check_name="brand_tracking",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Awareness funnel out of order: usage question appears before consideration question — consideration should be measured before usage",
                    action_taken=None
                ))
        
        # Check 5: If tracking study, should not have stimulus_display
        brief_desc = self.brief.get("description", "").lower()
        primary_method = self.brief.get("primary_methodology", "").lower()
        
        is_tracking = "tracking" in brief_desc or primary_method == "tracking"
        
        if is_tracking:
            main = self.survey.get("MAIN_SECTION", {})
            has_stimulus = False
            
            for subsec in main.get("sub_sections", []):
                for q in subsec.get("questions", []):
                    if q.get("question_type") == "stimulus_display":
                        has_stimulus = True
                        break
                if has_stimulus:
                    break
            
            if has_stimulus:
                self.results.append(ValidationResult(
                    check_id="METH_011",
                    check_name="brand_tracking",
                    severity="warning",
                    question_id=None,
                    section="MAIN_SECTION",
                    message="Brand tracking surveys should measure natural brand health without stimulus exposure — stimulus_display questions found",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_012: market_share_tracking
    # ========================================================================
    def _check_market_share_tracking(self):
        """Validate market share tracking design."""
        # Check 1: Time-bounded category usage question (error)
        time_usage_questions = self._find_questions_matching(
            self.TIME_REFERENCE_KEYWORDS,
            self.USAGE_KEYWORDS
        )
        
        if not time_usage_questions:
            self.results.append(ValidationResult(
                check_id="METH_012",
                check_name="market_share_tracking",
                severity="error",
                question_id=None,
                section=None,
                message="Market share tracking requires a time-bounded category usage question (expected question with time reference like 'past month' + usage verb like 'purchase', 'use', 'buy')",
                action_taken=None
            ))
        
        # Check 2: Competitive set question with multiple brands
        brand_questions = []
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtype = q.get("question_type")
                        qtext = q.get("question_text", "").lower()
                        options = q.get("options", [])
                        
                        if qtype in ["single_choice", "multiple_choice"] and len(options) >= 5:
                            if ("brand" in qtext or "which of the following" in qtext) and \
                               any(kw in qtext for kw in ["purchase", "use", "buy"]):
                                brand_questions.append(q)
            else:
                for q in section.get("questions", []):
                    qtype = q.get("question_type")
                    qtext = q.get("question_text", "").lower()
                    options = q.get("options", [])
                    
                    if qtype in ["single_choice", "multiple_choice"] and len(options) >= 5:
                        if ("brand" in qtext or "which of the following" in qtext) and \
                           any(kw in qtext for kw in ["purchase", "use", "buy"]):
                            brand_questions.append(q)
        
        if not brand_questions:
            self.results.append(ValidationResult(
                check_id="METH_012",
                check_name="market_share_tracking",
                severity="warning",
                question_id=None,
                section=None,
                message="Market share tracking should include a competitive set question listing specific brands (expected single/multiple choice question with 5+ brand options)",
                action_taken=None
            ))
        
        # Check 3: Primary vs secondary brand distinction
        has_primary = False
        has_secondary = False
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "").lower()
                        qtype = q.get("question_type")
                        
                        if ("main brand" in qtext or "most often" in qtext) and qtype == "single_choice":
                            has_primary = True
                        if ("also use" in qtext or "all brands" in qtext) and qtype == "multiple_choice":
                            has_secondary = True
            else:
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "").lower()
                    qtype = q.get("question_type")
                    
                    if ("main brand" in qtext or "most often" in qtext) and qtype == "single_choice":
                        has_primary = True
                    if ("also use" in qtext or "all brands" in qtext) and qtype == "multiple_choice":
                        has_secondary = True
        
        if has_primary and not has_secondary:
            self.results.append(ValidationResult(
                check_id="METH_012",
                check_name="market_share_tracking",
                severity="warning",
                question_id=None,
                section=None,
                message="Primary brand question found but no secondary/all brands question — market share tracking should distinguish primary vs multi-brand usage",
                action_taken=None
            ))
        elif has_secondary and not has_primary:
            self.results.append(ValidationResult(
                check_id="METH_012",
                check_name="market_share_tracking",
                severity="warning",
                question_id=None,
                section=None,
                message="Multi-brand usage question found but no primary brand question — market share tracking should distinguish primary vs secondary usage",
                action_taken=None
            ))
        
        # Check 4: Usage questions should be categorical, not open-ended
        for q, section_id, pos in time_usage_questions:
            if q.get("question_type") == "open_ended":
                self.results.append(ValidationResult(
                    check_id="METH_012",
                    check_name="market_share_tracking",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Market share questions should use categorical options for consistent measurement, not open-ended",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_013: market_share_benchmarking
    # ========================================================================
    def _check_market_share_benchmarking(self):
        """Validate market share benchmarking design."""
        # Check if this is the primary methodology or just a secondary skill
        primary_methodology = self.brief.get("primary_methodology", "")
        is_primary = primary_methodology in ["market_share", "market_share_benchmarking", "benchmarking"]
        
        # Check 1: Time-bounded usage question (same as METH_012)
        time_usage_questions = self._find_questions_matching(
            self.TIME_REFERENCE_KEYWORDS,
            self.USAGE_KEYWORDS
        )
        
        # Only error if this is primary methodology; warning otherwise
        if not time_usage_questions:
            self.results.append(ValidationResult(
                check_id="METH_013",
                check_name="market_share_benchmarking",
                severity="error" if is_primary else "warning",
                question_id=None,
                section=None,
                message="Market share benchmarking requires a time-bounded category usage question (expected question with time reference + usage verb)",
                action_taken=None
            ))
        
        # Check 2: Competitive set question (same as METH_012)
        brand_questions = []
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtype = q.get("question_type")
                        qtext = q.get("question_text", "").lower()
                        options = q.get("options", [])
                        
                        if qtype in ["single_choice", "multiple_choice"] and len(options) >= 5:
                            if ("brand" in qtext or "which of the following" in qtext) and \
                               any(kw in qtext for kw in ["purchase", "use", "buy"]):
                                brand_questions.append(q)
            else:
                for q in section.get("questions", []):
                    qtype = q.get("question_type")
                    qtext = q.get("question_text", "").lower()
                    options = q.get("options", [])
                    
                    if qtype in ["single_choice", "multiple_choice"] and len(options) >= 5:
                        if ("brand" in qtext or "which of the following" in qtext) and \
                           any(kw in qtext for kw in ["purchase", "use", "buy"]):
                            brand_questions.append(q)
        
        if not brand_questions:
            self.results.append(ValidationResult(
                check_id="METH_013",
                check_name="market_share_benchmarking",
                severity="warning",
                question_id=None,
                section=None,
                message="Market share benchmarking should include a competitive set question listing specific brands",
                action_taken=None
            ))
        
        # Check 3: Primary vs secondary distinction (same as METH_012)
        has_primary = False
        has_secondary = False
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "").lower()
                        qtype = q.get("question_type")
                        
                        if ("main brand" in qtext or "most often" in qtext) and qtype == "single_choice":
                            has_primary = True
                        if ("also use" in qtext or "all brands" in qtext) and qtype == "multiple_choice":
                            has_secondary = True
            else:
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "").lower()
                    qtype = q.get("question_type")
                    
                    if ("main brand" in qtext or "most often" in qtext) and qtype == "single_choice":
                        has_primary = True
                    if ("also use" in qtext or "all brands" in qtext) and qtype == "multiple_choice":
                        has_secondary = True
        
        if (has_primary and not has_secondary) or (has_secondary and not has_primary):
            self.results.append(ValidationResult(
                check_id="METH_013",
                check_name="market_share_benchmarking",
                severity="warning",
                question_id=None,
                section=None,
                message="Market share benchmarking should distinguish primary vs secondary brand usage",
                action_taken=None
            ))
        
        # Check 4: Volume or frequency measure for share-of-requirements
        frequency_keywords = ["how often", "how many times", "frequency", "how much"]
        frequency_questions = []
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "").lower()
                        if any(kw in qtext for kw in frequency_keywords):
                            frequency_questions.append(q)
            else:
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "").lower()
                    if any(kw in qtext for kw in frequency_keywords):
                        frequency_questions.append(q)
        
        if not frequency_questions:
            self.results.append(ValidationResult(
                check_id="METH_013",
                check_name="market_share_benchmarking",
                severity="warning",
                question_id=None,
                section=None,
                message="Market share benchmarking should include a volume/frequency measure for share-of-requirements calculation (expected question with 'how often', 'how many times', 'frequency', or 'how much')",
                action_taken=None
            ))
        
        # Check 5: Competitive set should include "Other" option
        for q in brand_questions:
            options = [opt.lower() for opt in q.get("options", [])]
            has_other = any("other" in opt for opt in options)
            
            if not has_other:
                self.results.append(ValidationResult(
                    check_id="METH_013",
                    check_name="market_share_benchmarking",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=None,
                    message="Competitive brand list should include an 'Other brand' or 'Other' option to capture long-tail",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_014: penetration_frequency_loyalty
    # ========================================================================
    def _check_penetration_frequency_loyalty(self):
        """Validate penetration/frequency/loyalty design."""
        # Check 1: Penetration question (binary ever-used within time period)
        penetration_keywords = ["ever"] + self.USAGE_KEYWORDS
        penetration_questions = self._find_questions_matching(penetration_keywords)
        
        # Also look for time-bounded category usage as alternative penetration measure
        time_usage_questions = self._find_questions_matching(
            self.TIME_REFERENCE_KEYWORDS,
            self.USAGE_KEYWORDS
        )
        
        if not penetration_questions and not time_usage_questions:
            self.results.append(ValidationResult(
                check_id="METH_014",
                check_name="penetration_frequency_loyalty",
                severity="error",
                question_id=None,
                section=None,
                message="Penetration/frequency/loyalty analysis requires a penetration question (expected question with 'ever' + usage verb OR time-bounded usage question)",
                action_taken=None
            ))
        
        # Check 2: Frequency question with time bounds
        frequency_keywords = ["how often", "how many times", "how frequently"]
        frequency_questions = []
        
        for q, section_id, pos in self._find_questions_matching(frequency_keywords):
            qtext = q.get("question_text", "").lower()
            # Check if it also has time reference
            if any(time_kw in qtext for time_kw in self.TIME_REFERENCE_KEYWORDS):
                frequency_questions.append((q, section_id, pos))
        
        if not frequency_questions:
            self.results.append(ValidationResult(
                check_id="METH_014",
                check_name="penetration_frequency_loyalty",
                severity="error",
                question_id=None,
                section=None,
                message="Penetration/frequency/loyalty analysis requires a frequency question with explicit time bounds (expected question with 'how often', 'how many times', or 'how frequently' + time reference)",
                action_taken=None
            ))
        
        # Check 3: Frequency should be categorical, not open-ended
        for q, section_id, pos in frequency_questions:
            if q.get("question_type") == "open_ended":
                self.results.append(ValidationResult(
                    check_id="METH_014",
                    check_name="penetration_frequency_loyalty",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Frequency questions should use categorical options for consistent measurement, not open-ended",
                    action_taken=None
                ))
        
        # Check 4: Loyalty/sole usage measure
        loyalty_keywords = ["only brand", "sole", "exclusive", "always buy", "most often"]
        loyalty_questions = self._find_questions_matching(loyalty_keywords)
        
        if not loyalty_questions:
            self.results.append(ValidationResult(
                check_id="METH_014",
                check_name="penetration_frequency_loyalty",
                severity="warning",
                question_id=None,
                section=None,
                message="Penetration/frequency/loyalty analysis should include a loyalty measure (expected question with 'only brand', 'sole', 'exclusive', 'always buy', or 'most often')",
                action_taken=None
            ))
        
        # Check 5: Behavioral funnel order (penetration → frequency → loyalty)
        all_penetration = penetration_questions + time_usage_questions
        
        if all_penetration and frequency_questions:
            first_penetration_pos = min(p[2] for p in all_penetration)
            first_frequency_pos = frequency_questions[0][2]
            
            if first_frequency_pos < first_penetration_pos:
                self.results.append(ValidationResult(
                    check_id="METH_014",
                    check_name="penetration_frequency_loyalty",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Behavioral funnel out of order: frequency question appears before penetration question — penetration should be measured first",
                    action_taken=None
                ))
        
        if frequency_questions and loyalty_questions:
            first_frequency_pos = frequency_questions[0][2]
            first_loyalty_pos = loyalty_questions[0][2]
            
            if first_loyalty_pos < first_frequency_pos:
                self.results.append(ValidationResult(
                    check_id="METH_014",
                    check_name="penetration_frequency_loyalty",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Behavioral funnel out of order: loyalty question appears before frequency question — frequency should be measured before loyalty",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_015: awareness_trial_usage
    # ========================================================================
    def _check_awareness_trial_usage(self):
        """Validate awareness-trial-usage funnel design."""
        awareness_keywords = ["aware of", "heard of", "familiar with", "know of"]
        trial_keywords = ["ever tried", "ever used", "first time", "tried for the first time"]
        usage_keywords = ["currently use", "use regularly", "used in the past", "how often do you use"]
        
        # Check 1: Must include all three funnel stages
        awareness_questions = self._find_questions_matching(awareness_keywords)
        trial_questions = self._find_questions_matching(trial_keywords)
        usage_questions = self._find_questions_matching(usage_keywords)
        
        if not awareness_questions:
            self.results.append(ValidationResult(
                check_id="METH_015",
                check_name="awareness_trial_usage",
                severity="error",
                question_id=None,
                section=None,
                message="ATU funnel missing awareness stage (expected question with 'aware of', 'heard of', 'familiar with', or 'know of')",
                action_taken=None
            ))
        
        if not trial_questions:
            self.results.append(ValidationResult(
                check_id="METH_015",
                check_name="awareness_trial_usage",
                severity="error",
                question_id=None,
                section=None,
                message="ATU funnel missing trial stage (expected question with 'ever tried', 'ever used', 'first time', or 'tried for the first time')",
                action_taken=None
            ))
        
        if not usage_questions:
            self.results.append(ValidationResult(
                check_id="METH_015",
                check_name="awareness_trial_usage",
                severity="error",
                question_id=None,
                section=None,
                message="ATU funnel missing usage stage (expected question with 'currently use', 'use regularly', 'used in the past', or 'how often do you use')",
                action_taken=None
            ))
        
        # Check 2: Funnel order (awareness → trial → usage)
        if awareness_questions and trial_questions:
            awareness_pos = awareness_questions[0][2]
            trial_pos = trial_questions[0][2]
            
            if trial_pos < awareness_pos:
                self.results.append(ValidationResult(
                    check_id="METH_015",
                    check_name="awareness_trial_usage",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="ATU funnel out of order: trial question appears before awareness question — awareness should be measured first",
                    action_taken=None
                ))
        
        if trial_questions and usage_questions:
            trial_pos = trial_questions[0][2]
            usage_pos = usage_questions[0][2]
            
            if usage_pos < trial_pos:
                self.results.append(ValidationResult(
                    check_id="METH_015",
                    check_name="awareness_trial_usage",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="ATU funnel out of order: usage question appears before trial question — trial should be measured before usage",
                    action_taken=None
                ))
        
        # Check 3: Trial should measure past behaviour, not intent
        intent_keywords = ["would you try", "likely to try", "consider trying"]
        for q, section_id, pos in trial_questions:
            qtext = q.get("question_text", "")
            if self._text_contains_any(qtext, intent_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_015",
                    check_name="awareness_trial_usage",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Trial should measure actual past behaviour, not future intent",
                    action_taken=None
                ))
        
        # Check 4: Usage questions should include time frame
        for q, section_id, pos in usage_questions:
            qtext = q.get("question_text", "").lower()
            has_timeframe = any(time_kw in qtext for time_kw in self.TIME_REFERENCE_KEYWORDS)
            
            if not has_timeframe:
                self.results.append(ValidationResult(
                    check_id="METH_015",
                    check_name="awareness_trial_usage",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Usage question missing time frame — results will be ambiguous without a defined period",
                    action_taken=None
                ))
        
        # Check 5: Funnel leakage check (consistent question types)
        if awareness_questions and trial_questions:
            awareness_type = awareness_questions[0][0].get("question_type")
            trial_type = trial_questions[0][0].get("question_type")
            
            # If trial allows multiple brands but awareness doesn't, flag it
            if trial_type == "multiple_choice" and awareness_type == "single_choice":
                self.results.append(ValidationResult(
                    check_id="METH_015",
                    check_name="awareness_trial_usage",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Awareness and trial question types should support consistent funnel logic — if trial allows multiple brands, awareness should too",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_016: market_sizing
    # ========================================================================
    def _check_market_sizing(self):
        """Validate market sizing design."""
        # Check 1: Incidence/qualification question
        incidence_keywords = ["do you currently", "have you ever", "in the past"]
        incidence_questions = []
        
        # Search in all sections including SCREENER
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "").lower()
                        if any(kw in qtext for kw in incidence_keywords):
                            incidence_questions.append((q, subsec.get("section_id"), 0))
            else:
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "").lower()
                    if any(kw in qtext for kw in incidence_keywords):
                        incidence_questions.append((q, section_key, 0))
        
        if not incidence_questions:
            self.results.append(ValidationResult(
                check_id="METH_016",
                check_name="market_sizing",
                severity="error",
                question_id=None,
                section=None,
                message="Market sizing requires an incidence/qualification question to establish target market proportion (expected question with 'do you currently', 'have you ever', or 'in the past')",
                action_taken=None
            ))
        
        # Check 2: Frequency/volume question
        frequency_keywords = ["how often", "how many times", "how much do you spend", "how many do you"]
        frequency_questions = self._find_questions_matching(frequency_keywords)
        
        # Check if they also have time references
        frequency_with_time = []
        for q, section_id, pos in frequency_questions:
            qtext = q.get("question_text", "").lower()
            if any(time_kw in qtext for time_kw in self.TIME_REFERENCE_KEYWORDS):
                frequency_with_time.append((q, section_id, pos))
        
        if not frequency_with_time:
            self.results.append(ValidationResult(
                check_id="METH_016",
                check_name="market_sizing",
                severity="error",
                question_id=None,
                section=None,
                message="Market sizing requires a frequency/volume question to estimate per-capita consumption (expected question with 'how often', 'how many times', or 'how much' + time reference)",
                action_taken=None
            ))
        
        # Check 3: Price/spend question if objective mentions value
        brief_objective = self.brief.get("objective", "").lower()
        brief_desc = self.brief.get("description", "").lower()
        
        value_related = any(kw in brief_objective + brief_desc for kw in ["market size", "revenue", "value"])
        
        if value_related:
            spend_keywords = ["how much", "spend", "pay", "price"]
            spend_questions = self._find_questions_matching(spend_keywords)
            
            if not spend_questions:
                self.results.append(ValidationResult(
                    check_id="METH_016",
                    check_name="market_sizing",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="Brief mentions market size/revenue/value but survey lacks a price/spend question for value estimation",
                    action_taken=None
                ))
        
        # Check 4: Multiple sizing questions required
        sizing_question_count = len(incidence_questions) + len(frequency_with_time)
        if sizing_question_count < 3:
            self.results.append(ValidationResult(
                check_id="METH_016",
                check_name="market_sizing",
                severity="warning",
                question_id=None,
                section=None,
                message="Market sizing typically requires multiple funnel questions (incidence, frequency, value) for reliable estimates",
                action_taken=None
            ))
        
        # Check 5: Incidence questions should be categorical
        for q, section_id, pos in incidence_questions:
            if q.get("question_type") == "open_ended":
                self.results.append(ValidationResult(
                    check_id="METH_016",
                    check_name="market_sizing",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Incidence questions should use categorical options for consistent measurement, not open-ended",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_017: customer_lifecycle
    # ========================================================================
    def _check_customer_lifecycle(self):
        """Validate customer lifecycle design."""
        # Check 1: Stage classification question
        stage_keywords_a = ["how long have you been", "when did you first", "current status", "which best describes your relationship", "how would you describe"]
        stage_keywords_b = ["customer", "subscriber", "member"]
        
        stage_questions = []
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        qtext = q.get("question_text", "").lower()
                        if self._text_contains_any(qtext, stage_keywords_a) and \
                           self._text_contains_any(qtext, stage_keywords_b):
                            stage_questions.append((q, subsec.get("section_id")))
            else:
                for q in section.get("questions", []):
                    qtext = q.get("question_text", "").lower()
                    if self._text_contains_any(qtext, stage_keywords_a) and \
                       self._text_contains_any(qtext, stage_keywords_b):
                        stage_questions.append((q, section_key))
        
        if not stage_questions:
            self.results.append(ValidationResult(
                check_id="METH_017",
                check_name="customer_lifecycle",
                severity="error",
                question_id=None,
                section=None,
                message="Customer lifecycle study requires a stage classification question (expected question with lifecycle stage language + customer/subscriber/member reference)",
                action_taken=None
            ))
        
        # Check 2: Stage classification should be behavioural, not attitudinal
        attitudinal_keywords = ["how do you feel about", "how satisfied are you with your status"]
        for q, section_id in stage_questions:
            qtext = q.get("question_text", "")
            if self._text_contains_any(qtext, attitudinal_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_017",
                    check_name="customer_lifecycle",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Lifecycle stage should be defined by behaviour (tenure, recency, frequency) not attitudes",
                    action_taken=None
                ))
        
        # Check 3: Stage classification should be categorical (single_choice)
        for q, section_id in stage_questions:
            if q.get("question_type") == "open_ended":
                self.results.append(ValidationResult(
                    check_id="METH_017",
                    check_name="customer_lifecycle",
                    severity="warning",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Lifecycle stage classification should use categorical options (single_choice), not open-ended",
                    action_taken=None
                ))
        
        # Check 4: Transition trigger questions
        trigger_keywords = ["what made you", "why did you", "what caused", "what led you to", "reason for"]
        trigger_questions = self._find_questions_matching(trigger_keywords)
        
        if not trigger_questions:
            self.results.append(ValidationResult(
                check_id="METH_017",
                check_name="customer_lifecycle",
                severity="warning",
                question_id=None,
                section=None,
                message="Customer lifecycle studies should include transition trigger questions to understand what causes movement between stages (expected question with 'what made you', 'why did you', 'what caused', etc.)",
                action_taken=None
            ))
        
        # Check 5: Routing based on stage classification
        if stage_questions:
            stage_question = stage_questions[0][0]
            stage_qid = stage_question.get("question_id")
            
            # Check if FLOW routing rules reference the stage question
            flow = self.survey.get("FLOW", {})
            routing_rules = flow.get("routing_rules", [])
            
            has_stage_routing = False
            for rule in routing_rules:
                condition = rule.get("condition", "")
                action = rule.get("action", "")
                if stage_qid in condition or stage_qid in action:
                    has_stage_routing = True
                    break
            
            # Also check for display_logic in questions
            if not has_stage_routing:
                for section_key in ["MAIN_SECTION"]:
                    section = self.survey.get(section_key, {})
                    for subsec in section.get("sub_sections", []):
                        for q in subsec.get("questions", []):
                            display_logic = q.get("display_logic", "")
                            if stage_qid in display_logic:
                                has_stage_routing = True
                                break
            
            if not has_stage_routing:
                self.results.append(ValidationResult(
                    check_id="METH_017",
                    check_name="customer_lifecycle",
                    severity="warning",
                    question_id=None,
                    section="FLOW",
                    message="Consider routing respondents to stage-specific question paths based on lifecycle classification",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_018: churn_retention
    # ========================================================================
    def _check_churn_retention(self):
        """Validate churn/retention study design."""
        # Check 1: Must include a churn classification question
        churn_keywords = [
            "cancelled", "canceled", "stopped using", "no longer", 
            "ended your subscription", "left", "discontinued",
            "leave", "leaving", "switch", "switched"  # Add flexible patterns
        ]
        churn_questions = self._find_questions_matching(churn_keywords)
        
        if not churn_questions:
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="error",
                question_id=None,
                section=None,
                message="Churn/retention study requires a churn classification question that identifies churn status behaviourally (expected question with 'cancelled', 'stopped using', 'no longer', 'ended your subscription', 'left', or 'discontinued')",
                action_taken=None
            ))
        
        # Check 2: Churn must be defined by behaviour, not attitude
        intent_keywords = ["thinking about leaving", "considering cancelling", "how likely are you to leave"]
        has_intent_only = False
        
        for q, section_id, _ in churn_questions:
            qtext = q.get("question_text", "")
            if self._text_contains_any(qtext, intent_keywords):
                has_intent_only = True
        
        # If we have intent questions but no behavioural churn questions
        if has_intent_only and not any(
            self._text_contains_any(q.get("question_text", ""), churn_keywords)
            for q, _, __ in churn_questions
            if not self._text_contains_any(q.get("question_text", ""), intent_keywords)
        ):
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="warning",
                question_id=churn_questions[0][0].get("question_id") if churn_questions else None,
                section=churn_questions[0][1] if churn_questions else None,
                message="Churn should be classified by actual behaviour (cancelled, stopped), not intent. Intent questions are useful but should supplement, not replace, behavioural classification",
                action_taken=None
            ))
        
        # Check 3: Must include a primary reason question
        reason_keywords = [
            "main reason", "primary reason", "most important reason",
            "single most important reason",  # Add this pattern
            "biggest factor", "biggest reason", "key reason",
            "why did you", "what led you", "what caused you"
        ]
        reason_questions = self._find_questions_matching(reason_keywords, churn_keywords)
        
        if not reason_questions:
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="error",
                question_id=None,
                section=None,
                message="Churn/retention study must include a primary reason question (expected question with 'main reason', 'primary reason', 'most important reason', 'biggest factor', or 'why did you' combined with churn-related keywords)",
                action_taken=None
            ))
        
        # Check 4: Must distinguish voluntary vs involuntary churn
        voluntary_keywords = ["your decision", "chose to", "involuntary", "forced", "contract ended", "price increase"]
        voluntary_questions = self._find_questions_matching(voluntary_keywords)
        
        if not voluntary_questions:
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="warning",
                question_id=None,
                section=None,
                message="Churn/retention study should distinguish voluntary vs involuntary churn (expected question with 'your decision', 'chose to', 'involuntary', 'forced', 'contract ended', or 'price increase')",
                action_taken=None
            ))
        
        # Check 5: Must include a recency question
        recency_keywords = ["when did you", "how long ago", "how recently"]
        recency_questions = self._find_questions_matching(recency_keywords, churn_keywords)
        
        if not recency_questions:
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="warning",
                question_id=None,
                section=None,
                message="Churn recency is important for data quality — recent churners provide more reliable recall (expected question with 'when did you', 'how long ago', or 'how recently' combined with churn keywords)",
                action_taken=None
            ))
        
        # Check 6: Lifecycle stage should be captured
        tenure_keywords = ["how long were you", "how long had you been", "tenure", "length of time"]
        tenure_questions = self._find_questions_matching(tenure_keywords)
        
        if not tenure_questions:
            self.results.append(ValidationResult(
                check_id="METH_018",
                check_name="churn_retention",
                severity="warning",
                question_id=None,
                section=None,
                message="Churn/retention study should capture lifecycle stage or tenure before churn (expected question with 'how long were you', 'how long had you been', 'tenure', or 'length of time')",
                action_taken=None
            ))
    
    # ========================================================================
    # METH_019: employee_engagement
    # ========================================================================
    def _check_employee_engagement(self):
        """Validate employee engagement survey design."""
        # Check 1: Must include overall engagement measure
        engagement_keywords = ["engaged", "motivated", "committed", "proud to work", "recommend as a place to work"]
        engagement_questions = self._find_questions_matching(engagement_keywords)
        
        if not engagement_questions:
            self.results.append(ValidationResult(
                check_id="METH_019",
                check_name="employee_engagement",
                severity="error",
                question_id=None,
                section=None,
                message="Employee engagement survey requires an overall engagement measure (expected question with 'engaged', 'motivated', 'committed', 'proud to work', or 'recommend as a place to work')",
                action_taken=None
            ))
        
        # Check 2: Must include manager/leadership measure
        manager_keywords = ["manager", "supervisor", "leadership", "direct report", "team leader"]
        manager_questions = self._find_questions_matching(manager_keywords)
        
        if not manager_questions:
            self.results.append(ValidationResult(
                check_id="METH_019",
                check_name="employee_engagement",
                severity="warning",
                question_id=None,
                section=None,
                message="Employee engagement survey should include a manager/leadership measure (expected question with 'manager', 'supervisor', 'leadership', 'direct report', or 'team leader')",
                action_taken=None
            ))
        
        # Check 3: Must include growth/development measure
        growth_keywords = ["growth", "development", "career", "learning", "opportunity", "advance"]
        growth_questions = self._find_questions_matching(growth_keywords)
        
        if not growth_questions:
            self.results.append(ValidationResult(
                check_id="METH_019",
                check_name="employee_engagement",
                severity="warning",
                question_id=None,
                section=None,
                message="Employee engagement survey should include a growth/development measure (expected question with 'growth', 'development', 'career', 'learning', 'opportunity', or 'advance')",
                action_taken=None
            ))
        
        # Check 4: Anonymity protection - check for identifying combinations
        all_questions = []
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    all_questions.extend([(q, section_key) for q in subsec.get("questions", [])])
            else:
                all_questions.extend([(q, section_key) for q in section.get("questions", [])])
        
        has_department = False
        has_role = False
        has_tenure = False
        has_location = False
        
        for q, _ in all_questions:
            qtext = q.get("question_text", "").lower()
            if "department" in qtext or "team" in qtext:
                has_department = True
            if "role" in qtext or "title" in qtext or "position" in qtext:
                has_role = True
            if "tenure" in qtext or "how long have you" in qtext or "years at" in qtext:
                has_tenure = True
            if "location" in qtext or "office" in qtext or "site" in qtext:
                has_location = True
        
        if has_department and has_role and has_tenure and has_location:
            self.results.append(ValidationResult(
                check_id="METH_019",
                check_name="employee_engagement",
                severity="warning",
                question_id=None,
                section="DEMOGRAPHICS",
                message="Combination of department, role, tenure, and location questions may compromise respondent anonymity in small teams. Consider reducing identifying questions or aggregating categories",
                action_taken=None
            ))
        
        # Check 5: All attitudinal questions should use consistent scale format
        if not self._check_scale_consistency():
            point_counts = self._get_all_scale_point_counts()
            self.results.append(ValidationResult(
                check_id="METH_019",
                check_name="employee_engagement",
                severity="warning",
                question_id=None,
                section=None,
                message=f"Employee engagement surveys should use consistent scale format throughout for reliable index construction (found mixed scales: {set(point_counts)})",
                action_taken=None
            ))
        
        # Check 6: Demographics must not include name, employee ID, or email
        identifying_keywords = ["your name", "employee id", "employee number", "email address", "staff number"]
        
        for q, section_id in all_questions:
            qtext = q.get("question_text", "")
            if self._text_contains_any(qtext, identifying_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_019",
                    check_name="employee_engagement",
                    severity="error",
                    question_id=q.get("question_id"),
                    section=section_id,
                    message="Employee engagement surveys must not collect names, employee IDs, or email addresses to protect anonymity",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_020: voc_programs
    # ========================================================================
    def _check_voc_programs(self):
        """Validate Voice of Customer program design."""
        # Check 1: Must include a touchpoint/interaction identification question
        touchpoint_keywords = ["recent experience", "recent interaction", "contact us", "visit", "transaction", "purchase", "service call", "support"]
        touchpoint_questions = self._find_questions_matching(touchpoint_keywords)
        
        if not touchpoint_questions:
            self.results.append(ValidationResult(
                check_id="METH_020",
                check_name="voc_programs",
                severity="error",
                question_id=None,
                section=None,
                message="VoC program requires a touchpoint/interaction identification question (expected question with 'recent experience', 'recent interaction', 'contact us', 'visit', 'transaction', 'purchase', 'service call', or 'support')",
                action_taken=None
            ))
        
        # Check 2: Must include an overall satisfaction or effort measure
        satisfaction_keywords = ["how satisfied", "satisfaction", "how easy", "effort", "how would you rate"]
        satisfaction_questions = self._find_questions_matching(satisfaction_keywords)
        
        if not satisfaction_questions:
            self.results.append(ValidationResult(
                check_id="METH_020",
                check_name="voc_programs",
                severity="error",
                question_id=None,
                section=None,
                message="VoC program requires an overall satisfaction or effort measure (expected question with 'how satisfied', 'satisfaction', 'how easy', 'effort', or 'how would you rate')",
                action_taken=None
            ))
        
        # Check 3: Must include an open-ended feedback question
        has_open_feedback = False
        
        for section_key in ["SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"]:
            section = self.survey.get(section_key, {})
            
            if section_key == "MAIN_SECTION":
                for subsec in section.get("sub_sections", []):
                    for q in subsec.get("questions", []):
                        if q.get("question_type") == "open_ended":
                            qtext = q.get("question_text", "").lower()
                            if any(kw in qtext for kw in ["tell us more", "additional comments", "feedback", "describe", "explain", "anything else"]):
                                has_open_feedback = True
                                break
            else:
                for q in section.get("questions", []):
                    if q.get("question_type") == "open_ended":
                        qtext = q.get("question_text", "").lower()
                        if any(kw in qtext for kw in ["tell us more", "additional comments", "feedback", "describe", "explain", "anything else"]):
                            has_open_feedback = True
                            break
        
        if not has_open_feedback:
            self.results.append(ValidationResult(
                check_id="METH_020",
                check_name="voc_programs",
                severity="warning",
                question_id=None,
                section=None,
                message="VoC program should include an open-ended feedback question (expected open_ended question with 'tell us more', 'additional comments', 'feedback', 'describe', 'explain', or 'anything else')",
                action_taken=None
            ))
        
        # Check 4: Must include a follow-up/resolution question if service interactions
        service_keywords = ["issue", "problem", "resolved", "resolution", "complaint"]
        service_questions = self._find_questions_matching(service_keywords)
        
        if service_questions:
            resolution_keywords = ["resolved", "fixed", "addressed", "handled"]
            resolution_questions = self._find_questions_matching(resolution_keywords)
            
            if not resolution_questions:
                self.results.append(ValidationResult(
                    check_id="METH_020",
                    check_name="voc_programs",
                    severity="warning",
                    question_id=None,
                    section=None,
                    message="VoC survey covers service interactions but lacks a resolution measure (expected question with 'resolved', 'fixed', 'addressed', or 'handled')",
                    action_taken=None
                ))
        
        # Check 5: Survey should be short (under 15 questions)
        total_questions = self._count_total_questions()
        
        if total_questions > 15:
            self.results.append(ValidationResult(
                check_id="METH_020",
                check_name="voc_programs",
                severity="warning",
                question_id=None,
                section=None,
                message=f"VoC surveys should be concise (typically under 15 questions) to maximise response rates for post-interaction feedback (current: {total_questions} questions)",
                action_taken=None
            ))
    
    # ========================================================================
    # METH_021: usability_testing
    # ========================================================================
    def _check_usability_testing(self):
        """Validate usability testing design."""
        # Check 1: Must include at least one task completion measure
        task_keywords = ["able to complete", "successfully", "task", "find what you were looking for", "accomplish"]
        task_questions = self._find_questions_matching(task_keywords)
        
        if not task_questions:
            self.results.append(ValidationResult(
                check_id="METH_021",
                check_name="usability_testing",
                severity="error",
                question_id=None,
                section=None,
                message="Usability testing requires at least one task completion measure (expected question with 'able to complete', 'successfully', 'task', 'find what you were looking for', or 'accomplish')",
                action_taken=None
            ))
        
        # Check 2: Must include a satisfaction/ease measure
        ease_keywords = ["easy to use", "ease of use", "user-friendly", "intuitive", "difficult", "how easy"]
        ease_questions = self._find_questions_matching(ease_keywords)
        
        if not ease_questions:
            self.results.append(ValidationResult(
                check_id="METH_021",
                check_name="usability_testing",
                severity="warning",
                question_id=None,
                section=None,
                message="Usability testing should include a satisfaction/ease measure (expected question with 'easy to use', 'ease of use', 'user-friendly', 'intuitive', 'difficult', or 'how easy')",
                action_taken=None
            ))
        
        # Check 3: If SUS is used, it must have exactly 10 questions
        sus_keywords = [
            "use this system frequently", "unnecessarily complex", "easy to use", 
            "need technical support", "well integrated", "inconsistency", 
            "learn to use quickly", "cumbersome", "confident using", "learn a lot before"
        ]
        
        # Find questions that match SUS items
        sus_questions = []
        
        for section_key in ["MAIN_SECTION"]:
            section = self.survey.get(section_key, {})
            for subsec in section.get("sub_sections", []):
                for q in subsec.get("questions", []):
                    qtext = q.get("question_text", "")
                    if self._text_contains_any(qtext, sus_keywords):
                        sus_questions.append((q, subsec.get("section_id")))
        
        # If 3+ SUS items found, check exactly 10 exist
        if len(sus_questions) >= 3:
            if len(sus_questions) != 10:
                self.results.append(ValidationResult(
                    check_id="METH_021",
                    check_name="usability_testing",
                    severity="error",
                    question_id=None,
                    section=sus_questions[0][1] if sus_questions else None,
                    message=f"System Usability Scale requires exactly 10 standardised items — do not modify, add, or remove items (found {len(sus_questions)} SUS items)",
                    action_taken=None
                ))
            
            # Check 4: SUS questions must use 5-point agreement scale
            for q, section_id, _ in sus_questions:
                options = q.get("options", [])
                if len(options) != 5:
                    self.results.append(ValidationResult(
                        check_id="METH_021",
                        check_name="usability_testing",
                        severity="error",
                        question_id=q.get("question_id"),
                        section=section_id,
                        message="System Usability Scale questions must use exactly 5-point agreement scale ('Strongly disagree' to 'Strongly agree')",
                        action_taken=None
                    ))
                    break
        
        # Check 5: Task-based questions should appear before overall satisfaction
        if task_questions and ease_questions:
            task_position = self._get_question_position(task_questions[0][0].get("question_id"))
            ease_position = self._get_question_position(ease_questions[0][0].get("question_id"))
            
            if task_position > ease_position and task_position != -1 and ease_position != -1:
                self.results.append(ValidationResult(
                    check_id="METH_021",
                    check_name="usability_testing",
                    severity="warning",
                    question_id=task_questions[0][0].get("question_id"),
                    section=task_questions[0][1],
                    message="Task completion questions should appear before overall satisfaction/ease measures to avoid biasing task completion",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_022: brand_positioning
    # ========================================================================
    def _check_brand_positioning(self):
        """Validate brand positioning study design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Every positioning artefact must have stimulus_display
        for artefact in artefacts:
            artefact_id = artefact.get("artefact_id")
            if artefact_id not in artefact_to_subsection:
                self.results.append(ValidationResult(
                    check_id="METH_022",
                    check_name="brand_positioning",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Positioning artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
        
        # Check 2: Each positioning subsection must include all four core metrics
        clarity_keywords = ["clear", "clarity", "understand", "easy to understand", "what this brand stands for"]
        relevance_keywords = ["relevant", "applies to me", "matters to me", "for someone like me", "meaningful"]
        differentiation_keywords = ["different", "unique", "stand out", "distinctive", "sets apart"]
        credibility_keywords = ["believable", "credible", "trust", "deliver on", "live up to"]
        
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            
            if not self._subsection_has_pattern(subsec, clarity_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_022",
                    check_name="brand_positioning",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Positioning evaluation subsection missing clarity measure (expected question with 'clear', 'clarity', 'understand', 'easy to understand', or 'what this brand stands for')",
                    action_taken=None
                ))
            
            if not self._subsection_has_pattern(subsec, relevance_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_022",
                    check_name="brand_positioning",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Positioning evaluation subsection missing relevance measure (expected question with 'relevant', 'applies to me', 'matters to me', 'for someone like me', or 'meaningful')",
                    action_taken=None
                ))
            
            if not self._subsection_has_pattern(subsec, differentiation_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_022",
                    check_name="brand_positioning",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Positioning evaluation subsection missing differentiation measure (expected question with 'different', 'unique', 'stand out', 'distinctive', or 'sets apart')",
                    action_taken=None
                ))
            
            if not self._subsection_has_pattern(subsec, credibility_keywords):
                self.results.append(ValidationResult(
                    check_id="METH_022",
                    check_name="brand_positioning",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Positioning evaluation subsection missing credibility measure (expected question with 'believable', 'credible', 'trust', 'deliver on', or 'live up to')",
                    action_taken=None
                ))
        
        # Check 3: Clarity must be measured before preference/intent
        preference_keywords = ["prefer", "purchase intent", "would you buy"]
        
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            clarity_position = None
            preference_position = None
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                if self._text_contains_any(qtext, clarity_keywords) and clarity_position is None:
                    clarity_position = idx
                if self._text_contains_any(qtext, preference_keywords) and preference_position is None:
                    preference_position = idx
            
            if clarity_position is not None and preference_position is not None:
                if preference_position < clarity_position:
                    self.results.append(ValidationResult(
                        check_id="METH_022",
                        check_name="brand_positioning",
                        severity="warning",
                        question_id=questions[preference_position].get("question_id"),
                        section=subsec_id,
                        message=f"Preference/intent question at position {preference_position+1} appears before clarity at position {clarity_position+1}",
                        action_taken=None
                    ))
        
        # Check 4: Purchase intent should NOT be the primary KPI
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            # Find first evaluation question after stimulus
            first_eval_idx = None
            for idx, q in enumerate(questions):
                if q.get("question_type") != "stimulus_display":
                    first_eval_idx = idx
                    break
            
            if first_eval_idx is not None:
                first_eval_q = questions[first_eval_idx]
                qtext = first_eval_q.get("question_text", "")
                if self._text_contains_any(qtext, preference_keywords):
                    self.results.append(ValidationResult(
                        check_id="METH_022",
                        check_name="brand_positioning",
                        severity="warning",
                        question_id=first_eval_q.get("question_id"),
                        section=subsec_id,
                        message="Positioning research should prioritise clarity, relevance, and differentiation over purchase intent as primary metrics",
                        action_taken=None
                    ))
        
        # Check 5: Evaluation subsections must have consistent structure
        self._check_subsection_consistency(eval_subsections, "METH_022", "brand_positioning")
    
    # ========================================================================
    # METH_023: brand_architecture
    # ========================================================================
    def _check_brand_architecture(self):
        """Validate brand architecture study design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Must test complete brand systems, not isolated elements
        for artefact in artefacts:
            artefact_type = artefact.get("artefact_type", "")
            artefact_id = artefact.get("artefact_id")
            
            if artefact_type and not any(term in artefact_type.lower() for term in ["architecture", "system", "portfolio", "hierarchy"]):
                # Check if it's isolated element
                if any(term in artefact_type.lower() for term in ["name", "logo"]):
                    self.results.append(ValidationResult(
                        check_id="METH_023",
                        check_name="brand_architecture",
                        severity="warning",
                        question_id=None,
                        section="STUDY_METADATA",
                        message=f"Artefact '{artefact_id}' appears to be an isolated element ('{artefact_type}'). Brand architecture studies should test complete systems, not isolated names or logos",
                        action_taken=None
                    ))
        
        # Check 2: Must include a clarity/understanding measure for each architecture
        clarity_keywords = ["clear", "understand", "relationship between", "how these brands relate", "makes sense"]
        
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, clarity_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_023",
                    check_name="brand_architecture",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Brand architecture subsection missing clarity/understanding measure (expected question with 'clear', 'understand', 'relationship between', 'how these brands relate', or 'makes sense')",
                    action_taken=None
                ))
        
        # Check 3: Clarity must be assessed before preference
        preference_keywords = ["prefer", "prefer overall", "which do you prefer"]
        
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            clarity_position = None
            preference_position = None
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                if self._text_contains_any(qtext, clarity_keywords) and clarity_position is None:
                    clarity_position = idx
                if self._text_contains_any(qtext, preference_keywords) and preference_position is None:
                    preference_position = idx
            
            if clarity_position is not None and preference_position is not None:
                if preference_position < clarity_position:
                    self.results.append(ValidationResult(
                        check_id="METH_023",
                        check_name="brand_architecture",
                        severity="warning",
                        question_id=questions[preference_position].get("question_id"),
                        section=subsec_id,
                        message=f"Preference question at position {preference_position+1} appears before clarity at position {clarity_position+1}",
                        action_taken=None
                    ))
        
        # Check 4: Must include open-ended diagnostics
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            has_open_ended = any(q.get("question_type") == "open_ended" for q in questions)
            
            if not has_open_ended:
                self.results.append(ValidationResult(
                    check_id="METH_023",
                    check_name="brand_architecture",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Brand architecture subsection missing open-ended diagnostics (expected at least one open_ended question)",
                    action_taken=None
                ))
        
        # Check 5: If multiple architectures tested, monadic or sequential monadic required
        if len(artefacts) > 1:
            flow = self.survey.get("FLOW", {})
            flow_desc = flow.get("description", "").lower()
            routing_rules = flow.get("routing_rules", [])
            
            has_rotation = (
                "rotation" in flow_desc or "randomiz" in flow_desc or 
                "random" in flow_desc or "monadic" in flow_desc
            ) or any(
                "rotation" in rule.get("action", "").lower() or 
                "random" in rule.get("action", "").lower()
                for rule in routing_rules
            )
            
            if not has_rotation:
                self.results.append(ValidationResult(
                    check_id="METH_023",
                    check_name="brand_architecture",
                    severity="warning",
                    question_id=None,
                    section="FLOW",
                    message=f"Multiple brand architectures ({len(artefacts)}) require monadic or sequential monadic design with rotation to avoid order bias",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_024: go_to_market_validation
    # ========================================================================
    def _check_go_to_market_validation(self):
        """Validate go-to-market validation study design."""
        # Check 1: Must include a value proposition measure
        value_keywords = ["value", "benefit", "what would you gain", "why would you", "worth"]
        value_questions = self._find_questions_matching(value_keywords)
        
        if not value_questions:
            self.results.append(ValidationResult(
                check_id="METH_024",
                check_name="go_to_market_validation",
                severity="warning",
                question_id=None,
                section=None,
                message="Go-to-market validation should include a value proposition measure (expected question with 'value', 'benefit', 'what would you gain', 'why would you', or 'worth')",
                action_taken=None
            ))
        
        # Check 2: Must include a competitive context question
        competitive_keywords = ["alternative", "competitor", "instead of", "currently use", "compared to", "switch from"]
        competitive_questions = self._find_questions_matching(competitive_keywords)
        
        if not competitive_questions:
            self.results.append(ValidationResult(
                check_id="METH_024",
                check_name="go_to_market_validation",
                severity="warning",
                question_id=None,
                section=None,
                message="Go-to-market validation should include a competitive context question (expected question with 'alternative', 'competitor', 'instead of', 'currently use', 'compared to', or 'switch from')",
                action_taken=None
            ))
        
        # Check 3: Must include an objection/barrier measure
        barrier_keywords = ["concern", "hesitation", "prevent", "barrier", "worry", "hold you back", "reason not to"]
        barrier_questions = self._find_questions_matching(barrier_keywords)
        
        if not barrier_questions:
            self.results.append(ValidationResult(
                check_id="METH_024",
                check_name="go_to_market_validation",
                severity="warning",
                question_id=None,
                section=None,
                message="Go-to-market validation should include an objection/barrier measure (expected question with 'concern', 'hesitation', 'prevent', 'barrier', 'worry', 'hold you back', or 'reason not to')",
                action_taken=None
            ))
        
        # Check 4: Must include a target audience fit measure
        target_keywords = ["for someone like me", "relevant to", "right for me", "intended for", "target"]
        target_questions = self._find_questions_matching(target_keywords)
        
        if not target_questions:
            self.results.append(ValidationResult(
                check_id="METH_024",
                check_name="go_to_market_validation",
                severity="warning",
                question_id=None,
                section=None,
                message="Go-to-market validation should include a target audience fit measure (expected question with 'for someone like me', 'relevant to', 'right for me', 'intended for', or 'target')",
                action_taken=None
            ))
        
        # Check 5: If pricing is part of GTM validation, pricing skill should be present
        pricing_keywords = ["price", "pay", "cost", "expensive", "afford"]
        pricing_questions = self._find_questions_matching(pricing_keywords)
        
        if pricing_questions and "pricing-study" not in self.skills:
            self.results.append(ValidationResult(
                check_id="METH_024",
                check_name="go_to_market_validation",
                severity="warning",
                question_id=pricing_questions[0][0].get("question_id"),
                section=pricing_questions[0][1],
                message="Survey includes pricing questions but pricing-study skill was not selected — consider adding it for proper pricing methodology",
                action_taken=None
            ))
    
    # ========================================================================
    # METH_025: segmentation
    # ========================================================================
    def _check_segmentation(self):
        """Validate segmentation study design."""
        # Check 1: Must include attitudinal/psychographic battery
        has_attitudinal_battery = False
        attitudinal_battery_rows = 0
        
        for section_key in ["MAIN_SECTION"]:
            section = self.survey.get(section_key, {})
            for subsec in section.get("sub_sections", []):
                for q in subsec.get("questions", []):
                    if q.get("question_type") == "matrix":
                        rows = q.get("rows", [])
                        columns = q.get("columns", [])
                        
                        # Check if it's an agreement scale matrix
                        is_agreement = any("agree" in col.lower() for col in columns) and any("disagree" in col.lower() for col in columns)
                        
                        if is_agreement and len(rows) >= 8:
                            has_attitudinal_battery = True
                            attitudinal_battery_rows = len(rows)
        
        if not has_attitudinal_battery:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section=None,
                message="Segmentation typically requires a substantial attitudinal battery (15-30 statements) for stable segment extraction",
                action_taken=None
            ))
        
        # Check 2: Attitudinal battery should be substantial
        if has_attitudinal_battery and attitudinal_battery_rows < 15:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section=None,
                message=f"Attitudinal battery has fewer than 15 statements ({attitudinal_battery_rows} found) — segments may be unstable. Consider expanding to 15-30 statements",
                action_taken=None
            ))
        
        # Check 3: Must include behavioural measures alongside attitudinal
        behavioural_keywords = ["how often", "how many", "frequency", "purchase", "use"]
        behavioural_questions = self._find_questions_matching(behavioural_keywords)
        
        if not behavioural_questions:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section=None,
                message="Segmentation based solely on attitudes without behavioural validation produces less actionable segments",
                action_taken=None
            ))
        
        # Check 4: Must include demographics for segment profiling
        demographics = self.survey.get("DEMOGRAPHICS", {})
        demo_questions = demographics.get("questions", [])
        
        if len(demo_questions) < 3:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section="DEMOGRAPHICS",
                message=f"Segmentation requires demographics for segment profiling (found {len(demo_questions)} questions, recommend at least 3)",
                action_taken=None
            ))
        
        # Check 5: Sample size consideration
        constraints = self.brief.get("constraints", {})
        # Handle case where constraints is a string instead of dict
        if isinstance(constraints, dict):
            total_sample = constraints.get("sample_size", 0)
        else:
            total_sample = 0
        
        # Check if quotas define sample size
        if not total_sample:
            quotas = self.brief.get("quotas", [])
            if quotas:
                total_sample = sum(q.get("target", 0) for q in quotas)
        
        if total_sample > 0 and total_sample < 800:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section=None,
                message=f"Segmentation studies typically require n=800+ for stable segment solutions. Current sample ({total_sample}) may be insufficient",
                action_taken=None
            ))
        
        # Check 6: Should NOT segment on a single variable
        # Count matrix batteries
        matrix_count = 0
        other_attitudinal_count = 0
        
        for section_key in ["MAIN_SECTION"]:
            section = self.survey.get(section_key, {})
            for subsec in section.get("sub_sections", []):
                for q in subsec.get("questions", []):
                    if q.get("question_type") == "matrix":
                        matrix_count += 1
                    elif q.get("question_type") in ["rating_scale", "likert_scale"]:
                        other_attitudinal_count += 1
        
        if matrix_count == 1 and other_attitudinal_count == 0 and not behavioural_questions:
            self.results.append(ValidationResult(
                check_id="METH_025",
                check_name="segmentation",
                severity="warning",
                question_id=None,
                section=None,
                message="Segmentation should draw on multiple variable types (attitudes, behaviours, needs) for robust solutions",
                action_taken=None
            ))
    
    # ========================================================================
    # METH_006: ad_testing
    # ========================================================================
    def _check_ad_testing(self):
        """Validate ad testing design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Every ad artefact must have stimulus_display
        for artefact in artefacts:
            artefact_id = artefact.get("artefact_id")
            if artefact_id not in artefact_to_subsection:
                self.results.append(ValidationResult(
                    check_id="METH_006",
                    check_name="ad_testing",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Ad artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
        
        # Check 2: Each ad subsection must include notice/attention measure
        notice_keywords = ["notice", "attention", "stand out", "catch your eye"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, notice_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_006",
                    check_name="ad_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Ad evaluation subsection missing notice/attention measure (expected question with 'notice', 'attention', 'stand out', or 'catch your eye')",
                    action_taken=None
                ))
        
        # Check 3: Each ad subsection must include communication/message measure
        communication_keywords = ["main message", "communicate", "takeaway", "trying to say"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, communication_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_006",
                    check_name="ad_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Ad evaluation subsection missing communication/message takeaway measure (expected question with 'main message', 'communicate', 'takeaway', or 'trying to say')",
                    action_taken=None
                ))
        
        # Check 4: Each ad subsection must include brand linkage
        brand_keywords = ["which brand", "brand", "advertiser", "who is"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, brand_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_006",
                    check_name="ad_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Ad evaluation subsection missing brand linkage measure (expected question with 'which brand', 'brand', 'advertiser', or 'who is')",
                    action_taken=None
                ))
        
        # Check 5: Consistent structure across ad subsections
        self._check_subsection_consistency(eval_subsections, "METH_006", "ad_testing")
        
        # Check 6: Multiple ads should have rotation/assignment logic in FLOW
        if len(artefacts) > 1:
            flow = self.survey.get("FLOW", {})
            flow_desc = flow.get("description", "").lower()
            routing_rules = flow.get("routing_rules", [])
            
            has_assignment = (
                "rotation" in flow_desc or "random" in flow_desc or 
                "cell" in flow_desc or "group" in flow_desc or "assign" in flow_desc
            ) or any(
                "rotation" in rule.get("action", "").lower() or 
                "random" in rule.get("action", "").lower() or
                "cell" in rule.get("condition", "").lower() or
                "group" in rule.get("condition", "").lower()
                for rule in routing_rules
            )
            
            if not has_assignment:
                self.results.append(ValidationResult(
                    check_id="METH_006",
                    check_name="ad_testing",
                    severity="warning",
                    question_id=None,
                    section="FLOW",
                    message="Multiple ads detected but no rotation/cell assignment mentioned in FLOW — consider randomization to control for order bias or between-group design",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_007: message_test
    # ========================================================================
    def _check_message_test(self):
        """Validate message testing design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Every message artefact must have stimulus_display
        for artefact in artefacts:
            artefact_id = artefact.get("artefact_id")
            if artefact_id not in artefact_to_subsection:
                self.results.append(ValidationResult(
                    check_id="METH_007",
                    check_name="message_test",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Message artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
        
        # Check 2: Comprehension before persuasion in each subsection
        comprehension_keywords = ["main message", "key takeaway", "communicate", "in your own words"]
        persuasion_keywords = ["how likely", "purchase intent", "how persuasive", "how convincing"]
        
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            comprehension_idx = None
            persuasion_idx = None
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                if comprehension_idx is None and self._text_contains_any(qtext, comprehension_keywords):
                    comprehension_idx = idx
                if persuasion_idx is None and self._text_contains_any(qtext, persuasion_keywords):
                    persuasion_idx = idx
            
            if comprehension_idx is None:
                self.results.append(ValidationResult(
                    check_id="METH_007",
                    check_name="message_test",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Message evaluation subsection missing comprehension measure (expected question with 'main message', 'key takeaway', 'communicate', or 'in your own words')",
                    action_taken=None
                ))
            elif persuasion_idx is not None and comprehension_idx > persuasion_idx:
                self.results.append(ValidationResult(
                    check_id="METH_007",
                    check_name="message_test",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Comprehension measure appears after persuasion measure — comprehension should be measured before persuasion",
                    action_taken=None
                ))
        
        # Check 3: Each message subsection must include relevance
        relevance_keywords = ["relevant", "applies to me", "for someone like me"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, relevance_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_007",
                    check_name="message_test",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Message evaluation subsection missing relevance measure (expected question with 'relevant', 'applies to me', or 'for someone like me')",
                    action_taken=None
                ))
        
        # Check 4: Consistent structure across message subsections
        self._check_subsection_consistency(eval_subsections, "METH_007", "message_test")
        
        # Check 5: Sequential monadic max 5 messages
        if len(artefacts) > 5:
            self.results.append(ValidationResult(
                check_id="METH_007",
                check_name="message_test",
                severity="warning",
                question_id=None,
                section="STUDY_METADATA",
                message=f"Sequential monadic message tests typically evaluate a maximum of 5 messages (found {len(artefacts)}). Consider reducing the number of messages or using monadic design with separate cells.",
                action_taken=None
            ))
    
    # ========================================================================
    # METH_008: claims_testing
    # ========================================================================
    def _check_claims_testing(self):
        """Validate claims testing design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Every claim artefact must have stimulus_display
        for artefact in artefacts:
            artefact_id = artefact.get("artefact_id")
            if artefact_id not in artefact_to_subsection:
                self.results.append(ValidationResult(
                    check_id="METH_008",
                    check_name="claims_testing",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Claim artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
        
        # Check 2: Each claim subsection must include believability
        believability_keywords = ["believable", "believe", "credible", "credibility"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, believability_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_008",
                    check_name="claims_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Claim evaluation subsection missing believability measure (expected question with 'believable', 'believe', 'credible', or 'credibility')",
                    action_taken=None
                ))
        
        # Check 3: Each claim subsection must include clarity/comprehension
        clarity_keywords = ["clear", "clarity", "understand", "easy to understand"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, clarity_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_008",
                    check_name="claims_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Claim evaluation subsection missing clarity/comprehension measure (expected question with 'clear', 'clarity', 'understand', or 'easy to understand')",
                    action_taken=None
                ))
        
        # Check 4: Clarity should appear before believability
        for subsec in eval_subsections:
            subsec_id = subsec.get("section_id")
            questions = subsec.get("questions", [])
            
            clarity_idx = None
            believability_idx = None
            
            for idx, q in enumerate(questions):
                qtext = q.get("question_text", "")
                if clarity_idx is None and self._text_contains_any(qtext, clarity_keywords):
                    clarity_idx = idx
                if believability_idx is None and self._text_contains_any(qtext, believability_keywords):
                    believability_idx = idx
            
            if clarity_idx is not None and believability_idx is not None and clarity_idx > believability_idx:
                self.results.append(ValidationResult(
                    check_id="METH_008",
                    check_name="claims_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Clarity measure appears after believability measure — clarity/comprehension should be measured before believability",
                    action_taken=None
                ))
        
        # Check 5: Claims must be tested in isolation
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            subsec_id = subsec.get("section_id")
            stimulus_questions = [
                q for q in subsec.get("questions", [])
                if q.get("question_type") == "stimulus_display"
            ]
            
            if len(stimulus_questions) > 1:
                self.results.append(ValidationResult(
                    check_id="METH_008",
                    check_name="claims_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Multiple stimulus_display questions in one subsection — claims should be tested in isolation (one claim per subsection)",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_009: naming_testing
    # ========================================================================
    def _check_naming_testing(self):
        """Validate naming testing design."""
        artefacts = self._get_artefacts()
        
        # Count name artefacts
        name_artefacts = [
            a for a in artefacts
            if "name" in a.get("artefact_type", "").lower()
        ]
        
        # Check 1: Minimum 5 name candidates
        if len(name_artefacts) < 5:
            self.results.append(ValidationResult(
                check_id="METH_009",
                check_name="naming_testing",
                severity="warning",
                question_id=None,
                section="STUDY_METADATA",
                message=f"Naming tests typically evaluate a minimum of 5 name candidates (found {len(name_artefacts)} name artefacts). Consider testing more alternatives.",
                action_taken=None
            ))
        
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 2: Each name subsection must include ease of pronunciation
        pronunciation_keywords = ["easy to say", "pronounce", "pronunciation", "say out loud"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, pronunciation_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_009",
                    check_name="naming_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Name evaluation subsection missing ease of pronunciation measure (expected question with 'easy to say', 'pronounce', 'pronunciation', or 'say out loud')",
                    action_taken=None
                ))
        
        # Check 3: Each name subsection must include memorability
        memorability_keywords = ["remember", "memorable", "recall", "stick in your mind"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, memorability_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_009",
                    check_name="naming_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Name evaluation subsection missing memorability measure (expected question with 'remember', 'memorable', 'recall', or 'stick in your mind')",
                    action_taken=None
                ))
        
        # Check 4: Each name subsection must include brand fit
        brand_fit_keywords = ["fit", "appropriate", "suitable", "right for"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, brand_fit_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_009",
                    check_name="naming_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Name evaluation subsection missing brand fit/appropriateness measure (expected question with 'fit', 'appropriate', 'suitable', or 'right for')",
                    action_taken=None
                ))
        
        # Check 5: Individual evaluation before comparison
        main = self.survey.get("MAIN_SECTION", {})
        subsections = main.get("sub_sections", [])
        
        comparative_keywords = ["prefer", "rank", "compare", "which name"]
        
        first_comparative_idx = None
        last_individual_idx = None
        
        for idx, subsec in enumerate(subsections):
            has_stimulus = any(
                q.get("question_type") == "stimulus_display"
                for q in subsec.get("questions", [])
            )
            has_comparative = any(
                self._text_contains_any(q.get("question_text", ""), comparative_keywords)
                for q in subsec.get("questions", [])
            )
            
            if has_comparative and first_comparative_idx is None:
                first_comparative_idx = idx
            if has_stimulus:
                last_individual_idx = idx
        
        if first_comparative_idx is not None and last_individual_idx is not None:
            if first_comparative_idx < last_individual_idx:
                self.results.append(ValidationResult(
                    check_id="METH_009",
                    check_name="naming_testing",
                    severity="warning",
                    question_id=None,
                    section="MAIN_SECTION",
                    message="Comparative name questions appear before all individual name evaluations — names should be evaluated in isolation before any comparison",
                    action_taken=None
                ))
    
    # ========================================================================
    # METH_010: pack_testing
    # ========================================================================
    def _check_pack_testing(self):
        """Validate pack testing design."""
        artefacts = self._get_artefacts()
        artefact_to_subsection = self._get_stimulus_questions()
        eval_subsections = self._get_evaluation_subsections()
        
        # Check 1: Every pack artefact must have stimulus_display
        for artefact in artefacts:
            artefact_id = artefact.get("artefact_id")
            if artefact_id not in artefact_to_subsection:
                self.results.append(ValidationResult(
                    check_id="METH_010",
                    check_name="pack_testing",
                    severity="error",
                    question_id=None,
                    section="STUDY_METADATA",
                    message=f"Pack artefact '{artefact_id}' has no corresponding stimulus_display question",
                    action_taken=None
                ))
        
        # Check 2: At least one question should measure shelf standout
        standout_keywords = ["stand out", "notice", "shelf", "eye-catching", "visible"]
        main = self.survey.get("MAIN_SECTION", {})
        has_standout = False
        
        for subsec in main.get("sub_sections", []):
            if self._subsection_has_pattern(subsec, standout_keywords):
                has_standout = True
                break
        
        if not has_standout:
            self.results.append(ValidationResult(
                check_id="METH_010",
                check_name="pack_testing",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message="Pack testing missing shelf standout/visibility measure (expected question with 'stand out', 'notice', 'shelf', 'eye-catching', or 'visible')",
                action_taken=None
            ))
        
        # Check 3: Standout should be measured before detailed evaluation
        subsections = main.get("sub_sections", [])
        standout_idx = None
        detail_keywords = ["appeal", "like", "rate", "purchase intent", "communicate"]
        detail_idx = None
        
        for idx, subsec in enumerate(subsections):
            if standout_idx is None and self._subsection_has_pattern(subsec, standout_keywords):
                standout_idx = idx
            if detail_idx is None and self._subsection_has_pattern(subsec, detail_keywords):
                detail_idx = idx
        
        if standout_idx is not None and detail_idx is not None and standout_idx > detail_idx:
            self.results.append(ValidationResult(
                check_id="METH_010",
                check_name="pack_testing",
                severity="warning",
                question_id=None,
                section="MAIN_SECTION",
                message="Standout/visibility measure appears after detailed evaluation questions — standout should be measured before detailed pack evaluation",
                action_taken=None
            ))
        
        # Check 4: Each pack subsection must include communication measure
        communication_keywords = ["communicate", "tells you", "expect", "what does this"]
        for subsec in eval_subsections:
            if not self._subsection_has_pattern(subsec, communication_keywords):
                subsec_id = subsec.get("section_id")
                self.results.append(ValidationResult(
                    check_id="METH_010",
                    check_name="pack_testing",
                    severity="warning",
                    question_id=None,
                    section=subsec_id,
                    message="Pack evaluation subsection missing communication measure (expected question with 'communicate', 'tells you', 'expect', or 'what does this')",
                    action_taken=None
                ))
        
        # Check 5: Consistent structure across pack subsections
        self._check_subsection_consistency(eval_subsections, "METH_010", "pack_testing")

    # ========================================================================
    # OPTIONAL SECTION VALIDATORS (V2 Schema)
    # ========================================================================
    
    def _run_optional_section_validators(self):
        """Validate optional V2 schema sections (warnings if present but malformed)."""
        self._check_sample_requirements_section()
        self._check_programming_specifications_section()
        self._check_analysis_plan_section()
        self._check_question_v2_fields()
    
    def _check_sample_requirements_section(self):
        """Validate SAMPLE_REQUIREMENTS section if present."""
        sample_req = self.survey.get("SAMPLE_REQUIREMENTS")
        if sample_req and isinstance(sample_req, dict):
            if not sample_req.get("total_sample"):
                self.results.append(ValidationResult(
                    check_id="V2_001",
                    check_name="sample_requirements_completeness",
                    severity="warning",
                    question_id=None,
                    section="SAMPLE_REQUIREMENTS",
                    message="SAMPLE_REQUIREMENTS section exists but total_sample is missing",
                    action_taken=None,
                    suggestion="Specify target sample size"
                ))
            
            # Check if qualification_criteria is empty
            if not sample_req.get("qualification_criteria"):
                self.results.append(ValidationResult(
                    check_id="V2_001",
                    check_name="sample_requirements_completeness",
                    severity="warning",
                    question_id=None,
                    section="SAMPLE_REQUIREMENTS",
                    message="SAMPLE_REQUIREMENTS section exists but qualification_criteria is empty",
                    action_taken=None,
                    suggestion="Add audience qualification criteria"
                ))
    
    def _check_programming_specifications_section(self):
        """Validate PROGRAMMING_SPECIFICATIONS section if present."""
        prog_spec = self.survey.get("PROGRAMMING_SPECIFICATIONS")
        if prog_spec and isinstance(prog_spec, dict):
            loi_breakdown = prog_spec.get("loi_breakdown")
            if loi_breakdown and isinstance(loi_breakdown, dict):
                # Check if LOI breakdown sections match actual survey sections
                valid_sections = {"SCREENER", "MAIN_SECTION", "DEMOGRAPHICS"}
                breakdown_sections = set(loi_breakdown.keys())
                invalid_sections = breakdown_sections - valid_sections
                
                if invalid_sections:
                    self.results.append(ValidationResult(
                        check_id="V2_002",
                        check_name="programming_specifications_validity",
                        severity="warning",
                        question_id=None,
                        section="PROGRAMMING_SPECIFICATIONS",
                        message=f"LOI breakdown references unknown sections: {sorted(invalid_sections)}",
                        action_taken=None,
                        suggestion="Update section names to match survey structure (SCREENER, MAIN_SECTION, DEMOGRAPHICS)"
                    ))
            
            # Check if quality_controls is empty
            if not prog_spec.get("quality_controls"):
                self.results.append(ValidationResult(
                    check_id="V2_002",
                    check_name="programming_specifications_validity",
                    severity="warning",
                    question_id=None,
                    section="PROGRAMMING_SPECIFICATIONS",
                    message="PROGRAMMING_SPECIFICATIONS section exists but quality_controls is empty",
                    action_taken=None,
                    suggestion="Add quality control measures"
                ))
    
    def _check_analysis_plan_section(self):
        """Validate ANALYSIS_PLAN section if present."""
        analysis_plan = self.survey.get("ANALYSIS_PLAN")
        if analysis_plan and isinstance(analysis_plan, dict):
            if not analysis_plan.get("primary_analyses"):
                self.results.append(ValidationResult(
                    check_id="V2_003",
                    check_name="analysis_plan_completeness",
                    severity="warning",
                    question_id=None,
                    section="ANALYSIS_PLAN",
                    message="ANALYSIS_PLAN section exists but primary_analyses is empty",
                    action_taken=None,
                    suggestion="Add at least one primary analysis method"
                ))
            
            if not analysis_plan.get("deliverables") and not analysis_plan.get("strategic_outputs"):
                self.results.append(ValidationResult(
                    check_id="V2_003",
                    check_name="analysis_plan_completeness",
                    severity="warning",
                    question_id=None,
                    section="ANALYSIS_PLAN",
                    message="ANALYSIS_PLAN section exists but both deliverables and strategic_outputs are empty",
                    action_taken=None,
                    suggestion="Specify expected deliverables or strategic outputs"
                ))
    
    def _check_question_v2_fields(self):
        """Check V2 question fields (numeric_input type, required, notes)."""
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            for q in section.get("questions", []):
                self._validate_v2_question_fields(q, section_name)
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            for q in subsec.get("questions", []):
                self._validate_v2_question_fields(q, subsec.get("subsection_id"))
    
    def _validate_v2_question_fields(self, q: dict, section: str):
        """Validate V2-specific question fields."""
        qtype = q.get("question_type")
        qid = q.get("question_id")
        
        # Validate numeric_input type
        if qtype == "numeric_input":
            if q.get("options"):
                q["options"] = []
                self.results.append(ValidationResult(
                    check_id="V2_004",
                    check_name="question_v2_field_compatibility",
                    severity="auto_fix",
                    question_id=qid,
                    section=section,
                    message="numeric_input questions must have empty options",
                    action_taken="Cleared options array"
                ))
        
        # Ensure required field exists (default to True if missing)
        if "required" not in q:
            q["required"] = True
            self.results.append(ValidationResult(
                check_id="V2_004",
                check_name="question_v2_field_compatibility",
                severity="auto_fix",
                question_id=qid,
                section=section,
                message="Missing 'required' field",
                action_taken="Set required to True (default)"
            ))
    
    # ========================================================================
    # QUALITY ADVISORIES (V2 Schema)
    # ========================================================================
    
    def _run_quality_advisories(self):
        """Generate advisory-level quality suggestions."""
        self._check_missing_optional_sections()
        self._check_question_notes_coverage()
        self._check_subsection_purposes()
        self._check_estimated_loi()
    
    def _check_missing_optional_sections(self):
        """Advisory if optional V2 sections are missing."""
        if not self.survey.get("SAMPLE_REQUIREMENTS"):
            self.results.append(ValidationResult(
                check_id="ADV_001",
                check_name="missing_optional_sections",
                severity="advisory",
                question_id=None,
                section="Root",
                message="Survey is missing SAMPLE_REQUIREMENTS section",
                action_taken=None,
                suggestion="Add sample requirements for better project documentation"
            ))
        
        if not self.survey.get("PROGRAMMING_SPECIFICATIONS"):
            self.results.append(ValidationResult(
                check_id="ADV_001",
                check_name="missing_optional_sections",
                severity="advisory",
                question_id=None,
                section="Root",
                message="Survey is missing PROGRAMMING_SPECIFICATIONS section",
                action_taken=None,
                suggestion="Add programming specs to guide survey implementation"
            ))
        
        if not self.survey.get("ANALYSIS_PLAN"):
            self.results.append(ValidationResult(
                check_id="ADV_001",
                check_name="missing_optional_sections",
                severity="advisory",
                question_id=None,
                section="Root",
                message="Survey is missing ANALYSIS_PLAN section",
                action_taken=None,
                suggestion="Add analysis plan to clarify research deliverables"
            ))
    
    def _check_question_notes_coverage(self):
        """Advisory if no questions have notes/rationale."""
        questions = []
        
        for section_name in ["SCREENER", "DEMOGRAPHICS"]:
            section = self.survey.get(section_name, {})
            questions.extend(section.get("questions", []))
        
        main = self.survey.get("MAIN_SECTION", {})
        for subsec in main.get("sub_sections", []):
            questions.extend(subsec.get("questions", []))
        
        questions_with_notes = sum(1 for q in questions if q.get("notes"))
        
        if questions_with_notes == 0 and len(questions) > 0:
            self.results.append(ValidationResult(
                check_id="ADV_002",
                check_name="question_notes_coverage",
                severity="advisory",
                question_id=None,
                section="Questions",
                message="No questions have notes/rationale",
                action_taken=None,
                suggestion="Add notes to questions to document programming intent and analysis purpose"
            ))
    
    def _check_subsection_purposes(self):
        """Advisory if subsections lack purpose statements."""
        main = self.survey.get("MAIN_SECTION", {})
        subsections = main.get("sub_sections", [])
        subsections_with_purpose = sum(1 for s in subsections if s.get("purpose"))
        
        if subsections_with_purpose == 0 and len(subsections) > 0:
            self.results.append(ValidationResult(
                check_id="ADV_003",
                check_name="subsection_purposes",
                severity="advisory",
                question_id=None,
                section="MAIN_SECTION",
                message="No subsections have purpose statements",
                action_taken=None,
                suggestion="Add purpose to subsections to document measurement intent"
            ))
    
    def _check_estimated_loi(self):
        """Advisory if estimated LOI is missing."""
        metadata = self.survey.get("STUDY_METADATA", {})
        if not metadata.get("estimated_loi_minutes"):
            self.results.append(ValidationResult(
                check_id="ADV_004",
                check_name="estimated_loi",
                severity="advisory",
                question_id=None,
                section="STUDY_METADATA",
                message="Study metadata missing estimated_loi_minutes",
                action_taken=None,
                suggestion="Add estimated LOI to help with project planning"
            ))


def main():
    """Main entry point for validation pipeline."""
    # Load inputs
    survey_path = Path("survey_output.json")
    brief_path = Path("brief_output.json")
    
    if not survey_path.exists():
        print(f"❌ Error: {survey_path} not found")
        sys.exit(1)
    
    if not brief_path.exists():
        print(f"❌ Error: {brief_path} not found")
        sys.exit(1)
    
    survey = json.loads(survey_path.read_text(encoding="utf-8"))
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    
    # Run validation
    validator = SurveyValidator(survey, brief)
    patched_survey, results = validator.validate()
    
    # Write outputs
    Path("survey_output_validated.json").write_text(
        json.dumps(patched_survey, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # Build log
    log = {
        "status": "failed" if any(r.severity == "error" for r in results) else "passed",
        "summary": {
            "errors": sum(1 for r in results if r.severity == "error"),
            "warnings": sum(1 for r in results if r.severity == "warning"),
            "auto_fixes": sum(1 for r in results if r.severity == "auto_fix"),
            "advisories": sum(1 for r in results if r.severity == "advisory")
        },
        "checks": [r.to_dict() for r in results]
    }
    
    Path("validation_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # Print summary
    errors = [r for r in results if r.severity == "error"]
    if errors:
        print(f"❌ Validation FAILED — {len(errors)} error(s)")
        for e in errors:
            section_info = f" [{e.section}]" if e.section else ""
            qid_info = f" {e.question_id}" if e.question_id else ""
            print(f"  {e.check_id}{section_info}{qid_info}: {e.message}")
        sys.exit(1)
    else:
        fixes = sum(1 for r in results if r.severity == "auto_fix")
        warns = sum(1 for r in results if r.severity == "warning")
        advisories = sum(1 for r in results if r.severity == "advisory")
        print(f"✅ Validation passed — {fixes} auto-fix(es), {warns} warning(s), {advisories} advisory/ies")
        
        if fixes > 0:
            print("\nAuto-fixes applied:")
            for r in results:
                if r.severity == "auto_fix":
                    section_info = f" [{r.section}]" if r.section else ""
                    qid_info = f" {r.question_id}" if r.question_id else ""
                    print(f"  {r.check_id}{section_info}{qid_info}: {r.action_taken}")
        
        if warns > 0:
            print("\nWarnings:")
            for r in results:
                if r.severity == "warning":
                    section_info = f" [{r.section}]" if r.section else ""
                    qid_info = f" {r.question_id}" if r.question_id else ""
                    print(f"  {r.check_id}{section_info}{qid_info}: {r.message}")
                    if r.suggestion:
                        print(f"    → {r.suggestion}")
        
        if advisories > 0:
            print("\n💡 Quality Suggestions:")
            for r in results:
                if r.severity == "advisory":
                    section_info = f" [{r.section}]" if r.section else ""
                    print(f"  {r.check_id}{section_info}: {r.message}")
                    if r.suggestion:
                        print(f"    → {r.suggestion}")


if __name__ == "__main__":
    main()
