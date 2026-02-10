import React, { useState } from 'react';

interface QuestionCardProps {
  question: any;
  sectionColor: 'blue' | 'green' | 'purple';
  onPin?: (questionId: string) => void;
  onExclude?: (questionId: string) => void;
  onResetOverride?: (questionId: string) => void;
  onEdit?: (questionId: string, updates: any) => void;
  onDelete?: (questionId: string) => void;
  onReorder?: (questionId: string, direction: 'up' | 'down') => void;
  isFirst?: boolean;
  isLast?: boolean;
  readOnly?: boolean;
}

const COLOR_CLASSES = {
  blue: {
    badge: 'bg-blue-100 text-blue-700',
    border: 'border-blue-200',
    matrixHeader: 'bg-blue-50',
    pinBadge: 'bg-blue-600 text-white',
  },
  green: {
    badge: 'bg-green-100 text-green-700',
    border: 'border-green-200',
    matrixHeader: 'bg-green-50',
    pinBadge: 'bg-green-600 text-white',
  },
  purple: {
    badge: 'bg-purple-100 text-purple-700',
    border: 'border-purple-200',
    matrixHeader: 'bg-purple-50',
    pinBadge: 'bg-purple-600 text-white',
  },
};

export default function QuestionCard({
  question: q,
  sectionColor,
  onPin,
  onExclude,
  onResetOverride,
  onEdit,
  onDelete,
  onReorder,
  isFirst = false,
  isLast = false,
  readOnly = false,
}: QuestionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditingText, setIsEditingText] = useState(false);
  const [editedText, setEditedText] = useState(q.question_text);
  const [editingOptions, setEditingOptions] = useState(false);
  const [editedOptions, setEditedOptions] = useState(q.options || []);
  
  const isHidden = q.loi_visibility === 'hidden';
  const isPinned = q.user_override === 'pinned';
  const isExcluded = q.user_override === 'excluded';
  
  const colors = COLOR_CLASSES[sectionColor];
  
  const handleSaveText = () => {
    if (editedText !== q.question_text && onEdit) {
      onEdit(q.question_id, { question_text: editedText });
    }
    setIsEditingText(false);
  };
  
  const handleSaveOptions = () => {
    if (JSON.stringify(editedOptions) !== JSON.stringify(q.options) && onEdit) {
      onEdit(q.question_id, { options: editedOptions });
    }
    setEditingOptions(false);
  };
  
  const handleAddOption = () => {
    setEditedOptions([...editedOptions, 'New option']);
  };
  
  const handleRemoveOption = (index: number) => {
    setEditedOptions(editedOptions.filter((_: any, i: number) => i !== index));
  };
  
  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...editedOptions];
    newOptions[index] = value;
    setEditedOptions(newOptions);
  };
  
  const handleDelete = () => {
    if (confirm(`Delete question ${q.question_id}?`)) {
      onDelete?.(q.question_id);
    }
  };

  // Hidden/excluded collapsed view
  if ((isHidden && !isPinned) || isExcluded) {
    return (
      <div className={`bg-gray-50 border border-dashed ${isExcluded ? 'border-red-300' : 'border-gray-300'} rounded-lg p-3`}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {isExcluded ? (
                <span className="text-red-500" title="Excluded by you">🚫</span>
              ) : (
                <span className="text-gray-400" title="Hidden at current LOI">○</span>
              )}
              <span className={`text-sm font-medium ${isExcluded ? 'line-through text-gray-500' : 'text-gray-600'}`}>
                {q.question_id}
              </span>
              {q.priority && (
                <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 rounded">
                  {q.priority}
                </span>
              )}
            </div>
            <p className={`text-sm mt-1 ${isExcluded ? 'line-through text-gray-400' : 'text-gray-500'}`}>
              {q.question_text}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {isExcluded ? 'Excluded by you' : 'Hidden at current LOI'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {isExcluded ? (
              <button
                onClick={() => onResetOverride?.(q.question_id)}
                className="text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
              >
                Un-exclude
              </button>
            ) : (
              <>
                <button
                  onClick={() => onPin?.(q.question_id)}
                  className="text-xs px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
                >
                  📌 Pin to include
                </button>
                {!isExpanded && (
                  <button
                    onClick={() => setIsExpanded(true)}
                    className="text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
                  >
                    ▼ Expand
                  </button>
                )}
              </>
            )}
          </div>
        </div>
        
        {/* Expanded preview (read-only) */}
        {isExpanded && !isExcluded && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="opacity-60 pointer-events-none">
              {renderQuestionContent(q, colors)}
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="mt-3 text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
            >
              ▲ Collapse
            </button>
          </div>
        )}
      </div>
    );
  }

  // Visible question (normal or pinned)
  return (
    <div className={`bg-white rounded-lg p-4 border ${isPinned ? `border-l-4 border-l-blue-500 ${colors.border}` : 'border-gray-200'} shadow-sm`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 flex-1">
          {isPinned && (
            <span className={`text-sm px-2 py-0.5 ${colors.pinBadge} rounded`} title="Pinned by you">
              📌
            </span>
          )}
          <p className="font-semibold text-gray-800">
            {q.question_id}
          </p>
          {q.priority && (
            <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 rounded">
              {q.priority}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs ${colors.badge} px-2 py-1 rounded font-medium`}>
            {q.question_type}
          </span>
          {!readOnly && (
            <>
              {/* Reorder buttons */}
              {onReorder && (
                <div className="flex gap-1">
                  <button
                    onClick={() => onReorder(q.question_id, 'up')}
                    disabled={isFirst}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    title="Move up"
                  >
                    ↑
                  </button>
                  <button
                    onClick={() => onReorder(q.question_id, 'down')}
                    disabled={isLast}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    title="Move down"
                  >
                    ↓
                  </button>
                </div>
              )}
              {/* Pin/Exclude buttons */}
              {isPinned ? (
                <button
                  onClick={() => onResetOverride?.(q.question_id)}
                  className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
                  title="Unpin (return to LOI-based visibility)"
                >
                  Unpin
                </button>
              ) : (
                <>
                  <button
                    onClick={() => onPin?.(q.question_id)}
                    className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition-colors"
                    title="Pin to always show"
                  >
                    📌
                  </button>
                  <button
                    onClick={() => onExclude?.(q.question_id)}
                    className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                    title="Exclude to always hide"
                  >
                    🚫
                  </button>
                </>
              )}
              {/* Delete button */}
              {onDelete && (
                <button
                  onClick={handleDelete}
                  className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                  title="Delete question"
                >
                  🗑️
                </button>
              )}
            </>
          )}
        </div>
      </div>
      
      {/* Question Text - Editable */}
      {!readOnly && isEditingText ? (
        <div className="mb-3">
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            className="w-full p-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            autoFocus
            onBlur={handleSaveText}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                handleSaveText();
              }
              if (e.key === 'Escape') {
                setEditedText(q.question_text);
                setIsEditingText(false);
              }
            }}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleSaveText}
              className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              Save
            </button>
            <button
              onClick={() => {
                setEditedText(q.question_text);
                setIsEditingText(false);
              }}
              className="text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div
          className={`text-gray-700 mb-3 ${!readOnly && onEdit ? 'cursor-pointer hover:bg-gray-50 rounded p-2 -ml-2' : ''}`}
          onClick={() => !readOnly && onEdit && setIsEditingText(true)}
          title={!readOnly && onEdit ? 'Click to edit' : ''}
        >
          {q.question_text}
        </div>
      )}
      
      {/* Question Content */}
      {readOnly || !editingOptions ? (
        <div onClick={() => !readOnly && onEdit && q.options && setEditingOptions(true)}>
          {renderQuestionContent(q, colors, !readOnly && onEdit !== undefined)}
        </div>
      ) : (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500 mb-2">Edit Options:</p>
          <div className="space-y-2">
            {editedOptions.map((opt: string, i: number) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-sm text-gray-600">{i + 1}.</span>
                <input
                  type="text"
                  value={opt}
                  onChange={(e) => handleOptionChange(i, e.target.value)}
                  className="flex-1 p-1 px-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  onClick={() => handleRemoveOption(i)}
                  className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleAddOption}
              className="text-xs px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded transition-colors"
            >
              + Add Option
            </button>
            <button
              onClick={handleSaveOptions}
              className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              Save
            </button>
            <button
              onClick={() => {
                setEditedOptions(q.options || []);
                setEditingOptions(false);
              }}
              className="text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      {q.notes && (
        <div className="mt-3 text-xs text-gray-500 italic border-t border-gray-200 pt-2">
          Note: {q.notes}
        </div>
      )}
      
      {q.quota_attribute && (
        <div className="mt-2 text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded inline-block">
          Quota: {q.quota_attribute} ({q.quota_type})
        </div>
      )}
    </div>
  );
}

function renderQuestionContent(q: any, colors: typeof COLOR_CLASSES.blue, editable: boolean = false) {
  // Matrix questions
  if (Array.isArray(q.rows) && Array.isArray(q.columns)) {
    return (
      <div className="mt-4 overflow-x-auto">
        <div className="inline-block min-w-full">
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr>
                <th className="border border-gray-300 bg-gray-100 px-3 py-2 text-left text-xs font-medium text-gray-600 w-1/3">
                  
                </th>
                {q.columns.map((col: string, colIdx: number) => (
                  <th key={colIdx} className={`border border-gray-300 ${colors.matrixHeader} px-2 py-2 text-center text-xs font-medium text-gray-700`}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {q.rows.map((row: string, rowIdx: number) => (
                <tr key={rowIdx} className="hover:bg-gray-50">
                  <td className="border border-gray-300 bg-gray-50 px-3 py-2 text-xs text-gray-700 font-medium">
                    {row}
                  </td>
                  {q.columns.map((_: string, colIdx: number) => (
                    <td key={colIdx} className="border border-gray-300 px-2 py-2 text-center">
                      <div className="w-4 h-4 mx-auto rounded-full border-2 border-gray-400"></div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
  
  // Questions with options
  if (Array.isArray(q.options) && q.options.length > 0) {
    return (
      <div className={`mt-2 ${editable ? 'cursor-pointer hover:bg-gray-50 rounded p-2 -ml-2' : ''}`}>
        <p className="text-xs font-medium text-gray-500 mb-1">
          Options: {editable && <span className="text-blue-500">(click to edit)</span>}
        </p>
        <ul className="space-y-1">
          {q.options.map((opt: string, i: number) => (
            <li key={i} className="text-sm text-gray-600 ml-4">
              {i + 1}. {opt}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  
  return null;
}