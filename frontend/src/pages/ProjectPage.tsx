import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, generateSurvey, generateSurveyStream, updateProject, updateLOI, pinQuestion, excludeQuestion, resetQuestionOverride, editQuestion, deleteQuestion, reorderQuestion, editSection, addQuestion } from '../api/client';
import type { Project, ValidationLogEntry } from '../types';
import LOISlider from '../components/LOISlider';
import QuestionCard from '../components/QuestionCard';
import StreamingModal from '../components/StreamingModal';
import EditableHeader from '../components/EditableHeader';
import AddQuestionModal from '../components/AddQuestionModal';

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState('');
  const [showStreamingModal, setShowStreamingModal] = useState(false);
  
  const [selectedTab, setSelectedTab] = useState<'overview' | 'survey' | 'validation'>('overview');
  const [loiCollapsed, setLoiCollapsed] = useState(false);
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  async function loadProject() {
    if (!projectId) return;
    
    setLoading(true);
    const response = await getProject(projectId);
    
    if (response.success && response.data) {
      setProject(response.data);
      setError(null);
      // Auto-select survey tab if survey exists
      if (response.data.survey_json) {
        setSelectedTab('survey');
      }
    } else {
      setError(response.error || 'Failed to load project');
    }
    
    setLoading(false);
  }

  async function handleGenerateSurvey() {
    if (!project || !projectId) return;

    if (!project.brief_data) {
      setGenerateError('No brief data found. Please start over from Setup.');
      return;
    }

    setGenerating(true);
    setGenerateError(null);
    setStreamingContent('');
    setShowStreamingModal(true);

    try {
      let finalResult = null;
      
      // Stream the response for visual feedback and capture final result
      for await (const message of generateSurveyStream(project.brief_data)) {
        if (message.type === 'chunk') {
          setStreamingContent(prev => prev + message.data + '\n');
        } else if (message.type === 'final') {
          finalResult = message.data;
        }
      }

      // Use the final result from streaming (no second API call needed)
      if (finalResult) {
        // Validate the survey structure
        const validationLog = finalResult.validation_log || { is_valid: true, errors: [], warnings: [] };
        
        // Update project with survey and validation log
        const updateResponse = await updateProject(projectId, {
          survey_json: finalResult,
          validation_log: validationLog,
        });

        if (updateResponse.success) {
          await loadProject();
          setShowStreamingModal(false);
          setSelectedTab('survey');
        } else {
          console.error('Failed to update project:', updateResponse);
          setGenerateError(`Survey generated but failed to save: ${updateResponse.error || 'Unknown error'}`);
          setShowStreamingModal(false);
        }
      } else {
        setGenerateError('No final result received from stream');
        setShowStreamingModal(false);
      }
    } catch (error) {
      setGenerateError(error instanceof Error ? error.message : 'Streaming failed');
      setShowStreamingModal(false);
    }

    setGenerating(false);
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function getSeverityColor(severity: string) {
    switch (severity) {
      case 'error': return 'text-red-600 bg-red-100 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-100 border-blue-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  }

  async function handleLOISliderChange(newPosition: number) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await updateLOI(project.survey_json, newPosition);
    
    if (response.success && response.data) {
      // Update project with new survey state
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handlePinQuestion(questionId: string) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await pinQuestion(project.survey_json, questionId);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleExcludeQuestion(questionId: string) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await excludeQuestion(project.survey_json, questionId);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleResetQuestionOverride(questionId: string) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await resetQuestionOverride(project.survey_json, questionId);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleEditQuestion(questionId: string, updates: any) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await editQuestion(project.survey_json, questionId, updates);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleDeleteQuestion(questionId: string) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await deleteQuestion(project.survey_json, questionId);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleReorderQuestion(questionId: string, direction: 'up' | 'down') {
    if (!project || !project.survey_json || !projectId) return;

    const response = await reorderQuestion(project.survey_json, questionId, direction);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleEditSection(sectionId: string, subsectionId: string | null, title: string) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await editSection(project.survey_json, sectionId, subsectionId, title);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  async function handleAddQuestion(sectionId: string, subsectionId: string | null, question: any, position?: number) {
    if (!project || !project.survey_json || !projectId) return;

    const response = await addQuestion(project.survey_json, sectionId, subsectionId, question, position);
    
    if (response.success && response.data) {
      await updateProject(projectId, {
        survey_json: response.data.survey,
      });
      await loadProject();
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading project...</div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || 'Project not found'}
        </div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  // Prepare sections data for Add Question modal
  const modalSections = project?.survey_json ? {
    screener: !!project.survey_json.SCREENER,
    mainSections: project.survey_json.MAIN_SECTION?.sub_sections?.map((s: any) => ({
      id: s.subsection_id,
      title: s.subsection_title
    })) || [],
    demographics: !!project.survey_json.DEMOGRAPHICS,
  } : { screener: false, mainSections: [], demographics: false };

  return (
    <>
      <StreamingModal
        isOpen={showStreamingModal}
        title="Generating Survey from Blueprint"
        content={streamingContent}
      />
      <AddQuestionModal
        isOpen={showAddQuestionModal}
        onClose={() => setShowAddQuestionModal(false)}
        onAdd={handleAddQuestion}
        sections={modalSections}
      />
      <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:text-blue-700 mb-2 flex items-center"
        >
          ← Back to Dashboard
        </button>
        <h2 className="text-3xl font-bold text-gray-800">{project.name}</h2>
        {project.description && (
          <p className="text-gray-600 mt-1">{project.description}</p>
        )}
        <p className="text-sm text-gray-500 mt-2">
          Last updated: {formatDate(project.updated_at)}
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setSelectedTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              selectedTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setSelectedTab('survey')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              selectedTab === 'survey'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Survey {project.survey_json && '✓'}
          </button>
          <button
            onClick={() => setSelectedTab('validation')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              selectedTab === 'validation'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Validation {project.validation_log && '🔍'}
          </button>
        </nav>
      </div>

      {/* Overview Tab */}
      {selectedTab === 'overview' && (
        <div className="space-y-6">
          {/* Generate Survey Section */}
          {!project.survey_json && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                Generate Survey
              </h3>
              <p className="text-gray-600 mb-6">
                Ready to create your survey based on the brief and selected methodologies.
              </p>
              
              {generateError && (
                <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {generateError}
                </div>
              )}

              <button
                onClick={handleGenerateSurvey}
                disabled={generating}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {generating ? 'Generating Survey...' : '🎯 Generate Survey'}
              </button>
            </div>
          )}

          {/* Brief Information */}
          {project.brief_data && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                Research Brief
              </h3>
              
              {project.brief_data.objectives && project.brief_data.objectives.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Objectives</h4>
                  <ul className="space-y-1">
                    {project.brief_data.objectives.map((obj: string, idx: number) => (
                      <li key={idx} className="text-gray-600 flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        {obj}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {project.brief_data.target_audience && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Target Audience</h4>
                  <p className="text-gray-600">{project.brief_data.target_audience}</p>
                </div>
              )}

              {project.brief_data.topics && project.brief_data.topics.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {project.brief_data.topics.map((topic: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {project.brief_data.identified_skills && project.brief_data.identified_skills.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Selected Methodologies</h4>
                  <div className="flex flex-wrap gap-2">
                    {project.brief_data.identified_skills.map((skill: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Original Brief Text */}
          {project.brief_text && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                Original Brief
              </h3>
              <div className="bg-gray-50 rounded p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{project.brief_text}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Survey Tab */}
      {selectedTab === 'survey' && (
        <div className="space-y-0">
          {project.survey_json ? (
            <>
              {/* LOI Slider */}
              {project.survey_json.loi_config && (
                <LOISlider
                  loiConfig={project.survey_json.loi_config}
                  onSliderChange={handleLOISliderChange}
                  collapsed={loiCollapsed}
                  onToggleCollapse={() => setLoiCollapsed(!loiCollapsed)}
                />
              )}

              <div className="p-6 space-y-6">
                <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-900">
                    ✓ Survey generated successfully
                  </p>
                  <button
                    onClick={() => setShowAddQuestionModal(true)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium flex items-center gap-2"
                  >
                    <span className="text-lg">+</span> Add Question
                  </button>
                </div>

              {/* Study Metadata */}
              {project.survey_json.STUDY_METADATA && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Study Overview</h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>Type:</strong> {project.survey_json.STUDY_METADATA.study_type}</p>
                    <p><strong>Estimated LOI:</strong> {project.survey_json.STUDY_METADATA.estimated_loi_minutes} minutes</p>
                    <p className="text-gray-700">{project.survey_json.STUDY_METADATA.description}</p>
                  </div>
                </div>
              )}

              {/* Sample Requirements */}
              {project.survey_json.SAMPLE_REQUIREMENTS && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Sample Design</h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>Total Sample:</strong> n={project.survey_json.SAMPLE_REQUIREMENTS.total_sample}</p>
                    <p><strong>Target Audience:</strong> {project.survey_json.SAMPLE_REQUIREMENTS.target_audience_summary}</p>
                    
                    {project.survey_json.SAMPLE_REQUIREMENTS.qualification_criteria && (
                      <div className="mt-3">
                        <p className="font-medium mb-1">Qualification Criteria:</p>
                        <ul className="ml-4 space-y-1 text-gray-700">
                          {project.survey_json.SAMPLE_REQUIREMENTS.qualification_criteria.map((c: string, i: number) => (
                            <li key={i}>• {c}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {(project.survey_json.SAMPLE_REQUIREMENTS.hard_quotas || project.survey_json.SAMPLE_REQUIREMENTS.soft_quotas) && (
                      <div className="mt-3">
                        <p className="font-medium mb-1">Quotas:</p>
                        
                        {project.survey_json.SAMPLE_REQUIREMENTS.hard_quotas && Object.entries(project.survey_json.SAMPLE_REQUIREMENTS.hard_quotas).map(([key, value]: [string, any]) => (
                          <div key={`hard-${key}`} className="ml-4 text-gray-700">
                            <p className="font-medium text-xs uppercase text-gray-500">{key} (Hard Quota):</p>
                            <ul className="ml-4 space-y-1">
                              {typeof value === 'object' && Object.entries(value).map(([k, v]: [string, any]) => (
                                <li key={k} className="text-sm">• {k}: {v === null || v === undefined ? 'Proportional' : `n=${v}`}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                        
                        {project.survey_json.SAMPLE_REQUIREMENTS.soft_quotas && Object.entries(project.survey_json.SAMPLE_REQUIREMENTS.soft_quotas).map(([key, value]: [string, any]) => (
                          <div key={`soft-${key}`} className="ml-4 text-gray-700">
                            <p className="font-medium text-xs uppercase text-gray-500">{key} (Soft Quota):</p>
                            <ul className="ml-4 space-y-1">
                              {typeof value === 'object' && Object.entries(value).map(([k, v]: [string, any]) => (
                                <li key={k} className="text-sm">• {k}: {v === null || v === undefined ? 'Natural fall' : `n=${v}`}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Screener Questions */}
              {project.survey_json.SCREENER && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="mb-4 border-l-4 border-blue-500 pl-4">
                    <EditableHeader
                      title={`${project.survey_json.SCREENER.section_title || 'Screener'} (${project.survey_json.SCREENER.questions?.length || 0} questions)`}
                      onSave={(newTitle) => handleEditSection('SCREENER', null, newTitle.split(' (')[0])}
                      className="text-xl font-semibold text-gray-800"
                    />
                  </div>
                  <div className="space-y-4">
                    {project.survey_json.SCREENER.questions?.map((q: any, idx: number) => (
                      <QuestionCard
                        key={idx}
                        question={q}
                        sectionColor="blue"
                        onPin={handlePinQuestion}
                        onExclude={handleExcludeQuestion}
                        onResetOverride={handleResetQuestionOverride}
                        onEdit={handleEditQuestion}
                        onDelete={handleDeleteQuestion}
                        onReorder={handleReorderQuestion}
                        isFirst={idx === 0}
                        isLast={idx === (project.survey_json.SCREENER.questions?.length || 0) - 1}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Main Survey */}
              {project.survey_json.MAIN_SECTION && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4 border-l-4 border-green-500 pl-4">
                    Main Survey
                  </h3>
                  {project.survey_json.MAIN_SECTION.sub_sections?.map((subsection: any, subIdx: number) => (
                    <div key={subIdx} className="mb-6">
                      <div className="mb-3 border-l-4 border-green-300 pl-3">
                        <EditableHeader
                          title={`${subsection.subsection_id}: ${subsection.subsection_title}`}
                          onSave={(newTitle) => {
                            const titleWithoutId = newTitle.includes(':') ? newTitle.split(': ').slice(1).join(': ') : newTitle;
                            handleEditSection('MAIN_SECTION', subsection.subsection_id, titleWithoutId);
                          }}
                          className="text-lg font-semibold text-gray-700"
                        />
                      </div>
                      {subsection.purpose && (
                        <p className="text-sm text-gray-600 mb-4 italic ml-3">
                          {subsection.purpose}
                        </p>
                      )}
                      <div className="space-y-4">
                        {subsection.questions?.map((q: any, idx: number) => (
                          <div key={idx} className="ml-3">
                            <QuestionCard
                              question={q}
                              sectionColor="green"
                              onPin={handlePinQuestion}
                              onExclude={handleExcludeQuestion}
                              onResetOverride={handleResetQuestionOverride}
                              onEdit={handleEditQuestion}
                              onDelete={handleDeleteQuestion}
                              onReorder={handleReorderQuestion}
                              isFirst={idx === 0}
                              isLast={idx === (subsection.questions?.length || 0) - 1}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Demographics */}
              {project.survey_json.DEMOGRAPHICS && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="mb-4 border-l-4 border-purple-500 pl-4">
                    <EditableHeader
                      title={`${project.survey_json.DEMOGRAPHICS.section_title || 'Demographics'} (${project.survey_json.DEMOGRAPHICS.questions?.length || 0} questions)`}
                      onSave={(newTitle) => handleEditSection('DEMOGRAPHICS', null, newTitle.split(' (')[0])}
                      className="text-xl font-semibold text-gray-800"
                    />
                  </div>
                  <div className="space-y-4">
                    {project.survey_json.DEMOGRAPHICS.questions?.map((q: any, idx: number) => (
                      <QuestionCard
                        key={idx}
                        question={q}
                        sectionColor="purple"
                        onPin={handlePinQuestion}
                        onExclude={handleExcludeQuestion}
                        onResetOverride={handleResetQuestionOverride}
                        onEdit={handleEditQuestion}
                        onDelete={handleDeleteQuestion}
                        onReorder={handleReorderQuestion}
                        isFirst={idx === 0}
                        isLast={idx === (project.survey_json.DEMOGRAPHICS.questions?.length || 0) - 1}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Next Steps
                </h3>
                <div className="flex space-x-4">
                  <button
                    onClick={() => navigate(`/project/${projectId}/preview`)}
                    className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
                  >
                    👁️ Preview as Respondent
                  </button>
                  <button
                    disabled
                    className="bg-gray-300 text-gray-600 px-6 py-3 rounded-lg cursor-not-allowed"
                    title="Reporting coming in Phase 5"
                  >
                    Generate Report (Coming Soon)
                  </button>
                </div>
              </div>
              </div>
            </>
          ) : (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded m-6">
              No survey generated yet. Go to the Overview tab to generate your survey.
            </div>
          )}
        </div>
      )}

      {/* Validation Tab */}
      {selectedTab === 'validation' && (
        <div className="space-y-6">
          {project.validation_log ? (
            <>
              {/* Summary */}
              <div className={`rounded-lg p-4 ${
                project.validation_log.is_valid
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}>
                <h3 className={`font-semibold mb-2 ${
                  project.validation_log.is_valid ? 'text-green-900' : 'text-red-900'
                }`}>
                  {project.validation_log.is_valid ? '✓ Validation Passed' : '⚠ Validation Issues Found'}
                </h3>
                <p className={project.validation_log.is_valid ? 'text-green-800' : 'text-red-800'}>
                  {project.validation_log.error_count} errors, {project.validation_log.warning_count} warnings
                </p>
              </div>

              {/* Validation Entries */}
              {project.validation_log.entries && project.validation_log.entries.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    Validation Report
                  </h3>
                  <div className="space-y-3">
                    {project.validation_log.entries.map((entry: ValidationLogEntry, idx: number) => (
                      <div
                        key={idx}
                        className={`border rounded-lg p-4 ${getSeverityColor(entry.severity)}`}
                      >
                        <div className="flex items-start justify-between mb-1">
                          <span className="font-mono text-xs font-semibold">
                            {entry.rule_id}
                          </span>
                          <span className="text-xs uppercase font-semibold">
                            {entry.severity}
                          </span>
                        </div>
                        <p className="text-sm">{entry.message}</p>
                        {entry.location && (
                          <p className="text-xs mt-2 opacity-75">
                            Location: {entry.location}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded">
              No validation log available. Generate a survey first.
            </div>
          )}
        </div>
      )}
    </div>
    </>
  );
}
