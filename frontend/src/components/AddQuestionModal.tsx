import { useState } from 'react';

interface AddQuestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (sectionId: string, subsectionId: string | null, question: any, position?: number) => void;
  sections: {
    screener?: boolean;
    mainSections?: Array<{ id: string; title: string }>;
    demographics?: boolean;
  };
}

const QUESTION_TYPES = [
  { value: 'single_choice', label: 'Single Select', needsOptions: true },
  { value: 'multiple_choice', label: 'Multi Select', needsOptions: true },
  { value: 'open_ended', label: 'Open End (Text)', needsOptions: false },
  { value: 'numeric_input', label: 'Numeric Entry', needsOptions: false },
  { value: 'scale', label: 'Rating Scale', needsOptions: true },
  { value: 'matrix', label: 'Matrix Grid', needsOptions: false },
  { value: 'ranking', label: 'Ranking', needsOptions: true },
];

export default function AddQuestionModal({ isOpen, onClose, onAdd, sections }: AddQuestionModalProps) {
  const [questionType, setQuestionType] = useState('single_choice');
  const [questionText, setQuestionText] = useState('');
  const [options, setOptions] = useState<string[]>(['Option 1', 'Option 2']);
  const [targetSection, setTargetSection] = useState('SCREENER');
  const [targetSubsection, setTargetSubsection] = useState<string | null>(null);
  const [priority, setPriority] = useState<'required' | 'recommended' | 'optional'>('recommended');

  const selectedType = QUESTION_TYPES.find(t => t.value === questionType);

  const handleAddOption = () => {
    setOptions([...options, `Option ${options.length + 1}`]);
  };

  const handleRemoveOption = (index: number) => {
    if (options.length > 1) {
      setOptions(options.filter((_, i) => i !== index));
    }
  };

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const handleSubmit = () => {
    if (!questionText.trim()) {
      alert('Please enter question text');
      return;
    }

    // Generate question ID
    const sectionPrefix = targetSection === 'SCREENER' ? 'SCR' : 
                         targetSection === 'DEMOGRAPHICS' ? 'DEM' : 
                         targetSubsection || 'MS';
    const timestamp = Date.now().toString().slice(-6);
    const questionId = `${sectionPrefix}_Q${timestamp}`;

    // Build question object
    const question: any = {
      question_id: questionId,
      question_text: questionText.trim(),
      question_type: questionType,
      priority: priority,
      loi_visibility: 'visible',
      user_override: 'none',
      estimated_seconds: 10,
    };

    // Add options if applicable
    if (selectedType?.needsOptions) {
      question.options = options.filter(o => o.trim());
    }

    // Add metadata based on type
    if (questionType === 'numeric_input') {
      question.validation = { type: 'numeric' };
    } else if (questionType === 'scale') {
      question.scale_points = options.length;
    }

    onAdd(targetSection, targetSubsection, question);
    handleReset();
    onClose();
  };

  const handleReset = () => {
    setQuestionType('single_choice');
    setQuestionText('');
    setOptions(['Option 1', 'Option 2']);
    setTargetSection('SCREENER');
    setTargetSubsection(null);
    setPriority('recommended');
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">Add New Question</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Target Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add to Section
            </label>
            <select
              value={targetSubsection || targetSection}
              onChange={(e) => {
                const value = e.target.value;
                if (value === 'SCREENER' || value === 'DEMOGRAPHICS') {
                  setTargetSection(value);
                  setTargetSubsection(null);
                } else {
                  setTargetSection('MAIN_SECTION');
                  setTargetSubsection(value);
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {sections.screener && <option value="SCREENER">Screener</option>}
              {sections.mainSections?.map(ms => (
                <option key={ms.id} value={ms.id}>Main Survey: {ms.title}</option>
              ))}
              {sections.demographics && <option value="DEMOGRAPHICS">Demographics</option>}
            </select>
          </div>

          {/* Question Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Type
            </label>
            <select
              value={questionType}
              onChange={(e) => setQuestionType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {QUESTION_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          {/* Question Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question Text *
            </label>
            <textarea
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              placeholder="Enter your question here..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Response Options (if applicable) */}
          {selectedType?.needsOptions && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Response Options
              </label>
              <div className="space-y-2">
                {options.map((opt, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 w-6">{idx + 1}.</span>
                    <input
                      type="text"
                      value={opt}
                      onChange={(e) => handleOptionChange(idx, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    {options.length > 1 && (
                      <button
                        onClick={() => handleRemoveOption(idx)}
                        className="px-2 py-1 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button
                onClick={handleAddOption}
                className="mt-3 text-sm px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded transition-colors"
              >
                + Add Option
              </button>
            </div>
          )}

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority (for LOI calculation)
            </label>
            <div className="flex gap-4">
              {(['required', 'recommended', 'optional'] as const).map(p => (
                <label key={p} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value={p}
                    checked={priority === p}
                    onChange={(e) => setPriority(e.target.value as any)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">{p}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Preview</h3>
            <div className="bg-white p-3 rounded border border-gray-200">
              <p className="text-sm font-medium text-gray-800 mb-2">
                {questionText || 'Your question will appear here...'}
              </p>
              {selectedType?.needsOptions && options.length > 0 && (
                <ul className="space-y-1 text-sm text-gray-600">
                  {options.filter(o => o.trim()).map((opt, idx) => (
                    <li key={idx} className="ml-4">
                      {questionType === 'multiple_choice' ? '☐' : '○'} {opt}
                    </li>
                  ))}
                </ul>
              )}
              {questionType === 'open_ended' && (
                <div className="border border-gray-300 rounded p-2 text-xs text-gray-400">
                  [Text input field]
                </div>
              )}
              {questionType === 'numeric_input' && (
                <div className="border border-gray-300 rounded p-2 text-xs text-gray-400 w-32">
                  [Number input]
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={handleClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!questionText.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Add Question
          </button>
        </div>
      </div>
    </div>
  );
}
