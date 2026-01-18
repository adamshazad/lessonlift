import React, { useState } from 'react'
import { Check } from 'lucide-react'
import { Button } from '../ui/Button'
import { createCheckoutSession } from '../../services/stripe'
import { StripeProduct } from '../../stripe-config'

interface PricingCardProps {
  product: StripeProduct
  isPopular?: boolean
  currentPlan?: string
}

export function PricingCard({ product, isPopular = false, currentPlan }: PricingCardProps) {
  const [loading, setLoading] = useState(false)

  const handleSubscribe = async () => {
    try {
      setLoading(true)
      const { url } = await createCheckoutSession({
        priceId: product.priceId,
        mode: product.mode,
        planType: product.planType,
      })

      if (url) {
        window.location.href = url
      }
    } catch (error) {
      console.error('Error creating checkout session:', error)
      alert('Failed to create checkout session. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const isCurrentPlan = currentPlan === product.name

  const features = getFeaturesByPlan(product.name)

  return (
    <div className={`relative bg-white rounded-2xl shadow-lg ${isPopular ? 'ring-2 ring-indigo-600' : ''}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}
      
      <div className="p-8">
        <h3 className="text-2xl font-bold text-gray-900">{product.name}</h3>
        <p className="mt-4 text-gray-600">{product.description}</p>
        
        <div className="mt-6">
          <span className="text-4xl font-bold text-gray-900">
            £{product.price}
          </span>
          <span className="text-gray-600">/month</span>
        </div>

        <ul className="mt-8 space-y-4">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              <span className="text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>

        <div className="mt-8">
          {isCurrentPlan ? (
            <Button variant="outline" className="w-full" disabled>
              Current Plan
            </Button>
          ) : (
            <Button
              onClick={handleSubscribe}
              loading={loading}
              className="w-full"
              variant={isPopular ? 'primary' : 'outline'}
            >
              Subscribe Now
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

function getFeaturesByPlan(planName: string): string[] {
  switch (planName) {
    case 'LessonLift – Starter':
      return [
        '1 lesson plan per day',
        '30 lesson plans per month',
        'PDF export',
        'Basic templates',
        'Email support'
      ]
    case 'LessonLift – Standard':
      return [
        '3 lesson plans per day',
        '90 lesson plans per month',
        'PDF & DOCX export',
        'Advanced templates',
        'Priority email support',
        'Lesson history'
      ]
    case 'LessonLift – Pro':
      return [
        '5 lesson plans per day',
        '150 lesson plans per month',
        'All export formats (PDF, DOCX, TXT)',
        'Premium templates',
        'Priority support',
        'Advanced lesson history',
        'Team collaboration'
      ]
    default:
      return []
  }
}