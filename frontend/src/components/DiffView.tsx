import { useState } from 'react';

interface Edit {
  question_id: string;
  field: string;
  old_value: any;
  new_value: any;
  reason: string;
}

interface DiffViewProps {
  edits: Edit[];
  onApply: (acceptedEdits: Edit[]) => void;
  onCancel: () => void;
}

export default function DiffView({ edits, onApply, onCancel }: DiffViewProps) {
  const [selections, setSelections] = useState<Record<number, boolean>>(
    Object.fromEntries(edits.map((_, idx) => [idx, true]))
  );

  const toggleSelection = (index: number) => {
    setSelections({ ...selections, [index]: !selections[index] });
  };

  const selectAll = () => {
    setSelections(Object.fromEntries(edits.map((_, idx) => [idx, true])));
  };

  const deselectAll = () => {
    setSelections(Object.fromEntries(edits.map((_, idx) => [idx, false])));
  };

  const handleApply = () => {
    const acceptedEdits = edits.filter((_, idx) => selections[idx]);
    onApply(acceptedEdits);
  };

  const selectedCount = Object.values(selections).filter(Boolean).length;

  const renderValue = (value: any): string => {
    if (Array.isArray(value)) {
      return value.map(v => `• ${v}`).join('\n');
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-2xl font-bold text-gray-800">Review AI Edits</h2>
          <p className="text-sm text-gray-600 mt-1">
            {edits.length} edit{edits.length !== 1 ? 's' : ''} proposed • {selectedCount} selected
          </p>
        </div>

        {/* Controls */}
        <div className="border-b border-gray-200 px-6 py-3 flex items-center gap-4">
          <button
            onClick={selectAll}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            className="text-sm text-gray-600 hover:text-gray-700 font-medium"
          >
            Deselect All
          </button>
        </div>

        {/* Edits List */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-6">
            {edits.map((edit, idx) => (
              <div
                key={idx}
                className={`border-2 rounded-lg transition-all ${
                  selections[idx]
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 bg-white'
                }`}
              >
                {/* Edit Header */}
                <div className="flex items-start gap-3 p-4 border-b border-gray-200">
                  <input
                    type="checkbox"
                    checked={selections[idx]}
                    onChange={() => toggleSelection(idx)}
                    className="mt-1 w-5 h-5 text-green-600 focus:ring-green-500 rounded"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-sm bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                        {edit.question_id}
                      </span>
                      <span className="text-sm text-gray-600">•</span>
                      <span className="text-sm text-gray-600 capitalize">
                        {edit.field.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">
                      💡 {edit.reason}
                    </p>
                  </div>
                </div>

                {/* Before/After */}
                <div className="grid grid-cols-2 gap-4 p-4">
                  {/* Before */}
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                      Before
                    </h4>
                    <div className="bg-red-50 border border-red-200 rounded p-3">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                        {renderValue(edit.old_value)}
                      </pre>
                    </div>
                  </div>

                  {/* After */}
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                      After
                    </h4>
                    <div className="bg-green-50 border border-green-200 rounded p-3">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                        {renderValue(edit.new_value)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 flex items-center justify-between">
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors font-medium"
          >
            Cancel
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleApply}
              disabled={selectedCount === 0}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Apply {selectedCount} Change{selectedCount !== 1 ? 's' : ''}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
