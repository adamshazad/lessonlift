# Plan Isolation and Management Fix

## Problem Fixed
Users were sharing the same lesson limits regardless of their subscription plan. All users saw "5 remaining today / 5 this month" regardless of whether they were on Trial, Starter, Standard, or Pro plans.

## Solution Implemented
Complete isolation of plan counters and proper plan management system with automatic Stripe integration.

---

## Changes Made

### 1. Database Migration - Plan Management System
**File**: `supabase/migrations/fix_plan_isolation_and_management.sql`

Created new database functions to properly manage subscription plans:

- **`set_user_subscription_plan(user_id, plan_type)`**: Updates a user's subscription plan
  - Validates plan type (starter, standard, pro)
  - Resets counters when upgrading from trial
  - Stores plan in `auth.users.raw_app_meta_data`

- **`reset_plan_counters(user_id)`**: Clears daily/monthly counters
  - Used when upgrading from trial to paid plan
  - Ensures fresh start with new plan limits

- **`get_user_subscription_status(user_id)`**: Comprehensive status function
  - Returns trial info for trial users
  - Returns plan-specific usage for paid users
  - Includes daily/monthly counts and limits

- **Updated `get_user_plan(user_id)`**:
  - Never defaults to a paid plan
  - Returns 'trial' for users without paid plans
  - Validates plan types

### 2. Stripe Webhook Handler
**File**: `supabase/functions/stripe-webhook/index.ts`

Created webhook to handle payment events automatically:

- **`checkout.session.completed`**: Sets user's plan after successful payment
- **`customer.subscription.updated`**: Handles plan upgrades/downgrades
- **`customer.subscription.deleted`**: Reverts user to trial when cancelled

The webhook extracts user ID and plan type from metadata and updates the database accordingly.

### 3. Updated Checkout Session
**File**: `supabase/functions/create-checkout-session/index.ts`

Enhanced to include user metadata:

- Authenticates user before creating session
- Validates plan type (starter, standard, pro)
- Embeds user ID and plan type in both session and subscription metadata
- Includes customer email for Stripe records

### 4. Updated Usage Service
**File**: `src/services/lessonService.ts`

Changed to use the new comprehensive status endpoint:

- Now calls `get_user_subscription_status` instead of `get_daily_lesson_count`
- Returns complete plan information with proper isolation
- Maintains backward compatibility with existing UI components

---

## How It Works Now

### Free Trial Users
- **Limits**: 5 total lessons, 7 days
- **Counters**: Stored in `auth.users.raw_app_meta_data.trial_lessons_used`
- **Display**: Shows lessons remaining and days remaining
- **No daily/monthly refresh** - trial is total limit only

### Paid Plan Users (After Upgrade)

#### Starter Plan
- **Limits**: 1 lesson/day, 30 lessons/month
- **Counters**: Separate `daily_lesson_counts` and `monthly_lesson_counts` tables
- **Display**: Shows "X / 1" today, "Y / 30" this month
- **Exports**: PDF only

#### Standard Plan
- **Limits**: 3 lessons/day, 90 lessons/month
- **Counters**: Separate tables, isolated from other plans
- **Display**: Shows "X / 3" today, "Y / 90" this month
- **Exports**: PDF + DOCX

#### Pro Plan
- **Limits**: 5 lessons/day, 150 lessons/month
- **Counters**: Separate tables, isolated from other plans
- **Display**: Shows "X / 5" today, "Y / 150" this month
- **Exports**: PDF + DOCX + TXT

---

## Upgrade Flow

1. **User clicks "Upgrade"** on pricing page
2. **Frontend calls** `create-checkout-session` with plan type
3. **Edge function creates** Stripe checkout with user metadata
4. **User completes payment** in Stripe
5. **Stripe sends webhook** to `stripe-webhook` function
6. **Webhook calls** `set_user_subscription_plan` database function
7. **Database function**:
   - Updates `auth.users.raw_app_meta_data.subscription_plan`
   - Resets daily/monthly counters
   - Leaves trial data for record-keeping
8. **User immediately sees** new plan limits on next page load

---

## Counter Isolation

Each plan type now has completely isolated counters:

### Trial Users
- Uses: `auth.users.raw_app_meta_data.trial_lessons_used`
- Never touches daily/monthly tables

### Paid Users
- Uses: `daily_lesson_counts` and `monthly_lesson_counts` tables
- Separate rows per user (isolated by user_id)
- Daily counts reset at midnight
- Monthly counts reset on the 1st of each month

### Key Enforcement Points

1. **`check_and_increment_daily_count` function**:
   - Checks if user has paid plan first
   - If trial → uses trial counters
   - If paid → uses daily/monthly counters
   - No overlap between trial and paid counters

2. **Plan Limit Functions**:
   - `get_plan_daily_limit(plan)`: Returns correct daily limit per plan
   - `get_plan_monthly_limit(plan)`: Returns correct monthly limit per plan
   - Hard-coded authoritative limits (not user-modifiable)

---

## Security Features

- All functions use `SECURITY DEFINER` for proper permissions
- RLS policies protect user data
- Plan changes only via Stripe webhooks or admin functions
- Users cannot modify their own subscription_plan directly
- Server-side enforcement prevents client manipulation

---

## Next Steps for Setup

### 1. Configure Stripe Webhook (Required)

After deploying, you need to configure the Stripe webhook endpoint:

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://YOUR_PROJECT.supabase.co/functions/v1/stripe-webhook`
3. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy the webhook signing secret
5. Add to Supabase secrets:
   ```bash
   supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### 2. Testing

To test the plan isolation:

1. Sign up as a new user (automatically on trial)
2. Generate a lesson (should show "4 / 5 lessons remaining")
3. Go through Stripe checkout for a paid plan
4. After payment, refresh the page
5. Should see plan-specific limits (e.g., "0 / 1 today, 1 / 30 this month" for Starter)
6. Generate more lessons to verify limits are enforced correctly

### 3. Monitor Webhook Events

Check Supabase Edge Function logs to verify webhooks are processing:
- Successful plan updates will log: "Successfully set USER_ID to PLAN_TYPE plan"
- Failed updates will log errors for debugging

---

## Summary

All plans now have properly isolated counters and limits. Users will see accurate usage based on their specific subscription plan, and upgrades/downgrades are handled automatically through Stripe webhooks.
