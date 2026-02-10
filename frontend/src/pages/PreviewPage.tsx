import { useState, useEffect } from 'react';
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

  useEffect(() => {
    loadProject();
    loadComments();
  }, [projectId]);

  useEffect(() => {
    if (project?.survey_json) {
      extractVisibleQuestions();
    }
  }, [project]);

  async function loadProject() {
    if (!projectId) return;
    
    setLoading(true);
    const response = await getProject(projectId);
    
    if (response.success && response.data) {
      setProject(response.data);
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

  function extractVisibleQuestions() {
    if (!project?.survey_json) return;

    const questions: PreviewQuestion[] = [];
    const survey = project.survey_json;

    // Helper to add questions from a section
    const addQuestions = (sectionQuestions: any[], sectionName: string) => {
      sectionQuestions?.forEach((q: any) => {
        // Only include visible questions
        if (q.loi_visibility === 'visible' || q.user_override === 'pinned') {
          questions.push({
            id: q.question_id,
            text: q.question_text,
            type: q.question_type,
            options: q.options,
            rows: q.rows,
            columns: q.columns,
            section: sectionName,
          });
        }
      });
    };

    // Add screener questions
    if (survey.SCREENER?.questions) {
      addQuestions(survey.SCREENER.questions, 'Screener');
    }

    // Add main section questions
    if (survey.MAIN_SECTION?.sub_sections) {
      survey.MAIN_SECTION.sub_sections.forEach((subsection: any) => {
        if (subsection.questions) {
          addQuestions(subsection.questions, subsection.subsection_title || 'Main Survey');
        }
      });
    }

    // Add demographics questions
    if (survey.DEMOGRAPHICS?.questions) {
      addQuestions(survey.DEMOGRAPHICS.questions, 'Demographics');
    }

    setPreviewQuestions(questions);
  }

  const currentQuestion = previewQuestions[currentQuestionIndex];
  const progress = previewQuestions.length > 0 
    ? ((currentQuestionIndex + 1) / previewQuestions.length) * 100 
    : 0;

  const handleNext = async () => {
    if (currentQuestionIndex < previewQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setShowCommentBox(false);
      setCommentText('');
    } else {
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
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setShowCommentBox(false);
      setCommentText('');
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
      setAnswers({
        ...answers,
        [currentQuestion.id]: value,
      });
    }
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-amber-50">
        <div className="text-gray-600">Loading preview...</div>
      </div>
    );
  }

  if (!project || !project.survey_json || previewQuestions.length === 0) {
    return (
      <div className="min-h-screen bg-amber-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-700">No survey available to preview.</p>
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

      {/* Progress Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Question {currentQuestionIndex + 1} of {previewQuestions.length}
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(progress)}% complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Question Display */}
      <div className="max-w-2xl mx-auto p-8">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          {/* Question Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <span className="text-sm text-gray-500 mb-2 block">{currentQuestion.section}</span>
                <h2 className="text-2xl font-medium text-gray-800">
                  {currentQuestion.text}
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
            {renderQuestionInput(currentQuestion, answers[currentQuestion.id], handleAnswer)}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between pt-6 border-t border-gray-200">
            <button
              onClick={handleBack}
              disabled={currentQuestionIndex === 0}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Back
            </button>
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              {currentQuestionIndex === previewQuestions.length - 1 ? 'Finish Preview' : 'Next →'}
            </button>
          </div>
        </div>

        {/* Editor Notes */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
          <p className="font-medium mb-1">💡 Editor Notes</p>
          <p>Question ID: <code className="bg-blue-100 px-2 py-0.5 rounded">{currentQuestion.id}</code></p>
          <p>Type: {currentQuestion.type}</p>
        </div>
      </div>
    </div>
  );
}

function renderQuestionInput(question: PreviewQuestion, answer: any, onAnswer: (value: any) => void) {
  const { type, options, rows, columns } = question;

  // Single Select (single_choice or single_select)
  if ((type === 'single_choice' || type === 'single_select') && options) {
    return (
      <div className="space-y-3">
        {options.map((option, idx) => (
          <label
            key={idx}
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <input
              type="radio"
              name={question.id}
              value={option}
              checked={answer === option}
              onChange={(e) => onAnswer(e.target.value)}
              className="w-5 h-5 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-gray-700">{option}</span>
          </label>
        ))}
      </div>
    );
  }

  // Multi Select (multiple_choice or multi_select)
  if ((type === 'multiple_choice' || type === 'multi_select') && options) {
    const selectedOptions = answer || [];
    return (
      <div className="space-y-3">
        {options.map((option, idx) => (
          <label
            key={idx}
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
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
              className="w-5 h-5 text-blue-600 focus:ring-blue-500 rounded"
            />
            <span className="text-gray-700">{option}</span>
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
        placeholder="Type your answer here..."
        rows={4}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
    );
  }

  // Numeric (numeric_input or numeric)
  if (type === 'numeric_input' || type === 'numeric') {
    return (
      <input
        type="number"
        value={answer || ''}
        onChange={(e) => onAnswer(e.target.value)}
        placeholder="Enter a number"
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
    );
  }

  // Rating Scale (scale or rating_scale)
  if ((type === 'scale' || type === 'rating_scale') && options) {
    return (
      <div className="flex justify-between gap-2">
        {options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => onAnswer(option)}
            className={`flex-1 px-4 py-3 border-2 rounded-lg font-medium transition-colors ${
              answer === option
                ? 'border-blue-600 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    );
  }

  // Matrix
  if (type === 'matrix' && rows && columns) {
    const matrixAnswers = answer || {};
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 bg-gray-100 px-4 py-2 text-left"></th>
              {columns.map((col, idx) => (
                <th key={idx} className="border border-gray-300 bg-gray-100 px-4 py-2 text-center text-sm">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx}>
                <td className="border border-gray-300 bg-gray-50 px-4 py-3 font-medium text-sm">
                  {row}
                </td>
                {columns.map((col, colIdx) => (
                  <td key={colIdx} className="border border-gray-300 px-4 py-3 text-center">
                    <input
                      type="radio"
                      name={`${question.id}_${row}`}
                      checked={matrixAnswers[row] === col}
                      onChange={() => onAnswer({ ...matrixAnswers, [row]: col })}
                      className="w-5 h-5 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Default fallback
  return (
    <div className="p-4 bg-gray-100 border border-gray-300 rounded-lg text-gray-600">
      Preview not available for this question type ({type})
    </div>
  );
}
