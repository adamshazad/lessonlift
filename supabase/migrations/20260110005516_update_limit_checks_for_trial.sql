/*
  # Update Limit Checks to Support Trial System

  1. Overview
    - Modifies check_and_increment_daily_count to check trial first
    - Trial users use trial limits (5 total lessons, 7 days)
    - Paid plan users use daily/monthly limits as before
    - Updates get_daily_lesson_count to include trial information

  2. Changes
    - check_and_increment_daily_count now checks trial before plan limits
    - get_daily_lesson_count returns trial info for trial users
*/

-- Update check_and_increment_daily_count to check trial first
CREATE OR REPLACE FUNCTION check_and_increment_daily_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_daily_count integer;
  v_monthly_count integer;
  v_date date := CURRENT_DATE;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_daily_max integer;
  v_monthly_max integer;
  v_has_plan boolean;
  v_trial_check json;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  -- If user doesn't have a paid plan, check trial limits
  IF NOT v_has_plan THEN
    v_trial_check := check_and_increment_trial_usage(p_user_id);
    
    -- If trial check says not allowed, return that
    IF NOT (v_trial_check->>'allowed')::boolean THEN
      RETURN v_trial_check;
    END IF;
    
    -- If trial allows it, return success with trial info
    RETURN v_trial_check;
  END IF;

  -- User has paid plan, use regular daily/monthly limits
  v_plan := get_user_plan(p_user_id);
  v_daily_max := get_plan_daily_limit(v_plan);
  v_monthly_max := get_plan_monthly_limit(v_plan);
  
  -- Check monthly limit first
  SELECT count INTO v_monthly_count
  FROM monthly_lesson_counts
  WHERE user_id = p_user_id AND year_month = v_year_month;
  
  IF v_monthly_count IS NULL THEN
    v_monthly_count := 0;
  END IF;

  IF v_monthly_count >= v_monthly_max THEN
    RETURN json_build_object(
      'allowed', false,
      'is_trial', false,
      'current_count', v_monthly_count,
      'max_count', v_monthly_max,
      'plan', v_plan,
      'limit_type', 'monthly',
      'message', 'You have reached your monthly limit. Upgrade your plan to generate more lessons this month.'
    );
  END IF;
  
  -- Check daily limit
  INSERT INTO daily_lesson_counts (user_id, date, count)
  VALUES (p_user_id, v_date, 0)
  ON CONFLICT (user_id, date) DO NOTHING;

  SELECT count INTO v_daily_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_daily_count >= v_daily_max THEN
    RETURN json_build_object(
      'allowed', false,
      'is_trial', false,
      'current_count', v_daily_count,
      'max_count', v_daily_max,
      'plan', v_plan,
      'limit_type', 'daily',
      'message', 'You have reached your daily limit. Try again tomorrow or upgrade your plan for more lessons per day.',
      'monthly_current', v_monthly_count,
      'monthly_max', v_monthly_max
    );
  END IF;

  -- Increment both counts
  UPDATE daily_lesson_counts
  SET count = count + 1, updated_at = now()
  WHERE user_id = p_user_id AND date = v_date;

  INSERT INTO monthly_lesson_counts (user_id, year_month, count)
  VALUES (p_user_id, v_year_month, 1)
  ON CONFLICT (user_id, year_month) 
  DO UPDATE SET count = monthly_lesson_counts.count + 1, updated_at = now();

  RETURN json_build_object(
    'allowed', true,
    'is_trial', false,
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

-- Update get_daily_lesson_count to include trial information
CREATE OR REPLACE FUNCTION get_daily_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_daily_count integer;
  v_monthly_count integer;
  v_date date := CURRENT_DATE;
  v_year_month text := to_char(CURRENT_DATE, 'YYYY-MM');
  v_plan text;
  v_daily_max integer;
  v_monthly_max integer;
  v_has_plan boolean;
  v_trial_status json;
BEGIN
  v_has_plan := has_paid_plan(p_user_id);
  
  -- If user doesn't have paid plan, return trial status
  IF NOT v_has_plan THEN
    v_trial_status := get_trial_status(p_user_id);
    
    RETURN v_trial_status || json_build_object(
      'export_formats', get_plan_export_formats('trial')
    );
  END IF;

  -- User has paid plan, return regular usage info
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
    'is_trial', false,
    'has_paid_plan', true,
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
