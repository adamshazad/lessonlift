export interface StripeProduct {
  id: string;
  priceId: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  currencySymbol: string;
  mode: 'subscription' | 'payment';
  planType: 'starter' | 'standard' | 'pro';
}

export const STRIPE_PRODUCTS: StripeProduct[] = [
  {
    id: 'prod_TnAum2tJCPsAXA',
    priceId: 'price_1SpaYECVrhYYeZRkoBDVNJU1',
    name: 'LessonLift – Starter',
    description: '1 lesson plan per day. Ideal for individual teachers.',
    price: 5.00,
    currency: 'gbp',
    currencySymbol: '£',
    mode: 'subscription',
    planType: 'starter'
  },
  {
    id: 'prod_TnAuHIxKdvWdv6',
    priceId: 'price_1SpaYaCVrhYYeZRkzoB3NAVC',
    name: 'LessonLift – Standard',
    description: '3 lesson plans per day. Perfect for regular classroom use.',
    price: 8.00,
    currency: 'gbp',
    currencySymbol: '£',
    mode: 'subscription',
    planType: 'standard'
  },
  {
    id: 'prod_TnAuPA6dWzUD4e',
    priceId: 'price_1SpaYuCVrhYYeZRkL3hXHreu',
    name: 'LessonLift – Pro',
    description: '5 lesson plans per day. Best for power users and departments.',
    price: 13.00,
    currency: 'gbp',
    currencySymbol: '£',
    mode: 'subscription',
    planType: 'pro'
  }
];

export const getProductByPriceId = (priceId: string): StripeProduct | undefined => {
  return STRIPE_PRODUCTS.find(product => product.priceId === priceId);
};

export const getProductByName = (name: string): StripeProduct | undefined => {
  return STRIPE_PRODUCTS.find(product => product.name === name);
};