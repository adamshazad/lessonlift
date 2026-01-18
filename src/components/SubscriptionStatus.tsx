import React, { useEffect, useState } from 'react';
import { Crown, Calendar, CreditCard } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';

interface SubscriptionData {
  is_trial: boolean;
  has_paid_plan: boolean;
  plan: string;
  current_count?: number;
  max_count?: number;
  remaining?: number;
  monthly_current?: number;
  monthly_max?: number;
  monthly_remaining?: number;
  lessons_used?: number;
  lessons_remaining?: number;
  days_remaining?: number;
  is_expired?: boolean;
}

export function SubscriptionStatus() {
  const { user } = useAuth();
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchSubscriptionData();
    }
  }, [user]);

  const fetchSubscriptionData = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase.rpc('get_user_subscription_status', {
        p_user_id: user.id
      });

      if (error) throw error;
      setSubscriptionData(data);
    } catch (error) {
      console.error('Error fetching subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !subscriptionData) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const getPlanDisplayName = (plan: string) => {
    switch (plan) {
      case 'starter': return 'Starter';
      case 'standard': return 'Standard';
      case 'pro': return 'Pro';
      case 'trial': return 'Free Trial';
      default: return 'Unknown';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'starter': return 'text-blue-600 bg-blue-50';
      case 'standard': return 'text-purple-600 bg-purple-50';
      case 'pro': return 'text-yellow-600 bg-yellow-50';
      case 'trial': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <Crown className="h-5 w-5 text-gray-400 mr-2" />
          <span className="font-medium text-gray-900">Current Plan</span>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPlanColor(subscriptionData.plan)}`}>
          {getPlanDisplayName(subscriptionData.plan)}
        </span>
      </div>

      {subscriptionData.is_trial ? (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Lessons Used</span>
            <span className="font-medium">
              {subscriptionData.lessons_used || 0} / 5
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Days Remaining</span>
            <span className="font-medium">
              {subscriptionData.days_remaining || 0}
            </span>
          </div>
          {subscriptionData.is_expired && (
            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              Your trial has expired. Upgrade to continue generating lessons.
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Today</span>
            <span className="font-medium">
              {subscriptionData.current_count || 0} / {subscriptionData.max_count || 0}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">This Month</span>
            <span className="font-medium">
              {subscriptionData.monthly_current || 0} / {subscriptionData.monthly_max || 0}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}