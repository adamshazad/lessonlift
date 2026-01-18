/*
  # Fix Security Issues: RLS Performance and Function Search Path

  ## Summary
  Addresses critical security and performance issues identified by Supabase security scan:
  - Optimizes RLS policies to prevent per-row auth function re-evaluation
  - Secures database functions with explicit search_path
  - Ensures optimal query performance at scale

  ## Changes

  ### 1. RLS Policy Performance Optimization
  All RLS policies updated to use `(select auth.uid())` instead of `auth.uid()`.
  This evaluates the auth function once per query instead of once per row, significantly
  improving performance with large datasets.

  Affected tables:
  - `lessons` (3 policies)
  - `daily_lesson_counts` (1 policy)
  - `monthly_lesson_counts` (1 policy)

  ### 2. Function Security Hardening
  All database functions updated with explicit `SET search_path = public, auth`.
  This prevents search_path injection attacks by locking down the schema resolution.

  Affected functions (17 total):
  - get_daily_lesson_count
  - get_user_plan
  - check_and_increment_monthly_count
  - get_monthly_lesson_count
  - has_paid_plan
  - start_trial_if_needed
  - is_trial_expired_by_time
  - is_trial_exhausted
  - get_trial_status
  - check_and_increment_trial_usage
  - get_plan_daily_limit
  - get_plan_monthly_limit
  - get_plan_export_formats
  - check_and_increment_daily_count
  - set_user_subscription_plan
  - reset_plan_counters
  - get_user_subscription_status

  ## Performance Impact
  - Queries on tables with RLS will see significant performance improvements
  - Function execution is now protected against search_path manipulation

  ## Security Impact
  - Prevents potential SQL injection through search_path manipulation
  - Maintains all existing access controls while improving security posture
*/

-- ============================================================================
-- PART 1: FIX RLS POLICIES FOR PERFORMANCE
-- ============================================================================

-- Drop and recreate lessons table policies with optimized auth checks
DROP POLICY IF EXISTS "Users can read own lessons" ON lessons;
DROP POLICY IF EXISTS "Users can insert own lessons" ON lessons;
DROP POLICY IF EXISTS "Users can delete own lessons" ON lessons;

CREATE POLICY "Users can read own lessons"
  ON lessons FOR SELECT
  TO authenticated
  USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert own lessons"
  ON lessons FOR INSERT
  TO authenticated
  WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete own lessons"
  ON lessons FOR DELETE
  TO authenticated
  USING ((select auth.uid()) = user_id);

-- Fix daily_lesson_counts policies
DROP POLICY IF EXISTS "Users can view own daily counts" ON daily_lesson_counts;

CREATE POLICY "Users can view own daily counts"
  ON daily_lesson_counts
  FOR SELECT
  TO authenticated
  USING ((select auth.uid()) = user_id);

-- Fix monthly_lesson_counts policies
DROP POLICY IF EXISTS "Users can view own monthly counts" ON monthly_lesson_counts;

CREATE POLICY "Users can view own monthly counts"
  ON monthly_lesson_counts
  FOR SELECT
  TO authenticated
  USING ((select auth.uid()) = user_id);

-- ============================================================================
-- PART 2: SECURE FUNCTIONS WITH EXPLICIT SEARCH_PATH
-- ============================================================================

-- Fix get_user_plan function
CREATE OR REPLACE FUNCTION get_user_plan(p_user_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_plan text;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  IF v_has_plan THEN
    SELECT (raw_app_meta_data->>'subscription_plan')::text INTO v_plan
    FROM auth.users
    WHERE id = p_user_id;
    
    IF v_plan NOT IN ('starter', 'standard', 'pro') THEN
      RETURN 'trial';
    END IF;
    
    RETURN v_plan;
  ELSE
    RETURN 'trial';
  END IF;
END;
$$;

-- Fix has_paid_plan function
CREATE OR REPLACE FUNCTION has_paid_plan(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_plan text;
BEGIN
  SELECT (raw_app_meta_data->>'subscription_plan')::text INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;
  
  RETURN v_plan IN ('starter', 'standard', 'pro');
END;
$$;

-- Fix get_plan_daily_limit function
CREATE OR REPLACE FUNCTION get_plan_daily_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
SET search_path = public
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'trial' THEN 5
    WHEN 'starter' THEN 1
    WHEN 'standard' THEN 3
    WHEN 'pro' THEN 5
    ELSE 1
  END;
END;
$$;

-- Fix get_plan_monthly_limit function
CREATE OR REPLACE FUNCTION get_plan_monthly_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
SET search_path = public
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'trial' THEN 5
    WHEN 'starter' THEN 30
    WHEN 'standard' THEN 90
    WHEN 'pro' THEN 150
    ELSE 5
  END;
END;
$$;

-- Fix get_plan_export_formats function
CREATE OR REPLACE FUNCTION get_plan_export_formats(p_plan text)
RETURNS json
LANGUAGE plpgsql
IMMUTABLE
SET search_path = public
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'trial' THEN '["pdf"]'::json
    WHEN 'starter' THEN '["pdf"]'::json
    WHEN 'standard' THEN '["pdf", "docx"]'::json
    WHEN 'pro' THEN '["pdf", "docx", "txt"]'::json
    ELSE '["pdf"]'::json
  END;
END;
$$;

-- Fix check_and_increment_daily_count function
CREATE OR REPLACE FUNCTION check_and_increment_daily_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_daily_count integer;
  v_monthly_count integer;
  v_date date := CURRENT_DATE;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_daily_max integer;
  v_monthly_max integer;
BEGIN
  v_plan := get_user_plan(p_user_id);
  v_daily_max := get_plan_daily_limit(v_plan);
  v_monthly_max := get_plan_monthly_limit(v_plan);
  
  SELECT count INTO v_monthly_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;
  
  IF v_monthly_count IS NULL THEN
    v_monthly_count := 0;
  END IF;

  IF v_monthly_count >= v_monthly_max THEN
    RETURN json_build_object(
      'allowed', false,
      'current_count', v_monthly_count,
      'max_count', v_monthly_max,
      'plan', v_plan,
      'limit_type', 'monthly',
      'message', 'You have reached your monthly limit. Upgrade your plan to generate more lessons this month.'
    );
  END IF;
  
  INSERT INTO daily_lesson_counts (user_id, date, count)
  VALUES (p_user_id, v_date, 0)
  ON CONFLICT (user_id, date) DO NOTHING;

  SELECT count INTO v_daily_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_daily_count >= v_daily_max THEN
    RETURN json_build_object(
      'allowed', false,
      'current_count', v_daily_count,
      'max_count', v_daily_max,
      'plan', v_plan,
      'limit_type', 'daily',
      'message', 'You have reached your daily limit. Try again tomorrow or upgrade your plan for more lessons per day.',
      'monthly_current', v_monthly_count,
      'monthly_max', v_monthly_max
    );
  END IF;

  UPDATE daily_lesson_counts
  SET count = count + 1, updated_at = now()
  WHERE user_id = p_user_id AND date = v_date;

  INSERT INTO monthly_lesson_counts (user_id, year_month, count)
  VALUES (p_user_id, v_year_month, 1)
  ON CONFLICT (user_id, year_month) 
  DO UPDATE SET count = monthly_lesson_counts.count + 1, updated_at = now();

  RETURN json_build_object(
    'allowed', true,
    'current_count', v_daily_count + 1,
    'max_count', v_daily_max,
    'plan', v_plan,
    'remaining', v_daily_max - (v_daily_count + 1),
    'monthly_current', v_monthly_count + 1,
    'monthly_max', v_monthly_max,
    'monthly_remaining', v_monthly_max - (v_monthly_count + 1)
  );
END;
$$;

-- Fix get_daily_lesson_count function
CREATE OR REPLACE FUNCTION get_daily_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_daily_count integer;
  v_monthly_count integer;
  v_date date := CURRENT_DATE;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_daily_max integer;
  v_monthly_max integer;
BEGIN
  v_plan := get_user_plan(p_user_id);
  v_daily_max := get_plan_daily_limit(v_plan);
  v_monthly_max := get_plan_monthly_limit(v_plan);
  
  SELECT count INTO v_daily_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_daily_count IS NULL THEN
    v_daily_count := 0;
  END IF;

  SELECT count INTO v_monthly_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;

  IF v_monthly_count IS NULL THEN
    v_monthly_count := 0;
  END IF;

  RETURN json_build_object(
    'current_count', v_daily_count,
    'max_count', v_daily_max,
    'plan', v_plan,
    'remaining', v_daily_max - v_daily_count,
    'export_formats', get_plan_export_formats(v_plan),
    'monthly_current', v_monthly_count,
    'monthly_max', v_monthly_max,
    'monthly_remaining', v_monthly_max - v_monthly_count
  );
END;
$$;

-- Fix check_and_increment_monthly_count function
CREATE OR REPLACE FUNCTION check_and_increment_monthly_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_current_count integer;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_max_count integer;
BEGIN
  v_plan := get_user_plan(p_user_id);
  v_max_count := get_plan_monthly_limit(v_plan);
  
  INSERT INTO monthly_lesson_counts (user_id, year_month, count)
  VALUES (p_user_id, v_year_month, 0)
  ON CONFLICT (user_id, year_month) DO NOTHING;

  SELECT count INTO v_current_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;

  IF v_current_count >= v_max_count THEN
    RETURN json_build_object(
      'allowed', false,
      'current_count', v_current_count,
      'max_count', v_max_count,
      'plan', v_plan,
      'limit_type', 'monthly',
      'message', 'Monthly limit reached for your plan. Upgrade to generate more lessons this month.'
    );
  END IF;

  UPDATE monthly_lesson_counts
  SET count = count + 1, updated_at = now()
  WHERE user_id = p_user_id AND year_month = v_year_month;

  RETURN json_build_object(
    'allowed', true,
    'current_count', v_current_count + 1,
    'max_count', v_max_count,
    'plan', v_plan,
    'remaining', v_max_count - (v_current_count + 1)
  );
END;
$$;

-- Fix get_monthly_lesson_count function
CREATE OR REPLACE FUNCTION get_monthly_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_current_count integer;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_max_count integer;
BEGIN
  v_plan := get_user_plan(p_user_id);
  v_max_count := get_plan_monthly_limit(v_plan);
  
  SELECT count INTO v_current_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;

  IF v_current_count IS NULL THEN
    v_current_count := 0;
  END IF;

  RETURN json_build_object(
    'current_count', v_current_count,
    'max_count', v_max_count,
    'plan', v_plan,
    'remaining', v_max_count - v_current_count
  );
END;
$$;

-- Fix start_trial_if_needed function
CREATE OR REPLACE FUNCTION start_trial_if_needed(p_user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_trial_started timestamptz;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  IF v_has_plan THEN
    RETURN;
  END IF;

  SELECT (raw_app_meta_data->>'trial_started_at')::timestamptz INTO v_trial_started
  FROM auth.users
  WHERE id = p_user_id;

  IF v_trial_started IS NULL THEN
    UPDATE auth.users
    SET raw_app_meta_data = 
      COALESCE(raw_app_meta_data, '{}'::jsonb) || 
      jsonb_build_object(
        'trial_started_at', now(),
        'trial_lessons_used', 0
      )
    WHERE id = p_user_id;
  END IF;
END;
$$;

-- Fix is_trial_expired_by_time function
CREATE OR REPLACE FUNCTION is_trial_expired_by_time(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_trial_started timestamptz;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  IF v_has_plan THEN
    RETURN false;
  END IF;

  SELECT (raw_app_meta_data->>'trial_started_at')::timestamptz INTO v_trial_started
  FROM auth.users
  WHERE id = p_user_id;

  IF v_trial_started IS NULL THEN
    RETURN false;
  END IF;

  RETURN (now() - v_trial_started) > INTERVAL '7 days';
END;
$$;

-- Fix is_trial_exhausted function
CREATE OR REPLACE FUNCTION is_trial_exhausted(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_lessons_used integer;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  IF v_has_plan THEN
    RETURN false;
  END IF;

  SELECT COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0) INTO v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  RETURN v_lessons_used >= 5;
END;
$$;

-- Fix get_trial_status function
CREATE OR REPLACE FUNCTION get_trial_status(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_trial_started timestamptz;
  v_lessons_used integer;
  v_has_plan boolean;
  v_plan text;
  v_days_remaining integer;
  v_lessons_remaining integer;
  v_is_expired boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  SELECT COALESCE((raw_app_meta_data->>'subscription_plan')::text, 'trial') INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;

  IF v_has_plan THEN
    RETURN json_build_object(
      'is_trial', false,
      'has_paid_plan', true,
      'plan', v_plan
    );
  END IF;

  SELECT 
    (raw_app_meta_data->>'trial_started_at')::timestamptz,
    COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0)
  INTO v_trial_started, v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  IF v_trial_started IS NULL THEN
    RETURN json_build_object(
      'is_trial', true,
      'has_paid_plan', false,
      'trial_started', false,
      'lessons_used', 0,
      'lessons_remaining', 5,
      'lessons_total', 5,
      'is_expired', false,
      'plan', 'trial'
    );
  END IF;

  v_days_remaining := GREATEST(0, 7 - EXTRACT(day FROM (now() - v_trial_started))::integer);
  v_lessons_remaining := GREATEST(0, 5 - v_lessons_used);
  
  v_is_expired := is_trial_expired_by_time(p_user_id) OR is_trial_exhausted(p_user_id);

  RETURN json_build_object(
    'is_trial', true,
    'has_paid_plan', false,
    'trial_started', true,
    'trial_started_at', v_trial_started,
    'days_elapsed', LEAST(7, EXTRACT(day FROM (now() - v_trial_started))::integer),
    'days_remaining', v_days_remaining,
    'days_total', 7,
    'lessons_used', v_lessons_used,
    'lessons_remaining', v_lessons_remaining,
    'lessons_total', 5,
    'is_expired', v_is_expired,
    'expired_by_time', is_trial_expired_by_time(p_user_id),
    'expired_by_lessons', is_trial_exhausted(p_user_id),
    'plan', 'trial'
  );
END;
$$;

-- Fix check_and_increment_trial_usage function
CREATE OR REPLACE FUNCTION check_and_increment_trial_usage(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_has_plan boolean;
  v_lessons_used integer;
  v_trial_started timestamptz;
  v_is_expired_time boolean;
  v_is_exhausted boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  IF v_has_plan THEN
    RETURN json_build_object(
      'allowed', true,
      'is_trial', false,
      'has_paid_plan', true
    );
  END IF;

  PERFORM start_trial_if_needed(p_user_id);

  SELECT 
    (raw_app_meta_data->>'trial_started_at')::timestamptz,
    COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0)
  INTO v_trial_started, v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  v_is_expired_time := is_trial_expired_by_time(p_user_id);
  v_is_exhausted := is_trial_exhausted(p_user_id);

  IF v_is_expired_time THEN
    RETURN json_build_object(
      'allowed', false,
      'is_trial', true,
      'expired_by', 'time',
      'lessons_used', v_lessons_used,
      'message', 'Your 7-day free trial has ended. Upgrade to continue generating lesson plans.'
    );
  END IF;

  IF v_is_exhausted THEN
    RETURN json_build_object(
      'allowed', false,
      'is_trial', true,
      'expired_by', 'lessons',
      'lessons_used', v_lessons_used,
      'message', 'You have used all 5 trial lessons. Upgrade to continue generating lesson plans.'
    );
  END IF;

  UPDATE auth.users
  SET raw_app_meta_data = 
    raw_app_meta_data || 
    jsonb_build_object('trial_lessons_used', v_lessons_used + 1)
  WHERE id = p_user_id;

  RETURN json_build_object(
    'allowed', true,
    'is_trial', true,
    'lessons_used', v_lessons_used + 1,
    'lessons_remaining', 5 - (v_lessons_used + 1)
  );
END;
$$;

-- Fix set_user_subscription_plan function
CREATE OR REPLACE FUNCTION set_user_subscription_plan(
  p_user_id uuid,
  p_plan text
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_old_plan text;
  v_was_trial boolean;
BEGIN
  IF p_plan NOT IN ('starter', 'standard', 'pro') THEN
    RAISE EXCEPTION 'Invalid plan type. Must be starter, standard, or pro.';
  END IF;

  v_was_trial := NOT has_paid_plan(p_user_id);
  v_old_plan := get_user_plan(p_user_id);

  UPDATE auth.users
  SET raw_app_meta_data = 
    COALESCE(raw_app_meta_data, '{}'::jsonb) || 
    jsonb_build_object('subscription_plan', p_plan)
  WHERE id = p_user_id;

  IF v_was_trial THEN
    PERFORM reset_plan_counters(p_user_id);
  END IF;

  RETURN json_build_object(
    'success', true,
    'plan', p_plan,
    'previous_plan', v_old_plan,
    'upgraded_from_trial', v_was_trial
  );
END;
$$;

-- Fix reset_plan_counters function
CREATE OR REPLACE FUNCTION reset_plan_counters(p_user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  DELETE FROM daily_lesson_counts
  WHERE user_id = p_user_id;

  DELETE FROM monthly_lesson_counts
  WHERE user_id = p_user_id;
END;
$$;

-- Fix get_user_subscription_status function
CREATE OR REPLACE FUNCTION get_user_subscription_status(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_has_plan boolean;
  v_plan text;
  v_trial_status json;
  v_daily_count integer;
  v_monthly_count integer;
  v_daily_max integer;
  v_monthly_max integer;
  v_date date := CURRENT_DATE;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_export_formats json;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  v_plan := get_user_plan(p_user_id);
  v_export_formats := get_plan_export_formats(v_plan);

  IF NOT v_has_plan THEN
    v_trial_status := get_trial_status(p_user_id);
    
    RETURN v_trial_status || json_build_object(
      'export_formats', v_export_formats
    );
  END IF;

  v_daily_max := get_plan_daily_limit(v_plan);
  v_monthly_max := get_plan_monthly_limit(v_plan);
  
  SELECT COALESCE(count, 0) INTO v_daily_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  SELECT COALESCE(count, 0) INTO v_monthly_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;

  RETURN json_build_object(
    'is_trial', false,
    'has_paid_plan', true,
    'plan', v_plan,
    'current_count', v_daily_count,
    'max_count', v_daily_max,
    'remaining', v_daily_max - v_daily_count,
    'monthly_current', v_monthly_count,
    'monthly_max', v_monthly_max,
    'monthly_remaining', v_monthly_max - v_monthly_count,
    'export_formats', v_export_formats
  );
END;
$$;