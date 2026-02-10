import React from 'react';

interface DataGenerationModalProps {
  isOpen: boolean;
  onClose?: () => void;
}

const DataGenerationModal: React.FC<DataGenerationModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="animate-pulse flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Generating Test Data...</h3>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Progress Steps */}
        <div className="space-y-4 mb-6">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Loading survey structure</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center animate-spin">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Generating Python script</p>
              <p className="text-xs text-gray-500">AI is creating realistic data patterns...</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-gray-500"></div>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-500">Creating respondent data</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-gray-500"></div>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-500">Validating quotas and logic</p>
            </div>
          </div>
        </div>

        {/* ETA */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Estimated time:</span> 30-60 seconds
          </p>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        .animation-delay-200 {
          animation: pulse 1.5s ease-in-out 0.2s infinite;
        }
        .animation-delay-400 {
          animation: pulse 1.5s ease-in-out 0.4s infinite;
        }
      `}</style>
    </div>
  );
};

export default DataGenerationModal;
