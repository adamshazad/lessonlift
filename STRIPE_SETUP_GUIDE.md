# Stripe Integration Setup Guide

## Overview
Your subscription system is now properly configured. When users subscribe to different plans, they'll automatically get the correct limits:

- **Starter**: 1 lesson/day, 30 lessons/month, PDF only
- **Standard**: 3 lessons/day, 90 lessons/month, PDF + DOCX
- **Pro**: 5 lessons/day, 150 lessons/month, PDF + DOCX + TXT

## What Was Fixed

1. **Stripe Integration**: The Pricing component now properly calls Stripe checkout
2. **Plan Type Passing**: The correct plan type (starter/standard/pro) is now passed to Stripe
3. **Database Functions**: All database functions are in place to set and track limits
4. **Webhook Handler**: The webhook properly updates user plans when payment succeeds

## Required Steps

### Step 1: Create Stripe Products and Prices

1. Go to your [Stripe Dashboard](https://dashboard.stripe.com/products)
2. Create products for each plan (Starter, Standard, Pro)
3. For each product, create two prices:
   - Monthly recurring price
   - Annual recurring price

### Step 2: Update Price IDs in Code

Once you have your Stripe prices created, update the price IDs in `src/components/Pricing.tsx`:

```typescript
const standardPlans = [
  {
    name: "Starter",
    planType: "starter" as const,
    monthlyPriceId: "price_YOUR_ACTUAL_MONTHLY_ID", // Replace this
    annualPriceId: "price_YOUR_ACTUAL_ANNUAL_ID",   // Replace this
    // ... rest of config
  },
  {
    name: "Standard",
    planType: "standard" as const,
    monthlyPriceId: "price_YOUR_ACTUAL_MONTHLY_ID", // Replace this
    annualPriceId: "price_YOUR_ACTUAL_ANNUAL_ID",   // Replace this
    // ... rest of config
  },
  {
    name: "Pro",
    planType: "pro" as const,
    monthlyPriceId: "price_YOUR_ACTUAL_MONTHLY_ID", // Replace this
    annualPriceId: "price_YOUR_ACTUAL_ANNUAL_ID",   // Replace this
    // ... rest of config
  }
];
```

### Step 3: Configure Stripe Webhook

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your webhook URL: `https://YOUR_PROJECT.supabase.co/functions/v1/stripe-webhook`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the webhook signing secret
6. Add it to your Supabase environment variables as `STRIPE_WEBHOOK_SECRET`

### Step 4: Test the Integration

1. Sign up for an account
2. Click on a plan in the pricing page
3. Complete the Stripe checkout (use test mode)
4. After successful payment, check your user's plan:

```sql
SELECT
  id,
  email,
  raw_app_meta_data->>'subscription_plan' as plan
FROM auth.users
WHERE email = 'your-test-email@example.com';
```

You should see the plan set to 'starter', 'standard', or 'pro'.

## How It Works

1. **User clicks plan button** → Pricing.tsx calls `createCheckoutSession()`
2. **Edge function creates session** → Passes `user_id` and `plan_type` to Stripe
3. **User completes payment** → Stripe sends webhook to your app
4. **Webhook handler** → Calls `set_user_subscription_plan()` in database
5. **Database function** → Updates user's `raw_app_meta_data` with plan
6. **Lesson generation** → Checks plan and applies correct limits

## Verifying Plan Limits

To verify a user's limits are working correctly:

```sql
-- Check user's plan
SELECT get_user_plan('USER_UUID_HERE');

-- Check daily limit for user's plan
SELECT get_plan_daily_limit(get_user_plan('USER_UUID_HERE'));

-- Check monthly limit for user's plan
SELECT get_plan_monthly_limit(get_user_plan('USER_UUID_HERE'));

-- Get full subscription status
SELECT get_user_subscription_status('USER_UUID_HERE');
```

## Troubleshooting

### Issue: User still has trial limits after payment
**Solution**: Check that:
1. Webhook was received (check Stripe dashboard logs)
2. Webhook secret is correctly configured
3. `set_user_subscription_plan` function exists in database

### Issue: Checkout button doesn't work
**Solution**: Check that:
1. User is logged in
2. Stripe price IDs are correctly set
3. `STRIPE_SECRET_KEY` is configured in Supabase

### Issue: Error creating checkout session
**Solution**: Check browser console for specific error messages

## Current Status

✅ Database schema with all plans and limits
✅ Stripe checkout integration
✅ Webhook handler for subscription events
✅ Plan isolation and counter management
✅ Trial system (7 days, 5 lessons)
⚠️ **Needs**: Real Stripe price IDs
⚠️ **Needs**: Webhook endpoint configured

Once you add the real Stripe price IDs and configure the webhook, the system is fully functional!
