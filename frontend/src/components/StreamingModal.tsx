import { useEffect, useRef } from 'react';

interface StreamingModalProps {
  isOpen: boolean;
  title: string;
  content: string;
  onClose?: () => void;
}

export default function StreamingModal({ isOpen, title, content, onClose }: StreamingModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom as content updates
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="animate-pulse flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
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

        {/* Content */}
        <div
          ref={contentRef}
          className="flex-1 overflow-y-auto px-6 py-4 font-mono text-sm text-gray-800 whitespace-pre-wrap bg-gray-50"
        >
          {content || 'Connecting...'}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-600">
          <p>Streaming response from AI agent...</p>
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
}
