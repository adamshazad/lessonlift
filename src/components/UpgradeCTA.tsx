import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, TrendingUp, Clock, FileText } from 'lucide-react';

interface UpgradeCTAProps {
  isTrial?: boolean;
  trialExpired?: boolean;
  expiredBy?: 'time' | 'lessons';
  lessonsUsed?: number;
  limitType?: 'daily' | 'monthly';
  currentPlan?: 'starter' | 'standard' | 'pro';
  currentCount?: number;
  maxCount?: number;
}

const UpgradeCTA: React.FC<UpgradeCTAProps> = ({
  isTrial,
  trialExpired,
  expiredBy,
  lessonsUsed,
  limitType,
  currentPlan,
  currentCount,
  maxCount
}) => {
  const navigate = useNavigate();

  if (isTrial && trialExpired) {
    return (
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 mt-1">
            <AlertCircle className="w-6 h-6 text-red-600" />
          </div>
          <div className="flex-grow">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Free Trial Ended
            </h3>
            <div className="mb-3">
              {expiredBy === 'time' && (
                <div className="flex items-center gap-2 text-gray-700 mb-2">
                  <Clock size={18} className="text-red-500" />
                  <p>Your 7-day free trial has expired.</p>
                </div>
              )}
              {expiredBy === 'lessons' && (
                <div className="flex items-center gap-2 text-gray-700 mb-2">
                  <FileText size={18} className="text-red-500" />
                  <p>You have used all 5 trial lesson plans.</p>
                </div>
              )}
              <p className="text-gray-700 mt-2">
                {lessonsUsed !== undefined && (
                  <span className="font-medium">Total lessons generated: {lessonsUsed}</span>
                )}
              </p>
            </div>
            <p className="text-gray-800 font-medium mb-4">
              Upgrade to a paid plan to continue generating professional lesson plans and unlock premium features.
            </p>
            <button
              onClick={() => navigate('/get-started#pricing')}
              className="flex items-center gap-2 bg-gradient-to-r from-[#4CAF50] to-[#45a049] hover:from-[#45a049] hover:to-[#3d8b40] text-white px-6 py-3 rounded-lg font-bold transition-all duration-300 shadow-md hover:shadow-lg"
            >
              <TrendingUp size={20} />
              View Plans & Upgrade
            </button>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-red-200">
          <h4 className="font-semibold text-gray-900 mb-3">Choose Your Plan</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-white border-2 border-gray-200">
              <div className="font-semibold text-gray-900 mb-1">Starter</div>
              <div className="text-sm text-gray-600">1 lesson/day</div>
              <div className="text-sm text-gray-600">30 lessons/month</div>
              <div className="text-sm text-gray-600">PDF export only</div>
            </div>
            <div className="p-4 rounded-lg bg-white border-2 border-green-300">
              <div className="font-semibold text-gray-900 mb-1">Standard</div>
              <div className="text-sm text-gray-600">3 lessons/day</div>
              <div className="text-sm text-gray-600">90 lessons/month</div>
              <div className="text-sm text-gray-600">PDF + DOCX exports</div>
              <div className="text-xs text-green-600 font-semibold mt-1">POPULAR</div>
            </div>
            <div className="p-4 rounded-lg bg-white border-2 border-gray-200">
              <div className="font-semibold text-gray-900 mb-1">Pro</div>
              <div className="text-sm text-gray-600">5 lessons/day</div>
              <div className="text-sm text-gray-600">150 lessons/month</div>
              <div className="text-sm text-gray-600">All export formats</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const getResetTime = () => {
    if (limitType === 'daily') {
      return 'tomorrow';
    } else {
      const now = new Date();
      const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
      return `on ${nextMonth.toLocaleDateString('en-GB', { day: 'numeric', month: 'long' })}`;
    }
  };

  const getUpgradeMessage = () => {
    if (currentPlan === 'starter') {
      return 'Upgrade to Standard or Pro to generate more lessons and unlock additional export formats.';
    } else if (currentPlan === 'standard') {
      return 'Upgrade to Pro to generate even more lessons and unlock all export formats.';
    }
    return 'You are already on the Pro plan with maximum limits.';
  };

  const canUpgrade = currentPlan !== 'pro';

  return (
    <div className="bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-200 rounded-xl p-6 mb-6">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 mt-1">
          <AlertCircle className="w-6 h-6 text-orange-600" />
        </div>
        <div className="flex-grow">
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {limitType === 'daily' ? 'Daily' : 'Monthly'} Limit Reached
          </h3>
          <p className="text-gray-700 mb-3">
            You have used <strong>{currentCount} of {maxCount}</strong> lessons on your{' '}
            <strong className="capitalize">{currentPlan}</strong> plan this {limitType === 'daily' ? 'day' : 'month'}.
          </p>
          <p className="text-gray-600 text-sm mb-4">
            Your limit will reset {getResetTime()}.
          </p>
          {canUpgrade && (
            <>
              <p className="text-gray-800 font-medium mb-4">
                {getUpgradeMessage()}
              </p>
              <button
                onClick={() => navigate('/get-started#pricing')}
                className="flex items-center gap-2 bg-gradient-to-r from-[#4CAF50] to-[#45a049] hover:from-[#45a049] hover:to-[#3d8b40] text-white px-6 py-3 rounded-lg font-bold transition-all duration-300 shadow-md hover:shadow-lg"
              >
                <TrendingUp size={20} />
                Upgrade Your Plan
              </button>
            </>
          )}
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-orange-200">
        <h4 className="font-semibold text-gray-900 mb-3">Plan Comparison</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`p-4 rounded-lg ${currentPlan === 'starter' ? 'bg-white border-2 border-orange-300' : 'bg-white/60'}`}>
            <div className="font-semibold text-gray-900 mb-1">Starter</div>
            <div className="text-sm text-gray-600">1 lesson/day</div>
            <div className="text-sm text-gray-600">30 lessons/month</div>
            <div className="text-sm text-gray-600">PDF export only</div>
          </div>
          <div className={`p-4 rounded-lg ${currentPlan === 'standard' ? 'bg-white border-2 border-orange-300' : 'bg-white/60'}`}>
            <div className="font-semibold text-gray-900 mb-1">Standard</div>
            <div className="text-sm text-gray-600">3 lessons/day</div>
            <div className="text-sm text-gray-600">90 lessons/month</div>
            <div className="text-sm text-gray-600">PDF + DOCX exports</div>
          </div>
          <div className={`p-4 rounded-lg ${currentPlan === 'pro' ? 'bg-white border-2 border-orange-300' : 'bg-white/60'}`}>
            <div className="font-semibold text-gray-900 mb-1">Pro</div>
            <div className="text-sm text-gray-600">5 lessons/day</div>
            <div className="text-sm text-gray-600">150 lessons/month</div>
            <div className="text-sm text-gray-600">All export formats</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpgradeCTA;
