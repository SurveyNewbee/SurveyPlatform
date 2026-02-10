import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { extractBrief, extractBriefStream, getSkills, createProject } from '../api/client';
import type { ExtractedBrief, Skill } from '../types';
import StreamingModal from '../components/StreamingModal';

export default function SetupPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<'brief' | 'review' | 'skills'>('brief');
  
  // Step 1: Brief input
  const [briefText, setBriefText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState('');
  const [showStreamingModal, setShowStreamingModal] = useState(false);
  
  // Step 2: Extracted brief data
  const [extractedBrief, setExtractedBrief] = useState<ExtractedBrief | null>(null);
  
  // Step 3: Skills
  const [allSkills, setAllSkills] = useState<Skill[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [loadingSkills, setLoadingSkills] = useState(false);
  
  // Project creation
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadSkills();
  }, []);

  async function loadSkills() {
    setLoadingSkills(true);
    const response = await getSkills();
    if (response.success && response.data) {
      setAllSkills(response.data);
    }
    setLoadingSkills(false);
  }

  async function handleExtractBrief() {
    if (!briefText.trim()) {
      setExtractError('Please enter your research brief');
      return;
    }

    setExtracting(true);
    setExtractError(null);
    setStreamingContent('');
    setShowStreamingModal(true);

    try {
      let finalResult = null;
      
      // Stream the response for visual feedback and capture final result
      for await (const message of extractBriefStream(briefText)) {
        if (message.type === 'chunk') {
          setStreamingContent(prev => prev + message.data + '\n');
        } else if (message.type === 'final') {
          finalResult = message.data;
        }
      }

      // Use the final result from streaming (no second API call needed)
      if (finalResult) {
        setExtractedBrief(finalResult);
        // Pre-select identified skills if present
        if (finalResult.identified_skills) {
          setSelectedSkills(finalResult.identified_skills);
        }
        setShowStreamingModal(false);
        setStep('review');
      } else {
        setExtractError('No final result received from stream');
        setShowStreamingModal(false);
      }
    } catch (error) {
      setExtractError(error instanceof Error ? error.message : 'Streaming failed');
      setShowStreamingModal(false);
    }
    
    setExtracting(false);
  }

  function handleSkillToggle(skillId: string) {
    setSelectedSkills(prev =>
      prev.includes(skillId)
        ? prev.filter(id => id !== skillId)
        : [...prev, skillId]
    );
  }

  async function handleCreateProject() {
    if (!projectName.trim()) {
      alert('Please enter a project name');
      return;
    }

    setCreating(true);

    const response = await createProject({
      name: projectName,
      description: projectDescription,
      brief_text: briefText,
      brief_data: extractedBrief,
    });

    if (response.success && response.data) {
      // Navigate to project page to continue with survey generation
      navigate(`/project/${response.data.id}`);
    } else {
      alert(response.error || 'Failed to create project');
      setCreating(false);
    }
  }

  if (step === 'brief') {
    return (
      <>
        <StreamingModal
          isOpen={showStreamingModal}
          title="Extracting Brief & Generating Blueprint"
          content={streamingContent}
        />
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">New Project Setup</h2>
          <p className="text-gray-600 mb-8">
            Enter your research brief and we'll help you design the perfect survey
          </p>

        <div className="bg-white rounded-lg shadow-md p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Research Brief
          </label>
          <textarea
            value={briefText}
            onChange={(e) => setBriefText(e.target.value)}
            placeholder="Describe your research objectives, target audience, key topics to explore, timeline, and any specific requirements..."
            className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={extracting}
          />
          
          {extractError && (
            <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {extractError}
            </div>
          )}

          <div className="mt-6 flex space-x-4">
            <button
              onClick={handleExtractBrief}
              disabled={extracting || !briefText.trim()}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {extracting ? 'Analyzing...' : 'Analyze Brief'}
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">💡 Tips for a great brief:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Clearly state your research objectives</li>
            <li>• Describe your target audience demographics</li>
            <li>• List key topics or questions to explore</li>
            <li>• Mention timeline and budget if applicable</li>
            <li>• Include any specific methodologies you're considering</li>
          </ul>
        </div>
      </div>
      </>
    );
  }

  if (step === 'review') {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Review Extracted Information</h2>
        <p className="text-gray-600 mb-8">
          We've analyzed your brief. Review and proceed to select methodologies.
        </p>

        <div className="space-y-6">
          {/* Objectives */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Research Objectives</h3>
            {extractedBrief?.objectives && extractedBrief.objectives.length > 0 ? (
              <ul className="space-y-2">
                {extractedBrief.objectives.map((obj, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span className="text-gray-700">{obj}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 italic">No objectives identified</p>
            )}
          </div>

          {/* Target Audience */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Target Audience</h3>
            <p className="text-gray-700">
              {extractedBrief?.target_audience || 'Not specified'}
            </p>
          </div>

          {/* Topics */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Key Topics</h3>
            {extractedBrief?.topics && extractedBrief.topics.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {extractedBrief.topics.map((topic, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No topics identified</p>
            )}
          </div>

          {/* Sample Design */}
          {(extractedBrief?.total_sample_size || extractedBrief?.quotas) && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Sample Design</h3>
              
              {extractedBrief.total_sample_size && (
                <div className="mb-4">
                  <span className="text-sm text-gray-600">Total Sample:</span>
                  <p className="text-gray-800 font-semibold text-lg">n={extractedBrief.total_sample_size}</p>
                </div>
              )}
              
              {extractedBrief.quotas && extractedBrief.quotas.length > 0 && (
                <div>
                  <span className="text-sm text-gray-600 mb-2 block">Quotas:</span>
                  <div className="space-y-3">
                    {extractedBrief.quotas.map((quota, idx) => (
                      <div key={idx} className="border-l-4 border-blue-400 pl-3">
                        <p className="font-medium text-gray-800 capitalize">
                          {quota.attribute} ({quota.type} quota)
                        </p>
                        <div className="mt-1 space-y-1">
                          {quota.groups.map((group, gIdx) => (
                            <div key={gIdx} className="text-sm text-gray-600 flex justify-between">
                              <span>{group.label}:</span>
                              <span className="font-medium">
                                {group.min && group.max && group.min === group.max 
                                  ? `n=${group.min}` 
                                  : group.min 
                                    ? `min ${group.min}${group.max ? `, max ${group.max}` : ''}`
                                    : group.proportion 
                                      ? `${(group.proportion * 100).toFixed(0)}%`
                                      : 'Not specified'}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Market Context */}
          {extractedBrief?.market_context && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Market Context</h3>
              <div className="space-y-2 text-sm">
                {extractedBrief.market_context.client_brand && (
                  <div>
                    <span className="text-gray-600">Client Brand:</span>{' '}
                    <span className="text-gray-800 font-medium">{extractedBrief.market_context.client_brand}</span>
                  </div>
                )}
                {extractedBrief.market_context.category && (
                  <div>
                    <span className="text-gray-600">Category:</span>{' '}
                    <span className="text-gray-800 font-medium">{extractedBrief.market_context.category}</span>
                  </div>
                )}
                {extractedBrief.market_context.market && (
                  <div>
                    <span className="text-gray-600">Market:</span>{' '}
                    <span className="text-gray-800 font-medium">{extractedBrief.market_context.market}</span>
                  </div>
                )}
                {extractedBrief.market_context.competitor_brands && extractedBrief.market_context.competitor_brands.length > 0 && (
                  <div>
                    <span className="text-gray-600">Competitors:</span>{' '}
                    <span className="text-gray-800">{extractedBrief.market_context.competitor_brands.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Study Classification */}
          {(extractedBrief?.study_type || extractedBrief?.primary_methodology) && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Study Classification</h3>
              <div className="space-y-2 text-sm">
                {extractedBrief.study_type && (
                  <div>
                    <span className="text-gray-600">Study Type:</span>{' '}
                    <span className="text-gray-800 font-medium capitalize">{extractedBrief.study_type.replace(/_/g, ' ')}</span>
                  </div>
                )}
                {extractedBrief.primary_methodology && (
                  <div>
                    <span className="text-gray-600">Primary Methodology:</span>{' '}
                    <span className="text-gray-800 font-medium capitalize">{extractedBrief.primary_methodology.replace(/_/g, ' ')}</span>
                  </div>
                )}
                {extractedBrief.secondary_objectives && extractedBrief.secondary_objectives.length > 0 && (
                  <div>
                    <span className="text-gray-600">Secondary Objectives:</span>{' '}
                    <span className="text-gray-800">{extractedBrief.secondary_objectives.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Operational Details */}
          {extractedBrief?.operational && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Operational Details</h3>
              <div className="space-y-2 text-sm">
                {extractedBrief.operational.target_loi_minutes && (
                  <div>
                    <span className="text-gray-600">Target LOI:</span>{' '}
                    <span className="text-gray-800 font-medium">{extractedBrief.operational.target_loi_minutes} minutes</span>
                  </div>
                )}
                {extractedBrief.operational.fieldwork_mode && (
                  <div>
                    <span className="text-gray-600">Fieldwork Mode:</span>{' '}
                    <span className="text-gray-800 font-medium">{extractedBrief.operational.fieldwork_mode}</span>
                  </div>
                )}
                {extractedBrief.operational.market_specifics && (
                  <div>
                    <span className="text-gray-600">Market Specifics:</span>{' '}
                    <span className="text-gray-800">{extractedBrief.operational.market_specifics}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Timeline & Budget */}
          {(extractedBrief?.timeline || extractedBrief?.budget) && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Project Details</h3>
              <div className="grid grid-cols-2 gap-4">
                {extractedBrief?.timeline && (
                  <div>
                    <span className="text-sm text-gray-600">Timeline:</span>
                    <p className="text-gray-800 font-medium">{extractedBrief.timeline}</p>
                  </div>
                )}
                {extractedBrief?.budget && (
                  <div>
                    <span className="text-sm text-gray-600">Budget:</span>
                    <p className="text-gray-800 font-medium">{extractedBrief.budget}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Recommended Skills */}
          {extractedBrief?.identified_skills && extractedBrief.identified_skills.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-3">
                🎯 Recommended Methodologies
              </h3>
              <div className="flex flex-wrap gap-2">
                {extractedBrief.identified_skills.map((skillId) => {
                  const skill = allSkills.find(s => s.id === skillId);
                  return (
                    <span
                      key={skillId}
                      className="px-3 py-1 bg-green-200 text-green-900 rounded-full text-sm font-medium"
                    >
                      {skill?.name || skillId}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-4">
            <button
              onClick={() => setStep('skills')}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Continue to Methodology Selection
            </button>
            <button
              onClick={() => setStep('brief')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Edit Brief
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'skills') {
    const recommendedSkills = allSkills.filter(s => 
      extractedBrief?.identified_skills?.includes(s.id)
    );
    const otherSkills = allSkills.filter(s => 
      !extractedBrief?.identified_skills?.includes(s.id)
    );

    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Select Methodologies</h2>
        <p className="text-gray-600 mb-8">
          Choose the research methodologies for your survey. Recommended skills are pre-selected.
        </p>

        {/* Info banner about blueprint-based generation */}
        {allSkills.length === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm text-blue-900 font-medium mb-1">New Blueprint-Based Generation</p>
                <p className="text-sm text-blue-800">
                  This platform now uses an intelligent two-agent workflow. The AI will automatically design 
                  a custom survey blueprint based on your brief during the generation process. Manual methodology 
                  selection is no longer required.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Project Name & Description */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Project Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., Q1 2026 Brand Tracking Study"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (optional)
              </label>
              <input
                type="text"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="Brief description of this project"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Recommended Skills */}
        {recommendedSkills.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              🎯 Recommended for Your Project
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendedSkills.map((skill) => (
                <button
                  key={skill.id}
                  onClick={() => handleSkillToggle(skill.id)}
                  className={`text-left p-4 rounded-lg border-2 transition-all ${
                    selectedSkills.includes(skill.id)
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800">{skill.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">{skill.description}</p>
                    </div>
                    <div className={`ml-4 w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                      selectedSkills.includes(skill.id)
                        ? 'bg-green-500 border-green-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedSkills.includes(skill.id) && (
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* All Skills */}
        {otherSkills.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              All Available Methodologies
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {otherSkills.map((skill) => (
                <button
                  key={skill.id}
                  onClick={() => handleSkillToggle(skill.id)}
                  className={`text-left p-4 rounded-lg border-2 transition-all ${
                    selectedSkills.includes(skill.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800">{skill.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">{skill.description}</p>
                    </div>
                    <div className={`ml-4 w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                      selectedSkills.includes(skill.id)
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-gray-300'
                    }`}>
                      {selectedSkills.includes(skill.id) && (
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Selection Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-900">
            {allSkills.length === 0 ? (
              <>Ready to proceed with blueprint-based generation</>
            ) : (
              <>
                <strong>{selectedSkills.length}</strong> methodolog{selectedSkills.length === 1 ? 'y' : 'ies'} selected
              </>
            )}
          </p>
        </div>

        {/* Actions */}
        <div className="flex space-x-4">
          <button
            onClick={handleCreateProject}
            disabled={creating || !projectName.trim()}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {creating ? 'Creating Project...' : 'Create Project & Continue'}
          </button>
          <button
            onClick={() => setStep('review')}
            disabled={creating}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  return null;
}
