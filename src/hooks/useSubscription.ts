import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { useAuth } from './useAuth'
import { getProductByPriceId } from '../stripe-config'

export interface SubscriptionData {
  customer_id: string | null
  subscription_id: string | null
  subscription_status: string | null
  price_id: string | null
  current_period_start: number | null
  current_period_end: number | null
  cancel_at_period_end: boolean | null
  payment_method_brand: string | null
  payment_method_last4: string | null
}

export function useSubscription() {
  const { user } = useAuth()
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) {
      setSubscription(null)
      setLoading(false)
      return
    }

    const fetchSubscription = async () => {
      try {
        setLoading(true)
        setError(null)

        const { data, error } = await supabase
          .from('stripe_user_subscriptions')
          .select('*')
          .maybeSingle()

        if (error) {
          console.error('Error fetching subscription:', error)
          setError('Failed to fetch subscription data')
          return
        }

        setSubscription(data)
      } catch (err) {
        console.error('Unexpected error:', err)
        setError('An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchSubscription()
  }, [user])

  const getActivePlan = () => {
    if (!subscription?.price_id) return null
    return getProductByPriceId(subscription.price_id)
  }

  const isActive = () => {
    return subscription?.subscription_status === 'active'
  }

  const isTrialing = () => {
    return subscription?.subscription_status === 'trialing'
  }

  const isCanceled = () => {
    return subscription?.subscription_status === 'canceled'
  }

  return {
    subscription,
    loading,
    error,
    getActivePlan,
    isActive,
    isTrialing,
    isCanceled,
    refetch: () => {
      if (user) {
        setLoading(true)
        // Trigger re-fetch by updating a dependency
        setSubscription(null)
      }
    }
  }
}