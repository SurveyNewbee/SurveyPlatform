---
name: usability-testing
description: |
  Evaluates how easily users can complete key tasks within digital products, websites, or applications through behavioral observation and task-based testing. Use when you need to identify specific friction points, failure modes, or efficiency issues that impact conversion or user satisfaction. Measures task success rates, completion times, and error patterns rather than opinions or preferences. Commonly combined with journey-mapping to validate pain points or CSAT studies to link usability issues to satisfaction scores. Not suitable for early concept evaluation, brand perception studies, or aesthetic preference testing.
category: user_experience
foundational: false
primary_use_case: Identify and diagnose specific usability problems that prevent users from successfully completing key tasks in digital interfaces
secondary_applications:
  - Validate design changes and measure improvement over time
  - Benchmark task performance against competitors
  - Prioritize product roadmap based on user friction points
  - Support conversion rate optimization initiatives
commonly_combined_with:
  - journey-mapping
  - nps-csat
  - rating-scales
  - screening
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - experience_breakdown
  - performance_tracking
  - decline_diagnosis
decision_stages:
  - design
  - validate
  - optimize
study_types:
  - user_experience_research
  - digital_optimization
not_suitable_for:
  - Early-stage concept testing before functional prototypes exist
  - Brand perception or aesthetic preference evaluation
  - Opinion-based research about features or positioning
---


# Usability Testing

## Overview
Usability testing is a task-based research methodology used to evaluate how easily users can complete key actions within a digital product, website, or application. It focuses on effectiveness, efficiency, and satisfaction by observing users as they attempt realistic tasks. Usability testing identifies friction, confusion, and failure points that directly impact conversion, retention, and satisfaction.

## Core Principles
Usability testing is fundamentally different from opinion-based research. Always follow these principles:

- **Behavior over opinion:** What users do matters more than what they say.
- **Task realism:** Tasks must reflect real-world user goals, not internal workflows.
- **Minimal guidance:** The interface—not the moderator—should enable success.
- **Diagnostic depth:** The goal is to understand *why* users struggle, not just whether they do.
- **Actionability:** Findings must translate directly into design or product changes.

## Survey Design Requirements

### Testing Approach Selection

#### Moderated Usability Testing
Use when:
- You need deep diagnostic insight
- Tasks are complex or novel
- Early-stage prototypes are being tested

Characteristics:
- Live moderator
- Think-aloud protocol
- Smaller sample sizes (5–15 users)

#### Unmoderated Usability Testing
Use when:
- You need speed or scale
- Tasks are well-defined
- The interface is relatively mature

Characteristics:
- Self-guided tasks
- Automated metrics
- Larger samples (20–100+ users)

Do not mix moderated and unmoderated data in the same analysis.

---

### Task Scenario Design

#### Task Construction Rules
Each task MUST:
- Be written as a **goal**, not an instruction
- Use **plain language**, not UI labels
- Avoid revealing the correct path
- Focus on one primary objective

**Correct task format:**
```

You want to change the shipping address for an upcoming order. Please show how you would do this.

```

**Incorrect task format:**
- “Click on ‘Account Settings’ and update your address.”
- “Find the shipping address section.”

Never reference navigation labels, buttons, or page names in tasks.

---

### Number and Order of Tasks
- Use **3–7 core tasks** per session
- Order tasks from simple to complex
- Avoid dependency between tasks whenever possible

If tasks must build on each other, explicitly reset context between them.

---

### Success Metrics

#### Task Outcome Coding
Every task must be coded into one of the following:

- **Success:** Task completed without assistance
- **Partial success:** Task completed with difficulty or workaround
- **Failure:** Task not completed or abandoned

Do not rely solely on self-reported success.

---

#### Efficiency Metrics
Capture at least one of the following:
- Time on task
- Number of clicks or steps
- Error count
- Path deviation

Use consistent benchmarks across participants.

---

### Think-Aloud Protocol

#### Instructions to Respondents
Always instruct respondents:
```

As you complete each task, please say out loud what you are thinking, what you are looking for, and anything that feels confusing or unexpected.

```

Rules:
- Do not prompt or correct during tasks
- Allow silence; do not fill gaps
- Probe only after task completion

---

### Post-Task Questions

After each task, include:
- Perceived ease or difficulty
- Confidence in completion
- Open-ended diagnostic probe

**Example:**
```

How easy or difficult was this task to complete?

* Very easy
* Somewhat easy
* Neither easy nor difficult
* Somewhat difficult
* Very difficult

```

Follow with:
```

What, if anything, made this task difficult?

```

---

### System Usability Scale (SUS)

#### SUS Structure
The SUS is a standardized 10-item questionnaire used to measure overall usability.

Rules:
- Use the **exact standard wording**
- Use a **5-point agreement scale**
- Alternate positive and negative statements
- Ask SUS **after all tasks are complete**

Never reword SUS items or change their order.

---

### Scale Design

#### Post-Task and Post-Test Scales
- Use 5-point scales for ease, confidence, and satisfaction
- Label all scale points
- Keep polarity consistent throughout the study

Avoid 7- or 10-point scales; they add noise without diagnostic value.

---

### Sample Questions

#### Task Scenario Example
```

You want to return an item you purchased last week. Please show how you would start that process.

```

#### Post-Task Diagnostic
```

What did you expect to happen when you clicked there?

```

#### Overall Satisfaction
```

Overall, how satisfied are you with your experience using this product?

```

---

## Common Mistakes to Avoid

### Mistake 1: Asking Users What They Would Do
**Wrong:**  
“What would you do if you wanted to change your password?”

**Why it’s wrong:**  
Hypothetical behavior does not reveal usability issues.

**Correct approach:**  
Ask users to actually attempt the task.

---

### Mistake 2: Over-Explaining Tasks
**Wrong:**  
Providing step-by-step guidance in the task description.

**Why it’s wrong:**  
Masks real usability problems.

**Correct approach:**  
State the goal only. Let the interface do the work.

---

### Mistake 3: Treating Usability Like Satisfaction Research
**Wrong:**  
Relying on satisfaction scores alone.

**Why it’s wrong:**  
Users may report satisfaction despite failures.

**Correct approach:**  
Prioritize task success and observed behavior.

---

### Mistake 4: Ignoring Edge Cases
**Wrong:**  
Testing only “happy path” scenarios.

**Why it’s wrong:**  
Real users encounter errors, changes, and exceptions.

**Correct approach:**  
Include at least one recovery or exception task when relevant.

---

## Analysis & Output Requirements

### Required Data Structure
Each task must include:
- Task ID
- Completion status
- Time on task
- Error notes
- Verbatim commentary

Do not aggregate tasks prematurely.

---

### Core Outputs
Always report:
- Task success rate (%)
- Average time on task
- Common failure points
- Thematic usability issues
- Severity ratings (e.g., critical / major / minor)

Tie findings directly to UI elements or flows.

---

### Severity Classification
Classify issues by:
- Frequency
- Impact on task completion
- Impact on business outcomes

Avoid vague prioritization like “nice to have.”

---

## Integration with Other Methods

Usability testing commonly integrates with:
- **Journey mapping:** Validate pain points at specific stages
- **CSAT / NPS:** Link usability issues to satisfaction
- **A/B testing:** Quantify impact of design fixes
- **Product analytics:** Triangulate behavioral data

Keep usability testing diagnostic, not evaluative.

---

## Quality Checklist

- [ ] Tasks are goal-based and realistic
- [ ] Users perform tasks without guidance
- [ ] Success is behaviorally coded
- [ ] Think-aloud instructions are included
- [ ] SUS uses exact standard wording
- [ ] Post-task diagnostics capture root causes
- [ ] Findings are tied to actionable design changes
- [ ] Severity and priority are clearly defined

---

## Final Guidance
Usability testing is not about opinions, aesthetics, or preferences—it is about **whether users can successfully achieve their goals**. If users fail, the design has failed. Treat usability findings as design requirements, not suggestions.
```

---
