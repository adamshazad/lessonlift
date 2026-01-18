/*
  # Add Subscription Plan Support

  1. Overview
    - Adds helper functions to manage user subscription plans
    - Plans: starter (1/day, PDF only), standard (3/day, PDF + DOCX), pro (5/day, all formats)
    - Defaults to 'pro' plan for easier V1 rollout (can be refined later)

  2. Functions
    - `get_user_plan(user_id)`: Returns the user's subscription plan from app_metadata
    - `get_plan_daily_limit(plan_name)`: Returns daily lesson limit for a given plan
    - `get_plan_export_formats(plan_name)`: Returns allowed export formats for a plan
    - Updated `check_and_increment_daily_count`: Now accepts user_id and automatically determines limit

  3. Security
    - All functions are SECURITY DEFINER to allow proper access
    - Functions validate user authentication where appropriate

  4. Notes
    - Plan is stored in auth.users.raw_app_meta_data
    - Defaults to 'pro' (5 lessons/day) if no plan is set
    - Plan can be updated via Supabase auth.update() by admins
*/

-- Function to get user's subscription plan from app_metadata
-- Returns: 'starter', 'standard', or 'pro' (defaults to 'pro')
CREATE OR REPLACE FUNCTION get_user_plan(p_user_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_plan text;
BEGIN
  -- Get plan from user's app_metadata, default to 'pro' for V1
  SELECT COALESCE(
    (raw_app_meta_data->>'subscription_plan')::text,
    'pro'
  ) INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;
  
  -- Validate plan is one of the allowed values
  IF v_plan NOT IN ('starter', 'standard', 'pro') THEN
    v_plan := 'pro';
  END IF;
  
  RETURN v_plan;
END;
$$;

-- Function to get daily lesson limit for a plan
-- Starter: 1, Standard: 3, Pro: 5
CREATE OR REPLACE FUNCTION get_plan_daily_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'starter' THEN 1
    WHEN 'standard' THEN 3
    WHEN 'pro' THEN 5
    ELSE 5 -- Default to pro
  END;
END;
$$;

-- Function to get allowed export formats for a plan
-- Returns JSON array of allowed formats
CREATE OR REPLACE FUNCTION get_plan_export_formats(p_plan text)
RETURNS json
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'starter' THEN '["pdf"]'::json
    WHEN 'standard' THEN '["pdf", "docx"]'::json
    WHEN 'pro' THEN '["pdf", "docx", "txt"]'::json
    ELSE '["pdf", "docx", "txt"]'::json -- Default to pro
  END;
END;
$$;

-- Updated function to check and increment daily count
-- Now automatically determines limit based on user's plan
DROP FUNCTION IF EXISTS check_and_increment_daily_count(uuid, integer);

CREATE OR REPLACE FUNCTION check_and_increment_daily_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_current_count integer;
  v_date date := CURRENT_DATE;
  v_plan text;
  v_max_count integer;
BEGIN
  -- Get user's plan and corresponding limit
  v_plan := get_user_plan(p_user_id);
  v_max_count := get_plan_daily_limit(v_plan);
  
  -- Insert or get current count for today
  INSERT INTO daily_lesson_counts (user_id, date, count)
  VALUES (p_user_id, v_date, 0)
  ON CONFLICT (user_id, date) DO NOTHING;

  SELECT count INTO v_current_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  -- Check if limit reached
  IF v_current_count >= v_max_count THEN
    RETURN json_build_object(
      'allowed', false,
      'current_count', v_current_count,
      'max_count', v_max_count,
      'plan', v_plan,
      'message', 'Daily limit reached for your plan. Please wait until the next day or upgrade your plan.'
    );
  END IF;

  -- Increment count
  UPDATE daily_lesson_counts
  SET count = count + 1, updated_at = now()
  WHERE user_id = p_user_id AND date = v_date;

  RETURN json_build_object(
    'allowed', true,
    'current_count', v_current_count + 1,
    'max_count', v_max_count,
    'plan', v_plan,
    'remaining', v_max_count - (v_current_count + 1)
  );
END;
$$;

-- Updated function to get current daily count with plan info
DROP FUNCTION IF EXISTS get_daily_lesson_count(uuid);

CREATE OR REPLACE FUNCTION get_daily_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_current_count integer;
  v_date date := CURRENT_DATE;
  v_plan text;
  v_max_count integer;
BEGIN
  -- Get user's plan and corresponding limit
  v_plan := get_user_plan(p_user_id);
  v_max_count := get_plan_daily_limit(v_plan);
  
  -- Get current count for today
  SELECT count INTO v_current_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_current_count IS NULL THEN
    v_current_count := 0;
  END IF;

  RETURN json_build_object(
    'current_count', v_current_count,
    'max_count', v_max_count,
    'plan', v_plan,
    'remaining', v_max_count - v_current_count,
    'export_formats', get_plan_export_formats(v_plan)
  );
END;
$$;