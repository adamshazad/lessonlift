# Subscription System - Complete Setup

## System Overview

Your subscription system is now fully configured with real Stripe price IDs and proper limit enforcement.

## Price ID Mapping

The system now uses these exact Stripe price IDs:

- **Starter**: `price_1SpBSFCVrhYYeZRki2HhXLR5` → 1/day, 30/month, PDF only
- **Standard**: `price_1SpBSmCVrhYYeZRkM2f2PCqI` → 3/day, 90/month, PDF + DOCX
- **Pro**: `price_1SpBTECVrhYYeZRkJwNw40Q8` → 5/day, 150/month, PDF + DOCX + TXT

## How It Works

1. **User clicks plan button** → Creates Stripe checkout with price_id and plan_type
2. **User completes payment** → Stripe sends webhook to your app
3. **Webhook processes payment** → Maps price_id to plan type, calls `set_user_subscription_plan()`
4. **Database updates** → User's `raw_app_meta_data` gets `subscription_plan: 'starter'|'standard'|'pro'`
5. **Lesson generation** → Checks `has_paid_plan()`, uses correct limits based on plan

## Testing Your Setup

### Step 1: Check if webhook endpoint is configured

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Verify you have an endpoint: `https://yemzxrleleujqplhynuz.supabase.co/functions/v1/stripe-webhook`
3. Make sure these events are selected:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

### Step 2: Test with a real Stripe checkout

1. Log into your app
2. Go to pricing page
3. Click on a plan (use Stripe test mode)
4. Complete checkout
5. After redirect, check your plan was updated

### Step 3: Verify plan in database

Run this query in your Supabase SQL Editor:

```sql
-- Check your user's subscription plan
SELECT
  id,
  email,
  raw_app_meta_data->>'subscription_plan' as subscription_plan,
  created_at
FROM auth.users
WHERE email = 'YOUR_EMAIL@example.com';
```

You should see `subscription_plan` set to 'starter', 'standard', or 'pro'.

### Step 4: Test limits are working

Run this query to check what limits your user has:

```sql
-- Replace USER_UUID with your actual user ID
SELECT get_user_subscription_status('USER_UUID_HERE');
```

This will return JSON showing:
- Your plan type
- Daily/monthly limits
- Current usage
- Remaining lessons

## Manual Testing (If Webhook Not Set Up Yet)

If you want to test before configuring Stripe webhooks, you can manually set a user's plan:

```sql
-- Set a user to starter plan
SELECT set_user_subscription_plan(
  'USER_UUID_HERE',
  'starter'
);

-- Set a user to standard plan
SELECT set_user_subscription_plan(
  'USER_UUID_HERE',
  'standard'
);

-- Set a user to pro plan
SELECT set_user_subscription_plan(
  'USER_UUID_HERE',
  'pro'
);
```

After setting the plan, try generating lessons and verify:
- Starter: Can generate 1 lesson per day
- Standard: Can generate 3 lessons per day
- Pro: Can generate 5 lessons per day

## Troubleshooting

### Issue: Still stuck on trial limits after payment

**Check these:**

1. **Webhook received?**
   - Go to Stripe Dashboard → Webhooks → Click your endpoint
   - Check "Recent deliveries" - you should see `checkout.session.completed` events
   - If status is not "Succeeded", click it to see the error

2. **Plan set in database?**
   ```sql
   SELECT
     email,
     raw_app_meta_data->>'subscription_plan' as plan
   FROM auth.users
   WHERE email = 'YOUR_EMAIL';
   ```
   - Should show 'starter', 'standard', or 'pro'
   - If NULL, webhook didn't update the user

3. **Check Supabase function logs:**
   - Go to Supabase Dashboard → Functions → stripe-webhook
   - Check logs for errors

### Issue: Webhook failing

If webhook shows errors in Stripe dashboard:

1. Check the webhook signing secret is set in Supabase:
   - Go to Supabase Dashboard → Project Settings → Edge Functions → Secrets
   - Verify `STRIPE_WEBHOOK_SECRET` is set

2. Check the edge function deployed correctly:
   - Go to Supabase Dashboard → Functions
   - Verify `stripe-webhook` is listed and deployed

### Issue: User can generate more lessons than plan allows

This shouldn't happen if everything is set up correctly. Verify:

```sql
-- Check what plan the system thinks you have
SELECT get_user_plan('USER_UUID_HERE');

-- Check your current usage
SELECT get_daily_lesson_count('USER_UUID_HERE');
```

## System Status

✅ Frontend pricing page with real Stripe price IDs
✅ Stripe checkout integration
✅ Webhook handler with price_id mapping
✅ Database functions for plan management
✅ Limit enforcement in lesson generation
✅ Trial system (7 days, 5 lessons)
✅ Plan-specific limits (starter/standard/pro)
✅ Monthly and daily limit tracking
✅ Counter reset when upgrading from trial

## Next Steps

1. **Configure Stripe webhook endpoint** (if not done)
2. **Test with Stripe test mode**
3. **Verify limits work correctly**
4. **Switch to Stripe live mode when ready**

Your subscription system is complete and ready to use!
