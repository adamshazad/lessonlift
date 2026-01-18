import React from 'react';
import { X, Crown, Calendar, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface LimitReachedModalProps {
  isOpen: boolean;
  onClose: () => void;
  limitInfo?: {
    is_trial: boolean;
    is_expired: boolean;
    limit_type: string;
    current_count: number;
    limit: number;
  };
}

export function LimitReachedModal({ isOpen, onClose, limitInfo }: LimitReachedModalProps) {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleUpgrade = () => {
    onClose();
    navigate('/pricing');
  };

  const isTrialExpired = limitInfo?.is_trial && limitInfo?.is_expired;
  const isMonthlyLimit = limitInfo?.limit_type === 'monthly';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {isTrialExpired ? 'Trial Expired' : 'Limit Reached'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-6">
          {isTrialExpired ? (
            <div className="flex items-start space-x-3">
              <Crown className="h-6 w-6 text-yellow-500 mt-1" />
              <div>
                <p className="text-gray-700 mb-2">
                  Your free trial has expired. Upgrade to continue using all features.
                </p>
              </div>
            </div>
          ) : isMonthlyLimit ? (
            <div className="flex items-start space-x-3">
              <Calendar className="h-6 w-6 text-blue-500 mt-1" />
              <div>
                <p className="text-gray-700 mb-2">
                  You've reached your monthly limit of {limitInfo?.limit} items.
                </p>
                <p className="text-sm text-gray-600">
                  Upgrade your plan to increase your monthly limits.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-start space-x-3">
              <div>
                <p className="text-gray-700 mb-2">
                  You've reached your usage limit.
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors border border-gray-300 rounded-lg"
            >
              Close
            </button>
            {(isTrialExpired || isMonthlyLimit) && (
              <button
                onClick={handleUpgrade}
                className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors flex items-center"
              >
                Upgrade Plan
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}