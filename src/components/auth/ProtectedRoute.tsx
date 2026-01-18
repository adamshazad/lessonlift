import React, { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { supabase } from '../../lib/supabase'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireActivePlan?: boolean
}

export function ProtectedRoute({ children, requireActivePlan = false }: ProtectedRouteProps) {
  const { user, loading: authLoading } = useAuth()
  const [planStatus, setPlanStatus] = useState<any>(null)
  const [planLoading, setPlanLoading] = useState(requireActivePlan)

  useEffect(() => {
    if (requireActivePlan && user) {
      checkPlanStatus()
    } else if (!requireActivePlan) {
      setPlanLoading(false)
    }
  }, [user, requireActivePlan])

  const checkPlanStatus = async () => {
    if (!user) {
      setPlanLoading(false)
      return
    }

    try {
      const { data, error } = await supabase.rpc('get_user_subscription_status', {
        p_user_id: user.id
      })

      if (error) {
        console.error('Error fetching plan status:', error)
        setPlanStatus(null)
      } else {
        setPlanStatus(data)
      }
    } catch (err) {
      console.error('Error checking plan status:', err)
      setPlanStatus(null)
    } finally {
      setPlanLoading(false)
    }
  }

  if (authLoading || planLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#4CAF50]"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (requireActivePlan && planStatus) {
    if (planStatus.is_trial && planStatus.is_expired) {
      return <Navigate to="/pricing" replace />
    }

    if (!planStatus.is_trial && !planStatus.has_paid_plan) {
      return <Navigate to="/pricing" replace />
    }
  }

  return <>{children}</>
}