import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject } from '../api/client';
import type { Project } from '../types';
import BarChart from '../components/BarChart';
import GroupedBarChart from '../components/GroupedBarChart';
import VanWestendorpChart from '../components/VanWestendorpChart';
import seedPricingData from '../data/seed-pricing-study.json';

interface ReportData {
  survey_id: string;
  title: string;
  field_dates: {
    start: string;
    end: string;
  };
  sample_size: number;
  completion_rate: number;
  actual_loi_minutes: number;
  executive_summary: string[];
  demographics: {
    [key: string]: { [value: string]: number };
  };
  questions: QuestionResult[];
  specialty_analyses?: SpecialtyAnalysis[];
}

interface QuestionResult {
  question_id: string;
  question_text: string;
  question_type: string;
  sample_size: number;
  results: {
    options: OptionResult[];
    mean?: number;
    median?: number;
  };
  significance_tests?: SignificanceTest[];
  ai_insight: string;
}

interface OptionResult {
  label: string;
  count: number;
  percentage: number;
  breaks?: {
    [breakVariable: string]: { [breakValue: string]: number };
  };
}

interface SignificanceTest {
  break_variable: string;
  groups_compared: string[];
  p_value: number;
  significant: boolean;
}

interface SpecialtyAnalysis {
  type: string;
  data: any;
}

export default function ReportPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [breakVariable, setBreakVariable] = useState<string>('none');
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    const response = await getProject(projectId);
    
    if (response.success && response.data) {
      setProject(response.data);
      // Load or generate report data
      loadReportData();
    }
    
    setLoading(false);
  };

  const loadReportData = async () => {
    // For MVP, we'll load seed data
    // In production, this would fetch actual field results
    const seedData = generateSeedData();
    setReportData(seedData);
  };

  const generateSeedData = (): ReportData => {
    // For MVP, return seed data
    // In production, this would fetch actual field results
    return seedPricingData as ReportData;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-gray-600">Loading report...</div>
      </div>
    );
  }

  if (!project || !reportData) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-700">No report data available.</p>
            <button
              onClick={() => navigate(`/project/${projectId}`)}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              ← Back to Project
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-800">{reportData.title}</h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                <span>
                  Fielded: {new Date(reportData.field_dates.start).toLocaleDateString()} - {new Date(reportData.field_dates.end).toLocaleDateString()}
                </span>
                <span>|</span>
                <span>n={reportData.sample_size}</span>
                <span>|</span>
                <span>LOI: {reportData.actual_loi_minutes} min</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                📄 Export PDF
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                📊 Export PPTX
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto flex">
        {/* Sidebar Navigation */}
        <div className="w-60 bg-gray-50 border-r border-gray-200 min-h-[calc(100vh-73px)] p-4">
          <nav className="space-y-1">
            <a
              href="#executive-summary"
              className="block px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              📊 Executive Summary
            </a>
            <a
              href="#screener"
              className="block px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            >
              📋 Screener Results
            </a>
            <a
              href="#core"
              className="block px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            >
              📋 Core Findings
            </a>
            <a
              href="#pricing"
              className="block px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            >
              📋 Pricing Analysis
            </a>
            <a
              href="#demographics"
              className="block px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            >
              📋 Demographics
            </a>
          </nav>

          {/* Cross-tab Control */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Break By:
            </label>
            <select
              value={breakVariable}
              onChange={(e) => setBreakVariable(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="none">None</option>
              <option value="age">Age</option>
              <option value="gender">Gender</option>
              <option value="income">Income</option>
              <option value="region">Region</option>
            </select>
          </div>
        </div>

        {/* Report Canvas */}
        <div className="flex-1 p-8 overflow-y-auto">
          {/* Executive Summary */}
          <div id="executive-summary" className="mb-8">
            <div className="bg-white border-l-4 border-blue-600 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                📊 Executive Summary
              </h2>
              <div className="space-y-2">
                {reportData.executive_summary.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <p className="text-gray-700 flex-1">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Question Results */}
          {reportData.questions.length === 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
              <p className="text-gray-600 mb-2">No question results available yet.</p>
              <p className="text-sm text-gray-500">
                Seed data will be loaded in the next implementation step.
              </p>
            </div>
          )}

          {reportData.questions.map((question) => (
            <div key={question.question_id} className="bg-white rounded-lg border border-gray-200 p-6 mb-6 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-gray-800 mb-1">
                    {question.question_text}
                  </h3>
                  <p className="text-sm text-gray-500">n={question.sample_size}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setViewMode('chart')}
                    className={`px-3 py-1 text-sm rounded ${
                      viewMode === 'chart'
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    📊 Chart
                  </button>
                  <button
                    onClick={() => setViewMode('table')}
                    className={`px-3 py-1 text-sm rounded ${
                      viewMode === 'table'
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    📋 Table
                  </button>
                </div>
              </div>

              {viewMode === 'chart' ? (
                <div className="mt-4">
                  {breakVariable === 'none' ? (
                    <BarChart
                      data={question.results.options.map(opt => ({
                        label: opt.label,
                        value: opt.count,
                        percentage: opt.percentage
                      }))}
                      height={Math.max(250, question.results.options.length * 40)}
                      showPercentage={true}
                      color="#2563EB"
                      horizontal={true}
                    />
                  ) : (
                    <GroupedBarChart
                      data={question.results.options.map(opt => ({
                        label: opt.label,
                        groups: opt.breaks?.[breakVariable] || {}
                      }))}
                      height={Math.max(300, question.results.options.length * 50)}
                    />
                  )}
                </div>
              ) : (
                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-full border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 border-b">
                          Option
                        </th>
                        <th className="px-4 py-2 text-right text-sm font-medium text-gray-700 border-b">
                          n
                        </th>
                        <th className="px-4 py-2 text-right text-sm font-medium text-gray-700 border-b">
                          %
                        </th>
                        {breakVariable !== 'none' && 
                          Object.keys(reportData.demographics[breakVariable] || {}).map(breakValue => (
                            <th key={breakValue} className="px-4 py-2 text-right text-sm font-medium text-gray-700 border-b">
                              {breakValue}
                            </th>
                          ))
                        }
                      </tr>
                    </thead>
                    <tbody>
                      {question.results.options.map((opt, idx) => (
                        <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="px-4 py-2 text-sm text-gray-800 border-b">
                            {opt.label}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-600 text-right border-b">
                            {opt.count}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-600 text-right border-b">
                            {Math.round(opt.percentage * 100)}%
                          </td>
                          {breakVariable !== 'none' && 
                            Object.keys(reportData.demographics[breakVariable] || {}).map(breakValue => (
                              <td key={breakValue} className="px-4 py-2 text-sm text-gray-600 text-right border-b">
                                {opt.breaks?.[breakVariable]?.[breakValue] 
                                  ? `${Math.round(opt.breaks[breakVariable][breakValue] * 100)}%`
                                  : '-'
                                }
                              </td>
                            ))
                          }
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* AI Insight */}
              {question.ai_insight && (
                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium text-blue-700">💡 Insight:</span> {question.ai_insight}
                  </p>
                </div>
              )}
            </div>
          ))}

          {/* Specialty Analyses */}
          {reportData.specialty_analyses && reportData.specialty_analyses.length > 0 && (
            <div className="mt-8 space-y-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                📊 Specialty Analyses
              </h2>
              {reportData.specialty_analyses.map((analysis, idx) => (
                <div key={idx}>
                  {analysis.type === 'van_westendorp' && (
                    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        Van Westendorp Price Sensitivity Meter
                      </h3>
                      <VanWestendorpChart data={analysis.data} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}