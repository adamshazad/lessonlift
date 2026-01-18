import { supabase } from '../lib/supabase'

export interface CreateCheckoutSessionParams {
  priceId: string
  mode: 'subscription' | 'payment'
  planType?: 'starter' | 'standard' | 'pro'
  successUrl?: string
  cancelUrl?: string
}

export async function createCheckoutSession({
  priceId,
  mode,
  planType,
  successUrl = `${window.location.origin}/success`,
  cancelUrl = `${window.location.origin}/pricing`
}: CreateCheckoutSessionParams) {
  const { data: { session } } = await supabase.auth.getSession()

  if (!session?.access_token) {
    throw new Error('No active session found')
  }

  const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/stripe-checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    },
    body: JSON.stringify({
      price_id: priceId,
      mode,
      plan_type: planType,
      success_url: successUrl,
      cancel_url: cancelUrl,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error || 'Failed to create checkout session')
  }

  const data = await response.json()
  return data
}