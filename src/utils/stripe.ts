import { supabase } from '../contexts/AuthContext';

interface CheckoutSessionParams {
  priceId: string;
  planType: 'starter' | 'standard' | 'pro';
}

export async function createCheckoutSession({ priceId, planType }: CheckoutSessionParams): Promise<void> {
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;

  if (!supabaseUrl) {
    throw new Error('Supabase URL not configured');
  }

  // Get the current user's session token
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    throw new Error('You must be logged in to checkout');
  }

  const apiUrl = `${supabaseUrl}/functions/v1/create-checkout-session`;

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ priceId, planType }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    console.error('Checkout error:', errorData);
    throw new Error(errorData.error || 'Failed to create checkout session');
  }

  const { url } = await response.json();

  if (!url) {
    throw new Error('No Stripe checkout URL returned');
  }

  window.location.href = url;
}
