/*
  # Add Monthly Lesson Limits and Update Plan Defaults

  1. Overview
    - Adds monthly lesson limit tracking alongside existing daily limits
    - Updates plan limits to match requirements:
      - Starter: 1/day, 30/month, PDF only
      - Standard: 3/day, 90/month, PDF + DOCX
      - Pro: 5/day, 150/month, PDF + DOCX + TXT
    - Changes default plan from 'pro' to 'starter' for new users

  2. New Tables
    - `monthly_lesson_counts`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `year_month` (text, format: 'YYYY-MM')
      - `count` (integer, default 0)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)

  3. New Functions
    - `get_plan_monthly_limit(plan)`: Returns monthly limit for a plan
    - `check_and_increment_monthly_count(user_id)`: Checks and increments monthly count
    - `get_monthly_lesson_count(user_id)`: Gets current monthly count
    - Updated `get_user_plan`: Now defaults to 'starter' instead of 'pro'
    - Updated `check_and_increment_daily_count`: Returns more detailed limit info

  4. Security
    - Enable RLS on monthly_lesson_counts table
    - Policies for users to view their own counts
    - Service role can manage all counts
*/

-- Create monthly lesson counts table
CREATE TABLE IF NOT EXISTS monthly_lesson_counts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  year_month text NOT NULL,
  count integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS monthly_lesson_counts_user_month_idx 
  ON monthly_lesson_counts(user_id, year_month);

ALTER TABLE monthly_lesson_counts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own monthly counts"
  ON monthly_lesson_counts
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage monthly counts"
  ON monthly_lesson_counts
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Function to get monthly lesson limit for a plan
CREATE OR REPLACE FUNCTION get_plan_monthly_limit(p_plan text)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  RETURN CASE p_plan
    WHEN 'starter' THEN 30
    WHEN 'standard' THEN 90
    WHEN 'pro' THEN 150
    ELSE 30 -- Default to starter
  END;
END;
$$;

-- Update get_user_plan to default to 'starter' instead of 'pro'
CREATE OR REPLACE FUNCTION get_user_plan(p_user_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_plan text;
BEGIN
  SELECT COALESCE(
    (raw_app_meta_data->>'subscription_plan')::text,
    'starter'  -- Changed from 'pro' to 'starter'
  ) INTO v_plan
  FROM auth.users
  WHERE id = p_user_id;
  
  IF v_plan NOT IN ('starter', 'standard', 'pro') THEN
    v_plan := 'starter';
  END IF;
  
  RETURN v_plan;
END;
$$;

-- Function to check and increment monthly count
CREATE OR REPLACE FUNCTION check_and_increment_monthly_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
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

-- Function to get current monthly count
CREATE OR REPLACE FUNCTION get_monthly_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
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

-- Update the combined usage function to include monthly limits
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

-- Update check_and_increment_daily_count to also return monthly info and specify limit type
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
BEGIN
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
