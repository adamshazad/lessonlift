/*
  # Create Lessons Table

  ## Summary
  Creates a comprehensive lessons table to store all generated lesson plans with full metadata and content.

  ## New Tables
    - `lessons`
      - `id` (uuid, primary key) - Unique identifier for each lesson
      - `user_id` (uuid, foreign key) - References auth.users, tracks lesson owner
      - `year_group` (text) - Year group selection (Year 1-6)
      - `ability_level` (text) - Ability level (Mixed, Lower, Higher)
      - `lesson_duration` (integer) - Duration in minutes (30, 45, 60)
      - `subject` (text) - Subject area
      - `topic` (text) - Lesson topic
      - `learning_objective` (text, nullable) - Optional learning objective
      - `sen_eal_notes` (text, nullable) - Optional SEN/EAL notes
      - `regeneration_instruction` (text, nullable) - Regeneration prompt if applicable
      - `lesson_content` (text) - Full generated lesson HTML content
      - `lesson_text` (text) - Plain text version of lesson
      - `created_at` (timestamptz) - Creation timestamp

  ## Security
    - Enable RLS on `lessons` table
    - Add policy for authenticated users to read their own lessons
    - Add policy for authenticated users to insert their own lessons
    - Add policy for authenticated users to delete their own lessons

  ## Notes
    - Lessons are tied to authenticated users only
    - History tracking enabled through created_at timestamp
    - Full content stored for preview and downloads
*/

CREATE TABLE IF NOT EXISTS lessons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  year_group text NOT NULL,
  ability_level text NOT NULL,
  lesson_duration integer NOT NULL,
  subject text NOT NULL,
  topic text NOT NULL,
  learning_objective text,
  sen_eal_notes text,
  regeneration_instruction text,
  lesson_content text NOT NULL,
  lesson_text text NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL
);

ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own lessons"
  ON lessons FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own lessons"
  ON lessons FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own lessons"
  ON lessons FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS lessons_user_id_created_at_idx ON lessons(user_id, created_at DESC);
