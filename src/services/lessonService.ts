import { supabase } from '../contexts/AuthContext';

export interface LessonRequest {
  yearGroup: string;
  abilityLevel: string;
  lessonDuration: number;
  subject: string;
  topic: string;
  learningObjective?: string;
  senEalNotes?: string;
  regenerationInstruction?: string;
}

export interface Lesson {
  id: string;
  user_id: string;
  year_group: string;
  ability_level: string;
  lesson_duration: number;
  subject: string;
  topic: string;
  learning_objective?: string;
  sen_eal_notes?: string;
  regeneration_instruction?: string;
  lesson_content: string;
  lesson_text: string;
  created_at: string;
}

export interface GenerateLessonResponse {
  success: boolean;
  lesson?: any;
  error?: string;
  limitReached?: boolean;
  isTrial?: boolean;
  trialExpired?: boolean;
  expiredBy?: 'time' | 'lessons';
  lessonsUsed?: number;
  limitType?: 'daily' | 'monthly';
  currentCount?: number;
  maxCount?: number;
  monthlyCount?: number;
  monthlyMax?: number;
  plan?: 'starter' | 'standard' | 'pro';
  usage?: any;
}

export async function generateLesson(request: LessonRequest): Promise<GenerateLessonResponse> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      throw new Error('Not authenticated');
    }

    const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/generate-lesson`;
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Edge function error:', data);
      const errorResponse: GenerateLessonResponse = {
        success: false,
        error: data.error || `Request failed with status ${response.status}`,
        limitReached: data.limitReached || false,
        isTrial: data.isTrial,
      };

      if (data.isTrial) {
        errorResponse.trialExpired = data.trialExpired;
        errorResponse.expiredBy = data.expiredBy;
        errorResponse.lessonsUsed = data.lessonsUsed;
      } else {
        errorResponse.limitType = data.limitType;
        errorResponse.currentCount = data.currentCount;
        errorResponse.maxCount = data.maxCount;
        errorResponse.monthlyCount = data.monthlyCount;
        errorResponse.monthlyMax = data.monthlyMax;
        errorResponse.plan = data.plan;
      }

      return errorResponse;
    }

    return data;
  } catch (error: any) {
    console.error('Generate lesson error:', error);
    return { success: false, error: error.message || 'An unexpected error occurred' };
  }
}

export async function fetchLessonHistory(): Promise<Lesson[]> {
  try {
    const { data, error } = await supabase
      .from('lessons')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(20);

    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching lesson history:', error);
    return [];
  }
}

export async function deleteLesson(lessonId: string): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('lessons')
      .delete()
      .eq('id', lessonId);

    if (error) throw error;
    return true;
  } catch (error) {
    console.error('Error deleting lesson:', error);
    return false;
  }
}

export interface TrialInfo {
  isTrial: true;
  hasPaidPlan: false;
  trialStarted: boolean;
  trialStartedAt?: string;
  daysElapsed?: number;
  daysRemaining?: number;
  daysTotal: number;
  lessonsUsed: number;
  lessonsRemaining: number;
  lessonsTotal: number;
  isExpired: boolean;
  expiredByTime?: boolean;
  expiredByLessons?: boolean;
  plan: 'trial';
  exportFormats: string[];
}

export interface PaidPlanInfo {
  isTrial: false;
  hasPaidPlan: true;
  dailyCount: number;
  dailyMax: number;
  dailyRemaining: number;
  monthlyCount: number;
  monthlyMax: number;
  monthlyRemaining: number;
  plan: 'starter' | 'standard' | 'pro';
  exportFormats: string[];
}

export type UsageInfo = TrialInfo | PaidPlanInfo;

export async function getUsageInfo(): Promise<UsageInfo | null> {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    const { data, error } = await supabase.rpc('get_user_subscription_status', {
      p_user_id: user.id
    });

    if (error) throw error;

    if (data.is_trial) {
      const trialInfo: TrialInfo = {
        isTrial: true,
        hasPaidPlan: false,
        trialStarted: data.trial_started,
        trialStartedAt: data.trial_started_at,
        daysElapsed: data.days_elapsed,
        daysRemaining: data.days_remaining,
        daysTotal: data.days_total || 7,
        lessonsUsed: data.lessons_used,
        lessonsRemaining: data.lessons_remaining,
        lessonsTotal: data.lessons_total || 5,
        isExpired: data.is_expired,
        expiredByTime: data.expired_by_time,
        expiredByLessons: data.expired_by_lessons,
        plan: 'trial',
        exportFormats: data.export_formats,
      };
      return trialInfo;
    } else {
      const paidInfo: PaidPlanInfo = {
        isTrial: false,
        hasPaidPlan: true,
        dailyCount: data.current_count,
        dailyMax: data.max_count,
        dailyRemaining: data.remaining,
        monthlyCount: data.monthly_current,
        monthlyMax: data.monthly_max,
        monthlyRemaining: data.monthly_remaining,
        plan: data.plan,
        exportFormats: data.export_formats,
      };
      return paidInfo;
    }
  } catch (error) {
    console.error('Error fetching usage info:', error);
    return null;
  }
}
