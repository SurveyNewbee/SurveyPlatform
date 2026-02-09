from __future__ import annotations

import copy
import json
import hashlib
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple, Union


# ----------------------------
# Error model (for targeted repair)
# ----------------------------

@dataclass
class ValidationIssue:
    issue_id: str
    issue_fingerprint: str
    error_code: str
    json_path: str
    message: str
    fragment_ref: Dict[str, Any]
    fragment: Any


# ----------------------------
# JSON Patch (RFC 6902) - minimal support
# ----------------------------

class JsonPatchError(Exception):
    pass


def _split_pointer(path: str) -> List[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise JsonPatchError(f"Invalid JSON pointer: {path}")
    parts = path.lstrip("/").split("/")
    return [p.replace("~1", "/").replace("~0", "~") for p in parts]


def _get_parent_and_key(doc: Any, pointer: str) -> Tuple[Any, Union[str, int]]:
    parts = _split_pointer(pointer)
    if not parts:
        raise JsonPatchError("Pointer must not be empty for parent/key lookup.")

    parent = doc
    for p in parts[:-1]:
        if isinstance(parent, list):
            idx = int(p)
            parent = parent[idx]
        elif isinstance(parent, dict):
            parent = parent[p]
        else:
            raise JsonPatchError(f"Cannot traverse into non-container at '{p}'.")

    last = parts[-1]
    if isinstance(parent, list):
        return parent, int(last)
    return parent, last


def apply_json_patch(doc: Any, patch_ops: List[Dict[str, Any]]) -> Any:
    doc = doc
    for op in patch_ops:
        operation = op.get("op")
        path = op.get("path")
        value = op.get("value")

        if operation not in {"add", "replace", "remove"}:
            raise JsonPatchError(f"Unsupported op: {operation}")
        if path is None:
            raise JsonPatchError("Patch op missing 'path'")

        if operation == "remove":
            parent, key = _get_parent_and_key(doc, path)
            if isinstance(parent, list):
                parent.pop(key)
            else:
                parent.pop(key, None)
            continue

        parent, key = _get_parent_and_key(doc, path)
        if isinstance(parent, list):
            if operation == "add":
                if key == len(parent):
                    parent.append(value)
                else:
                    parent.insert(key, value)
            else:
                parent[key] = value
        else:
            parent[key] = value

    return doc


# ----------------------------
# Core validator/normaliser
# ----------------------------

REQUIRED_TOP_LEVEL_KEYS = [
    "STUDY_METADATA",
    "SCREENER",
    "MAIN_SECTION",
    "DEMOGRAPHICS",
    "FLOW",
    "DIMENSION_COVERAGE_SUMMARY",
]

ALLOWED_Q_TYPES = {"single_choice", "multiple_choice", "scale", "matrix", "open_ended", "stimulus_display", "numeric_input", "ranking"}


def _fingerprint(error_code: str, json_path: str, question_id: Optional[str]) -> str:
    payload = f"{error_code}|{json_path}|{question_id or ''}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _issue_id(counter: int) -> str:
    return f"ISSUE_{counter:04d}"


def validate_and_normalise(survey: Dict[str, Any]) -> Tuple[Dict[str, Any], List[ValidationIssue]]:
    issues: List[ValidationIssue] = []
    s = copy.deepcopy(survey)
    issue_counter = 0

    def add_issue(
        *,
        error_code: str,
        json_path: str,
        message: str,
        fragment_ref: Dict[str, Any],
        fragment: Any,
    ):
        nonlocal issue_counter
        issue_counter += 1
        qid = fragment_ref.get("question_id")
        issues.append(
            ValidationIssue(
                issue_id=_issue_id(issue_counter),
                issue_fingerprint=_fingerprint(error_code, json_path, qid),
                error_code=error_code,
                json_path=json_path,
                message=message,
                fragment_ref=fragment_ref,
                fragment=fragment,
            )
        )

    # Top-level keys
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in s:
            add_issue(
                error_code="E_TOPLEVEL_MISSING_KEY",
                json_path=f"/{k}",
                message=f"Missing top-level key '{k}'.",
                fragment_ref={"section": k},
                fragment={"missing_key": k},
            )

    if issues:
        return s, issues

    def norm_question(q: Dict[str, Any], path: str, fragment_ref: Dict[str, Any]) -> Dict[str, Any]:
        hard_required = ["question_id", "question_text", "question_type"]
        for f in hard_required:
            if f not in q or q.get(f) in (None, ""):
                add_issue(
                    error_code="E_QUESTION_MISSING_REQUIRED",
                    json_path=f"{path}/{f}",
                    message=f"Question missing required field '{f}'.",
                    fragment_ref=fragment_ref,
                    fragment=q,
                )

        if "options" not in q or not isinstance(q.get("options"), list):
            q["options"] = []
        if "rows" not in q:
            q["rows"] = None
        if "columns" not in q:
            q["columns"] = None
        if "display_logic" not in q:
            q["display_logic"] = None
        if "piping" not in q:
            q["piping"] = None
        if "required" not in q:
            q["required"] = True
        if "notes" not in q:
            q["notes"] = None

        qtype = q.get("question_type")
        if qtype not in ALLOWED_Q_TYPES:
            add_issue(
                error_code="E_QUESTION_BAD_TYPE",
                json_path=f"{path}/question_type",
                message=f"Invalid question_type '{qtype}'. Allowed: {sorted(ALLOWED_Q_TYPES)}",
                fragment_ref=fragment_ref,
                fragment=q,
            )

        options = q.get("options")
        if not isinstance(options, list):
            add_issue(
                error_code="E_OPTIONS_NOT_ARRAY",
                json_path=f"{path}/options",
                message="Field 'options' must be an array.",
                fragment_ref=fragment_ref,
                fragment=q,
            )
            q["options"] = []

        if qtype in {"open_ended", "matrix", "numeric_input"}:
            if q.get("options") != []:
                add_issue(
                    error_code="E_OPTIONS_MUST_BE_EMPTY",
                    json_path=f"{path}/options",
                    message=f"For question_type '{qtype}', options must be [].",
                    fragment_ref=fragment_ref,
                    fragment=q,
                )
                q["options"] = []

        if qtype in {"single_choice", "multiple_choice", "scale", "ranking"}:
            if len(q.get("options", [])) == 0:
                add_issue(
                    error_code="E_OPTIONS_REQUIRED",
                    json_path=f"{path}/options",
                    message=f"For question_type '{qtype}', options must be non-empty.",
                    fragment_ref=fragment_ref,
                    fragment=q,
                )

        if qtype == "matrix":
            if not q.get("rows") or not q.get("columns"):
                add_issue(
                    error_code="E_MATRIX_MISSING_ROWS_COLS",
                    json_path=path,
                    message="Matrix questions require non-empty 'rows' and 'columns'.",
                    fragment_ref=fragment_ref,
                    fragment=q,
                )
                q["rows"] = q.get("rows") or []
                q["columns"] = q.get("columns") or []
        else:
            if q.get("rows") is not None or q.get("columns") is not None:
                q["rows"] = None
                q["columns"] = None

        return q

    seen_qids = set()

    def validate_questions_block(
        questions: List[Dict[str, Any]],
        base_path: str,
        fragment_ref_base: Dict[str, Any],
    ):
        nonlocal seen_qids
        if not isinstance(questions, list):
            add_issue(
                error_code="E_QUESTIONS_NOT_ARRAY",
                json_path=base_path,
                message="Questions block must be an array.",
                fragment_ref=fragment_ref_base,
                fragment=questions,
            )
            return

        for i, q in enumerate(questions):
            q_path = f"{base_path}/{i}"
            if not isinstance(q, dict):
                add_issue(
                    error_code="E_QUESTION_NOT_OBJECT",
                    json_path=q_path,
                    message="Each question must be a JSON object.",
                    fragment_ref=fragment_ref_base,
                    fragment=q,
                )
                continue

            fragment_ref = dict(fragment_ref_base)
            fragment_ref["question_id"] = q.get("question_id")
            q = norm_question(q, q_path, fragment_ref)
            qid = q.get("question_id")
            if qid in seen_qids:
                add_issue(
                    error_code="E_DUPLICATE_QUESTION_ID",
                    json_path=f"{q_path}/question_id",
                    message=f"Duplicate question_id '{qid}'.",
                    fragment_ref=fragment_ref,
                    fragment=q,
                )
            else:
                seen_qids.add(qid)

    # Screener
    validate_questions_block(
        s["SCREENER"].get("questions"),
        "/SCREENER/questions",
        {"section": "SCREENER"},
    )

    # Main sections
    sub_sections = s["MAIN_SECTION"].get("sub_sections")
    if not isinstance(sub_sections, list):
        add_issue(
            error_code="E_SUBSECTIONS_NOT_ARRAY",
            json_path="/MAIN_SECTION/sub_sections",
            message="MAIN_SECTION.sub_sections must be an array.",
            fragment_ref={"section": "MAIN_SECTION"},
            fragment=sub_sections,
        )
    else:
        seen_ss_ids = set()
        for si, ss in enumerate(sub_sections):
            ss_path = f"/MAIN_SECTION/sub_sections/{si}"
            if not isinstance(ss, dict):
                add_issue(
                    error_code="E_SUBSECTION_NOT_OBJECT",
                    json_path=ss_path,
                    message="Each sub_section must be an object.",
                    fragment_ref={"section": "MAIN_SECTION"},
                    fragment=ss,
                )
                continue

            ss_id = ss.get("subsection_id")
            fragment_ref = {"section": "MAIN_SECTION", "subsection_id": ss_id}
            if not ss_id:
                add_issue(
                    error_code="E_SUBSECTION_MISSING_ID",
                    json_path=f"{ss_path}/subsection_id",
                    message="subsection_id is required.",
                    fragment_ref=fragment_ref,
                    fragment=ss,
                )
            elif ss_id in seen_ss_ids:
                add_issue(
                    error_code="E_DUPLICATE_SUBSECTION_ID",
                    json_path=f"{ss_path}/subsection_id",
                    message=f"Duplicate subsection_id '{ss_id}'.",
                    fragment_ref=fragment_ref,
                    fragment=ss,
                )
            else:
                seen_ss_ids.add(ss_id)

            validate_questions_block(
                ss.get("questions"),
                f"{ss_path}/questions",
                fragment_ref,
            )

    # Demographics
    validate_questions_block(
        s["DEMOGRAPHICS"].get("questions"),
        "/DEMOGRAPHICS/questions",
        {"section": "DEMOGRAPHICS"},
    )

    # Flow
    flow = s.get("FLOW", {})
    if "routing_rules" in flow and not isinstance(flow["routing_rules"], list):
        add_issue(
            error_code="E_ROUTING_RULES_NOT_ARRAY",
            json_path="/FLOW/routing_rules",
            message="FLOW.routing_rules must be an array.",
            fragment_ref={"section": "FLOW"},
            fragment=flow.get("routing_rules"),
        )

    # Dimension coverage summary
    summary = s.get("DIMENSION_COVERAGE_SUMMARY")
    if summary is not None and not isinstance(summary, list):
        add_issue(
            error_code="E_DIMENSION_SUMMARY_NOT_ARRAY",
            json_path="/DIMENSION_COVERAGE_SUMMARY",
            message="DIMENSION_COVERAGE_SUMMARY must be an array.",
            fragment_ref={"section": "DIMENSION_COVERAGE_SUMMARY"},
            fragment=summary,
        )

    return s, issues


# ----------------------------
# Rendering to UI spec
# ----------------------------

def render_ui_spec(survey: Dict[str, Any]) -> Dict[str, Any]:
    md = survey["STUDY_METADATA"]
    artefacts = md.get("artefacts", [])
    question_ids = _collect_question_ids(survey)
    routing_index, rule_metadata = _build_routing_index(survey.get("FLOW", {}), question_ids)
    
    # Create artefact lookup for conjoint display
    artefacts_by_id = {a.get("artefact_id"): a for a in artefacts}

    blocks: List[Dict[str, Any]] = []

    blocks.append(
        {
            "block_type": "study_header",
            "title": "Study Overview",
            "items": [
                {"label": "Study Type", "value": md.get("study_type")},
                {"label": "Description", "value": md.get("description")},
                {"label": "Estimated LOI", "value": f"{md.get('estimated_loi_minutes')} minutes" if md.get('estimated_loi_minutes') else None},
            ],
            "completeness": calculate_completeness(survey)
        }
    )
    
    # SAMPLE_REQUIREMENTS section (V2 - optional)
    sample_req = survey.get("SAMPLE_REQUIREMENTS")
    if sample_req:
        blocks.append(
            {
                "block_type": "sample_requirements",
                "title": "Sample Requirements",
                "total_sample": sample_req.get("total_sample"),
                "target_audience_summary": sample_req.get("target_audience_summary"),
                "qualification_criteria": sample_req.get("qualification_criteria", []),
                "hard_quotas": sample_req.get("hard_quotas"),
                "soft_quotas": sample_req.get("soft_quotas"),
                "exclusions": sample_req.get("exclusions", [])
            }
        )

    if artefacts:
        blocks.append(
            {
                "block_type": "artefacts",
                "title": "Stimuli / Artefacts",
                "artefacts": [
                    {
                        "artefact_id": a.get("artefact_id"),
                        "artefact_type": a.get("artefact_type"),
                        "title": a.get("title"),
                        "content": a.get("content"),
                        "parsed": _parse_conjoint_configuration(a.get("content")),
                    }
                    for a in artefacts
                ],
            }
        )

    # Configuration Summary (for conjoint studies)
    config_summary = _generate_configuration_summary(survey)
    if config_summary:
        blocks.append(
            {
                "block_type": "configuration_summary",
                "title": "Configuration Summary",
                "description": "Structural verification of conjoint choice tasks",
                "summary": config_summary
            }
        )

    # Add artefact assignments summary if detected
    artefact_assignments = _detect_artefact_assignment_rules(survey.get("FLOW", {}))
    if artefact_assignments:
        blocks.append(
            {
                "block_type": "artefact_assignments",
                "title": "Artefact Randomization & Assignment",
                "assignments": [
                    {
                        "assignment_id": key,
                        "method": info["method"],
                        "artefacts": info["artefacts"],
                        "description": info["description"],
                        "rule_id": info["rule_id"]
                    }
                    for key, info in artefact_assignments.items()
                ]
            }
        )
    
    # Build quota summary block
    quota_questions = [
        q for q in survey.get("SCREENER", {}).get("questions", [])
        if q.get("quota_attribute")
    ]
    
    if quota_questions:
        quota_summary_block = {
            "block_type": "quota_summary",
            "title": "Sample Quotas",
            "quotas": []
        }
        for q in quota_questions:
            quota_entry = {
                "attribute": q["quota_attribute"],
                "type": q.get("quota_type", "unknown"),
                "linked_question": q["question_id"],
                "groups": q.get("quota_groups", [])
            }
            quota_summary_block["quotas"].append(quota_entry)
        
        blocks.append(quota_summary_block)

    # Build artefact name/letter to ID mapping for concept detection
    artefact_map = {}
    artefacts = survey.get("STUDY_METADATA", {}).get("artefacts", [])
    for art in artefacts:
        art_id = art.get("artefact_id", "")
        title = art.get("title", "")
        # Extract letter from titles like "Concept A:", "Concept B:"
        letter_match = re.search(r'Concept\s+([A-Z])', title, re.IGNORECASE)
        if letter_match and art_id:
            artefact_map[letter_match.group(1).upper()] = art_id

    def q_display(q: Dict[str, Any], number: str, artefacts_by_id: Dict[str, Any] = None) -> Dict[str, Any]:
        qid = q.get("question_id")
        qtype = q.get("question_type")
        options_for_ui = _normalise_options_for_ui(q)
        
        if artefacts_by_id is None:
            artefacts_by_id = {}

        annotations: List[Dict[str, str]] = []
        
        # V2: Add notes to annotations if present
        if q.get("notes"):
            annotations.append({"type": "notes", "text": f"Notes: {q['notes']}"})
        
        if q.get("display_logic"):
            annotations.append({"type": "display_logic", "text": f"Display if: {q['display_logic']}"})
        if q.get("piping"):
            annotations.append({"type": "piping", "text": f"Piping: {q['piping']}"})
        
        # Quota annotation
        quota_attr = q.get("quota_attribute")
        if quota_attr:
            quota_groups = q.get("quota_groups", [])
            if quota_groups:
                group_summary = ", ".join(
                    f"{g['label']}: min {g.get('min', '—')}"
                    for g in quota_groups
                )
                annotations.append({
                    "type": "quota",
                    "text": f"Quota attribute: {quota_attr} — {group_summary}"
                })

        routing = routing_index.get(qid, {"shown_by_rules": [], "skipped_by_rules": [], "terminate_by_rules": []})
        
        # Generate user-centric routing annotations
        if routing["terminate_by_rules"]:
            # Termination rules: explain when survey ends
            termination_texts = []
            for rule_id in routing["terminate_by_rules"]:
                if rule_id in rule_metadata:
                    plain = rule_metadata[rule_id]["plain_condition"]
                    if plain:
                        termination_texts.append(f"Ends survey if {plain}.")
            if termination_texts:
                annotations.append({"type": "routing", "text": " ".join(termination_texts)})
        
        elif routing["shown_by_rules"]:
            # Show rules: explain when question is asked (answer-centric)
            show_conditions = []
            for rule_id in routing["shown_by_rules"]:
                if rule_id in rule_metadata:
                    plain = rule_metadata[rule_id]["plain_condition"]
                    if plain:
                        show_conditions.append(plain)
            
            if show_conditions:
                if len(show_conditions) == 1:
                    text = f"Asked only if {show_conditions[0]}."
                else:
                    # Multiple conditions (OR logic typically)
                    text = f"Asked if {' or '.join(show_conditions)}."
                annotations.append({"type": "routing", "text": text})

        meta = {
            "type_label": _type_label(qtype),
            "answer_format": _answer_format(qtype),
            "option_count": len(options_for_ui) if qtype in {"single_choice", "multiple_choice", "scale", "ranking"} else 0,
            "is_routed": bool(routing["shown_by_rules"] or routing["skipped_by_rules"] or routing["terminate_by_rules"]),
            "required": q.get("required", True),  # V2: Add required field
        }
        
        # Add quota metadata to meta
        if quota_attr:
            meta["quota_attribute"] = quota_attr
            meta["quota_groups"] = quota_groups
            meta["quota_type"] = q.get("quota_type")

        # Detect artefact display requirements
        artefact_refs = _extract_artefact_references(q.get("question_text", ""), artefact_map)
        if q.get("piping"):
            piping = q["piping"]
            if isinstance(piping, dict):
                if 'artefact_display' in piping:
                    artefact_refs.append(piping['artefact_display'])
            elif isinstance(piping, str):
                artefact_refs.extend(_extract_artefact_references(piping, artefact_map))
        
        if artefact_refs:
            meta["displays_artefacts"] = sorted(set(artefact_refs))

        # Add minimum exposure time if specified
        if q.get("piping") and isinstance(q["piping"], dict):
            if "minimum_exposure_seconds" in q["piping"]:
                meta["minimum_exposure_seconds"] = q["piping"]["minimum_exposure_seconds"]

        # Check if this question displays an artefact
        # Priority 1: stimulus_display type uses displays_artefact field directly
        # Priority 2: routing-based artefact assignment (for conjoint, etc.)
        displays_artefact_id = None
        if qtype == "stimulus_display":
            displays_artefact_id = q.get("displays_artefact")
        else:
            displays_artefact_id = routing.get("displays_artefact")
        
        artefact_content = None
        
        if displays_artefact_id and displays_artefact_id in artefacts_by_id:
            # Artefact-based display (when artefact content exists separately)
            artefact = artefacts_by_id[displays_artefact_id]
            artefact_content = {
                "artefact_id": artefact.get("artefact_id"),
                "artefact_type": artefact.get("artefact_type"),
                "title": artefact.get("title"),
                "content": artefact.get("content"),
                "parsed": _parse_conjoint_configuration(artefact.get("content"))
            }
        else:
            # Inline conjoint in question text (current survey format)
            # Parse question text directly for configurations
            parsed_configs = _parse_conjoint_configuration(q.get("question_text", ""))
            if parsed_configs:
                artefact_content = {
                    "artefact_id": None,  # Inline, no separate artefact
                    "artefact_type": "inline_conjoint",
                    "title": f"Conjoint Task: {qid}",
                    "content": q.get("question_text", ""),
                    "parsed": parsed_configs
                }

        d = {
            "number": number,
            "question_id": qid,
            "question_text": q.get("question_text"),
            "question_type": qtype,
            "options": options_for_ui if qtype in {"single_choice", "multiple_choice", "scale", "ranking"} else [],
            "rows": q.get("rows"),
            "columns": q.get("columns"),
            "display_logic": q.get("display_logic"),
            "piping": q.get("piping"),
            "annotations": annotations,
            "meta": meta,
            "routing": routing,
            "displays_artefact": artefact_content,
        }
        if annotations:
            d["annotation_text"] = [a["text"] for a in annotations]
        return d

    screener_qs = survey["SCREENER"]["questions"]
    blocks.append(
        {
            "block_type": "section",
            "section_id": "SCREENER",
            "title": "Screener",
            "questions": [q_display(q, f"S{i+1}", artefacts_by_id) for i, q in enumerate(screener_qs)],
        }
    )

    sub_sections = survey["MAIN_SECTION"]["sub_sections"]
    for ss_idx, ss in enumerate(sub_sections, start=1):
        qs = ss.get("questions", [])
        subsection_id = ss.get("subsection_id", f"MS{ss_idx}")
        blocks.append(
            {
                "block_type": "subsection",
                "section_id": "MAIN_SECTION",
                "subsection_id": subsection_id,
                "purpose": ss.get("purpose"),  # V2: Add purpose field
                "title": ss.get("subsection_title", f"Main Subsection {ss_idx}"),
                "questions": [q_display(q, f"{subsection_id}.{qi+1}", artefacts_by_id) for qi, q in enumerate(qs)],
            }
        )

    demo_qs = survey["DEMOGRAPHICS"]["questions"]
    blocks.append(
        {
            "block_type": "section",
            "section_id": "DEMOGRAPHICS",
            "title": "Demographics",
            "questions": [q_display(q, f"D{i+1}", artefacts_by_id) for i, q in enumerate(demo_qs)],
        }
    )
    
    # PROGRAMMING_SPECIFICATIONS section (V2 - optional)
    prog_spec = survey.get("PROGRAMMING_SPECIFICATIONS")
    if prog_spec:
        blocks.append(
            {
                "block_type": "programming_specifications",
                "title": "Programming Specifications",
                "estimated_loi_minutes": prog_spec.get("estimated_loi_minutes"),
                "loi_breakdown": prog_spec.get("loi_breakdown", {}),
                "quality_controls": prog_spec.get("quality_controls", []),
                "mobile_optimization": prog_spec.get("mobile_optimization"),
                "progress_indicator": prog_spec.get("progress_indicator"),
                "quota_management": prog_spec.get("quota_management"),
                "randomization_notes": prog_spec.get("randomization_notes")
            }
        )
    
    # ANALYSIS_PLAN section (V2 - optional)
    analysis_plan = survey.get("ANALYSIS_PLAN")
    if analysis_plan:
        blocks.append(
            {
                "block_type": "analysis_plan",
                "title": "Analysis Plan",
                "primary_analyses": analysis_plan.get("primary_analyses", []),
                "deliverables": analysis_plan.get("deliverables", []),
                "strategic_outputs": analysis_plan.get("strategic_outputs", [])
            }
        )

    flow = survey["FLOW"]
    routing_rules = flow.get("routing_rules", [])
    blocks.append(
        {
            "block_type": "appendix",
            "title": "Flow, Routing & Assignments",
            "description": flow.get("summary"),
            "routing_rules": routing_rules,
        }
    )

    blocks.append(
        {
            "block_type": "appendix",
            "title": "Dimension Coverage Summary",
            "items": survey.get("DIMENSION_COVERAGE_SUMMARY", []),
        }
    )

    return {
        "ui_spec_version": "1.0",
        "study_type": md.get("study_type"),
        "blocks": blocks,
    }


def _type_label(qtype: Optional[str]) -> str:
    return {
        "single_choice": "Single choice",
        "multiple_choice": "Multiple choice",
        "scale": "Scale",
        "matrix": "Matrix",
        "open_ended": "Open ended",
        "numeric_input": "Numeric input",  # V2: Add numeric_input
        "stimulus_display": "Stimulus display",
        "ranking": "Ranking",
    }.get(qtype or "", "")


def _answer_format(qtype: Optional[str]) -> str:
    return {
        "single_choice": "Select one",
        "multiple_choice": "Select one or more",
        "scale": "Select one",
        "matrix": "One response per row",
        "numeric_input": "Enter number",  # V2: Add numeric_input
        "open_ended": "Free text",
        "stimulus_display": "Read only — no response collected",
        "ranking": "Rank items in order",
    }.get(qtype or "", "")


def _normalise_options_for_ui(q: Dict[str, Any]) -> List[Dict[str, str]]:
    options = q.get("options") or []
    if not isinstance(options, list):
        return []

    def parse_leading_int(label: str) -> Optional[int]:
        match = re.match(r"^(\d+)(?:\s*-\s*.*)?$", label)
        if match:
            return int(match.group(1))
        return None

    labels = [str(opt).strip() for opt in options]
    parsed = [parse_leading_int(label) for label in labels]
    nps_candidates = {v for v in parsed if v is not None and 0 <= v <= 10}
    is_nps = nps_candidates == set(range(0, 11))

    if is_nps:
        used = {v for v in parsed if v is not None and 0 <= v <= 10}
        result: List[Dict[str, str]] = []
        for idx, opt in enumerate(options):
            label = str(opt)
            nps_value = parsed[idx]
            if nps_value is not None and 0 <= nps_value <= 10:
                code = str(nps_value)
            else:
                code = str(len(used))
                used.add(len(used))
            result.append({"code": code, "label": label})
        return result

    return [{"code": str(idx + 1), "label": str(opt)} for idx, opt in enumerate(options)]


def _condition_to_plain_language(condition: str) -> str:
    """Convert a rule condition to user-friendly plain language."""
    if not condition:
        return ""
    
    # Remove common technical patterns
    text = condition
    
    # Handle "= 'option text'" pattern
    text = re.sub(r"([A-Z][A-Z0-9_]*)\s*=\s*'([^']+)'", r"you answered '\2'", text)
    
    # Handle "does not include" pattern
    text = re.sub(r"([A-Z][A-Z0-9_]*)\s+does not include\s+'([^']+)'", r"you did not select '\2'", text)
    
    # Handle "includes" pattern
    text = re.sub(r"([A-Z][A-Z0-9_]*)\s+includes?\s+'([^']+)'", r"you selected '\2'", text)
    
    # Clean up AND/OR logic
    text = re.sub(r"\s+AND\s+", " and ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+OR\s+", " or ", text, flags=re.IGNORECASE)
    
    # Lowercase first character if not starting with specific words
    if text and not text.startswith(("You ", "If ")):
        text = text[0].lower() + text[1:] if len(text) > 1 else text.lower()
    
    return text.strip()


def _parse_conjoint_configuration(question_text: str) -> Optional[Dict[str, Any]]:
    """Parse conjoint choice task configurations from question text or artefact content.
    
    Extracts configurations in the format:
    [OPTION A]
    • Attribute: Value
    • Attribute: Value
    
    Args:
        question_text: Question text containing product configurations
        
    Returns:
        Structured configuration data with list of options and their attributes
    """
    if not question_text:
        return None
    
    configs = []
    
    # Split by [OPTION X] markers
    option_pattern = r'\[OPTION\s+([A-Z])\]\s*\n(.*?)(?=\[OPTION\s+[A-Z]\]|$)'
    matches = re.findall(option_pattern, question_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return None
    
    for option_letter, option_text in matches:
        # Extract attributes from bullet points
        attributes = {}
        
        # Match lines starting with bullet (•, -, *) followed by "Attribute: Value"
        attr_pattern = r'[•\-\*]\s*([^:]+):\s*([^\n]+)'
        attr_matches = re.findall(attr_pattern, option_text)
        
        for attr_name, attr_value in attr_matches:
            attributes[attr_name.strip()] = attr_value.strip()
        
        if attributes:
            configs.append({
                'config_id': f'Option {option_letter}',
                'attributes': attributes
            })
    
    return {
        'type': 'choice_task',
        'configurations': configs,
        'attribute_count': len(configs[0]['attributes']) if configs else 0,
        'config_count': len(configs)
    } if configs else None


def _generate_configuration_summary(survey: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate configuration summary for all conjoint questions.
    
    Returns array of metadata objects for the Configuration Summary table.
    """
    summary = []
    
    # Find all questions in MAIN_SECTION that look like conjoint tasks
    main_section = survey.get("MAIN_SECTION", {})
    sub_sections = main_section.get("sub_sections", [])
    
    artefact_counter = 1  # For inferring artefact IDs (A1, A2, A3...)
    
    for subsection in sub_sections:
        questions = subsection.get("questions", [])
        
        for question in questions:
            question_id = question.get("question_id", "")
            question_text = question.get("question_text", "")
            
            # Check if this is a conjoint question
            # (has [OPTION A], [OPTION B], [OPTION C] markers)
            if not re.search(r'\[OPTION\s+[A-Z]\]', question_text, re.IGNORECASE):
                continue
            
            # Parse configurations
            parsed = _parse_conjoint_configuration(question_text)
            
            if parsed and parsed.get('configurations'):
                # Infer artefact ID (A1, A2, A3...) from question order
                # In production, you'd get this from routing rules
                artefact_id = f"A{artefact_counter}"
                artefact_counter += 1
                
                summary.append({
                    "question_id": question_id,
                    "displays_artefact": artefact_id,
                    "configurations": parsed['config_count'],
                    "attributes_per_configuration": parsed['attribute_count']
                })
    
    return summary


def _extract_artefact_references(text: str, artefact_map: Dict[str, str] = None) -> List[str]:
    """Extract artefact IDs from question text or piping.
    
    Args:
        text: Text to search for artefact references
        artefact_map: Optional mapping from concept names/letters to artefact IDs
    """
    if not text:
        return []
    
    artefact_ids = []
    
    # Match patterns like [DISPLAY A1], {{artefact:A1}}, artefact_id="A1"
    matches = re.findall(r'\[DISPLAY\s+([A-Z]\d+)[:\s\]]|\{\{artefact:([A-Z]\d+)\}\}|artefact_id[\'"\']?\s*[:=]\s*[\'"\']?([A-Z]\d+)', text, re.IGNORECASE)
    for match_groups in matches:
        artefact_ids.extend([m for m in match_groups if m])
    
    # Match patterns like [DISPLAY CONCEPT A], [DISPLAY CONCEPT B]
    concept_matches = re.findall(r'\[DISPLAY\s+CONCEPT\s+([A-Z])', text, re.IGNORECASE)
    for letter in concept_matches:
        letter_upper = letter.upper()
        if artefact_map and letter_upper in artefact_map:
            artefact_ids.append(artefact_map[letter_upper])
        else:
            # Default mapping: A→A1, B→A2, C→A3, etc.
            artefact_ids.append(f"A{ord(letter_upper) - ord('A') + 1}")
    
    return sorted(set(artefact_ids))


def _detect_artefact_assignment_rules(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Detect artefact randomization/assignment from routing rules."""
    assignments = {}
    rules = flow.get("routing_rules", [])
    if not isinstance(rules, list):
        return assignments
    
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        action = str(rule.get("action", ""))
        
        # Look for randomization patterns
        if re.search(r'randomly?\s+assign|random.*rotation|permutation', action, re.IGNORECASE):
            # Extract artefact IDs (A1, A2, etc.) mentioned in action
            artefact_ids = re.findall(r'\b([A-Z]\d+)\b', action)
            
            # Also look for concept letter sequences like ABC, ACB, BAC
            if not artefact_ids:
                letter_sequences = re.findall(r'\b([A-Z]{2,})\b', action)
                if letter_sequences:
                    # Extract unique letters and convert to artefact IDs (A→A1, B→A2, C→A3)
                    letters = set()
                    for seq in letter_sequences:
                        letters.update(seq)
                    artefact_ids = [f"A{ord(letter) - ord('A') + 1}" for letter in sorted(letters)]
            
            if artefact_ids:
                assignments['concept_rotation'] = {
                    'rule_id': rule.get('rule_id'),
                    'method': 'random_permutation',
                    'artefacts': sorted(set(artefact_ids)),
                    'description': action
                }
    
    return assignments


def _build_routing_index(flow: Dict[str, Any], question_ids: List[str]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Build routing index and rule metadata.
    
    Returns:
        - routing_index: Maps question_id to {shown_by_rules, skipped_by_rules, terminate_by_rules}
        - rule_metadata: Maps rule_id to {condition, action, plain_condition, artefact_assignments}
    """
    routing_index: Dict[str, Dict[str, List[str]]] = {}
    rule_metadata: Dict[str, Dict[str, Any]] = {}
    rules = flow.get("routing_rules", [])
    if not isinstance(rules, list):
        return routing_index, rule_metadata

    qid_set = set(question_ids)
    
    # Detect artefact assignments
    artefact_assignments = _detect_artefact_assignment_rules(flow)

    # Build rule metadata first
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("rule_id", "")).strip()
        condition = str(rule.get("condition", ""))
        action = str(rule.get("action", ""))
        
        rule_metadata[rule_id] = {
            "condition": condition,
            "action": action,
            "plain_condition": _condition_to_plain_language(condition),
        }
        
        # Add artefact assignment info if this rule handles it
        for assignment_key, assignment_info in artefact_assignments.items():
            if assignment_info['rule_id'] == rule_id:
                rule_metadata[rule_id]['artefact_assignment'] = assignment_info

    def ensure(qid: str) -> Dict[str, Any]:
        if qid not in routing_index:
            routing_index[qid] = {
                "shown_by_rules": [],
                "skipped_by_rules": [],
                "terminate_by_rules": [],
                "displays_artefact": None,
            }
        return routing_index[qid]

    def find_qids(text: str) -> List[str]:
        if not text:
            return []
        tokens = re.findall(r"\b[A-Z][A-Z0-9_]*\b", text)
        return [token for token in tokens if token in qid_set]

    def apply_clause(rule_id: str, clause: str, bucket: str):
        clause_clean = re.sub(r"\bonly\b", "", clause, flags=re.IGNORECASE)
        qids = find_qids(clause_clean)
        for qid in qids:
            ensure(qid)[bucket].append(rule_id)

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("rule_id", "")).strip()
        condition = str(rule.get("condition", ""))
        action = str(rule.get("action", ""))

        # Detect "Display artefact X with question Y" pattern
        display_match = re.search(
            r'Display\s+artefact\s+([A-Z]\d+).*with.*question\s+([A-Z0-9_]+)',
            action,
            re.IGNORECASE
        )
        if display_match:
            artefact_id = display_match.group(1)
            question_id = display_match.group(2)
            ensure(question_id)["displays_artefact"] = artefact_id

        clauses = [c.strip() for c in action.split(";") if c.strip()]
        for clause in clauses:
            if re.match(r"^show\s+", clause, flags=re.IGNORECASE):
                apply_clause(rule_id, clause, "shown_by_rules")
            elif re.match(r"^skip\s+", clause, flags=re.IGNORECASE):
                apply_clause(rule_id, clause, "skipped_by_rules")
            elif re.match(r"^terminate\b", clause, flags=re.IGNORECASE):
                for qid in find_qids(condition):
                    ensure(qid)["terminate_by_rules"].append(rule_id)

    for qid, buckets in routing_index.items():
        for key in ("shown_by_rules", "skipped_by_rules", "terminate_by_rules"):
            buckets[key] = sorted(set(buckets.get(key, [])))

    return routing_index, rule_metadata


def _collect_question_ids(survey: Dict[str, Any]) -> List[str]:
    qids: List[str] = []
    for q in survey.get("SCREENER", {}).get("questions", []) or []:
        if q.get("question_id"):
            qids.append(q["question_id"])
    for ss in survey.get("MAIN_SECTION", {}).get("sub_sections", []) or []:
        for q in ss.get("questions", []) or []:
            if q.get("question_id"):
                qids.append(q["question_id"])
    for q in survey.get("DEMOGRAPHICS", {}).get("questions", []) or []:
        if q.get("question_id"):
            qids.append(q["question_id"])
    return qids


def calculate_completeness(survey: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate survey completeness score and missing components."""
    import random
    
    present = []
    missing = []
    
    # Check optional V2 sections
    if survey.get("SAMPLE_REQUIREMENTS"):
        present.append("Sample Requirements")
    else:
        missing.append("Sample Requirements")
    
    if survey.get("PROGRAMMING_SPECIFICATIONS"):
        present.append("Programming Specifications")
    else:
        missing.append("Programming Specifications")
    
    if survey.get("ANALYSIS_PLAN"):
        present.append("Analysis Plan")
    else:
        missing.append("Analysis Plan")
    
    # Check metadata quality
    has_loi = bool(survey.get("STUDY_METADATA", {}).get("estimated_loi_minutes"))
    if not has_loi:
        missing.append("Estimated LOI")
    else:
        present.append("Estimated LOI")
    
    # Check question notes (sample some questions)
    questions = []
    for section_name in ["SCREENER", "DEMOGRAPHICS"]:
        section = survey.get(section_name, {})
        questions.extend(section.get("questions", []))
    
    main = survey.get("MAIN_SECTION", {})
    for subsec in main.get("sub_sections", []):
        questions.extend(subsec.get("questions", []))
    
    if questions:
        sample_size = min(5, len(questions))
        sample_questions = random.sample(questions, sample_size)
        notes_count = sum(1 for q in sample_questions if q.get("notes"))
        has_notes = notes_count > 0
        if has_notes:
            present.append("Question notes")
        else:
            missing.append("Question notes/rationale")
    
    # Check subsection purposes
    subsections = main.get("sub_sections", [])
    if subsections:
        has_purposes = any(s.get("purpose") for s in subsections)
        if has_purposes:
            present.append("Subsection purposes")
        else:
            missing.append("Subsection purposes")
    
    # Calculate score
    total_components = len(present) + len(missing)
    score = (len(present) / total_components * 100) if total_components > 0 else 100
    
    status = "complete" if score == 100 else "good" if score >= 66 else "basic"
    
    return {
        "score": round(score),
        "present": present,
        "missing": missing,
        "status": status
    }


# ----------------------------
# Orchestration helpers
# ----------------------------

def _group_key_for_issue(issue: ValidationIssue) -> List[str]:
    ref = issue.fragment_ref
    section = ref.get("section")
    keys: List[str] = []
    if section:
        keys.append(section)
        if section == "MAIN_SECTION":
            ss_id = ref.get("subsection_id")
            if ss_id:
                keys.append(f"MAIN_SECTION:{ss_id}")
    return list(dict.fromkeys(keys))


def build_static_assets(survey_json: Dict[str, Any]) -> Dict[str, Any]:
    normalised, issues = validate_and_normalise(survey_json)

    issues_grouped: Dict[str, List[str]] = {}
    for issue in issues:
        for key in _group_key_for_issue(issue):
            issues_grouped.setdefault(key, []).append(issue.issue_id)

    ui_spec = None
    if not issues:
        ui_spec = render_ui_spec(normalised)

    return {
        "normalised_survey": normalised,
        "issues": [asdict(issue) for issue in issues],
        "issues_grouped": issues_grouped,
        "ui_spec": ui_spec,
    }


# ----------------------------
# Targeted repair prompt builder (engine -> model)
# ----------------------------

def make_targeted_repair_payload(issue: ValidationIssue) -> Dict[str, Any]:
    return {
        "task": "targeted_json_repair",
        "issue_id": issue.issue_id,
        "issue_fingerprint": issue.issue_fingerprint,
        "error_code": issue.error_code,
        "json_path": issue.json_path,
        "message": issue.message,
        "fragment": issue.fragment,
        "expected": {
            "note": "Return RFC6902 JSON Patch operations that fix ONLY the issue at json_path (or within fragment).",
            "format": {
                "patch": [
                    {"op": "replace|add|remove", "path": "<json_pointer>", "value": "<any>"}
                ]
            },
        },
    }


# ----------------------------
# CLI usage
# ----------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", default="survey_output_validated.json")
    parser.add_argument("--out_ui", default="ui_spec.json")
    parser.add_argument("--out_issues", default="issues.json")
    args = parser.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        survey = json.load(f)

    result = build_static_assets(survey)

    with open(args.out_issues, "w", encoding="utf-8") as f:
        json.dump(
            {"issues": result["issues"], "issues_grouped": result["issues_grouped"]},
            f,
            ensure_ascii=False,
            indent=2,
        )

    if result["ui_spec"] is not None:
        with open(args.out_ui, "w", encoding="utf-8") as f:
            json.dump(result["ui_spec"], f, ensure_ascii=False, indent=2)

        print(f"Rendered UI spec -> {args.out_ui}")
    else:
        print("Validation issues found. See issues.json.")