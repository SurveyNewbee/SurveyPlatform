import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface StatusMetrics {
  completes: number;
  target: number;
  incidenceRate: number;
  medianLOI: number;
  dropOffRate: number;
}

const StatusPage: React.FC = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<StatusMetrics>({
    completes: 247,
    target: 400,
    incidenceRate: 68,
    medianLOI: 8.7,
    dropOffRate: 12,
  });

  // Simulate progress animation for demo
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => {
        if (prev.completes < prev.target) {
          return {
            ...prev,
            completes: Math.min(prev.completes + Math.floor(Math.random() * 3) + 1, prev.target),
          };
        }
        return prev;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const progress = (metrics.completes / metrics.target) * 100;
  const isComplete = metrics.completes >= metrics.target;

  const estimatedCompletion = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000);

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
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${isComplete ? 'bg-green-500' : 'bg-green-500 animate-pulse'}`} />
                <h1 className="text-2xl font-bold text-gray-900">
                  {isComplete ? 'Study Complete' : 'Study is Live'}
                </h1>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Launched {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
              </p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate(`/project/${projectId}/report`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
              >
                View Interim Results
              </button>
              <button
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium"
              >
                Pause Study
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Collection Progress</h2>
            <span className="text-sm text-gray-600">
              {metrics.completes} of {metrics.target} completes
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  isComplete ? 'bg-green-500' : 'bg-blue-600'
                }`}
                style={{ width: `${Math.min(progress, 100)}%` }}
              />
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-sm font-medium text-blue-600">{progress.toFixed(1)}%</span>
              <span className="text-sm text-gray-600">
                {isComplete
                  ? 'Completed'
                  : `Estimated completion: ${estimatedCompletion.toLocaleDateString()}`}
              </span>
            </div>
          </div>

          {/* Status Message */}
          {!isComplete && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-start">
                <div className="text-blue-600 text-xl mr-3">📊</div>
                <div>
                  <p className="text-sm font-medium text-blue-900">Fielding in progress</p>
                  <p className="text-sm text-blue-700 mt-1">
                    Your survey is live and collecting responses. The progress bar updates in
                    real-time as respondents complete the survey.
                  </p>
                </div>
              </div>
            </div>
          )}

          {isComplete && (
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-start">
                <div className="text-green-600 text-xl mr-3">✓</div>
                <div>
                  <p className="text-sm font-medium text-green-900">Collection complete!</p>
                  <p className="text-sm text-green-700 mt-1">
                    Your study has reached the target sample size. View the full report to analyze
                    your results.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Completes */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Completes</h3>
              <span className="text-2xl">📋</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {metrics.completes} <span className="text-xl text-gray-500">/ {metrics.target}</span>
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {((metrics.completes / metrics.target) * 100).toFixed(1)}% of target
            </p>
          </div>

          {/* Incidence Rate */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Incidence Rate</h3>
              <span className="text-2xl">🎯</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metrics.incidenceRate}%</p>
            <p className="text-sm text-gray-600 mt-1">Respondents qualifying</p>
          </div>

          {/* Median LOI */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Median LOI</h3>
              <span className="text-2xl">⏱️</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metrics.medianLOI} min</p>
            <p className="text-sm text-gray-600 mt-1">Average completion time</p>
          </div>

          {/* Drop-off Rate */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Drop-off Rate</h3>
              <span className="text-2xl">⚠️</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metrics.dropOffRate}%</p>
            <p className="text-sm text-gray-600 mt-1">Started but didn't complete</p>
          </div>
        </div>

        {/* Detailed Metrics Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Fielding Details</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Metric
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Completes</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {metrics.completes} / {metrics.target}
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Incidence rate</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{metrics.incidenceRate}%</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Median LOI</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{metrics.medianLOI} min</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Drop-off rate</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{metrics.dropOffRate}%</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Starts</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {Math.floor(metrics.completes / (1 - metrics.dropOffRate / 100))}
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Launch date</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date().toLocaleDateString()}
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900">Estimated completion</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {estimatedCompletion.toLocaleDateString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-yellow-50 rounded-lg p-4 border border-yellow-200">
          <div className="flex items-start">
            <div className="text-yellow-600 text-xl mr-3">💡</div>
            <div>
              <p className="text-sm font-medium text-yellow-900">Demo Mode</p>
              <p className="text-sm text-yellow-700 mt-1">
                This status page simulates fielding progress for demonstration purposes. In
                production, these metrics would reflect real-time panel integration data.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPage;
