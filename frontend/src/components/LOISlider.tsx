import React, { useState, useEffect } from 'react';

interface LOISliderProps {
  loiConfig: {
    slider_position: number;
    snap_point: string;
    estimated_loi_minutes: number;
    total_questions: number;
    visible_questions: number;
    hidden_questions: number;
    user_pinned_count: number;
    user_excluded_count: number;
  };
  onSliderChange: (position: number) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const SNAP_POSITIONS = {
  quick: 15,
  standard: 50,
  deep: 85,
};

const SNAP_THRESHOLD = 10; // Snap when within 10% of snap point

const FOCUS_NOTES: Record<string, { title: string; description: string; drops: string }> = {
  quick: {
    title: '⚡ Quick',
    description: 'Fast validation on your core hypothesis. Includes screener and essential metrics only.',
    drops: 'Drops: diagnostic batteries, open-ends, secondary metrics, detailed demographics',
  },
  standard: {
    title: '📊 Standard',
    description: 'Balanced depth for most studies. Includes screener, core metrics, and key diagnostics.',
    drops: 'Drops: extended open-ends, secondary attribute batteries, detailed competitive comparison',
  },
  deep: {
    title: '🔬 Deep',
    description: 'Maximum diagnostic depth for complex decisions. Every question included.',
    drops: '',
  },
};

export default function LOISlider({ loiConfig, onSliderChange, collapsed = false, onToggleCollapse }: LOISliderProps) {
  const [sliderValue, setSliderValue] = useState(loiConfig.slider_position);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    setSliderValue(loiConfig.slider_position);
  }, [loiConfig.slider_position]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = parseInt(e.target.value);

    // Snap to closest point if within threshold
    const snapKeys = Object.keys(SNAP_POSITIONS) as Array<keyof typeof SNAP_POSITIONS>;
    for (const key of snapKeys) {
      const snapPos = SNAP_POSITIONS[key];
      if (Math.abs(newValue - snapPos) < SNAP_THRESHOLD) {
        newValue = snapPos;
        break;
      }
    }

    setSliderValue(newValue);
  };

  const handleSliderMouseUp = () => {
    setIsDragging(false);
    if (sliderValue !== loiConfig.slider_position) {
      onSliderChange(sliderValue);
    }
  };

  const handleSliderMouseDown = () => {
    setIsDragging(true);
  };

  const getTierFromPosition = (position: number): string => {
    if (position <= 30) return 'quick';
    if (position <= 70) return 'standard';
    return 'deep';
  };

  const currentTier = getTierFromPosition(sliderValue);
  const focusNote = FOCUS_NOTES[currentTier];

  // Calculate slider progress for styling
  const progressPercent = sliderValue;

  return (
    <div className="w-full bg-gray-50 border-b border-gray-200">
      {/* Header Row */}
      <div className="px-6 py-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Survey Length</h3>
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            {collapsed ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            )}
          </button>
        )}
      </div>

      {!collapsed && (
        <div className="px-6 pb-6">
          {/* Tier Labels */}
          <div className="flex justify-between mb-2 text-xs">
            <div className={`flex flex-col items-start ${currentTier === 'quick' ? 'text-blue-600 font-bold' : 'text-gray-500'}`}>
              <span>⚡ Quick</span>
              <span className="text-xs">3-5 min</span>
            </div>
            <div className={`flex flex-col items-center ${currentTier === 'standard' ? 'text-blue-600 font-bold' : 'text-gray-500'}`}>
              <span>📊 Standard</span>
              <span className="text-xs">8-12 min</span>
            </div>
            <div className={`flex flex-col items-end ${currentTier === 'deep' ? 'text-blue-600 font-bold' : 'text-gray-500'}`}>
              <span>🔬 Deep</span>
              <span className="text-xs">15-20 min</span>
            </div>
          </div>

          {/* Slider */}
          <div className="relative mb-2">
            <input
              type="range"
              min="0"
              max="100"
              value={sliderValue}
              onChange={handleSliderChange}
              onMouseDown={handleSliderMouseDown}
              onMouseUp={handleSliderMouseUp}
              onTouchStart={handleSliderMouseDown}
              onTouchEnd={handleSliderMouseUp}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
              style={{
                background: `linear-gradient(to right, #2563EB ${progressPercent}%, #E5E7EB ${progressPercent}%)`,
              }}
            />
          </div>

          {/* Current LOI Display */}
          <div className="text-center mb-4">
            <span className="text-sm font-semibold text-blue-600">
              current: ~{loiConfig.estimated_loi_minutes} min
            </span>
          </div>

          {/* Focus Note */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
            <div className="text-sm text-blue-900">
              <strong>{focusNote.title}:</strong> {focusNote.description}
            </div>
            {focusNote.drops && (
              <div className="text-xs text-blue-700 mt-2">{focusNote.drops}</div>
            )}
          </div>

          {/* Stats Row */}
          <div className="text-xs text-gray-600 flex items-center justify-between">
            <span>
              {loiConfig.visible_questions} of {loiConfig.total_questions} questions shown
            </span>
            <span className="px-2">|</span>
            <span>{loiConfig.hidden_questions} hidden</span>
            {loiConfig.user_pinned_count > 0 && (
              <>
                <span className="px-2">|</span>
                <span>{loiConfig.user_pinned_count} pinned by you</span>
              </>
            )}
            {loiConfig.user_excluded_count > 0 && (
              <>
                <span className="px-2">|</span>
                <span>{loiConfig.user_excluded_count} excluded by you</span>
              </>
            )}
          </div>
        </div>
      )}

      <style>{`
        .slider-thumb::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #2563EB;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          cursor: pointer;
        }

        .slider-thumb::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #2563EB;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          cursor: pointer;
        }
      `}</style>
    </div>
  );
}
