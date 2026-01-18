# Quick Stripe Setup - Copy & Paste Guide

## Step 1: Add Stripe Test Key to Supabase

1. Get your test key: https://dashboard.stripe.com/test/apikeys
2. Go to: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/settings/secrets
3. Add secret:
   - Name: `STRIPE_SECRET_KEY`
   - Value: `sk_test_...` (your key)

## Step 2: Create Stripe Products

Go to: https://dashboard.stripe.com/test/products

### Product 1: LessonLift Starter
- Name: `LessonLift Starter`
- Description: `1 lesson per day, 30 lessons per month`
- Monthly Price: `£4.99 GBP` recurring monthly
- Annual Price: `£45 GBP` recurring yearly
- Metadata: `plan_type` = `starter`

### Product 2: LessonLift Standard
- Name: `LessonLift Standard`
- Description: `3 lessons per day, 90 lessons per month`
- Monthly Price: `£7.99 GBP` recurring monthly
- Annual Price: `£75 GBP` recurring yearly
- Metadata: `plan_type` = `standard`

### Product 3: LessonLift Pro
- Name: `LessonLift Pro`
- Description: `5 lessons per day, 150 lessons per month`
- Monthly Price: `£12.99 GBP` recurring monthly
- Annual Price: `£120 GBP` recurring yearly
- Metadata: `plan_type` = `pro`

**Copy all 6 Price IDs** (they look like `price_xxxxxxxxxxxxx`)

## Step 3: Update Price IDs in Pricing Component

Open: `src/components/Pricing.tsx`

Find lines 38-98 and replace with your Price IDs:

```typescript
const standardPlans = [
  {
    name: "Starter",
    planType: "starter" as const,
    monthlyPrice: "£4.99",
    annualPrice: "£45",
    monthlyPriceId: "YOUR_STARTER_MONTHLY_PRICE_ID",
    annualPriceId: "YOUR_STARTER_ANNUAL_PRICE_ID",
    annualSavings: "Save £14.88!",
    description: "Perfect for trying out LessonLift.",
    features: [
      "1 lesson per day",
      "30 lessons per month",
      "UK curriculum-aligned",
      "Export as PDF",
      "Email support"
    ],
    cta: "Start Free Trial",
    popular: false,
  },
  {
    name: "Standard",
    planType: "standard" as const,
    monthlyPrice: "£7.99",
    annualPrice: "£75",
    monthlyPriceId: "YOUR_STANDARD_MONTHLY_PRICE_ID",
    annualPriceId: "YOUR_STANDARD_ANNUAL_PRICE_ID",
    annualSavings: "Save £20.88!",
    description: "Most popular choice for busy teachers.",
    features: [
      "3 lessons per day",
      "90 lessons per month",
      "UK curriculum-aligned",
      "Advanced customisation",
      "Export as PDF, DOCX",
      "Priority support"
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Pro",
    planType: "pro" as const,
    monthlyPrice: "£12.99",
    annualPrice: "£120",
    monthlyPriceId: "YOUR_PRO_MONTHLY_PRICE_ID",
    annualPriceId: "YOUR_PRO_ANNUAL_PRICE_ID",
    annualSavings: "Save £35.88!",
    description: "For schools and high-volume planning.",
    features: [
      "5 lessons per day",
      "150 lessons per month",
      "UK curriculum-aligned",
      "Advanced customisation",
      "Export as PDF, DOCX, TXT",
      "Priority support"
    ],
    cta: "Start Free Trial",
    popular: false,
  }
];
```

## Step 4: Update Price IDs in Webhook Function

Open: `supabase/functions/stripe-webhook/index.ts`

Find the `getPlanFromPriceId` function (around line 64) and update:

```typescript
const getPlanFromPriceId = (priceId: string): string | null => {
  const priceMap: { [key: string]: string } = {
    'YOUR_STARTER_MONTHLY_PRICE_ID': 'starter',
    'YOUR_STARTER_ANNUAL_PRICE_ID': 'starter',
    'YOUR_STANDARD_MONTHLY_PRICE_ID': 'standard',
    'YOUR_STANDARD_ANNUAL_PRICE_ID': 'standard',
    'YOUR_PRO_MONTHLY_PRICE_ID': 'pro',
    'YOUR_PRO_ANNUAL_PRICE_ID': 'pro',
  };
  console.log('Mapping price_id:', priceId, '-> plan:', priceMap[priceId] || 'NOT FOUND');
  return priceMap[priceId] || null;
};
```

## Step 5: Set Up Webhook in Stripe

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "+ Add endpoint"
3. Endpoint URL:
   ```
   https://yemzxrleleujqplhynuz.supabase.co/functions/v1/stripe-webhook
   ```
4. Select these 3 events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Click "Add endpoint"
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add to Supabase secrets:
   - Go to: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz/settings/secrets
   - Name: `STRIPE_WEBHOOK_SECRET`
   - Value: `whsec_...` (your signing secret)

## Step 6: Test the Integration

### Test Card Details:
- **Card Number**: 4242 4242 4242 4242
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any 5 digits (e.g., 12345)

### Test Flow:
1. Go to: https://lessonlift.co.uk/signup
2. Create an account
3. Use 5 free trial lessons
4. Go to: https://lessonlift.co.uk/pricing
5. Click any plan button
6. Complete checkout with test card
7. You should be redirected to: https://lessonlift.co.uk/payment-success
8. Test that your plan limits are enforced

### Verify in Stripe:
- Events: https://dashboard.stripe.com/test/events
- Should see `checkout.session.completed`
- Click event → Check webhook delivery succeeded

## Done!

Your Stripe integration is complete. After updating the Price IDs and setting up the webhook, users can subscribe to any plan and their limits will be automatically enforced.

### Important URLs:
- **Your Site**: https://lessonlift.co.uk
- **Success Page**: https://lessonlift.co.uk/payment-success
- **Cancel Page**: https://lessonlift.co.uk/pricing
- **Stripe Dashboard**: https://dashboard.stripe.com/test
- **Supabase Dashboard**: https://supabase.com/dashboard/project/yemzxrleleujqplhynuz
