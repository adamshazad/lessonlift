import React from 'react'
import { stripeProducts } from '../../stripe-config'
import { PricingCard } from './PricingCard'
import { useSubscription } from '../../hooks/useSubscription'

export function PricingPage() {
  const { subscription, loading } = useSubscription()

  const currentPlan = subscription?.price_id 
    ? stripeProducts.find(p => p.priceId === subscription.price_id)?.name
    : undefined

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
            Choose Your Plan
          </h1>
          <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
            Select the perfect plan for your teaching needs. All plans include our core lesson planning features.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center mt-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
            {stripeProducts.map((product, index) => (
              <PricingCard
                key={product.id}
                product={product}
                isPopular={index === 1} // Make Standard plan popular
                currentPlan={currentPlan}
              />
            ))}
          </div>
        )}

        <div className="mt-16 text-center">
          <p className="text-gray-600">
            All plans include a 7-day free trial. Cancel anytime.
          </p>
        </div>
      </div>
    </div>
  )
}