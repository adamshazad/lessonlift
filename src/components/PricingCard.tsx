import React, { useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { StripeProduct } from '../stripe-config';

interface PricingCardProps {
  product: StripeProduct;
  isPopular?: boolean;
  onSubscribe: (priceId: string) => Promise<void>;
  disabled?: boolean;
  currentPlan?: string;
}

export function PricingCard({ 
  product, 
  isPopular = false, 
  onSubscribe, 
  disabled = false,
  currentPlan 
}: PricingCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubscribe = async () => {
    if (disabled || isLoading) return;
    
    setIsLoading(true);
    try {
      await onSubscribe(product.priceId);
    } catch (error) {
      console.error('Subscription error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const planType = product.name.split(' – ')[1]?.toLowerCase();
  const isCurrentPlan = currentPlan === planType;

  const features = [
    `${product.description.split('.')[0]}`,
    'PDF export',
    ...(planType === 'standard' || planType === 'pro' ? ['DOCX export'] : []),
    ...(planType === 'pro' ? ['TXT export', 'Priority support'] : []),
    'Cancel anytime'
  ];

  return (
    <div className={`relative bg-white rounded-2xl shadow-lg border-2 transition-all duration-300 hover:shadow-xl ${
      isPopular ? 'border-indigo-500 scale-105' : 'border-gray-200'
    }`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-indigo-500 text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}
      
      <div className="p-8">
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            {product.name.split(' – ')[1]}
          </h3>
          <div className="flex items-center justify-center mb-4">
            <span className="text-4xl font-bold text-gray-900">
              {product.currencySymbol}{product.price}
            </span>
            <span className="text-gray-500 ml-2">/month</span>
          </div>
          <p className="text-gray-600">{product.description}</p>
        </div>

        <ul className="space-y-4 mb-8">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center">
              <Check className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
              <span className="text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>

        <button
          onClick={handleSubscribe}
          disabled={disabled || isLoading || isCurrentPlan}
          className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-200 flex items-center justify-center ${
            isCurrentPlan
              ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
              : isPopular
              ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-xl'
              : 'bg-gray-900 hover:bg-gray-800 text-white'
          } ${(disabled || isLoading) && !isCurrentPlan ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Processing...
            </>
          ) : isCurrentPlan ? (
            'Current Plan'
          ) : (
            'Subscribe Now'
          )}
        </button>
      </div>
    </div>
  );
}