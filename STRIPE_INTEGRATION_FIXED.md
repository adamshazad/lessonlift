# Stripe Integration Fixed

## What Was Fixed

### 1. Pricing Components
- Added `planType` field to Stripe product configuration
- Updated `PricingCard` component to pass plan type to checkout
- Added error handling with user feedback

### 2. Edge Functions
- **stripe-checkout**: Now includes plan metadata in subscription data
- **stripe-webhook**: Automatically sets user subscription plan when payment succeeds

### 3. Plan Limits (Enforced by Database)
- **Free Trial**: 5 lessons total over 7 days
- **Starter**: 1 lesson/day, 30 lessons/month
- **Standard**: 3 lessons/day, 90 lessons/month
- **Pro**: 5 lessons/day, 150 lessons/month

## Setup Required

### 1. Add Stripe Keys to Environment

You need to add your Stripe keys. The backend keys are automatically configured in Supabase, but you need to add the frontend key:

**Update `.env` file:**
```
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_51Pj2HGCVrhYYeZRk8dw19xB8kxEOBeWY10ZPjnnSFgbfrsrrlvmjPgpcHJLcWE0uzDv8SGVa2nifWTgHWR4DZvxs005FiX3Ofv
```

Get your keys from: https://dashboard.stripe.com/apikeys

### 2. Configure Stripe Webhook (IMPORTANT!)

For the webhook to work, you need to configure it in Stripe:

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL:
   ```
   https://rtmactxdmjjntlzwhqkm.supabase.co/functions/v1/create-checkout-session
   ```
4. Select these events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
5. Copy the webhook signing secret (starts with `whsec_...`)
6. Add it to your Supabase secrets as `STRIPE_WEBHOOK_SECRET`

## How to Test

### Test Flow:
1. Sign up for a new account at `/signup`
2. You'll start with free trial (5 lessons total)
3. Go to `/pricing` to see available plans
4. Click "Subscribe Now" on any plan
5. Complete checkout with Stripe test card: `4242 4242 4242 4242`
6. You'll be redirected to the success page
7. The webhook will:
   - Update your subscription status
   - Set your plan type (starter/standard/pro)
   - Reset your lesson counters
8. Go to `/dashboard` to generate lessons with your new limits

### Verify Plan Limits:
- Try generating lessons to confirm daily limits work
- Check that the correct plan name shows in the UI
- Verify lesson counters reset properly

## Database Functions Used

The following database functions handle plan management:

- `set_user_subscription_plan(user_id, plan_type)` - Sets user's subscription plan
- `get_user_plan(user_id)` - Gets current plan (returns 'trial' if no paid plan)
- `get_user_subscription_status(user_id)` - Returns full subscription status with limits
- `reset_plan_counters(user_id)` - Clears daily/monthly counters when upgrading

## Troubleshooting

### Checkout doesn't redirect:
- Check browser console for errors
- Verify `VITE_STRIPE_PUBLISHABLE_KEY` is set in `.env`
- Check that user is logged in

### Webhook not updating subscription:
- Verify webhook is configured in Stripe dashboard
- Check webhook signing secret is correct
- View webhook logs in Stripe dashboard
- Check Supabase function logs

### Plan limits not enforced:
- Check that webhook successfully ran
- Verify user's plan in database: `SELECT raw_app_meta_data FROM auth.users WHERE id = 'user_id'`
- Check daily/monthly counters in `daily_lesson_counts` and `monthly_lesson_counts` tables

## Architecture

```
User clicks plan
    ↓
Frontend calls stripe-checkout Edge Function
    ↓
Edge Function creates Stripe Checkout Session with metadata
    ↓
User completes payment in Stripe
    ↓
Stripe sends webhook event
    ↓
stripe-webhook Edge Function receives event
    ↓
Function syncs subscription data to database
    ↓
Function calls set_user_subscription_plan()
    ↓
User's plan is updated and counters reset
    ↓
User can now generate lessons with new limits
```

## Next Steps

1. Add your Stripe publishable key to `.env`
2. Configure the webhook endpoint in Stripe dashboard
3. Test with Stripe test cards
4. Monitor webhook logs to ensure proper processing
5. Test plan limits by generating lessons
