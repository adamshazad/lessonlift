/*
  # Add Free Trial System

  1. Overview
    - Implements a 7-day free trial with 5 total lesson limit
    - Trial starts on first lesson generation
    - No daily reset during trial
    - Server-side enforcement to prevent abuse
    - Trial is bypassed for users with paid plans

  2. Changes to auth.users metadata
    - Uses raw_app_meta_data to store:
      - trial_started_at: timestamp when trial began
      - trial_lessons_used: total lessons used during trial
      - subscription_plan: 'starter', 'standard', 'pro', or null (trial)

  3. New Functions
    - is_trial_active(user_id): Checks if user is in active trial
    - is_trial_expired(user_id): Checks if trial has expired
    - check_trial_limit(user_id): Checks if trial lessons exhausted
    - get_trial_status(user_id): Returns complete trial information
    - start_trial_if_needed(user_id): Initializes trial on first use
    - increment_trial_usage(user_id): Increments trial lesson count

  4. Trial Logic
    - Trial is active if: trial_started_at is set AND subscription_plan is null
    - Trial is expired if: 7 days passed OR 5 lessons used
    - Paid users (with subscription_plan) bypass all trial checks
*/

-- Function to check if user has a paid plan
CREATE OR REPLACE FUNCTION has_paid_plan(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_plan text;
BEGIN
  SELECT (raw_app_meta_data->>'subscription_plan')::text INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;
  
  -- User has paid plan if subscription_plan is set to starter, standard, or pro
  RETURN v_plan IN ('starter', 'standard', 'pro');
END;
$$;

-- Function to start trial if this is user's first lesson
CREATE OR REPLACE FUNCTION start_trial_if_needed(p_user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_trial_started timestamptz;
  v_has_plan boolean;
BEGIN
  -- Check if user has a paid plan
  v_has_plan := has_paid_plan(p_user_id);
  
  -- Don't start trial for paid users
  IF v_has_plan THEN
    RETURN;
  END IF;

  -- Check if trial already started
  SELECT (raw_app_meta_data->>'trial_started_at')::timestamptz INTO v_trial_started
  FROM auth.users
  WHERE id = p_user_id;

  -- If trial not started, initialize it now
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

-- Function to check if trial is expired (by time)
CREATE OR REPLACE FUNCTION is_trial_expired_by_time(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_trial_started timestamptz;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  -- Paid users don't have trial expiration
  IF v_has_plan THEN
    RETURN false;
  END IF;

  SELECT (raw_app_meta_data->>'trial_started_at')::timestamptz INTO v_trial_started
  FROM auth.users
  WHERE id = p_user_id;

  -- No trial started yet means not expired
  IF v_trial_started IS NULL THEN
    RETURN false;
  END IF;

  -- Check if 7 days have passed
  RETURN (now() - v_trial_started) > INTERVAL '7 days';
END;
$$;

-- Function to check if trial lessons are exhausted
CREATE OR REPLACE FUNCTION is_trial_exhausted(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_lessons_used integer;
  v_has_plan boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  -- Paid users don't have trial exhaustion
  IF v_has_plan THEN
    RETURN false;
  END IF;

  SELECT COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0) INTO v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  -- Trial exhausted if 5 or more lessons used
  RETURN v_lessons_used >= 5;
END;
$$;

-- Function to get complete trial status
CREATE OR REPLACE FUNCTION get_trial_status(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
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
  
  -- Get plan name
  SELECT COALESCE((raw_app_meta_data->>'subscription_plan')::text, 'trial') INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;

  -- If user has paid plan, return plan info without trial details
  IF v_has_plan THEN
    RETURN json_build_object(
      'is_trial', false,
      'has_paid_plan', true,
      'plan', v_plan
    );
  END IF;

  -- Get trial data
  SELECT 
    (raw_app_meta_data->>'trial_started_at')::timestamptz,
    COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0)
  INTO v_trial_started, v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  -- If trial not started
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

  -- Calculate days remaining
  v_days_remaining := GREATEST(0, 7 - EXTRACT(day FROM (now() - v_trial_started))::integer);
  v_lessons_remaining := GREATEST(0, 5 - v_lessons_used);
  
  -- Check if expired
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

-- Function to check and increment trial usage
CREATE OR REPLACE FUNCTION check_and_increment_trial_usage(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_has_plan boolean;
  v_lessons_used integer;
  v_trial_started timestamptz;
  v_is_expired_time boolean;
  v_is_exhausted boolean;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  -- Paid users bypass trial checks
  IF v_has_plan THEN
    RETURN json_build_object(
      'allowed', true,
      'is_trial', false,
      'has_paid_plan', true
    );
  END IF;

  -- Start trial if this is first lesson
  PERFORM start_trial_if_needed(p_user_id);

  -- Get current trial data
  SELECT 
    (raw_app_meta_data->>'trial_started_at')::timestamptz,
    COALESCE((raw_app_meta_data->>'trial_lessons_used')::integer, 0)
  INTO v_trial_started, v_lessons_used
  FROM auth.users
  WHERE id = p_user_id;

  -- Check if trial expired by time
  v_is_expired_time := is_trial_expired_by_time(p_user_id);
  
  -- Check if trial exhausted by lessons
  v_is_exhausted := is_trial_exhausted(p_user_id);

  -- If trial expired or exhausted, block generation
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

  -- Increment trial lesson count
  UPDATE auth.users
  SET raw_app_meta_data = 
    raw_app_meta_data || 
    jsonb_build_object('trial_lessons_used', v_lessons_used + 1)
  WHERE id = p_user_id;

  -- Return success
  RETURN json_build_object(
    'allowed', true,
    'is_trial', true,
    'lessons_used', v_lessons_used + 1,
    'lessons_remaining', 5 - (v_lessons_used + 1)
  );
END;
$$;

-- Update get_user_plan to return 'trial' for users without a paid plan
CREATE OR REPLACE FUNCTION get_user_plan(p_user_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
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
    
    RETURN v_plan;
  ELSE
    RETURN 'trial';
  END IF;
END;
$$;

-- Update get_plan_daily_limit to handle trial
CREATE OR REPLACE FUNCTION get_plan_daily_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'trial' THEN 5  -- Trial has total limit, not daily
    WHEN 'starter' THEN 1
    WHEN 'standard' THEN 3
    WHEN 'pro' THEN 5
    ELSE 1
  END;
END;
$$;

-- Update get_plan_monthly_limit to handle trial
CREATE OR REPLACE FUNCTION get_plan_monthly_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'trial' THEN 5  -- Trial has total limit, not monthly
    WHEN 'starter' THEN 30
    WHEN 'standard' THEN 90
    WHEN 'pro' THEN 150
    ELSE 5
  END;
END;
$$;

-- Update get_plan_export_formats to handle trial
CREATE OR REPLACE FUNCTION get_plan_export_formats(p_plan text)
RETURNS json
LANGUAGE plpgsql
IMMUTABLE
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
