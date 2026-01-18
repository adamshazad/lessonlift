import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, FileText, Sparkles, TrendingUp } from 'lucide-react';
import { TrialInfo } from '../services/lessonService';

interface TrialStatusBannerProps {
  trialInfo: TrialInfo;
}

const TrialStatusBanner: React.FC<TrialStatusBannerProps> = ({ trialInfo }) => {
  const navigate = useNavigate();

  if (!trialInfo.trialStarted) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-green-50 border-2 border-blue-200 rounded-xl p-4 min-w-[280px]">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles size={20} className="text-blue-600" />
          <h3 className="font-bold text-gray-900">Free Trial</h3>
        </div>
        <div className="space-y-2">
          <p className="text-sm text-gray-700">
            Start your <strong>7-day free trial</strong> with <strong>5 lesson plans</strong> included!
          </p>
          <p className="text-xs text-gray-600">
            Trial begins when you generate your first lesson.
          </p>
        </div>
      </div>
    );
  }

  const lessonsPercent = (trialInfo.lessonsUsed / trialInfo.lessonsTotal) * 100;
  const daysPercent = trialInfo.daysElapsed && trialInfo.daysTotal
    ? (trialInfo.daysElapsed / trialInfo.daysTotal) * 100
    : 0;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-green-50 border-2 border-blue-200 rounded-xl p-4 min-w-[320px]">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={20} className="text-blue-600" />
          <h3 className="font-bold text-gray-900">Free Trial Active</h3>
        </div>
        <button
          onClick={() => navigate('/get-started#pricing')}
          className="text-xs bg-gradient-to-r from-[#4CAF50] to-[#45a049] hover:from-[#45a049] hover:to-[#3d8b40] text-white px-3 py-1 rounded-md font-semibold transition-all"
        >
          Upgrade
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-1.5 text-sm text-gray-700">
              <FileText size={16} />
              <span className="font-medium">Lessons:</span>
            </div>
            <span className="font-semibold text-gray-900 text-sm">
              {trialInfo.lessonsUsed} / {trialInfo.lessonsTotal}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                trialInfo.lessonsRemaining === 0 ? 'bg-red-500' : 'bg-blue-500'
              }`}
              style={{ width: `${lessonsPercent}%` }}
            />
          </div>
          {trialInfo.lessonsRemaining > 0 && (
            <p className="text-xs text-gray-600 mt-1">
              {trialInfo.lessonsRemaining} lesson{trialInfo.lessonsRemaining !== 1 ? 's' : ''} remaining
            </p>
          )}
          {trialInfo.lessonsRemaining === 0 && (
            <p className="text-xs text-red-600 font-semibold mt-1">
              No lessons remaining
            </p>
          )}
        </div>

        {trialInfo.daysRemaining !== undefined && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5 text-sm text-gray-700">
                <Clock size={16} />
                <span className="font-medium">Time:</span>
              </div>
              <span className="font-semibold text-gray-900 text-sm">
                {trialInfo.daysRemaining} day{trialInfo.daysRemaining !== 1 ? 's' : ''} left
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  trialInfo.daysRemaining === 0 ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{ width: `${daysPercent}%` }}
              />
            </div>
            {trialInfo.daysRemaining === 0 && (
              <p className="text-xs text-red-600 font-semibold mt-1">
                Trial period ended
              </p>
            )}
          </div>
        )}

        {(trialInfo.lessonsRemaining <= 2 || (trialInfo.daysRemaining !== undefined && trialInfo.daysRemaining <= 2)) && !trialInfo.isExpired && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <p className="text-xs text-gray-700 mb-2">
              Upgrade now to unlock unlimited lessons and premium features!
            </p>
            <button
              onClick={() => navigate('/get-started#pricing')}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-[#4CAF50] to-[#45a049] hover:from-[#45a049] hover:to-[#3d8b40] text-white px-4 py-2 rounded-lg font-semibold transition-all text-sm"
            >
              <TrendingUp size={16} />
              View Plans
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrialStatusBanner;
