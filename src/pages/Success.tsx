import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';

export function Success() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [subscriptionData, setSubscriptionData] = useState<any>(null);

  useEffect(() => {
    if (user) {
      // Wait a moment for webhook to process, then fetch subscription data
      const timer = setTimeout(() => {
        fetchSubscriptionData();
      }, 2000);

      return () => clearTimeout(timer);
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

  const sessionId = searchParams.get('session_id');

  if (!user) {
    navigate('/auth');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
        {loading ? (
          <div className="space-y-4">
            <Loader2 className="h-16 w-16 text-indigo-600 animate-spin mx-auto" />
            <h1 className="text-2xl font-bold text-gray-900">
              Processing Your Subscription
            </h1>
            <p className="text-gray-600">
              Please wait while we set up your account...
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto" />
            
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Welcome to LessonLift!
              </h1>
              <p className="text-gray-600">
                Your subscription has been successfully activated.
              </p>
            </div>

            {subscriptionData && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Subscription Details
                </h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>Plan: <span className="font-medium capitalize">{subscriptionData.plan}</span></p>
                  <p>Daily Lessons: <span className="font-medium">{subscriptionData.max_count}</span></p>
                  <p>Monthly Lessons: <span className="font-medium">{subscriptionData.monthly_max}</span></p>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={() => navigate('/')}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
              >
                Start Creating Lessons
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
              
              <button
                onClick={() => navigate('/account')}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-lg transition-colors"
              >
                Manage Account
              </button>
            </div>

            {sessionId && (
              <p className="text-xs text-gray-400">
                Session ID: {sessionId}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}