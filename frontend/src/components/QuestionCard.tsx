import React, { useState } from 'react';

interface QuestionCardProps {
  question: any;
  sectionColor: 'blue' | 'green' | 'purple';
  onPin?: (questionId: string) => void;
  onExclude?: (questionId: string) => void;
  onResetOverride?: (questionId: string) => void;
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
}: QuestionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const isHidden = q.loi_visibility === 'hidden';
  const isPinned = q.user_override === 'pinned';
  const isExcluded = q.user_override === 'excluded';
  
  const colors = COLOR_CLASSES[sectionColor];

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
    <div className={`bg-gray-50 rounded-lg p-4 border ${isPinned ? `border-l-4 border-l-blue-500 ${colors.border}` : 'border-gray-200'}`}>
      <div className="flex items-start justify-between mb-2">
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
          <span className={`text-xs ${colors.badge} px-2 py-1 rounded`}>
            {q.question_type}
          </span>
          {/* Action buttons */}
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
        </div>
      </div>
      
      <p className="text-gray-700 mb-3">{q.question_text}</p>
      
      {renderQuestionContent(q, colors)}
      
      {q.notes && (
        <div className="mt-2 text-xs text-gray-500 italic border-t border-gray-200 pt-2">
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

function renderQuestionContent(q: any, colors: typeof COLOR_CLASSES.blue) {
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
      <div className="mt-2">
        <p className="text-xs font-medium text-gray-500 mb-1">Options:</p>
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
