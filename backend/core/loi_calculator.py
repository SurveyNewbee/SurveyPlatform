"""
LOI (Length of Interview) calculation and configuration management.
"""

from typing import Dict, Any, List, Tuple


class LOICalculator:
    """Calculates and manages LOI configuration for surveys."""
    
    # Slider position ranges for each tier
    QUICK_RANGE = (0, 30)
    STANDARD_RANGE = (30, 70)
    DEEP_RANGE = (70, 100)
    
    # Default snap points
    SNAP_QUICK = 15
    SNAP_STANDARD = 50
    SNAP_DEEP = 85
    
    def __init__(self, survey: Dict[str, Any]):
        """Initialize with survey data."""
        self.survey = survey
        
    def add_loi_config(self, initial_position: int = 50) -> Dict[str, Any]:
        """
        Add LOI configuration to survey JSON.
        
        Args:
            initial_position: Initial slider position (0-100). Defaults to Standard tier.
            
        Returns:
            Updated survey with loi_config added
        """
        # Ensure all questions have LOI fields
        self._ensure_question_loi_fields()
        
        # Calculate initial configuration
        loi_config = self._calculate_loi_config(initial_position)
        
        # Add to survey
        self.survey["loi_config"] = loi_config
        
        return self.survey
    
    def _ensure_question_loi_fields(self):
        """Ensure all questions have required LOI fields with defaults."""
        sections = [
            self.survey.get("SCREENER", {}).get("questions", []),
            self.survey.get("DEMOGRAPHICS", {}).get("questions", [])
        ]
        
        # Handle MAIN_SECTION with sub_sections
        main_section = self.survey.get("MAIN_SECTION", {})
        if "sub_sections" in main_section:
            for subsection in main_section["sub_sections"]:
                sections.append(subsection.get("questions", []))
        
        for question_list in sections:
            for question in question_list:
                # Add default priority if missing
                if "priority" not in question:
                    question["priority"] = self._infer_priority(question)
                
                # Add default priority_rank if missing
                if "priority_rank" not in question:
                    question["priority_rank"] = 1
                
                # Add default estimated_seconds if missing
                if "estimated_seconds" not in question:
                    question["estimated_seconds"] = self._estimate_question_time(question)
                
                # Add visibility state (defaults to visible)
                if "loi_visibility" not in question:
                    question["loi_visibility"] = "visible"
                
                # Add user override state
                if "user_override" not in question:
                    question["user_override"] = "none"
    
    def _infer_priority(self, question: Dict[str, Any]) -> str:
        """
        Infer priority level from question characteristics.
        
        Priority rules:
        - Screener questions are always "required"
        - Questions in DEMOGRAPHICS are "recommended"
        - Matrix questions with >5 rows are "optional"
        - Questions with display_logic are "optional"
        - Otherwise "recommended"
        """
        question_id = question.get("question_id", "")
        
        # Screener questions are required
        if question_id.startswith("SCR_"):
            return "required"
        
        # Demographics are recommended
        if question_id.startswith("DEM_"):
            return "recommended"
        
        # Large matrices are optional
        if question.get("rows") and len(question.get("rows", [])) > 5:
            return "optional"
        
        # Questions with display logic are often optional
        if question.get("display_logic"):
            return "optional"
        
        # Default to recommended
        return "recommended"
    
    def _estimate_question_time(self, question: Dict[str, Any]) -> int:
        """
        Estimate completion time for a question in seconds.
        
        Based on question type and complexity.
        """
        q_type = question.get("question_type", "")
        
        # Matrix questions
        if q_type == "matrix":
            row_count = len(question.get("rows", []))
            col_count = len(question.get("columns", []))
            # ~2-3 seconds per cell for simple matrices
            return min(row_count * 3, 45)
        
        # Single choice
        if q_type == "single_choice":
            option_count = len(question.get("options", []))
            if option_count <= 5:
                return 6
            elif option_count <= 10:
                return 10
            else:
                return 12
        
        # Multiple choice
        if q_type == "multiple_choice":
            return 12
        
        # Ranking
        if q_type == "ranking":
            item_count = len(question.get("options", []))
            return min(item_count * 5, 30)
        
        # Open-ended
        if q_type == "open_ended":
            return 30
        
        # Numeric input
        if q_type == "numeric_input":
            return 8
        
        # Scale
        if q_type == "scale":
            return 8
        
        # Default
        return 10
    
    def _calculate_loi_config(self, slider_position: int) -> Dict[str, Any]:
        """Calculate LOI configuration based on slider position."""
        # Determine snap point
        snap_point = self._get_snap_point(slider_position)
        
        # Get all questions
        all_questions = self._get_all_questions()
        
        # Update visibility based on slider position
        visible_count = 0
        hidden_count = 0
        pinned_count = 0
        excluded_count = 0
        total_seconds = 0
        
        for question in all_questions:
            # Check user overrides first
            override = question.get("user_override", "none")
            if override == "pinned":
                question["loi_visibility"] = "visible"
                pinned_count += 1
                visible_count += 1
                total_seconds += question.get("estimated_seconds", 10)
            elif override == "excluded":
                question["loi_visibility"] = "hidden"
                excluded_count += 1
                hidden_count += 1
            else:
                # Determine visibility based on slider position and priority
                priority = question.get("priority", "recommended")
                is_visible = self._should_show_question(slider_position, priority, question.get("priority_rank", 1))
                
                question["loi_visibility"] = "visible" if is_visible else "hidden"
                if is_visible:
                    visible_count += 1
                    total_seconds += question.get("estimated_seconds", 10)
                else:
                    hidden_count += 1
        
        # Calculate LOI in minutes
        estimated_loi = round(total_seconds / 60, 1)
        
        return {
            "slider_position": slider_position,
            "snap_point": snap_point,
            "estimated_loi_minutes": estimated_loi,
            "total_questions": len(all_questions),
            "visible_questions": visible_count,
            "hidden_questions": hidden_count,
            "user_pinned_count": pinned_count,
            "user_excluded_count": excluded_count
        }
    
    def _get_snap_point(self, position: int) -> str:
        """Determine which snap point the position represents."""
        if position <= self.QUICK_RANGE[1]:
            return "quick"
        elif position <= self.STANDARD_RANGE[1]:
            return "standard"
        else:
            return "deep"
    
    def _should_show_question(self, slider_position: int, priority: str, priority_rank: int) -> bool:
        """
        Determine if a question should be visible at a given slider position.
        
        Uses priority thresholds that expand based on slider position:
        - Quick (0-30): Only "required" questions shown
        - Standard (30-70): "required" + progressively add "recommended" by priority_rank
        - Deep (70-100): All "required" and "recommended", + progressively add "optional" by priority_rank
        
        Within each tier, lower priority_rank questions are shown first.
        """
        if priority == "required":
            # Always show required questions
            return True
        
        if priority == "recommended":
            # Below Quick tier: hide all recommended
            if slider_position <= 30:
                return False
            
            # At or above Deep tier: show all recommended
            if slider_position >= 70:
                return True
            
            # In Standard tier (30-70): progressive show based on priority_rank
            # Calculate what percentage through the Standard tier we are
            progress = (slider_position - 30) / 40  # 0.0 at position 30, 1.0 at position 70
            
            # Get max priority_rank among recommended questions
            max_recommended_rank = self._get_max_priority_rank("recommended")
            
            # Calculate threshold: at position 30, show rank 1 only; at 70, show all
            # Use ceiling so we always show at least 1 question
            rank_threshold = max(1, round(progress * max_recommended_rank))
            
            return priority_rank <= rank_threshold
        
        if priority == "optional":
            # Below Deep tier: hide all optional
            if slider_position < 70:
                return False
            
            # At max position: show all optional
            if slider_position >= 100:
                return True
            
            # In Deep tier (70-100): progressive show based on priority_rank
            progress = (slider_position - 70) / 30  # 0.0 at position 70, 1.0 at position 100
            
            # Get max priority_rank among optional questions
            max_optional_rank = self._get_max_priority_rank("optional")
            
            # Calculate threshold
            rank_threshold = max(1, round(progress * max_optional_rank))
            
            return priority_rank <= rank_threshold
        
        # Unknown priority - default to showing
        return True
    
    def _get_max_priority_rank(self, priority_level: str) -> int:
        """Get the maximum priority_rank value for a given priority level."""
        all_questions = self._get_all_questions()
        max_rank = 1
        
        for question in all_questions:
            if question.get("priority") == priority_level:
                rank = question.get("priority_rank", 1)
                max_rank = max(max_rank, rank)
        
        return max_rank
    
    def _get_all_questions(self) -> List[Dict[str, Any]]:
        """Get flat list of all questions in survey."""
        questions = []
        
        # Screener questions
        screener = self.survey.get("SCREENER", {})
        questions.extend(screener.get("questions", []))
        
        # Main section questions (with sub_sections)
        main_section = self.survey.get("MAIN_SECTION", {})
        if "sub_sections" in main_section:
            for subsection in main_section["sub_sections"]:
                questions.extend(subsection.get("questions", []))
        
        # Demographics questions
        demographics = self.survey.get("DEMOGRAPHICS", {})
        questions.extend(demographics.get("questions", []))
        
        return questions
    
    def update_loi_config(self, slider_position: int) -> Dict[str, Any]:
        """
        Update LOI configuration after slider movement or pin/exclude changes.
        
        Returns updated loi_config.
        """
        loi_config = self._calculate_loi_config(slider_position)
        self.survey["loi_config"] = loi_config
        return loi_config
    
    def pin_question(self, question_id: str) -> Dict[str, Any]:
        """Pin a question to always show it."""
        question = self._find_question(question_id)
        if question:
            question["user_override"] = "pinned"
            question["loi_visibility"] = "visible"
        
        # Recalculate LOI config
        current_position = self.survey.get("loi_config", {}).get("slider_position", 50)
        return self.update_loi_config(current_position)
    
    def exclude_question(self, question_id: str) -> Dict[str, Any]:
        """Exclude a question to always hide it."""
        question = self._find_question(question_id)
        if question:
            question["user_override"] = "excluded"
            question["loi_visibility"] = "hidden"
        
        # Recalculate LOI config
        current_position = self.survey.get("loi_config", {}).get("slider_position", 50)
        return self.update_loi_config(current_position)
    
    def reset_question_override(self, question_id: str) -> Dict[str, Any]:
        """Reset a question's user override to default LOI-based visibility."""
        question = self._find_question(question_id)
        if question:
            question["user_override"] = "none"
        
        # Recalculate LOI config
        current_position = self.survey.get("loi_config", {}).get("slider_position", 50)
        return self.update_loi_config(current_position)
    
    def _find_question(self, question_id: str) -> Dict[str, Any] | None:
        """Find a question by ID."""
        all_questions = self._get_all_questions()
        for question in all_questions:
            if question.get("question_id") == question_id:
                return question
        return None
