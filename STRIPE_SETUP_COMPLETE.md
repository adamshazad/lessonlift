# LessonLift Stripe Integration - Complete Setup Guide

## ✅ What's Already Configured

Your LessonLift application is now fully configured with Stripe integration for all three pricing tiers:

### Pricing Plans
- **Starter**: 1 lesson/day, 30/month - £4.99/month or £45/year
- **Standard**: 3 lessons/day, 90/month - £7.99/month or £75/year (Most Popular)
- **Pro**: 5 lessons/day, 150/month - £12.99/month or £120/year

### Features Implemented
✅ Stripe Checkout Sessions with 7-day free trial
✅ Edge Functions deployed (create-checkout-session, stripe-webhook)
✅ Production domain redirects to https://lessonlift.co.uk
✅ Success page: https://lessonlift.co.uk/payment-success
✅ Cancel page: https://lessonlift.co.uk/pricing
✅ Database functions for plan management
✅ RLS policies optimized for performance
✅ Frontend pricing page with billing toggle (monthly/annual)

---

## 🔧 Required Setup Steps

### Step 1: Add Stripe API Keys to Supabase

1. **Get Your Stripe API Keys**
   - Go to: https://dashboard.stripe.com/test/apikeys
   - Copy your **Secret Key** (starts with `sk_test_`)
   - Keep this tab open for the webhook setup

2. **Add Keys to Supabase**
   - Go to: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/settings/secrets
   - Add these secrets:
     ```
     Name: STRIPE_SECRET_KEY
     Value: sk_test_... (your test secret key)
     ```
   - Click "Add Secret"

### Step 2: Create Stripe Products & Prices

You need to create these products in your Stripe Dashboard and update the Price IDs in your code:

**Go to: https://dashboard.stripe.com/test/products**

#### Create Product 1: Starter Plan
1. Click "+ Add product"
2. **Name**: LessonLift Starter
3. **Description**: 1 lesson per day, 30 lessons per month
4. **Pricing**:
   - Monthly: £4.99 GBP recurring
   - Annual: £45 GBP recurring (yearly)
5. **Advanced options** → Add metadata:
   - `plan_type`: `starter`
6. Save and copy both Price IDs

#### Create Product 2: Standard Plan
1. Click "+ Add product"
2. **Name**: LessonLift Standard
3. **Description**: 3 lessons per day, 90 lessons per month
4. **Pricing**:
   - Monthly: £7.99 GBP recurring
   - Annual: £75 GBP recurring (yearly)
5. **Advanced options** → Add metadata:
   - `plan_type`: `standard`
6. Save and copy both Price IDs

#### Create Product 3: Pro Plan
1. Click "+ Add product"
2. **Name**: LessonLift Pro
3. **Description**: 5 lessons per day, 150 lessons per month
4. **Pricing**:
   - Monthly: £12.99 GBP recurring
   - Annual: £120 GBP recurring (yearly)
5. **Advanced options** → Add metadata:
   - `plan_type`: `pro`
6. Save and copy both Price IDs

### Step 3: Update Price IDs in Your Code

After creating the Stripe products, you'll have 6 Price IDs. Update them in two places:

#### File 1: `src/components/Pricing.tsx`
Find lines 44-85 and replace the Price IDs:

```typescript
const standardPlans = [
  {
    name: "Starter",
    planType: "starter" as const,
    monthlyPrice: "£4.99",
    annualPrice: "£45",
    monthlyPriceId: "price_xxxxxxxxxxxxx", // ← Your Starter Monthly Price ID
    annualPriceId: "price_xxxxxxxxxxxxx",  // ← Your Starter Annual Price ID
    // ...
  },
  {
    name: "Standard",
    planType: "standard" as const,
    monthlyPrice: "£7.99",
    annualPrice: "£75",
    monthlyPriceId: "price_xxxxxxxxxxxxx", // ← Your Standard Monthly Price ID
    annualPriceId: "price_xxxxxxxxxxxxx",  // ← Your Standard Annual Price ID
    // ...
  },
  {
    name: "Pro",
    planType: "pro" as const,
    monthlyPrice: "£12.99",
    annualPrice: "£120",
    monthlyPriceId: "price_xxxxxxxxxxxxx", // ← Your Pro Monthly Price ID
    annualPriceId: "price_xxxxxxxxxxxxx",  // ← Your Pro Annual Price ID
    // ...
  }
];
```

#### File 2: `supabase/functions/stripe-webhook/index.ts`
Find lines 64-71 and update the price mapping:

```typescript
const getPlanFromPriceId = (priceId: string): string | null => {
  const priceMap: { [key: string]: string } = {
    'price_xxxxxxxxxxxxx': 'starter',  // Starter Monthly
    'price_xxxxxxxxxxxxx': 'starter',  // Starter Annual
    'price_xxxxxxxxxxxxx': 'standard', // Standard Monthly
    'price_xxxxxxxxxxxxx': 'standard', // Standard Annual
    'price_xxxxxxxxxxxxx': 'pro',      // Pro Monthly
    'price_xxxxxxxxxxxxx': 'pro',      // Pro Annual
  };
  return priceMap[priceId] || null;
};
```

After updating, redeploy the webhook function (see Step 6).

### Step 4: Set Up Stripe Webhook

1. **Go to Stripe Webhooks**
   - URL: https://dashboard.stripe.com/test/webhooks
   - Click "+ Add endpoint"

2. **Configure Endpoint**
   - **Endpoint URL**:
     ```
     https://yemzxrleleujqplhynuz.supabase.co/functions/v1/stripe-webhook
     ```

3. **Select Events to Listen To**
   Click "Select events" and add these three:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`

4. **Save the Webhook**
   - Click "Add endpoint"
   - Copy the **Signing secret** (starts with `whsec_`)

5. **Add Webhook Secret to Supabase**
   - Go to: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/settings/secrets
   - Add new secret:
     ```
     Name: STRIPE_WEBHOOK_SECRET
     Value: whsec_... (your webhook signing secret)
     ```

### Step 5: Test the Integration

#### Test User Flow:
1. **Sign Up** → Go to https://lessonlift.co.uk/signup
2. **Start Free Trial** → Generate up to 5 lesson plans (7-day trial)
3. **View Pricing** → Go to https://lessonlift.co.uk/pricing
4. **Select a Plan** → Click any plan button
5. **Checkout** → Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits
6. **Verify Redirect** → Should redirect to https://lessonlift.co.uk/payment-success
7. **Test Limits** → Generate lessons to verify your plan limits work

#### Test Stripe Events:
- Go to: https://dashboard.stripe.com/test/events
- You should see `checkout.session.completed` event
- Click on it to verify webhook delivery succeeded

#### Check Database:
```sql
-- Run in Supabase SQL Editor
SELECT
  id,
  email,
  raw_app_meta_data->>'subscription_plan' as plan
FROM auth.users
WHERE email = 'your-test-email@example.com';
```
Should show the correct plan (starter/standard/pro).

### Step 6: Deploy Updated Code

After updating Price IDs in your files, deploy:

```bash
# Build the frontend
npm run build

# Deploy the updated webhook function (if you changed price IDs)
# This happens automatically in Bolt when you save the file
```

---

## 🧪 Testing Checklist

- [ ] Stripe test API keys added to Supabase secrets
- [ ] All 6 Price IDs created in Stripe (3 products × 2 billing cycles)
- [ ] Price IDs updated in `Pricing.tsx`
- [ ] Price IDs updated in `stripe-webhook/index.ts`
- [ ] Webhook endpoint created in Stripe
- [ ] Webhook secret added to Supabase secrets
- [ ] Webhook events configured (3 events)
- [ ] Test checkout completes successfully
- [ ] User redirected to success page
- [ ] Plan limits enforced correctly
- [ ] Webhook events processed in Stripe dashboard

---

## 🚀 Going Live (Production)

When ready to go live:

### 1. Switch to Live API Keys
- Get live keys from: https://dashboard.stripe.com/apikeys
- Update Supabase secrets:
  - `STRIPE_SECRET_KEY` → Use `sk_live_...`
  - `STRIPE_WEBHOOK_SECRET` → Create new webhook for live mode

### 2. Update Live Price IDs
- Create products in **Live mode** (same as test mode)
- Update Price IDs in your code
- Deploy updates

### 3. Create Live Webhook
- URL: https://dashboard.stripe.com/webhooks (live mode)
- Same endpoint URL and events as test mode
- Update `STRIPE_WEBHOOK_SECRET` with live secret

### 4. Test with Real Card
- Use a real credit card for final testing
- Verify everything works before announcing

---

## 📊 Monitoring & Support

### View Subscriptions
- Stripe Dashboard: https://dashboard.stripe.com/subscriptions
- See all active subscriptions, revenue, and customer details

### View Webhook Logs
- Stripe Webhooks: https://dashboard.stripe.com/webhooks
- Click your endpoint → View logs
- Debug failed events

### Supabase Edge Function Logs
- Go to: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/functions
- Click function name → View logs
- See all webhook processing logs

### Common Issues

**Webhook not receiving events:**
- Verify endpoint URL is correct
- Check webhook secret is set in Supabase
- Ensure all 3 events are selected

**User plan not updating:**
- Check Supabase function logs
- Verify Price ID mapping is correct
- Ensure user_id is in checkout metadata

**Checkout redirects to wrong URL:**
- Verify production domain in `create-checkout-session/index.ts`
- Test URL should be: https://lessonlift.co.uk/payment-success

---

## 📋 Quick Reference

### Your Stripe Dashboard URLs
- **Test API Keys**: https://dashboard.stripe.com/test/apikeys
- **Products**: https://dashboard.stripe.com/test/products
- **Webhooks**: https://dashboard.stripe.com/test/webhooks
- **Events**: https://dashboard.stripe.com/test/events
- **Subscriptions**: https://dashboard.stripe.com/test/subscriptions

### Your Supabase URLs
- **Secrets**: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/settings/secrets
- **Functions**: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/functions
- **SQL Editor**: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/sql

### Test Card Numbers
- **Success**: 4242 4242 4242 4242
- **Declined**: 4000 0000 0000 0002
- **3D Secure**: 4000 0027 6000 3184

---

## 🎉 You're All Set!

Your LessonLift Stripe integration is ready. Follow the steps above to complete the setup and start accepting payments!

For questions or issues, check:
- Stripe Documentation: https://stripe.com/docs
- Supabase Edge Functions: https://supabase.com/docs/guides/functions
