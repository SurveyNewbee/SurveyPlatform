import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, generateSurvey, updateProject } from '../api/client';
import type { Project, ValidationLogEntry } from '../types';

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  
  const [selectedTab, setSelectedTab] = useState<'overview' | 'survey' | 'validation'>('overview');

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

    const response = await generateSurvey(
      project.brief_data,
      project.brief_data.identified_skills || []
    );

    if (response.success && response.data) {
      // Update project with survey and validation log
      const updateResponse = await updateProject(projectId, {
        survey_json: response.data.survey,
        validation_log: response.data.validation_log,
      });

      if (updateResponse.success) {
        await loadProject();
        setSelectedTab('survey');
      } else {
        setGenerateError('Survey generated but failed to save');
      }
    } else {
      setGenerateError(response.error || 'Failed to generate survey');
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

  return (
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
        <div className="space-y-6">
          {project.survey_json ? (
            <>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-900">
                  ✓ Survey generated successfully with{' '}
                  <strong>{project.survey_json.sections?.length || 0}</strong> sections
                </p>
              </div>

              {/* Survey Structure */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Survey Structure
                </h3>
                
                {project.survey_json.sections?.map((section: any, idx: number) => (
                  <div key={idx} className="mb-6 last:mb-0 border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      Section {idx + 1}: {section.title}
                    </h4>
                    {section.description && (
                      <p className="text-sm text-gray-600 mb-3">{section.description}</p>
                    )}
                    <div className="space-y-2">
                      {section.questions?.map((question: any, qIdx: number) => (
                        <div key={qIdx} className="bg-gray-50 rounded p-3">
                          <p className="text-sm font-medium text-gray-700 mb-1">
                            Q{qIdx + 1}. {question.text}
                          </p>
                          <p className="text-xs text-gray-500">
                            Type: {question.type} | ID: {question.id}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Next Steps
                </h3>
                <div className="flex space-x-4">
                  <button
                    disabled
                    className="bg-gray-300 text-gray-600 px-6 py-3 rounded-lg cursor-not-allowed"
                    title="Editor coming in Phase 2"
                  >
                    Edit Survey (Coming Soon)
                  </button>
                  <button
                    disabled
                    className="bg-gray-300 text-gray-600 px-6 py-3 rounded-lg cursor-not-allowed"
                    title="Preview coming in Phase 3"
                  >
                    Preview (Coming Soon)
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded">
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
  );
}
