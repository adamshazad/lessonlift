import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, X, TrendingUp } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/Header';
import LessonForm from '../components/LessonForm';
import LessonPreview from '../components/LessonPreview';
import LessonHistory from '../components/LessonHistory';
import ProgressOverlay from '../components/ProgressOverlay';
import UpgradeCTA from '../components/UpgradeCTA';
import TrialStatusBanner from '../components/TrialStatusBanner';
import { generateLesson, fetchLessonHistory, getUsageInfo, LessonRequest, Lesson, UsageInfo, TrialInfo, PaidPlanInfo } from '../services/lessonService';

const LessonGeneratorPage: React.FC = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentLesson, setCurrentLesson] = useState<any | null>(null);
  const [lessonHistory, setLessonHistory] = useState<Lesson[]>([]);
  const [showHistory, setShowHistory] = useState(true);
  const [usageInfo, setUsageInfo] = useState<UsageInfo | null>(null);
  const [limitReached, setLimitReached] = useState<{
    isTrial?: boolean;
    trialExpired?: boolean;
    expiredBy?: 'time' | 'lessons';
    lessonsUsed?: number;
    limitType?: 'daily' | 'monthly';
    currentCount?: number;
    maxCount?: number;
    plan?: 'starter' | 'standard' | 'pro';
  } | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/signup');
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    if (user) {
      loadHistory();
      loadUsage();
    }
  }, [user]);

  const loadHistory = async () => {
    const lessons = await fetchLessonHistory();
    setLessonHistory(lessons);
  };

  const loadUsage = async () => {
    const usage = await getUsageInfo();
    setUsageInfo(usage);
  };

  const handleGenerate = async (request: LessonRequest) => {
    setIsGenerating(true);
    setError(null);
    setLimitReached(null);

    try {
      const result = await generateLesson(request);

      if (result.success && result.lesson) {
        setCurrentLesson(result.lesson);
        await loadHistory();
        await loadUsage();
        setLimitReached(null);
      } else if (result.limitReached) {
        if (result.isTrial && result.trialExpired) {
          setLimitReached({
            isTrial: true,
            trialExpired: true,
            expiredBy: result.expiredBy,
            lessonsUsed: result.lessonsUsed,
          });
        } else {
          setLimitReached({
            isTrial: false,
            limitType: result.limitType!,
            currentCount: result.currentCount!,
            maxCount: result.maxCount!,
            plan: result.plan!,
          });
        }
        setError(null);
      } else {
        setError(result.error || 'Failed to generate lesson. Please try again.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectLesson = (lesson: Lesson) => {
    setCurrentLesson({
      id: lesson.id,
      html: lesson.lesson_content,
      text: lesson.lesson_text,
      yearGroup: lesson.year_group,
      abilityLevel: lesson.ability_level,
      lessonDuration: lesson.lesson_duration,
      subject: lesson.subject,
      topic: lesson.topic,
      learningObjective: lesson.learning_objective,
      senEalNotes: lesson.sen_eal_notes,
    });
    setError(null);
  };

  const handleDeleteLesson = (lessonId: string) => {
    setLessonHistory((prev) => prev.filter((l) => l.id !== lessonId));
    if (currentLesson?.id === lessonId) {
      setCurrentLesson(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#4CAF50] mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-white flex flex-col">
      <Header />
      <ProgressOverlay isVisible={isGenerating} />

      <div className="flex-grow py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                  Lesson Generator
                </h1>
                <p className="text-gray-600 text-lg">
                  Create customised, UK curriculum-aligned lesson plans with AI
                </p>
              </div>

              {usageInfo && usageInfo.isTrial && (
                <TrialStatusBanner trialInfo={usageInfo as TrialInfo} />
              )}

              {usageInfo && !usageInfo.isTrial && (
                <div className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-4 min-w-[280px]">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={20} className="text-[#4CAF50]" />
                    <h3 className="font-bold text-gray-900">Your Usage</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center pb-2 border-b border-green-200">
                      <span className="text-sm text-gray-600">Plan:</span>
                      <span className="font-semibold text-[#4CAF50] capitalize">{usageInfo.plan}</span>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600 font-medium">Today:</span>
                        <span className="font-semibold text-gray-900">
                          {(usageInfo as PaidPlanInfo).dailyCount} / {(usageInfo as PaidPlanInfo).dailyMax}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            (usageInfo as PaidPlanInfo).dailyRemaining === 0 ? 'bg-red-500' : 'bg-[#4CAF50]'
                          }`}
                          style={{
                            width: `${((usageInfo as PaidPlanInfo).dailyCount / (usageInfo as PaidPlanInfo).dailyMax) * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600 font-medium">This Month:</span>
                        <span className="font-semibold text-gray-900">
                          {(usageInfo as PaidPlanInfo).monthlyCount} / {(usageInfo as PaidPlanInfo).monthlyMax}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            (usageInfo as PaidPlanInfo).monthlyRemaining === 0 ? 'bg-red-500' : 'bg-blue-500'
                          }`}
                          style={{
                            width: `${((usageInfo as PaidPlanInfo).monthlyCount / (usageInfo as PaidPlanInfo).monthlyMax) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {limitReached && (
            <UpgradeCTA
              isTrial={limitReached.isTrial}
              trialExpired={limitReached.trialExpired}
              expiredBy={limitReached.expiredBy}
              lessonsUsed={limitReached.lessonsUsed}
              limitType={limitReached.limitType}
              currentPlan={limitReached.plan}
              currentCount={limitReached.currentCount}
              maxCount={limitReached.maxCount}
            />
          )}

          {error && (
            <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-sm font-semibold text-red-800">Error</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700 transition-colors"
              >
                <X size={20} />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className={`${showHistory ? 'lg:col-span-8' : 'lg:col-span-12'} space-y-6`}>
              <LessonForm onGenerate={handleGenerate} isGenerating={isGenerating} />

              {currentLesson && (
                <LessonPreview
                  lesson={currentLesson}
                  onRegenerate={handleGenerate}
                  isRegenerating={isGenerating}
                  allowedExportFormats={usageInfo?.exportFormats || ['pdf']}
                />
              )}
            </div>

            {showHistory && (
              <div className="lg:col-span-4">
                <div className="sticky top-24 max-h-[calc(100vh-8rem)]">
                  <LessonHistory
                    lessons={lessonHistory}
                    onSelectLesson={handleSelectLesson}
                    onDeleteLesson={handleDeleteLesson}
                    selectedLessonId={currentLesson?.id}
                  />
                </div>
              </div>
            )}
          </div>

          <button
            onClick={() => setShowHistory(!showHistory)}
            className="lg:hidden fixed bottom-6 right-6 bg-[#4CAF50] hover:bg-[#45a049] text-white px-6 py-3 rounded-full shadow-lg font-semibold transition-all"
          >
            {showHistory ? 'Hide History' : 'Show History'}
          </button>
        </div>
      </div>

      <style>{`
        .lesson-preview-content .lesson-header {
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 3px solid #4CAF50;
        }

        .lesson-preview-content .lesson-header h1 {
          color: #4CAF50;
          font-size: 28px;
          font-weight: bold;
          margin-bottom: 12px;
        }

        .lesson-preview-content .lesson-meta {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
          font-size: 14px;
        }

        .lesson-preview-content .meta-item {
          color: #666;
          background: #f3f4f6;
          padding: 6px 12px;
          border-radius: 8px;
        }

        .lesson-preview-content .lesson-content {
          margin-top: 24px;
        }

        .lesson-preview-content .section-heading {
          color: #2c5f2d;
          font-size: 22px;
          font-weight: bold;
          margin-top: 28px;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 2px solid #e5e7eb;
        }

        .lesson-preview-content .subsection {
          color: #4CAF50;
          font-size: 18px;
          font-weight: 600;
          margin-top: 20px;
          margin-bottom: 10px;
        }

        .lesson-preview-content li {
          margin-bottom: 8px;
          line-height: 1.7;
          color: #374151;
        }

        .lesson-preview-content .nested-item {
          margin-left: 24px;
          color: #6b7280;
        }

        .lesson-preview-content p {
          line-height: 1.8;
          margin-bottom: 12px;
          color: #374151;
        }

        .lesson-preview-content h2,
        .lesson-preview-content h3,
        .lesson-preview-content h4 {
          scroll-margin-top: 100px;
        }

        @media (max-width: 1024px) {
          .lesson-preview-content .lesson-header h1 {
            font-size: 24px;
          }

          .lesson-preview-content .section-heading {
            font-size: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default LessonGeneratorPage;
