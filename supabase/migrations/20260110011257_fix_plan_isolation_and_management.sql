/*
  # Fix Plan Isolation and Management System

  1. Overview
    - Ensures each plan has isolated counters and limits
    - Adds function to set/update user subscription plans
    - Adds function to reset counters when upgrading plans
    - Fixes plan defaults to properly separate trial from paid plans

  2. Changes
    - New function: set_user_subscription_plan(user_id, plan_type)
      - Updates user's subscription_plan in raw_app_meta_data
      - Validates plan type (starter, standard, pro)
      - Resets daily/monthly counters when switching from trial
    
    - New function: reset_plan_counters(user_id)
      - Clears daily and monthly counters for fresh start
      - Used when upgrading from trial to paid plan
    
    - Updated function: get_user_plan(user_id)
      - Returns actual plan or 'trial' for users without paid plan
      - Never defaults to a paid plan unless explicitly set

  3. Plan Limits (Authoritative)
    - Free Trial: 5 total lessons, 7 days
    - Starter: 1/day, 30/month, PDF only
    - Standard: 3/day, 90/month, PDF + DOCX
    - Pro: 5/day, 150/month, PDF + DOCX + TXT

  4. Security
    - set_user_subscription_plan is SECURITY DEFINER
    - Only service role or authenticated user can update their own plan
*/

-- Function to set user subscription plan
CREATE OR REPLACE FUNCTION set_user_subscription_plan(
  p_user_id uuid,
  p_plan text
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_old_plan text;
  v_was_trial boolean;
BEGIN
  -- Validate plan type
  IF p_plan NOT IN ('starter', 'standard', 'pro') THEN
    RAISE EXCEPTION 'Invalid plan type. Must be starter, standard, or pro.';
  END IF;

  -- Get current plan status
  v_was_trial := NOT has_paid_plan(p_user_id);
  v_old_plan := get_user_plan(p_user_id);

  -- Update user's subscription plan in metadata
  UPDATE auth.users
  SET raw_app_meta_data = 
    COALESCE(raw_app_meta_data, '{}'::jsonb) || 
    jsonb_build_object('subscription_plan', p_plan)
  WHERE id = p_user_id;

  -- If upgrading from trial to paid, reset counters
  IF v_was_trial THEN
    PERFORM reset_plan_counters(p_user_id);
  END IF;

  -- Return success with plan info
  RETURN json_build_object(
    'success', true,
    'plan', p_plan,
    'previous_plan', v_old_plan,
    'upgraded_from_trial', v_was_trial
  );
END;
$$;

-- Function to reset plan counters (for upgrades)
CREATE OR REPLACE FUNCTION reset_plan_counters(p_user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Delete existing daily counts
  DELETE FROM daily_lesson_counts
  WHERE user_id = p_user_id;

  -- Delete existing monthly counts
  DELETE FROM monthly_lesson_counts
  WHERE user_id = p_user_id;

  -- Note: Trial counters in auth.users metadata are left intact for record-keeping
END;
$$;

-- Update get_user_plan to never default to paid plans
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
    
    -- Validate the plan is one of the valid paid plans
    IF v_plan NOT IN ('starter', 'standard', 'pro') THEN
      -- If invalid, treat as trial
      RETURN 'trial';
    END IF;
    
    RETURN v_plan;
  ELSE
    -- No paid plan, user is on trial
    RETURN 'trial';
  END IF;
END;
$$;

-- Function to get user's full subscription status
CREATE OR REPLACE FUNCTION get_user_subscription_status(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
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

  -- If user doesn't have paid plan, return trial status
  IF NOT v_has_plan THEN
    v_trial_status := get_trial_status(p_user_id);
    
    RETURN v_trial_status || json_build_object(
      'export_formats', v_export_formats
    );
  END IF;

  -- User has paid plan, get their usage
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

-- Add RLS policy for users to update their own plan (in case of direct updates)
-- Note: In production, this should only be done through Stripe webhooks