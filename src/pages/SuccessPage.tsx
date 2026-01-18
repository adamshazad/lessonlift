import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { useSubscription } from '../hooks/useSubscription'

export function SuccessPage() {
  const { refetch } = useSubscription()

  useEffect(() => {
    // Refetch subscription data after successful payment
    const timer = setTimeout(() => {
      refetch()
    }, 2000)

    return () => clearTimeout(timer)
  }, [refetch])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow rounded-lg text-center">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Payment Successful!
          </h1>
          
          <p className="text-gray-600 mb-6">
            Thank you for subscribing to LessonLift. Your account has been upgraded and you can now start creating amazing lesson plans.
          </p>
          
          <div className="space-y-3">
            <Link to="/" className="block">
              <Button className="w-full">
                Go to Dashboard
              </Button>
            </Link>
            
            <Link to="/pricing" className="block">
              <Button variant="outline" className="w-full">
                View Plans
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}