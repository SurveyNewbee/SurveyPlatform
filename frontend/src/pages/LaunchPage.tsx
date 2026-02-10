import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

// Types
interface AudienceConfig {
  country: string;
  demographics: {
    age: boolean;
    gender: boolean;
    income: boolean;
    region: boolean;
  };
}

interface QuotaRow {
  variable: string;
  distribution: string;
  target: string;
}

interface SampleConfig {
  sampleSize: number;
  quotas: QuotaRow[];
}

// Utility functions
const calculateMarginOfError = (sampleSize: number): string => {
  const moe = 1.96 * Math.sqrt(0.5 * 0.5 / sampleSize) * 100;
  return `±${moe.toFixed(1)}%`;
};

const calculateCost = (sampleSize: number): number => {
  const CPI = 3.50;
  const platformFee = 200;
  return sampleSize * CPI + platformFee;
};

const LaunchPage: React.FC = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Audience configuration state
  const [audienceConfig, setAudienceConfig] = useState<AudienceConfig>({
    country: 'US',
    demographics: {
      age: true,
      gender: true,
      income: false,
      region: false,
    },
  });

  // Sample configuration state
  const [sampleConfig, setSampleConfig] = useState<SampleConfig>({
    sampleSize: 400,
    quotas: [
      { variable: 'Gender', distribution: 'Natural', target: '50/50' },
      { variable: 'Age', distribution: 'Natural', target: 'Census proportional' },
    ],
  });

  // Project data (in real implementation, fetch from API)
  const [projectData, setProjectData] = useState<any>(null);

  useEffect(() => {
    // Load project data
    const loadProject = async () => {
      try {
        const response = await fetch(`http://localhost:8000/projects/${projectId}`);
        const data = await response.json();
        setProjectData(data);
      } catch (error) {
        console.error('Failed to load project:', error);
      }
    };
    loadProject();
  }, [projectId]);

  const handleNext = () => {
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleLaunch = () => {
    setShowConfirmModal(true);
  };

  const confirmLaunch = () => {
    // In real implementation, POST to /projects/:id/launch
    setShowConfirmModal(false);
    // Navigate to status page
    navigate(`/project/${projectId}/status`);
  };

  const handleDemographicToggle = (key: keyof typeof audienceConfig.demographics) => {
    setAudienceConfig({
      ...audienceConfig,
      demographics: {
        ...audienceConfig.demographics,
        [key]: !audienceConfig.demographics[key],
      },
    });
  };

  const handleSampleSizePreset = (size: number) => {
    setSampleConfig({
      ...sampleConfig,
      sampleSize: size,
    });
  };

  const marginOfError = calculateMarginOfError(sampleConfig.sampleSize);
  const totalCost = calculateCost(sampleConfig.sampleSize);

  // Step indicator component
  const StepIndicator = () => {
    const steps = ['Audience', 'Sample & Budget', 'Review'];
    return (
      <div className="flex items-center justify-center mb-8">
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  index < currentStep
                    ? 'bg-green-500 text-white'
                    : index === currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {index < currentStep ? '✓' : index + 1}
              </div>
              <div
                className={`mt-2 text-sm font-medium ${
                  index === currentStep ? 'text-blue-600' : 'text-gray-500'
                }`}
              >
                {step}
              </div>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-24 h-1 mx-4 ${
                  index < currentStep ? 'bg-green-500' : 'bg-gray-300'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  };

  // Step 1: Audience Configuration
  const AudienceStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Target Audience</h3>
        
        {/* Country Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Country
          </label>
          <select
            value={audienceConfig.country}
            onChange={(e) =>
              setAudienceConfig({ ...audienceConfig, country: e.target.value })
            }
            className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="US">United States</option>
            <option value="UK">United Kingdom</option>
            <option value="CA">Canada</option>
            <option value="AU">Australia</option>
          </select>
        </div>

        {/* Demographics */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Demographics
          </label>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(audienceConfig.demographics).map(([key, value]) => (
              <label key={key} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={() =>
                    handleDemographicToggle(key as keyof typeof audienceConfig.demographics)
                  }
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 capitalize">{key}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Screening Criteria */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Screening Criteria</h3>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p className="text-sm text-gray-600 mb-3">
            Auto-populated from your survey's screener section:
          </p>
          <ul className="space-y-2">
            {projectData?.survey?.sections?.find((s: any) => s.title === 'Screener')
              ?.questions?.slice(0, 3)
              .map((q: any, idx: number) => (
                <li key={idx} className="text-sm text-gray-700">
                  • {q.text || 'Screening question'}
                </li>
              )) || (
              <>
                <li className="text-sm text-gray-700">• Age 18-65</li>
                <li className="text-sm text-gray-700">
                  • Purchase decision maker for household products
                </li>
                <li className="text-sm text-gray-700">
                  • Purchased skincare in past 6 months
                </li>
              </>
            )}
          </ul>
          <button
            onClick={() => navigate(`/project/${projectId}`)}
            className="mt-3 text-sm text-blue-600 hover:text-blue-700"
          >
            Edit screening in survey editor →
          </button>
        </div>
      </div>
    </div>
  );

  // Step 2: Sample & Budget
  const SampleBudgetStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Size</h3>
        
        {/* Sample size presets */}
        <div className="flex space-x-2 mb-4">
          {[200, 400, 600, 1000].map((size) => (
            <button
              key={size}
              onClick={() => handleSampleSizePreset(size)}
              className={`px-4 py-2 rounded-md font-medium ${
                sampleConfig.sampleSize === size
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {size}
            </button>
          ))}
        </div>

        {/* Custom sample size input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Sample Size
          </label>
          <input
            type="number"
            value={sampleConfig.sampleSize}
            onChange={(e) =>
              setSampleConfig({ ...sampleConfig, sampleSize: parseInt(e.target.value) || 0 })
            }
            className="w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="50"
            max="5000"
          />
        </div>

        {/* Stats guidance */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-start">
            <div className="text-blue-600 mr-3">ℹ️</div>
            <div>
              <p className="text-sm font-medium text-blue-900">Statistical Guidance</p>
              <p className="text-sm text-blue-700 mt-1">
                Margin of error: <span className="font-semibold">{marginOfError}</span> at 95%
                confidence
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Minimum subgroup size for reliability: ~100 completes
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quotas */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Quotas</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Variable
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Distribution
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Target
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sampleConfig.quotas.map((quota, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 text-sm text-gray-900">{quota.variable}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{quota.distribution}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{quota.target}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cost Estimate */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Cost Estimate</h3>
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Field cost ({sampleConfig.sampleSize} × $3.50 CPI)</span>
              <span className="text-gray-900 font-medium">
                ${(sampleConfig.sampleSize * 3.5).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Platform fee</span>
              <span className="text-gray-900 font-medium">$200.00</span>
            </div>
            <div className="border-t pt-2 flex justify-between">
              <span className="text-base font-semibold text-gray-900">Total</span>
              <span className="text-base font-semibold text-blue-600">
                ${totalCost.toFixed(2)}
              </span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Estimated field time: 24-48 hours
          </p>
        </div>
      </div>
    </div>
  );

  // Step 3: Review & Launch
  const ReviewStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Your Configuration</h3>

        {/* Survey Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h4 className="font-medium text-gray-900 mb-3">Survey Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Survey Name:</span>
              <span className="ml-2 text-gray-900 font-medium">
                {projectData?.name || 'Untitled Survey'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Estimated LOI:</span>
              <span className="ml-2 text-gray-900 font-medium">
                {projectData?.loi || 12} minutes
              </span>
            </div>
          </div>
        </div>

        {/* Audience */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h4 className="font-medium text-gray-900 mb-3">Audience</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Country:</span>
              <span className="ml-2 text-gray-900">{audienceConfig.country}</span>
            </div>
            <div>
              <span className="text-gray-600">Demographics:</span>
              <span className="ml-2 text-gray-900">
                {Object.entries(audienceConfig.demographics)
                  .filter(([_, value]) => value)
                  .map(([key]) => key)
                  .join(', ')}
              </span>
            </div>
          </div>
        </div>

        {/* Sample */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h4 className="font-medium text-gray-900 mb-3">Sample</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Target completes:</span>
              <span className="ml-2 text-gray-900 font-medium">{sampleConfig.sampleSize}</span>
            </div>
            <div>
              <span className="text-gray-600">Margin of error:</span>
              <span className="ml-2 text-gray-900">{marginOfError}</span>
            </div>
          </div>
        </div>

        {/* Cost & Timeline */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-700">Total cost:</span>
              <span className="text-blue-900 font-semibold text-lg">${totalCost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700">Estimated completion:</span>
              <span className="text-gray-900">
                {new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Pre-launch Checklist */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Pre-Launch Checklist</h3>
        <div className="space-y-2">
          <label className="flex items-start space-x-2">
            <input
              type="checkbox"
              defaultChecked
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              I have reviewed the survey questions and logic in the preview
            </span>
          </label>
          <label className="flex items-start space-x-2">
            <input
              type="checkbox"
              defaultChecked
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              The audience configuration matches my research objectives
            </span>
          </label>
          <label className="flex items-start space-x-2">
            <input
              type="checkbox"
              defaultChecked
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              I understand the estimated cost and timeline
            </span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <AudienceStep />;
      case 1:
        return <SampleBudgetStep />;
      case 2:
        return <ReviewStep />;
      default:
        return null;
    }
  };

  if (!projectData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <button
            onClick={() => navigate(`/project/${projectId}`)}
            className="text-sm text-gray-600 hover:text-gray-900 mb-2"
          >
            ← Back to Project
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Launch Study</h1>
          <p className="text-sm text-gray-600 mt-1">
            Configure your audience and sample, then launch to field
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        <StepIndicator />

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          {renderStep()}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t">
            <button
              onClick={handleBack}
              disabled={currentStep === 0}
              className={`px-6 py-2 rounded-md font-medium ${
                currentStep === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              ← Back
            </button>

            {currentStep < 2 ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleLaunch}
                className="px-8 py-3 bg-green-600 text-white rounded-md font-semibold hover:bg-green-700 flex items-center"
              >
                🚀 Launch Study
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Confirm Launch</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to launch this study? Once launched, it will begin fielding to
              respondents.
            </p>
            <div className="bg-gray-50 rounded p-3 mb-6">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Sample size:</span>
                <span className="text-gray-900 font-medium">{sampleConfig.sampleSize}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Estimated cost:</span>
                <span className="text-gray-900 font-semibold">${totalCost.toFixed(2)}</span>
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={confirmLaunch}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
              >
                Confirm Launch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LaunchPage;
