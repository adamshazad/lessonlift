# Lesson Generator Setup Guide

## Overview

Your Lesson Generator is now fully built with a native Bolt UI and Supabase backend. The system includes:

- **Full form with all parameters**: Year Group, Ability Level, Duration, Subject, Topic, Learning Objectives, SEN/EAL Notes
- **Lesson generation via OpenAI GPT-4o**: Comprehensive UK curriculum-aligned lessons
- **Download functionality**: TXT, PDF, and DOCX formats
- **Lesson history**: Stored in Supabase with full CRUD operations
- **Regeneration options**: Multiple presets plus custom instructions
- **Mobile responsive design**: Works seamlessly on all devices

## ⚠️ CRITICAL: OpenAI API Key Setup Required

**The lesson generator will not work until you configure your OpenAI API key in Supabase.**

To enable lesson generation, follow these steps:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Go to your Supabase Dashboard: https://supabase.com/dashboard
3. Select your project: **yemzxrleleujqplhynuz**
4. Navigate to **Project Settings** (gear icon) → **Edge Functions** → **Manage secrets**
5. Add a new secret:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-...`)
6. Click **Save** or **Add Secret**
7. Wait 30 seconds for the secret to be available to Edge Functions

**Without this key configured, you will see an error message when trying to generate lessons.**

The Edge Function will automatically use this key once configured.

## Daily Lesson Limits & Subscription Plans

The system now enforces daily lesson generation limits based on subscription tiers:

### Plan Tiers
- **Starter**: 1 lesson per day → PDF export only
- **Standard**: 3 lessons per day → PDF + DOCX exports
- **Pro**: 5 lessons per day → PDF + DOCX + TXT exports

### How It Works
- Daily counter tracks lessons generated per user per day
- Counter automatically resets at midnight (database uses CURRENT_DATE)
- If limit is reached, generation is blocked with a clear message
- Usage is displayed in the top-right corner of the Lesson Generator page
- Export buttons are enabled/disabled based on your plan

### Default Configuration
- All users default to **Pro** plan (5 lessons/day, all exports) for V1
- Plans can be configured later by updating user metadata in Supabase

### Checking Your Usage
The Lesson Generator page displays:
- Current plan name
- Lessons used today / Daily limit
- Visual progress bar
- Warning when limit is reached

## Features Implemented

### 1. Lesson Generation Form
- Year Group selection (Year 1-6)
- Ability Level (Mixed, Lower, Higher)
- Lesson Duration (30, 45, 60 minutes)
- Subject and Topic fields
- Optional Learning Objective
- Optional SEN/EAL Notes

### 2. Lesson Preview
- Fully styled HTML preview
- Professional formatting with color-coded sections
- Mobile responsive layout

### 3. Download Options
- **TXT**: Plain text format with headers
- **PDF**: Print-to-PDF with proper styling (opens print dialog)
- **DOCX**: Microsoft Word compatible format

### 4. Lesson History
- Shows last 20 lessons
- Click to view previous lessons
- Delete lessons you no longer need
- Displays metadata (year group, ability, duration)
- Shows creation time (relative and absolute)

### 5. Regeneration Options
- **Just regenerate**: Different variation of same lesson
- **More creative & engaging**: Interactive activities focus
- **More structured with timings**: Detailed timing and structure
- **Simplify for lower ability**: Accessible content with scaffolding
- **Challenge for higher ability**: Extended activities
- **Custom instruction**: Your own regeneration prompt

## Database Schema

The `lessons` table stores:
- User association (tied to authenticated users)
- All lesson parameters
- Generated HTML and text content
- Timestamps for history tracking
- Row Level Security ensures users only see their own lessons

## Edge Function

The `generate-lesson` Edge Function:
- Accepts lesson parameters via POST
- Builds detailed prompts for OpenAI
- Generates comprehensive lesson plans
- Formats output as HTML and text
- Saves to database automatically
- Returns formatted content to frontend

## Authentication Flow

1. Users must be logged in to access the Lesson Generator
2. Unauthenticated users are redirected to sign-up
3. All lessons are tied to the user's account
4. Only the lesson owner can view/delete their lessons

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Supabase Edge Functions (Deno runtime)
- **AI**: OpenAI GPT-4o
- **Database**: Supabase PostgreSQL with RLS
- **Authentication**: Supabase Auth

## Testing the Generator

1. Sign up or log in to your account
2. Fill in the lesson parameters
3. Click "Generate Lesson Plan"
4. Wait 10-30 seconds for generation
5. View the formatted lesson
6. Download in your preferred format
7. Try regenerating with different options
8. Check your history sidebar

## Customization Options

You can easily customize:
- Color scheme (currently green theme)
- Form fields (add/remove as needed)
- Prompt templates (in Edge Function)
- Formatting styles (CSS in LessonGeneratorPage)
- History limit (currently 20 lessons)

## Files Created/Modified

**New Files:**
- `src/services/lessonService.ts` - API service layer
- `src/utils/downloadUtils.ts` - Download functionality
- `src/components/LessonForm.tsx` - Form component
- `src/components/LessonPreview.tsx` - Preview component
- `src/components/LessonHistory.tsx` - History sidebar
- `supabase/functions/generate-lesson/index.ts` - Edge Function

**Modified Files:**
- `src/pages/LessonGeneratorPage.tsx` - Main page (replaced iframe)
- Database migrations added for lessons table

## Troubleshooting

### Error: "Failed to generate lesson"

If you see this error, check the following:

1. **OpenAI API Key Not Configured**
   - Most common cause
   - Go to Supabase Dashboard → Project Settings → Edge Functions → Manage secrets
   - Add `OPENAI_API_KEY` with your OpenAI key
   - Wait 30 seconds after saving

2. **Check Browser Console**
   - Press F12 to open Developer Tools
   - Go to Console tab
   - Look for detailed error messages
   - Error messages will show the specific issue

3. **Check Edge Function Logs**
   - Go to Supabase Dashboard
   - Navigate to Edge Functions → generate-lesson
   - Check the logs for errors
   - Common issues: Missing API key, database permission errors

4. **Verify Database Functions**
   - Functions should exist: `check_and_increment_daily_count`, `get_daily_lesson_count`
   - These were created by the migration files
   - If missing, re-run migrations

5. **Check Daily Limit**
   - You may have reached your daily limit
   - Check the usage display in the top-right corner
   - Wait until midnight for counter reset

### Getting More Details

To see the exact error:
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Try generating a lesson
4. Look for error messages in red
5. The console will show the actual error from the Edge Function

## Notes

- The Edge Function uses GPT-4o for high-quality lesson generation
- Lessons are saved automatically after generation
- Downloads happen client-side (no server storage needed)
- History is loaded on page mount and after each generation
- Mobile users can toggle history sidebar visibility
- All styling is native and fully customizable in Bolt
- Daily limits prevent excessive API usage and costs
- All lesson formatting and quality remain unchanged
