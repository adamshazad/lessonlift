/*
  # Add Daily Lesson Limit Tracking

  1. New Tables
    - `daily_lesson_counts`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `date` (date)
      - `count` (integer, default 0)
      - `created_at` (timestamptz, default now())
      - `updated_at` (timestamptz, default now())

  2. Indexes
    - Unique index on (user_id, date) for efficient lookups and preventing duplicates

  3. Security
    - Enable RLS on `daily_lesson_counts` table
    - Add policy for users to read their own daily counts
    - Add policy for service role to manage counts

  4. Functions
    - Function to check and increment daily lesson count
    - Function to get current daily count for a user
*/

CREATE TABLE IF NOT EXISTS daily_lesson_counts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date date NOT NULL DEFAULT CURRENT_DATE,
  count integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS daily_lesson_counts_user_date_idx 
  ON daily_lesson_counts(user_id, date);

ALTER TABLE daily_lesson_counts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own daily counts"
  ON daily_lesson_counts
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all counts"
  ON daily_lesson_counts
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE OR REPLACE FUNCTION check_and_increment_daily_count(p_user_id uuid, p_max_count integer DEFAULT 10)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_current_count integer;
  v_date date := CURRENT_DATE;
BEGIN
  INSERT INTO daily_lesson_counts (user_id, date, count)
  VALUES (p_user_id, v_date, 0)
  ON CONFLICT (user_id, date) DO NOTHING;

  SELECT count INTO v_current_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_current_count >= p_max_count THEN
    RETURN json_build_object(
      'allowed', false,
      'current_count', v_current_count,
      'max_count', p_max_count,
      'message', 'Daily lesson limit reached'
    );
  END IF;

  UPDATE daily_lesson_counts
  SET count = count + 1, updated_at = now()
  WHERE user_id = p_user_id AND date = v_date;

  RETURN json_build_object(
    'allowed', true,
    'current_count', v_current_count + 1,
    'max_count', p_max_count,
    'remaining', p_max_count - (v_current_count + 1)
  );
END;
$$;

CREATE OR REPLACE FUNCTION get_daily_lesson_count(p_user_id uuid)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_current_count integer;
  v_date date := CURRENT_DATE;
  v_max_count integer := 10;
BEGIN
  SELECT count INTO v_current_count
  FROM daily_lesson_counts
  WHERE user_id = p_user_id AND date = v_date;

  IF v_current_count IS NULL THEN
    v_current_count := 0;
  END IF;

  RETURN json_build_object(
    'current_count', v_current_count,
    'max_count', v_max_count,
    'remaining', v_max_count - v_current_count
  );
END;
$$;
