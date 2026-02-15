import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, saveComment, getComments, summarizeComments, updateProject } from '../api/client';
import type { Project } from '../types';

interface Comment {
  id: string;
  question_id: string;
  text: string;
  timestamp: number;
}

interface PreviewQuestion {
  id: string;
  text: string;
  type: string;
  options?: string[];
  rows?: string[];
  columns?: string[];
  section: string;
}

interface SkipLogic {
  condition_type: 'simple' | 'complex';
  simple_condition?: {
    target_question_id: string;
    operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than';
    value: any;
  };
  complex_condition?: {
    logic_operator: 'AND' | 'OR';
    conditions: Array<{
      target_question_id: string;
      operator: string;
      value: any;
    }>;
  };
  action: 'skip' | 'show' | 'terminate' | 'jump_to';
  jump_target?: string;
}

interface Piping {
  variables: Array<{
    placeholder: string;
    source_question_id: string;
    transform?: 'uppercase' | 'lowercase' | 'number_format';
  }>;
}

interface Question {
  id: string;
  text: string;
  type: string;
  section: string;
  options?: string[];
  rows?: string[];
  columns?: string[];
  skip_logic?: SkipLogic;
  display_logic?: string;
  piping?: Piping;
  min_value?: number;
  max_value?: number;
  step?: number;
  scale_labels?: {
    min: string;
    max: string;
  };
}

interface QuestionStatus {
  id: string;
  status: 'pending' | 'shown' | 'skipped' | 'error' | 'answered';
  reason?: string;
  visitedAt?: Date;
  pipedValues?: Record<string, string>;
}

// Matrix Question Component for sequential presentation
function MatrixQuestion({ 
  question, 
  answers, 
  onAnswer 
}: {
  question: PreviewQuestion;
  answers: Record<string, any>;
  onAnswer: (questionId: string, value: any) => void;
}) {
  const [currentMatrixItem, setCurrentMatrixItem] = useState(0);
  const matrixKey = question.id;
  const totalItems = question.rows?.length || 0;
  
  // Check if all items have been answered
  const allMatrixAnswered = question.rows?.every((row, idx) => 
    answers[`${matrixKey}_${idx}`] !== undefined
  );
  
  // Current item being shown
  const currentRow = question.rows?.[currentMatrixItem];
  const currentRowIndex = currentMatrixItem;
  
  const handleMatrixAnswer = (value: string) => {
    // Save the answer
    onAnswer(`${matrixKey}_${currentRowIndex}`, value);
    
    // Auto-advance to next item after brief delay
    setTimeout(() => {
      if (currentMatrixItem < totalItems - 1) {
        setCurrentMatrixItem(prev => prev + 1);
      }
    }, 300); // 300ms delay for visual feedback
  };
  
  const goToPreviousItem = () => {
    if (currentMatrixItem > 0) {
      setCurrentMatrixItem(prev => prev - 1);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Progress indicator for matrix items */}
      <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
        <span>Statement {currentMatrixItem + 1} of {totalItems}</span>
        <div className="flex gap-1">
          {question.rows?.map((_, idx) => (
            <div
              key={idx}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                idx < currentMatrixItem 
                  ? 'bg-green-500' 
                  : idx === currentMatrixItem 
                  ? 'bg-blue-600 w-2 h-2' 
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
      
      {/* Current statement - large and prominent */}
      <div 
        key={currentMatrixItem}
        className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-5 min-h-[100px] flex items-center justify-center animate-fadeIn"
      >
        <h3 className="text-base font-semibold text-gray-900 text-center leading-normal">
          {currentRow}
        </h3>
      </div>
      
      {/* Answer options - large clickable buttons */}
      <div className="grid grid-cols-1 gap-2.5">
        {question.columns?.map((option, idx) => {
          const isSelected = answers[`${matrixKey}_${currentRowIndex}`] === option;
          
          return (
            <button
              key={idx}
              onClick={() => handleMatrixAnswer(option)}
              className={`
                p-4 rounded-lg border-2 font-medium text-sm
                transition-all duration-200 text-left
                ${
                  isSelected
                    ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                    : 'bg-white border-gray-300 text-gray-900 hover:border-blue-400 hover:bg-blue-50'
                }
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              `}
            >
              <div className="flex items-center justify-between">
                <span>{option}</span>
                {isSelected && (
                  <svg className="w-5 h-5 flex-shrink-0 ml-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                )}
              </div>
            </button>
          );
        })}
      </div>
      
      {/* Navigation between matrix items */}
      {currentMatrixItem > 0 && (
        <button
          onClick={goToPreviousItem}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-xs transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
          </svg>
          Previous statement
        </button>
      )}
      
      {/* Show summary when all items answered */}
      {allMatrixAnswered && currentMatrixItem === totalItems - 1 && (
        <div className="mt-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
            </svg>
            <div>
              <div className="font-semibold text-green-900">All statements complete</div>
              <div className="text-sm text-green-700 mt-1">
                You've rated all {totalItems} statements. Click Continue to proceed.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PreviewPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [previewQuestions, setPreviewQuestions] = useState<PreviewQuestion[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [showCommentBox, setShowCommentBox] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isComplete, setIsComplete] = useState(false);
  const [improvements, setImprovements] = useState<any[]>([]);
  const [acceptedImprovements, setAcceptedImprovements] = useState<Set<string>>(new Set());
  const [loadingImprovements, setLoadingImprovements] = useState(false);
  const [processedCommentCount, setProcessedCommentCount] = useState(0);
  const [showIntro, setShowIntro] = useState(true);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [currentArtefact, setCurrentArtefact] = useState<any>(null);
  
  // Navigation Panel State
  const [showNavigationPanel, setShowNavigationPanel] = useState(true);
  const [questionValidation, setQuestionValidation] = useState<Record<string, QuestionStatus>>({});
  const [allQuestionsIncludingHidden, setAllQuestionsIncludingHidden] = useState<Question[]>([]);

  // Termination System State
  const [terminationNotification, setTerminationNotification] = useState<{
    reason: string;
    ruleId: string;
    questionId: string;
  } | null>(null);
  const [isTestMode, setIsTestMode] = useState(true);
  const [selectedCell, setSelectedCell] = useState<string>('Kawakawa');

  // Extract all questions regardless of skip logic
  const extractAllQuestions = useCallback((): Question[] => {
    if (!project?.survey_json) return [];
    
    const allQuestions: Question[] = [];
    const surveyJson = project.survey_json;
    
    // Extract from SCREENER
    if (surveyJson.SCREENER?.questions) {
      surveyJson.SCREENER.questions.forEach((q: any) => {
        allQuestions.push({
          id: q.question_id,
          text: q.question_text,
          type: q.question_type,
          section: 'SCREENER',
          options: q.options,
          rows: q.rows,
          columns: q.columns,
          skip_logic: q.skip_logic,
          display_logic: q.display_logic,
          piping: q.piping,
          min_value: q.min_value,
          max_value: q.max_value,
        });
      });
    }
    
    // Extract from MAIN_SECTION
    if (surveyJson.MAIN_SECTION?.sub_sections) {
      surveyJson.MAIN_SECTION.sub_sections.forEach((subsection: any) => {
        subsection.questions?.forEach((q: any) => {
          allQuestions.push({
            id: q.question_id,
            text: q.question_text,
            type: q.question_type,
            section: subsection.subsection_title || 'MAIN SURVEY',
            options: q.options,
            rows: q.rows,
            columns: q.columns,
            skip_logic: q.skip_logic,
            display_logic: q.display_logic,
            piping: q.piping,
            min_value: q.min_value,
            max_value: q.max_value,
          });
        });
      });
    }
    
    // Extract from DEMOGRAPHICS
    if (surveyJson.DEMOGRAPHICS?.questions) {
      surveyJson.DEMOGRAPHICS.questions.forEach((q: any) => {
        allQuestions.push({
          id: q.question_id,
          text: q.question_text,
          type: q.question_type,
          section: 'DEMOGRAPHICS',
          options: q.options,
          rows: q.rows,
          columns: q.columns,
          skip_logic: q.skip_logic,
          display_logic: q.display_logic,
          piping: q.piping,
          min_value: q.min_value,
          max_value: q.max_value,
        });
      });
    }
    
    return allQuestions;
  }, [project]);

// Skip logic evaluation function - handles both skip_logic and display_logic formats
  const evaluateSkipLogic = useCallback((
    question: Question, 
    currentAnswers: Record<string, any>
  ): { shouldShow: boolean; reason?: string } => {
    
    console.log(`[SKIP LOGIC] Evaluating question ${question.id}:`, {
      hasSkipLogic: !!question.skip_logic,
      hasDisplayLogic: !!question.display_logic,
      skipLogic: question.skip_logic,
      displayLogic: question.display_logic,
      currentAnswers
    });
    
    // Check FLOW rules for skip logic (R14, R15, R16)
    if (project?.survey_json?.FLOW?.routing_rules) {
      const rules = project.survey_json.FLOW.routing_rules;
      
      for (const rule of rules) {
        if (rule.action?.includes('SKIP')) {
          const targetQuestionId = rule.action.match(/SKIP (\S+)/)?.[1];
          
          if (targetQuestionId === question.id) {
            console.log(`[FLOW SKIP] Checking rule ${rule.rule_id} for ${question.id}`);
            
            // R14: MS5_Q3 = 'I would not purchase any of these' → SKIP MS5_Q4
            if (rule.rule_id === 'R14' && question.id === 'MS5_Q4') {
              if (currentAnswers['MS5_Q3'] === 'I would not purchase any of these') {
                console.log(`[FLOW SKIP] R14 triggered - skipping ${question.id}`);
                return { shouldShow: false, reason: 'No flavor preference selected' };
              }
            }
            
            // R15: MS6_Q1 ≠ 'Replace a brand I currently buy' → SKIP MS6_Q2
            if (rule.rule_id === 'R15' && question.id === 'MS6_Q2') {
              if (currentAnswers['MS6_Q1'] !== 'Replace a brand I currently buy') {
                console.log(`[FLOW SKIP] R15 triggered - skipping ${question.id}`);
                return { shouldShow: false, reason: 'Not replacing a brand' };
              }
            }
            
            // R16: No Fever-Tree awareness → SKIP MS6_Q4
            if (rule.rule_id === 'R16' && question.id === 'MS6_Q4') {
              const ms1q2 = currentAnswers['MS1_Q2'] || [];
              const ms1q3 = currentAnswers['MS1_Q3'] || [];
              const noFeverTree = !ms1q2.includes('Fever-Tree') && !ms1q3.includes('Fever-Tree');
              if (noFeverTree) {
                console.log(`[FLOW SKIP] R16 triggered - skipping ${question.id}`);
                return { shouldShow: false, reason: 'No Fever-Tree awareness' };
              }
            }
          }
        }
      }
    }
    
    // Handle display_logic format (used in actual survey data)
    if (question.display_logic) {
      const displayLogic = question.display_logic;
      console.log(`[DISPLAY LOGIC] Processing: ${displayLogic}`);
      
      try {
        // Parse "SHOW ONLY IF" conditions
        if (displayLogic.includes('SHOW ONLY IF')) {
          const condition = displayLogic.replace('SHOW ONLY IF ', '');
          
          // Handle cell assignment conditions
          if (condition.includes('assigned to') && condition.includes('cell')) {
            const cellMatch = condition.match(/assigned to (\w+) cell/);
            if (cellMatch) {
              const requiredCell = cellMatch[1];
              const assignedCell = currentAnswers['cell_assignment'] || currentAnswers['flavor_cell'];
              const shouldShow = assignedCell === requiredCell;
              console.log(`[DISPLAY LOGIC] Cell condition: need ${requiredCell}, have ${assignedCell}, show: ${shouldShow}`);
              return { 
                shouldShow, 
                reason: shouldShow ? undefined : `Wrong cell assignment (need ${requiredCell})` 
              };
            }
          }
          
          // Handle question response conditions like "MS5_Q3 ≠ 'value'"
          const responseMatch = condition.match(/(\w+)\s*[≠!=]\s*['"]([^'"]+)['"]/);
          if (responseMatch) {
            const [, questionId, value] = responseMatch;
            const targetAnswer = currentAnswers[questionId];
            const shouldShow = targetAnswer !== value;
            console.log(`[DISPLAY LOGIC] Response condition: ${questionId} ≠ "${value}", answer: "${targetAnswer}", show: ${shouldShow}`);
            return { 
              shouldShow, 
              reason: shouldShow ? undefined : `${questionId} equals "${value}"` 
            };
          }

          // Handle question response conditions like "MS6_Q1 = 'value'"
          const equalsMatch = condition.match(/(\w+)\s*[=]\s*['"]([^'"]+)['"]/);
          if (equalsMatch) {
            const [, questionId, value] = equalsMatch;
            const targetAnswer = currentAnswers[questionId];
            const shouldShow = targetAnswer === value;
            console.log(`[DISPLAY LOGIC] Equals condition: ${questionId} = "${value}", answer: "${targetAnswer}", show: ${shouldShow}`);
            return { 
              shouldShow, 
              reason: shouldShow ? undefined : `${questionId} does not equal "${value}"` 
            };
          }

          console.log(`[DISPLAY LOGIC] Unhandled condition format: ${condition}`);
        }
        
        // If no conditions match, default to show
        console.log(`[DISPLAY LOGIC] No matching conditions, defaulting to show`);
        return { shouldShow: true };
        
      } catch (error) {
        console.error('Display logic evaluation error:', error);
        return { shouldShow: true, reason: 'Error evaluating display logic' };
      }
    }
    
    // Handle legacy skip_logic format (structured format)
    if (question.skip_logic) {
      try {
        const { condition_type, simple_condition, complex_condition, action } = question.skip_logic;
        
        let conditionMet = false;
        let reason = '';
        
        if (condition_type === 'simple' && simple_condition) {
          const { target_question_id, operator, value } = simple_condition;
          const targetAnswer = currentAnswers[target_question_id];
          
          switch (operator) {
            case 'equals':
              conditionMet = targetAnswer === value;
              reason = `Q${target_question_id} equals "${value}"`;
              break;
            case 'not_equals':
              conditionMet = targetAnswer !== value;
              reason = `Q${target_question_id} does not equal "${value}"`;
              break;
            case 'contains':
              conditionMet = Array.isArray(targetAnswer) && targetAnswer.includes(value);
              reason = `Q${target_question_id} contains "${value}"`;
              break;
            case 'not_contains':
              conditionMet = !Array.isArray(targetAnswer) || !targetAnswer.includes(value);
              reason = `Q${target_question_id} does not contain "${value}"`;
              break;
            case 'greater_than':
              conditionMet = Number(targetAnswer) > Number(value);
              reason = `Q${target_question_id} (${targetAnswer}) > ${value}`;
              break;
            case 'less_than':
              conditionMet = Number(targetAnswer) < Number(value);
              reason = `Q${target_question_id} (${targetAnswer}) < ${value}`;
              break;
            default:
              conditionMet = false;
          }
        } else if (condition_type === 'complex' && complex_condition) {
          const { logic_operator, conditions } = complex_condition;
          const results = conditions.map(cond => {
            const targetAnswer = currentAnswers[cond.target_question_id];
            return targetAnswer === cond.value;
          });
          
          conditionMet = logic_operator === 'AND' 
            ? results.every(r => r) 
            : results.some(r => r);
          reason = `Complex logic: ${logic_operator}`;
        }
        
        // Determine if question should show based on action
        const shouldShow = action === 'skip' ? !conditionMet : conditionMet;
        
        console.log(`[SKIP LOGIC] Question ${question.id} evaluation result:`, {
          action,
          conditionMet,
          shouldShow,
          reason: shouldShow ? undefined : reason
        });
        
        return { 
          shouldShow, 
          reason: shouldShow ? undefined : reason 
        };
        
      } catch (error) {
        console.error('Skip logic evaluation error:', error);
        return { 
          shouldShow: true, 
          reason: 'Error evaluating skip logic' 
        };
      }
    }
    
    // No skip or display logic - show by default
    console.log(`[SKIP LOGIC] Question ${question.id} has no skip/display logic - showing`);
    return { shouldShow: true };
  }, []);

  // Piping function  
  const applyPiping = useCallback((
    text: string, 
    currentAnswers: Record<string, any>
  ): string => {
    if (!text) return text;
    
    let pipedText = text;
    
    // Handle [PIPE: ...] format from survey JSON
    pipedText = pipedText.replace(/\[PIPE:\s*([^\]]+)\]/g, (match, pipeType) => {
      const type = pipeType.trim().toLowerCase();
      
      // Handle different piping types
      switch (type) {
        case 'flavor name':
          // Get the selected cell assignment (flavor) - check answers first, then selectedCell
          const cellValue = currentAnswers.cell_assignment || currentAnswers.flavor_cell || selectedCell;
          const flavorMap: Record<string, string> = {
            'Kawakawa': 'Original Kawakawa',
            'Horopito': 'Spiced Horopito', 
            'Manuka': 'Manuka Honey & Lime'
          };
          return flavorMap[cellValue] || cellValue;
          
        case 'preferred flavor':
        case 'preferred flavor from ms5_q3':
          // Get the most preferred flavor from MS5_Q3 (flavor comparison)
          const preferredFlavor = currentAnswers['MS5_Q3'];
          return preferredFlavor || '[preferred flavor]';
          
        case 'randomized message':
          // For message randomization - would show actual message in real implementation
          return 'Message A';
          
        default:
          return `[${pipeType}]`; // Placeholder for unhandled pipe types
      }
    });
    
    // Handle simple {question_id} format (legacy support)
    pipedText = pipedText.replace(/\{([^}]+)\}/g, (match, questionId) => {
      const answer = currentAnswers[questionId];
      
      if (answer === undefined || answer === null) {
        return `[${questionId}]`; // Placeholder if not answered
      }
      
      if (Array.isArray(answer)) {
        return answer.join(', ');
      }
      
      return String(answer);
    });
    
    return pipedText;
  }, [selectedCell, answers]);

  useEffect(() => {
    loadProject();
    loadComments();
  }, [projectId]);

  useEffect(() => {
    if (project?.survey_json) {
      console.log('[PROJECT DATA] Survey JSON loaded:', project.survey_json);
      // Update allQuestionsIncludingHidden
      setAllQuestionsIncludingHidden(extractAllQuestions());
      extractVisibleQuestions();
    }
  }, [project]);

  // Re-evaluate visible questions when answers change
  useEffect(() => {
    if (project?.survey_json) {
      const oldCurrentQuestion = previewQuestions[currentQuestionIndex];
      extractVisibleQuestions();
      
      // If we have answers, we need to adjust currentQuestionIndex 
      // in case questions were skipped from the flow
      if (Object.keys(answers).length > 0 && oldCurrentQuestion) {
        // Find the new index of the current question after re-evaluation
        setTimeout(() => {
          setCurrentQuestionIndex(prevIndex => {
            const newIndex = previewQuestions.findIndex(q => q.id === oldCurrentQuestion.id);
            return newIndex !== -1 ? newIndex : Math.min(prevIndex, previewQuestions.length - 1);
          });
        }, 0);
      }
    }
  }, [answers, project]);

  // Extract all questions including hidden ones
  useEffect(() => {
    const allQs = extractAllQuestions();
    setAllQuestionsIncludingHidden(allQs);
  }, [extractAllQuestions]);

  // Update question status when answers change
  useEffect(() => {
    if (allQuestionsIncludingHidden.length > 0) {
      const newValidation: Record<string, QuestionStatus> = {};
      
      allQuestionsIncludingHidden.forEach(question => {
        const { shouldShow, reason } = evaluateSkipLogic(question, answers);
        const isAnswered = answers[question.id] !== undefined;
        const isCurrent = previewQuestions[currentQuestionIndex]?.id === question.id;
        
        if (isAnswered) {
          newValidation[question.id] = {
            status: 'answered',
            message: 'Completed successfully'
          };
        } else if (isCurrent) {
          newValidation[question.id] = {
            status: 'shown',
            message: 'Current question'
          };
        } else if (!shouldShow) {
          newValidation[question.id] = {
            status: 'skipped',
            message: reason || 'Skipped due to logic conditions'
          };
        } else {
          newValidation[question.id] = {
            status: 'pending',
            message: 'Not yet answered'
          };
        }
      });
      
      setQuestionValidation(newValidation);
    }
  }, [allQuestionsIncludingHidden, answers, currentQuestionIndex, previewQuestions, evaluateSkipLogic]);

  async function loadProject() {
    if (!projectId) return;
    
    console.log('[LOAD PROJECT] Starting to load project:', projectId);
    setLoading(true);
    const response = await getProject(projectId);
    
    console.log('[LOAD PROJECT] Get project response:', response);
    
    if (response.success && response.data) {
      console.log('[LOAD PROJECT] Setting project data:', response.data);
      setProject(response.data);
    } else {
      console.error('[LOAD PROJECT] Failed to load project:', response.error);
    }
    
    setLoading(false);
  }

  async function loadComments() {
    if (!projectId) return;
    
    console.log('Loading comments for project:', projectId);
    const response = await getComments(projectId);
    console.log('Get comments response:', response);
    
    if (response.success && response.data) {
      setComments(response.data.comments);
      console.log('Loaded comments:', response.data.comments);
    } else {
      console.error('Failed to load comments:', response.error);
    }
  }

  // Extract visible questions and filter by skip logic
  function extractVisibleQuestions() {
    if (!project?.survey_json) {
      console.log('[EXTRACT QUESTIONS] No project or survey_json');
      return;
    }

    console.log('[EXTRACT QUESTIONS] Starting extraction with project:', project.survey_json);
    const allQuestions = extractAllQuestions();
    console.log('[EXTRACT QUESTIONS] All questions extracted:', allQuestions);
    
    // Filter based on visibility AND skip logic
    const visibleQuestions = allQuestions.filter((q: any) => {
      // Check visibility first
      const originalQ = findOriginalQuestion(q.id);
      console.log(`[EXTRACT QUESTIONS] Checking question ${q.id}:`, {
        originalQ: originalQ ? { 
          question_id: originalQ.question_id, 
          loi_visibility: originalQ.loi_visibility, 
          user_override: originalQ.user_override 
        } : null
      });
      
      const isVisible = originalQ && (originalQ.loi_visibility === 'visible' || originalQ.user_override === 'pinned');
      console.log(`[EXTRACT QUESTIONS] Question ${q.id} visibility:`, isVisible);
      
      if (!isVisible) return false;
      
      // Check skip logic
      const { shouldShow } = evaluateSkipLogic(q, answers);
      console.log(`[EXTRACT QUESTIONS] Question ${q.id} skip logic result:`, shouldShow);
      return shouldShow;
    });

    console.log('[EXTRACT QUESTIONS] Visible questions after filtering:', visibleQuestions);

    // Convert to PreviewQuestion format
    const questions: PreviewQuestion[] = visibleQuestions.map((q: any) => ({
      id: q.id,
      text: q.text,
      type: q.type,
      options: q.options,
      rows: q.rows,
      columns: q.columns,
      section: q.section,
    }));

    console.log('[EXTRACT QUESTIONS] Final preview questions:', questions);
    setPreviewQuestions(questions);
  }

  // Helper to find original question data from survey JSON
  function findOriginalQuestion(questionId: string) {
    if (!project?.survey_json) return null;
    
    const survey = project.survey_json;
    const allSections = [
      ...(survey.SCREENER?.questions || []),
      ...(survey.MAIN_SECTION?.sub_sections?.flatMap((s: any) => s.questions || []) || []),
      ...(survey.DEMOGRAPHICS?.questions || [])
    ];
    
    return allSections.find((q: any) => q.question_id === questionId);
  }

  // Check for termination conditions based on FLOW rules
  const checkTerminationLogic = (
    questionId: string, 
    answer: any, 
    allAnswers: Record<string, any>
  ): { reason: string; ruleId: string; questionId: string } | null => {
    if (!project?.survey_json?.FLOW?.routing_rules) return null;
    
    const rules = project.survey_json.FLOW.routing_rules;
    
    for (const rule of rules) {
      if (rule.action?.includes('TERMINATE')) {
        // Parse the condition to see if it applies to this question
        if (rule.condition?.includes(questionId)) {
          console.log(`[TERMINATION CHECK] Evaluating rule ${rule.rule_id} for ${questionId}:`, {
            condition: rule.condition,
            answer,
            action: rule.action
          });
          
          // Simple condition parsing - check if answer matches any of the terminating values
          const conditionText = rule.condition.split('=')[1]?.trim() || '';
          
          // Handle OR conditions by splitting on 'OR'
          const terminatingValues = conditionText
            .split(' OR ')
            .map(val => val.replace(/'/g, '').trim())
            .filter(val => val.length > 0);
          
          console.log(`[TERMINATION CHECK] Terminating values for ${questionId}:`, terminatingValues);
          
          // Check if current answer matches any terminating value
          let shouldTerminate = false;
          
          if (Array.isArray(answer)) {
            // For multi-select questions (like industry exclusions)
            shouldTerminate = terminatingValues.some(val => answer.includes(val));
          } else {
            // For single-select questions
            shouldTerminate = terminatingValues.includes(answer);
          }
          
          if (shouldTerminate) {
            return {
              reason: rule.action.replace('TERMINATE - ', ''),
              ruleId: rule.rule_id,
              questionId
            };
          }
        }
      }
    }
    
    return null;
  };

  const currentQuestion = previewQuestions[currentQuestionIndex];
  console.log('Current question state:', { 
    currentQuestionIndex, 
    totalQuestions: previewQuestions.length,
    currentQuestion: currentQuestion?.id,
    questionExists: !!currentQuestion 
  });
  
  const progress = previewQuestions.length > 0 
    ? ((currentQuestionIndex + 1) / previewQuestions.length) * 100 
    : 0;
  const estimatedMinutes = project?.survey_json?.loi_config?.estimated_loi_minutes || 
    project?.survey_json?.PROGRAMMING_SPECIFICATIONS?.estimated_loi_minutes || 10;

  const handleNext = async () => {
    console.log('HandleNext called:', { 
      currentQuestionIndex, 
      totalQuestions: previewQuestions.length,
      currentQuestion: currentQuestion?.id 
    });
    
    // Mark current question as answered if it has an answer
    if (currentQuestion && answers[currentQuestion.id] !== undefined) {
      setQuestionValidation(prev => ({
        ...prev,
        [currentQuestion.id]: {
          status: 'answered',
          message: 'Completed successfully'
        }
      }));
    }
    
    if (currentQuestionIndex < previewQuestions.length - 1) {
      let nextIndex = currentQuestionIndex + 1;
      
      // Skip logic evaluation: Look ahead to find the next question that should be shown
      console.log(`[NAVIGATION] Looking for next question after index ${currentQuestionIndex}`);
      while (nextIndex < previewQuestions.length) {
        const nextQuestion = previewQuestions[nextIndex];
        console.log(`[NAVIGATION] Checking question at index ${nextIndex}: ${nextQuestion.id}`);
        const { shouldShow, reason } = evaluateSkipLogic(nextQuestion, answers);
        
        if (shouldShow) {
          // Found a question that should be shown
          console.log(`[NAVIGATION] Moving to question ${nextQuestion.id} at index ${nextIndex}`);
          setCurrentQuestionIndex(nextIndex);
          setShowCommentBox(false);
          setCommentText('');
          break;
        } else {
          // Mark the skipped question
          setQuestionValidation(prev => ({
            ...prev,
            [nextQuestion.id]: {
              status: 'skipped',
              message: reason || 'Skipped due to logic conditions'
            }
          }));
          
          console.log(`Question ${nextQuestion.id} skipped: ${reason}`);
          nextIndex++;
        }
      }
      
      // If we've gone through all remaining questions and none should be shown
      if (nextIndex >= previewQuestions.length) {
        console.log('All remaining questions skipped, showing completion screen');
        setIsComplete(true);
        // Generate improvements for commented questions
        if (comments.length > 0 && projectId) {
          setLoadingImprovements(true);
          // Store original count before clearing
          setProcessedCommentCount(comments.length);
          try {
            const response = await summarizeComments(projectId);
            console.log('Improvements response:', response);
            if (response.success && response.data && response.data.improvements) {
              setImprovements(response.data.improvements);
              // Auto-accept all improvements by default
              const allIds = new Set<string>(
                response.data.improvements.map((imp: any) => imp.question_id)
              );
              setAcceptedImprovements(allIds);
              // Clear comments after processing
              setComments([]);
            } else {
              console.error('Failed to generate improvements:', response.error);
            }
          } catch (error) {
            console.error('Error generating improvements:', error);
          } finally {
            setLoadingImprovements(false);
          }
        }
      }
    } else {
      console.log('Survey complete, showing completion screen');
      setIsComplete(true);
      // Generate improvements for commented questions
      if (comments.length > 0 && projectId) {
        setLoadingImprovements(true);
        // Store original count before clearing
        setProcessedCommentCount(comments.length);
        try {
          const response = await summarizeComments(projectId);
          console.log('Improvements response:', response);
          if (response.success && response.data && response.data.improvements) {
            setImprovements(response.data.improvements);
            // Auto-accept all improvements by default
            const allIds = new Set<string>(
              response.data.improvements.map((imp: any) => imp.question_id)
            );
            setAcceptedImprovements(allIds);
            // Clear comments after processing
            setComments([]);
          } else {
            console.error('Failed to generate improvements:', response.error);
          }
        } catch (error) {
          console.error('Error generating improvements:', error);
        } finally {
          setLoadingImprovements(false);
        }
      }
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      let prevIndex = currentQuestionIndex - 1;
      
      // Skip logic evaluation: Look backward to find the previous question that should be shown
      while (prevIndex >= 0) {
        const prevQuestion = previewQuestions[prevIndex];
        const { shouldShow } = evaluateSkipLogic(prevQuestion, answers);
        
        if (shouldShow) {
          // Found a question that should be shown
          setCurrentQuestionIndex(prevIndex);
          setShowCommentBox(false);
          setCommentText('');
          break;
        } else {
          console.log(`Question ${prevQuestion.id} skipped when going back`);
          prevIndex--;
        }
      }
      
      // If we've gone back to the beginning and no questions should be shown
      if (prevIndex < 0) {
        console.log('Cannot go back further - no previous questions to show');
        // Stay at current position
      }
    }
  };

  const handleAddComment = async () => {
    if (commentText.trim() && currentQuestion && projectId) {
      console.log('Saving comment:', { projectId, questionId: currentQuestion.id, text: commentText.trim() });
      const response = await saveComment(projectId, currentQuestion.id, commentText.trim());
      console.log('Save comment response:', response);
      
      if (response.success && response.data) {
        // Reload comments to get the updated list
        await loadComments();
        setCommentText('');
        setShowCommentBox(false);
      } else {
        console.error('Failed to save comment:', response.error);
        alert(`Failed to save comment: ${response.error || 'Unknown error'}`);
      }
    }
  };

  const getQuestionComments = (questionId: string) => {
    return comments.filter(c => c.question_id === questionId);
  };

  const handleAnswer = (value: any) => {
    if (currentQuestion) {
      console.log(`Answering ${currentQuestion.id}:`, value);
      
      const newAnswers = {
        ...answers,
        [currentQuestion.id]: value,
      };
      setAnswers(newAnswers);
      
      // Check for termination conditions in test mode
      if (isTestMode) {
        const termination = checkTerminationLogic(currentQuestion.id, value, newAnswers);
        if (termination) {
          console.log(`[TERMINATION] Would terminate: ${termination.reason}`);
          setTerminationNotification(termination);
          return; // Don't auto-advance when showing termination
        }
      }
    }
  };

  const handleMatrixAnswer = (questionId: string, value: any) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });
  };

  // Check if current question can proceed (for validation)
  const canProceed = () => {
    if (!currentQuestion) return false;
    
    // For unsupported question types (ones that show "Preview not available"), allow proceeding
    const isUnsupportedType = !(['single_choice', 'single_select', 'multiple_choice', 'multi_select', 
                                'open_ended', 'open_end', 'numeric_input', 'numeric', 'scale', 'rating_scale',
                                'matrix', 'stimulus_display', 'ranking'].includes(currentQuestion.type));
    
    if (isUnsupportedType) {
      return true; // Allow proceeding through unsupported question types
    }
    
    if (currentQuestion.type === 'matrix') {
      // Check all matrix items answered
      return currentQuestion.rows?.every((row, idx) => 
        answers[`${currentQuestion.id}_${idx}`] !== undefined
      ) || false;
    }
    if (currentQuestion.type === 'ranking') {
      // Check if at least some items are ranked
      const rankedItems = answers[currentQuestion.id] || [];
      return rankedItems.length > 0;
    }
    if (currentQuestion.type === 'stimulus_display') {
      // Stimulus display questions don't require input
      return true;
    }
    // For other question types, any answer is sufficient
    return answers[currentQuestion.id] !== undefined;
  };

  const handleApplyImprovements = async () => {
    if (!project || !projectId || acceptedImprovements.size === 0) return;
    
    try {
      const updatedSurvey = JSON.parse(JSON.stringify(project.survey_json));
      
      // Apply each accepted improvement
      for (const improvement of improvements) {
        if (acceptedImprovements.has(improvement.question_id)) {
          const updated = _findAndUpdateQuestion(
            updatedSurvey,
            improvement.question_id,
            improvement.improved
          );
          if (!updated) {
            console.warn(`Question ${improvement.question_id} not found`);
          }
        }
      }
      
      // Save updated survey
      const response = await updateProject(projectId, {
        survey_json: updatedSurvey
      });
      
      if (response.success) {
        alert(`Successfully applied ${acceptedImprovements.size} improvement${acceptedImprovements.size !== 1 ? 's' : ''}!`);
        navigate(`/project/${projectId}`);
      } else {
        alert('Failed to apply changes. Please try again.');
      }
    } catch (error) {
      console.error('Error applying improvements:', error);
      alert('Failed to apply changes. Please try again.');
    }
  };
  
  const _findAndUpdateQuestion = (survey: any, questionId: string, improvedData: any): boolean => {
    // Helper to update a question in the survey structure
    const updateQuestion = (q: any) => {
      if (q.question_id === questionId) {
        // Update question text
        if (improvedData.question_text) {
          q.question_text = improvedData.question_text;
        }
        // Update options if they exist
        if (improvedData.options && improvedData.options.length > 0) {
          q.options = improvedData.options;
        }
        return true;
      }
      return false;
    };
    
    // Check SCREENER
    if (survey.SCREENER?.questions) {
      for (const q of survey.SCREENER.questions) {
        if (updateQuestion(q)) return true;
      }
    }
    
    // Check MAIN_SECTION
    if (survey.MAIN_SECTION?.sub_sections) {
      for (const subsection of survey.MAIN_SECTION.sub_sections) {
        if (subsection.questions) {
          for (const q of subsection.questions) {
            if (updateQuestion(q)) return true;
          }
        }
      }
    }
    
    // Check DEMOGRAPHICS
    if (survey.DEMOGRAPHICS?.questions) {
      for (const q of survey.DEMOGRAPHICS.questions) {
        if (updateQuestion(q)) return true;
      }
    }
    
    return false;
  };

  console.log('[RENDER] Current render state:', {
    loading,
    hasProject: !!project,
    hasSurveyJson: !!project?.survey_json,
    previewQuestionsLength: previewQuestions.length,
    isComplete,
    currentQuestionIndex
  });

  if (loading) {
    console.log('[RENDER] Rendering loading state');
    return (
      <div className="flex items-center justify-center min-h-screen bg-amber-50">
        <div className="text-gray-600">Loading preview...</div>
      </div>
    );
  }

  if (!project || !project.survey_json || previewQuestions.length === 0) {
    console.log('[RENDER] Rendering no survey state:', {
      noProject: !project,
      noSurveyJson: !project?.survey_json,
      noPreviewQuestions: previewQuestions.length === 0
    });
    return (
      <div className="min-h-screen bg-amber-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-700">No survey available to preview.</p>
            <p className="text-sm text-gray-500 mt-2">
              Debug info: Project={!!project}, SurveyJSON={!!project?.survey_json}, Questions={previewQuestions.length}
            </p>
            <button
              onClick={() => navigate(`/project/${projectId}`)}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              ← Back to Project
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="min-h-screen bg-amber-50">
        {/* Header */}
        <div className="bg-amber-100 border-b border-amber-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-amber-700 font-semibold">⚠️ PREVIEW MODE</span>
            <span className="text-gray-600">|</span>
            <span className="text-gray-700">{project.name}</span>
          </div>
          <button
            onClick={() => navigate(`/project/${projectId}`)}
            className="text-gray-600 hover:text-gray-800 font-medium"
          >
            Exit Preview ✕
          </button>
        </div>

        {/* Completion Screen */}
        <div className="max-w-3xl mx-auto p-8">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Preview Complete</h2>
              <p className="text-gray-600">
                {previewQuestions.length} questions reviewed | {processedCommentCount || comments.length} comments added
              </p>
            </div>

            {comments.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Your Comments</h3>
                <div className="space-y-3">
                  {comments.map((comment) => {
                    const question = previewQuestions.find(q => q.id === comment.question_id);
                    return (
                      <div key={comment.id} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-2">
                          On: <span className="font-medium">{question?.id}</span>
                        </p>
                        <p className="text-gray-800">{comment.text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* AI Improvements */}
            {(loadingImprovements || improvements.length > 0) && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  🤖 AI Improvements
                </h3>
                
                {loadingImprovements ? (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                    <div className="animate-pulse text-blue-600">Generating improvements...</div>
                  </div>
                ) : improvements.length > 0 ? (
                  <>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                      <p className="text-gray-700">
                        Based on your feedback, AI has suggested improvements to {improvements.length} question{improvements.length !== 1 ? 's' : ''}.
                        Review each change and accept or reject it.
                      </p>
                    </div>
                    
                    <div className="space-y-6 mb-6">
                      {improvements.map((improvement) => {
                        const isAccepted = acceptedImprovements.has(improvement.question_id);
                        
                        return (
                          <div key={improvement.question_id} className="border-2 border-gray-300 rounded-lg p-4">
                            <div className="mb-3">
                              <span className="text-sm font-medium text-gray-600">Question ID: </span>
                              <code className="bg-gray-100 px-2 py-0.5 rounded text-sm">{improvement.question_id}</code>
                            </div>
                            
                            <div className="mb-3">
                              <span className="text-sm font-medium text-gray-600">Your feedback: </span>
                              <span className="text-sm italic text-gray-700">"{improvement.feedback}"</span>
                            </div>
                            
                            <div className="grid md:grid-cols-2 gap-4 mb-4">
                              {/* Original */}
                              <div className="bg-red-50 border border-red-200 rounded p-3">
                                <div className="text-xs font-semibold text-red-700 mb-2">ORIGINAL</div>
                                <div className="text-sm text-gray-800 font-medium mb-2">
                                  {improvement.original.question_text}
                                </div>
                                {improvement.original.options && improvement.original.options.length > 0 && (
                                  <div className="text-xs text-gray-600">
                                    <div className="font-medium mb-1">Options:</div>
                                    <ul className="list-disc list-inside">
                                      {improvement.original.options.map((opt: string, idx: number) => (
                                        <li key={idx}>{opt}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                              
                              {/* Improved */}
                              <div className="bg-green-50 border border-green-200 rounded p-3">
                                <div className="text-xs font-semibold text-green-700 mb-2">IMPROVED</div>
                                <div className="text-sm text-gray-800 font-medium mb-2">
                                  {improvement.improved.question_text}
                                </div>
                                {improvement.improved.options && improvement.improved.options.length > 0 && (
                                  <div className="text-xs text-gray-600">
                                    <div className="font-medium mb-1">Options:</div>
                                    <ul className="list-disc list-inside">
                                      {improvement.improved.options.map((opt: string, idx: number) => (
                                        <li key={idx}>{opt}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            {improvement.explanation && (
                              <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
                                <div className="text-xs font-semibold text-blue-700 mb-1">WHY THIS CHANGE</div>
                                <div className="text-sm text-gray-700">{improvement.explanation}</div>
                              </div>
                            )}
                            
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  const newAccepted = new Set(acceptedImprovements);
                                  if (isAccepted) {
                                    newAccepted.delete(improvement.question_id);
                                  } else {
                                    newAccepted.add(improvement.question_id);
                                  }
                                  setAcceptedImprovements(newAccepted);
                                }}
                                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                                  isAccepted
                                    ? 'bg-green-600 text-white hover:bg-green-700'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                              >
                                {isAccepted ? '✓ Accepted' : 'Accept'}
                              </button>
                              <button
                                onClick={() => {
                                  const newAccepted = new Set(acceptedImprovements);
                                  newAccepted.delete(improvement.question_id);
                                  setAcceptedImprovements(newAccepted);
                                }}
                                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                                  !isAccepted
                                    ? 'bg-red-600 text-white hover:bg-red-700'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                              >
                                {!isAccepted ? '✓ Rejected' : 'Reject'}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {acceptedImprovements.size > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                        <p className="text-green-800 font-medium mb-2">
                          {acceptedImprovements.size} improvement{acceptedImprovements.size !== 1 ? 's' : ''} accepted
                        </p>
                        <button
                          onClick={handleApplyImprovements}
                          className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
                        >
                          ✨ Apply Accepted Changes
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                    <p className="text-yellow-800">
                      No improvements could be generated from your comments.
                    </p>
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <button
                onClick={() => {
                  setIsComplete(false);
                  setCurrentQuestionIndex(0);
                }}
                className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors font-medium"
              >
                Review Again
              </button>
              <button
                onClick={() => navigate(`/project/${projectId}`)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
              >
                Return to Editor
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Navigation Panel Component
  const NavigationPanel = () => {
    const getQuestionNumber = (questionId: string): number => {
      return allQuestionsIncludingHidden.findIndex(q => q.id === questionId) + 1;
    };
    
    const getStatusIcon = (status: string) => {
      switch (status) {
        case 'answered':
          return (
            <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
              <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
              </svg>
            </div>
          );
        case 'shown':
          return (
            <div className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
              <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd"/>
              </svg>
            </div>
          );
        case 'skipped':
          return (
            <div className="w-4 h-4 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
              <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
              </svg>
            </div>
          );
        case 'error':
          return (
            <div className="w-4 h-4 rounded-full bg-orange-500 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">!</span>
            </div>
          );
        default: // pending
          return <div className="w-4 h-4 rounded-full bg-gray-300 flex-shrink-0"></div>;
      }
    };
    
    return (
      <div 
        className={`
          fixed left-0 top-16 bottom-0 w-80 bg-white border-r-2 border-gray-200 
          shadow-lg overflow-y-auto transition-transform z-20
          ${showNavigationPanel ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Panel Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-3 z-10">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-xs text-gray-900">Question Flow</h3>
            <button
              onClick={() => setShowNavigationPanel(false)}
              className="text-gray-400 hover:text-gray-600 text-xs transition-colors"
            >
              Hide Panel
            </button>
          </div>
          
          {/* Legend - 2 column grid, smaller */}
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
              <span className="text-gray-600 text-xs">Answered</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
              <span className="text-gray-600 text-xs">Current</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0"></div>
              <span className="text-gray-600 text-xs">Skipped</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-gray-300 flex-shrink-0"></div>
              <span className="text-gray-600 text-xs">Pending</span>
            </div>
          </div>
          
          {/* Cell Assignment Selector */}
          <div className="mt-3 border-t border-gray-200 pt-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">Test Cell Assignment</label>
            <select
              value={answers.cell_assignment || answers.flavor_cell || ''}
              onChange={(e) => {
                const value = e.target.value;
                setAnswers(prev => ({
                  ...prev,
                  cell_assignment: value,
                  flavor_cell: value
                }));
                setSelectedCell(value || 'Kawakawa'); // Also update selectedCell for piping
                console.log(`[CELL ASSIGNMENT] Changed to: ${value}`);
              }}
              className="w-full text-xs border border-gray-300 rounded px-2 py-1 bg-white text-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="">No Assignment</option>
              <option value="Kawakawa">Kawakawa Cell</option>
              <option value="Horopito">Horopito Cell</option>
              <option value="Manuka">Manuka Cell</option>
            </select>
          </div>
        </div>
        
        {/* Question List */}
        <div className="p-2 space-y-1">
          {allQuestionsIncludingHidden.map((question, index) => {
            const validation = questionValidation[question.id];
            const isCurrent = previewQuestions[currentQuestionIndex]?.id === question.id;
            
            // Evaluate skip logic for this question
            const { shouldShow, reason } = evaluateSkipLogic(question, answers);
            
            // Determine status
            let status: string;
            if (answers[question.id] !== undefined) {
              status = 'answered';
            } else if (isCurrent) {
              status = 'shown';
            } else if (!shouldShow) {
              status = 'skipped';
            } else if (validation?.status) {
              status = validation.status;
            } else {
              status = 'pending';
            }
            
            // Apply piping to question text
            const displayText = applyPiping(question.text, answers);
            
            // Check if question uses piping
            const usesPiping = question.text.includes('[PIPE:') || question.text.includes('{');
            let pipedSources: string[] = [];
            if (usesPiping) {
              // Check for both [PIPE: ...] and {question_id} formats
              const pipeMatches = question.text.match(/\[PIPE:\s*([^\]]+)\]/g);
              const simpleMatches = question.text.match(/\{([^}]+)\}/g);
              
              if (pipeMatches) {
                pipedSources.push(...pipeMatches.map(m => m.match(/\[PIPE:\s*([^\]]+)\]/)?.[1] || ''));
              }
              if (simpleMatches) {
                pipedSources.push(...simpleMatches.map(m => m.slice(1, -1)));
              }
              
              pipedSources = [...new Set(pipedSources.filter(s => s))];
            }
            
            return (
              <div
                key={question.id}
                onClick={() => {
                  const targetIndex = previewQuestions.findIndex(q => q.id === question.id);
                  if (targetIndex !== -1) {
                    setCurrentQuestionIndex(targetIndex);
                  }
                }}
                className={`
                  group p-2.5 rounded-md cursor-pointer
                  transition-all duration-150 border
                  ${isCurrent 
                    ? 'bg-blue-50 border-blue-300 shadow-sm' 
                    : status === 'skipped'
                    ? 'opacity-60 cursor-not-allowed border-transparent'
                    : 'border-transparent hover:bg-gray-50 hover:border-gray-200'
                  }
                `}
              >
                <div className="flex items-start gap-2.5">
                  {/* Status Indicator */}
                  {getStatusIcon(status)}
                  
                  {/* Question Info */}
                  <div className="flex-1 min-w-0">
                    {/* Question text - show 2 lines before truncating */}
                    <div 
                      className="text-xs font-medium text-gray-900 leading-tight overflow-hidden mb-1"
                      style={{
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}
                    >
                      Q{index + 1}: {displayText}
                    </div>
                    
                    {/* Section and type - very subtle */}
                    <div className="text-xs text-gray-500">
                      {question.section} • {question.type.replace(/_/g, ' ')}
                    </div>
                    
                    {/* Show answer if provided - subtle gray background */}
                    {answers[question.id] !== undefined && (
                      <div className="mt-1.5 text-xs text-gray-600 bg-gray-50 rounded px-2 py-1 border border-gray-200">
                        <span className="font-medium">Answer:</span>{' '}
                        <span className="text-gray-700">
                          {Array.isArray(answers[question.id]) 
                            ? answers[question.id].join(', ') 
                            : String(answers[question.id])}
                        </span>
                      </div>
                    )}
                    
                    {/* Show skip reason if skipped */}
                    {status === 'skipped' && reason && (
                      <div className="mt-1.5 p-1.5 bg-red-50 border border-red-200 rounded">
                        <div className="text-xs font-medium text-red-900">Skipped</div>
                        <div className="text-xs text-red-700 mt-0.5">{reason}</div>
                      </div>
                    )}
                    
                    {/* Show piping sources */}
                    {usesPiping && pipedSources.length > 0 && (
                      <div className="mt-1.5 flex items-center gap-1 flex-wrap">
                        <span className="text-xs text-blue-700 font-medium">⚡</span>
                        {pipedSources.map(src => (
                          <span key={src} className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                            {src}
                          </span>
                        ))}
                      </div>
                    )}
                    
                    {/* Show dependencies from skip logic */}
                    {question.skip_logic && (
                      <div className="mt-1.5 flex items-center gap-1">
                        <span className="text-xs text-amber-700 font-medium">⚠️</span>
                        <span className="text-xs text-amber-700">
                          {question.skip_logic.simple_condition && (
                            <>Depends on Q{question.skip_logic.simple_condition.target_question_id}</>
                          )}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Bottom indicator */}
        <div className="sticky bottom-0 bg-gradient-to-t from-white via-white to-transparent py-2 text-center">
          <div className="text-xs text-gray-400">
            {allQuestionsIncludingHidden.length} questions total
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-amber-50">
      {/* Navigation Panel */}
      <NavigationPanel />
      
      {/* Toggle Button When Panel Hidden */}
      {!showNavigationPanel && (
        <button
          onClick={() => setShowNavigationPanel(true)}
          className="fixed left-4 top-40 z-30 bg-blue-600 text-white p-3 rounded-r-lg shadow-lg hover:bg-blue-700 transition-all"
          title="Show Question Flow"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      )}
      
      {/* Main Content with Panel Offset */}
      <div className={`transition-all duration-300 ${showNavigationPanel ? 'ml-80' : 'ml-0'}`}>
      {/* Survey Introduction Screen */}
      {showIntro && (
        <div className="min-h-screen flex items-center justify-center p-6">
          <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md border border-gray-200 p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Survey Preview
            </h1>
            
            <div className="space-y-4 text-gray-700">
              <p className="text-lg">
                Thank you for participating in this survey. Your feedback is valuable to us.
              </p>
              
              <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                <div className="flex items-start gap-3">
                  <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <div className="font-semibold text-blue-900">Estimated Time</div>
                    <div className="text-blue-800">
                      This survey takes approximately {estimatedMinutes} minutes to complete
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 border border-gray-200 p-4 rounded">
                <div className="font-semibold text-gray-900 mb-2">What to expect:</div>
                <ul className="list-disc list-inside space-y-1 text-gray-700">
                  <li>{previewQuestions.length} questions total</li>
                  <li>You can go back to review your answers</li>
                  <li>Your progress is shown at the bottom of each page</li>
                  <li>You can add comments to any question for feedback</li>
                </ul>
              </div>
            </div>
            
            <button
              onClick={() => setShowIntro(false)}
              className="mt-6 w-full px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
            >
              Start Survey →
            </button>
          </div>
        </div>
      )}

      {/* Main Survey Interface */}
      {!showIntro && currentQuestion && (
        <>
          {/* Header */}
          <div className="sticky top-16 z-40 bg-amber-100 border-b border-amber-200 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-amber-700 font-semibold">⚠️ PREVIEW MODE</span>
              <span className="text-gray-600">|</span>
              <span className="text-gray-700">{project.name}</span>
            </div>
            <button
              onClick={() => navigate(`/project/${projectId}`)}
              className="text-gray-600 hover:text-gray-800 font-medium"
            >
              Exit Preview ✕
            </button>
          </div>

          {/* Question Counter - Keep at top */}
          <div className="sticky top-[120px] z-30 bg-white border-b border-gray-200 px-6 py-2.5">
        <div className="max-w-3xl mx-auto">
          <div className="text-center">
            <span className="text-sm font-medium text-gray-600">
              Question {currentQuestionIndex + 1} of {previewQuestions.length}
            </span>
          </div>
        </div>
      </div>

      {/* Question Display */}
      <div className="max-w-2xl mx-auto p-8 pt-8 pb-32">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          {/* Question Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1.5">
                  {currentQuestion.section}
                </div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 leading-normal">
                  {applyPiping(currentQuestion.text, answers)}
                </h2>
              </div>
              <button
                onClick={() => setShowCommentBox(!showCommentBox)}
                className="ml-4 px-4 py-2 bg-amber-100 hover:bg-amber-200 text-amber-700 rounded-lg transition-colors flex items-center gap-2"
              >
                💬 {getQuestionComments(currentQuestion.id).length > 0 
                  ? `${getQuestionComments(currentQuestion.id).length} comment${getQuestionComments(currentQuestion.id).length !== 1 ? 's' : ''}`
                  : 'Add Comment'}
              </button>
            </div>

            {/* Comment Box */}
            {showCommentBox && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add your feedback about this question:
                </label>
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="e.g., 'Add a not sure option' or 'Scale feels too granular'"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                />
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={handleAddComment}
                    disabled={!commentText.trim()}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Save Comment
                  </button>
                  <button
                    onClick={() => {
                      setShowCommentBox(false);
                      setCommentText('');
                    }}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Previous Comments */}
            {getQuestionComments(currentQuestion.id).length > 0 && !showCommentBox && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Your previous comments:
                </p>
                {getQuestionComments(currentQuestion.id).map((comment) => (
                  <div key={comment.id} className="text-sm text-gray-600 mb-1">
                    • {comment.text}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Question Response Area */}
          <div className="mb-8">
            {renderQuestionInput(currentQuestion, answers[currentQuestion.id], handleAnswer, answers, handleMatrixAnswer, project)}
          </div>

          {/* Navigation removed from here - now handled by sticky bottom navigation */}
        </div>

        {/* Editor Notes */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
          <p className="font-medium mb-1">💡 Editor Notes</p>
          <p>Question ID: <code className="bg-blue-100 px-2 py-0.5 rounded">{currentQuestion.id}</code></p>
          <p>Type: {currentQuestion.type}</p>
        </div>
      </div>

      {/* Sticky Navigation Buttons */}
      <div className={`fixed bottom-12 left-0 right-0 z-10 bg-white border-t border-gray-100 py-3 px-6 shadow-lg transition-all duration-300 ${showNavigationPanel ? 'ml-80' : 'ml-0'}`}>
        <div className="max-w-2xl mx-auto flex justify-between items-center gap-4">
          <button
            onClick={handleBack}
            disabled={currentQuestionIndex === 0}
            className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            aria-label="Go to previous question"
            aria-disabled={currentQuestionIndex === 0}
          >
            ← Back
          </button>
          
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className={`px-6 py-2.5 text-sm font-semibold rounded-lg transition-all shadow-sm ${
              canProceed()
                ? 'text-white bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            aria-label={currentQuestionIndex === previewQuestions.length - 1 ? 'Finish survey preview' : 'Go to next question'}
          >
            {currentQuestionIndex === previewQuestions.length - 1 ? 'Finish Preview' : 'Continue →'}
          </button>
        </div>
      </div>

      {/* Progress Bar - Bottom */}
      <div 
        className={`fixed bottom-0 left-0 right-0 z-0 bg-white border-t border-gray-200 px-6 py-2.5 shadow-lg transition-all duration-300 ${showNavigationPanel ? 'ml-80' : 'ml-0'}`}
        role="progressbar"
        aria-valuenow={Math.round(progress)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Survey progress: ${Math.round(progress)}% complete`}
      >
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1.5">
            <span className="font-medium">
              {Math.round(progress)}% complete
            </span>
            <span>
              {previewQuestions.length - currentQuestionIndex - 1} questions remaining
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
        </>
      )}

      {/* Fallback when no current question */}
      {!showIntro && !currentQuestion && (
        <div className="min-h-screen bg-amber-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Preview Complete</h2>
            <p className="text-gray-600 mb-6">
              You've reached the end of the survey preview.
            </p>
            <button
              onClick={() => navigate(`/project/${projectId}`)}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Return to Project
            </button>
          </div>
        </div>
      )}

      {/* Lightbox for image viewing */}
      {lightboxOpen && currentArtefact && (
        <div 
          className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4"
          onClick={() => setLightboxOpen(false)}
        >
          <img
            src={currentArtefact.url}
            alt={currentArtefact.title || 'Stimulus image'}
            className="max-w-full max-h-full object-contain"
          />
          <button
            className="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-75"
            onClick={() => setLightboxOpen(false)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
      
      {/* Termination Notification Modal */}
      {terminationNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Survey Termination</h3>
                <p className="text-sm text-gray-600">Rule: {terminationNotification.ruleId}</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              {terminationNotification.reason}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => {
                  setTerminationNotification(null);
                  // Go back to the question that caused termination
                  const questionIndex = previewQuestions.findIndex(q => q.id === terminationNotification.questionId);
                  if (questionIndex !== -1) {
                    setCurrentQuestionIndex(questionIndex);
                  }
                }}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Go Back & Fix Response
              </button>
              <button
                onClick={() => {
                  setTerminationNotification(null);
                  // Continue to next question (ignore termination in test mode)
                  if (currentQuestionIndex < previewQuestions.length - 1) {
                    setCurrentQuestionIndex(currentQuestionIndex + 1);
                  }
                }}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Skip & Continue Testing
              </button>
            </div>
          </div>
        </div>
      )}
      
      </div> {/* Close Main Content with Panel Offset */}
    </div>
  );
}

function renderQuestionInput(
  question: PreviewQuestion, 
  answer: any, 
  onAnswer: (value: any) => void,
  allAnswers?: Record<string, any>,
  onMatrixAnswer?: (questionId: string, value: any) => void,
  project?: any
) {
  const { type, options, rows, columns } = question;

  // Single Select (single_choice or single_select)
  if ((type === 'single_choice' || type === 'single_select') && options) {
    return (
      <div className="space-y-2.5">
        {options.map((option, idx) => (
          <label
            key={idx}
            className="flex items-center gap-3 p-3.5 border-2 rounded-lg cursor-pointer transition-all duration-150 hover:bg-blue-50 hover:border-blue-300 has-[:checked]:bg-blue-50 has-[:checked]:border-blue-600 min-h-[48px]"
          >
            <input
              type="radio"
              name={question.id}
              value={option}
              checked={answer === option}
              onChange={(e) => onAnswer(e.target.value)}
              className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            />
            <span className="text-sm font-normal text-gray-900 flex-1">{option}</span>
          </label>
        ))}
      </div>
    );
  }

  // Multi Select (multiple_choice or multi_select)
  if ((type === 'multiple_choice' || type === 'multi_select') && options) {
    const selectedOptions = answer || [];
    return (
      <div className="space-y-2.5">
        {options.map((option, idx) => (
          <label
            key={idx}
            className="flex items-center gap-3 p-3.5 border-2 rounded-lg cursor-pointer transition-all duration-150 hover:bg-blue-50 hover:border-blue-300 has-[:checked]:bg-blue-50 has-[:checked]:border-blue-600 min-h-[48px]"
          >
            <input
              type="checkbox"
              value={option}
              checked={selectedOptions.includes(option)}
              onChange={(e) => {
                const newSelected = e.target.checked
                  ? [...selectedOptions, option]
                  : selectedOptions.filter((o: string) => o !== option);
                onAnswer(newSelected);
              }}
              className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
            />
            <span className="text-sm font-normal text-gray-900 flex-1">{option}</span>
          </label>
        ))}
      </div>
    );
  }

  // Open End (open_ended or open_end)
  if (type === 'open_ended' || type === 'open_end') {
    return (
      <textarea
        value={answer || ''}
        onChange={(e) => onAnswer(e.target.value)}
        placeholder="Please share your thoughts..."
        rows={5}
        className="w-full p-3.5 border-2 border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none resize-y text-gray-900 placeholder-gray-400 transition-all leading-relaxed"
      />
    );
  }

  // Numeric (numeric_input or numeric)
  if (type === 'numeric_input' || type === 'numeric') {
    return (
      <div className="max-w-xs">
        <input
          type="number"
          value={answer || ''}
          onChange={(e) => onAnswer(e.target.value)}
          placeholder="Enter a number"
          className="w-full p-3.5 border-2 border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
      </div>
    );
  }

  // Rating Scale (scale or rating_scale)
  if ((type === 'scale' || type === 'rating_scale') && options) {
    return (
      <div className="py-3">
        <div className="flex justify-between gap-2">
          {options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => onAnswer(option)}
              className={`flex-1 py-3 px-2 rounded-lg border-2 font-semibold text-center transition-all duration-200 min-w-[44px] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                answer === option
                  ? 'bg-blue-600 border-blue-600 text-white shadow-md transform scale-105'
                  : 'bg-white border-gray-300 text-gray-700 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Matrix - Sequential presentation
  if (type === 'matrix' && rows && columns && allAnswers && onMatrixAnswer) {
    return (
      <MatrixQuestion 
        question={question}
        answers={allAnswers}
        onAnswer={onMatrixAnswer}
      />
    );
  }

  // Legacy Matrix fallback (if needed)
  if (type === 'matrix' && rows && columns) {
    const matrixAnswers = answer || {};
    return (
      <div className="text-center p-4 text-gray-600">
        Matrix questions are now displayed one item at a time for better user experience.
      </div>
    );
  }

  // Stimulus Display - Images/Videos
  if (type === 'stimulus_display') {
    // Find the artefact from STUDY_METADATA
    const artefacts = project?.survey_json?.STUDY_METADATA?.artefacts || [];
    const artefact = artefacts.find((a: any) => a.artefact_id === (question as any).displays_artefact);
    
    return (
      <div className="space-y-4">
        {artefact && (
          <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6">
            {artefact.title && (
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {artefact.title}
              </h3>
            )}
            
            {/* Image Display */}
            {artefact.artefact_type === 'image' && artefact.url && (
              <div className="relative">
                <img
                  src={artefact.url}
                  alt={artefact.title || 'Stimulus image'}
                  className="max-w-full h-auto rounded-lg shadow-md cursor-pointer hover:shadow-xl transition-shadow"
                  onClick={() => {
                    setCurrentArtefact(artefact);
                    setLightboxOpen(true);
                  }}
                  loading="lazy"
                />
                <div className="text-xs text-gray-500 mt-2 text-center">
                  Click to view larger
                </div>
              </div>
            )}
            
            {/* Video Display */}
            {artefact.artefact_type === 'video' && artefact.url && (
              <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
                <video
                  controls
                  className="w-full h-full"
                  poster={artefact.thumbnail_url}
                >
                  <source src={artefact.url} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            )}
            
            {/* Text Content */}
            {artefact.content && (
              <div className="prose max-w-none text-gray-700 mt-4">
                {artefact.content}
              </div>
            )}
          </div>
        )}
        
        <div className="text-sm text-gray-500 italic text-center">
          Please review the above before continuing.
        </div>
      </div>
    );
  }

  // Ranking Questions - Basic implementation (can be enhanced with drag-and-drop later)
  if (type === 'ranking' && options) {
    const rankedItems = answer || [];
    const availableItems = options.filter(item => !rankedItems.includes(item));
    
    const handleItemSelect = (item: string) => {
      const newRanked = [...rankedItems, item];
      onAnswer(newRanked);
    };
    
    const handleItemRemove = (index: number) => {
      const newRanked = rankedItems.filter((_: any, i: number) => i !== index);
      onAnswer(newRanked);
    };
    
    return (
      <div className="space-y-3">
        <div className="text-xs text-gray-600 mb-3">
          Click items below to rank them in order of preference (1 = most preferred)
        </div>
        
        {/* Ranked items */}
        {rankedItems.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-900">Your ranking:</h4>
            {rankedItems.map((item: string, index: number) => (
              <div
                key={item}
                className="flex items-center gap-3 p-3.5 bg-blue-50 border-2 border-blue-200 rounded-lg"
              >
                <div className="flex items-center justify-center w-7 h-7 bg-blue-600 text-white font-semibold rounded-full flex-shrink-0 text-xs">
                  {index + 1}
                </div>
                <div className="flex-1 font-normal text-sm text-gray-900">{item}</div>
                <button
                  onClick={() => handleItemRemove(index)}
                  className="text-red-600 hover:text-red-800 p-1 rounded transition-colors"
                  aria-label={`Remove ${item} from ranking`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        
        {/* Available items to rank */}
        {availableItems.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-900">
              {rankedItems.length === 0 ? 'Click to rank items:' : 'Remaining items:'}
            </h4>
            {availableItems.map((item: string) => (
              <button
                key={item}
                onClick={() => handleItemSelect(item)}
                className="w-full flex items-center gap-3 p-3.5 bg-white border-2 border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-left min-h-[48px]"
              >
                <div className="flex-1 font-normal text-sm text-gray-900">{item}</div>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }
  return (
    <div className="p-4 bg-gray-100 border border-gray-300 rounded-lg text-gray-600">
      Preview not available for this question type ({type})
    </div>
  );
}
