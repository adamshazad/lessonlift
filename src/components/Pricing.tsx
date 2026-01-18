import React, { useEffect, useState } from 'react';
import { Check, Star, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { createCheckoutSession } from '../utils/stripe';
import { useNavigate } from 'react-router-dom';

const Pricing: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handlePlanClick = async (planType: 'starter' | 'standard' | 'pro', priceId: string) => {
    if (!user) {
      navigate('/signup');
      return;
    }

    setLoadingPlan(planType);
    try {
      await createCheckoutSession({
        priceId,
        planType
      });
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to start checkout. Please try again.');
      setLoadingPlan(null);
    }
  };

  const standardPlans = [
    {
      name: "Starter",
      planType: "starter" as const,
      monthlyPrice: "£4.99",
      annualPrice: "£45",
      monthlyPriceId: "price_1SpaYECVrhYYeZRkoBDVNJU1",
      annualPriceId: "price_1SpaYECVrhYYeZRkoBDVNJU1",
      annualSavings: "Save £14.88!",
      description: "Perfect for trying out LessonLift.",
      features: [
        "1 lesson per day",
        "30 lessons per month",
        "UK curriculum-aligned",
        "Export as PDF",
        "Email support"
      ],
      cta: "Choose Starter",
      popular: false,
    },
    {
      name: "Standard",
      planType: "standard" as const,
      monthlyPrice: "£7.99",
      annualPrice: "£75",
      monthlyPriceId: "price_1SpaYaCVrhYYeZRkzoB3NAVC",
      annualPriceId: "price_1SpaYaCVrhYYeZRkzoB3NAVC",
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
      cta: "Choose Standard",
      popular: true,
    },
    {
      name: "Pro",
      planType: "pro" as const,
      monthlyPrice: "£12.99",
      annualPrice: "£120",
      monthlyPriceId: "price_1SpaYuCVrhYYeZRkL3hXHreu",
      annualPriceId: "price_1SpaYuCVrhYYeZRkL3hXHreu",
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
      cta: "Choose Pro",
      popular: false,
    }
  ];

  const displayPrice = (plan: typeof standardPlans[0]) => {
    return billingCycle === 'monthly' ? plan.monthlyPrice : plan.annualPrice;
  };

  const displayPeriod = () => {
    return billingCycle === 'monthly' ? 'per month' : 'per year';
  };

  return (
    <section id="pricing" className="py-16 sm:py-20 lg:py-24 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Free Trial Section */}
        <div className="bg-gradient-to-br from-[#4CAF50] to-[#45a049] rounded-3xl p-8 sm:p-12 lg:p-16 mb-16 sm:mb-20 shadow-lg text-white text-center">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4 tracking-tight">
            Start Your 7-Day Free Trial Today!
          </h2>
          <p className="text-lg sm:text-xl mb-2 opacity-95">
            Generate up to 5 lesson plans. No credit card required.
          </p>
          <p className="text-base sm:text-lg opacity-90 mb-8 max-w-2xl mx-auto">
            Experience the full power of LessonLift completely free for 7 days. Explore all customisation features and see how much time you can save on lesson planning. Cancel anytime, no hidden charges.
          </p>
          <a href="/signup" className="inline-block bg-white text-[#4CAF50] px-8 sm:px-10 py-4 rounded-lg font-bold text-base sm:text-lg hover:bg-gray-100 transition-all duration-200 shadow-md hover:shadow-lg">
            Start Free Trial
          </a>
        </div>

        {/* Section Header */}
        <div className="text-center mb-12 sm:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-6 tracking-tight">
            Simple, Transparent Pricing
          </h2>

          {/* Billing Toggle */}
          <div className="flex justify-center items-center gap-4 mb-12">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 sm:px-8 py-3 rounded-lg font-semibold transition-all duration-200 ${
                billingCycle === 'monthly'
                  ? 'bg-[#4CAF50] text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 sm:px-8 py-3 rounded-lg font-semibold transition-all duration-200 ${
                billingCycle === 'annual'
                  ? 'bg-[#4CAF50] text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Annual
            </button>
          </div>
        </div>

        {/* Standard Plans */}
        <div className="mb-16 sm:mb-20">
          <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-10 text-center">Individual Plans</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
            {standardPlans.map((plan, index) => (
              <div
                key={index}
                style={{ animationDelay: `${index * 100}ms` }}
                className={`pricing-card relative bg-white rounded-2xl flex flex-col h-full will-change-transform will-change-shadow transition-all duration-300 ${
                  isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                } ${
                  plan.popular
                    ? 'border-2 border-[#4CAF50] shadow-xl hover:shadow-2xl'
                    : 'border border-gray-200 shadow-md hover:shadow-xl'
                } hover:-translate-y-1`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <div className="bg-[#4CAF50] text-white px-4 sm:px-5 py-2 rounded-full flex items-center gap-1.5 text-xs font-semibold shadow-lg">
                      <Star size={14} fill="currentColor" />
                      <span>Most Popular</span>
                    </div>
                  </div>
                )}

                <div className="p-6 sm:p-8 lg:p-10 flex flex-col flex-grow">
                  {/* Plan Header */}
                  <div className="text-center mb-8">
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 tracking-tight">{plan.name}</h3>
                    <div className="flex items-baseline justify-center mb-2">
                      <span className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight">
                        {displayPrice(plan)}
                      </span>
                      <span className="text-gray-500 ml-2 text-sm font-medium">/{displayPeriod()}</span>
                    </div>
                    {billingCycle === 'annual' && (
                      <div className="text-sm font-semibold text-[#4CAF50] mb-3">
                        {plan.annualSavings}
                      </div>
                    )}
                    <p className="text-gray-600 text-sm sm:text-base leading-relaxed">{plan.description}</p>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-3.5 mb-8 flex-grow">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-0.5">
                          <Check size={20} className="text-[#4CAF50]" strokeWidth={2.5} />
                        </div>
                        <span className="text-gray-700 text-sm leading-relaxed">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <button
                    onClick={() => handlePlanClick(
                      plan.planType,
                      billingCycle === 'monthly' ? plan.monthlyPriceId : plan.annualPriceId
                    )}
                    disabled={loadingPlan === plan.planType}
                    className={`relative block w-full py-3.5 px-6 rounded-lg font-semibold text-base transition-all duration-200 text-center overflow-hidden ${
                      loadingPlan === plan.planType ? 'cursor-wait opacity-75' : ''
                    } ${
                      plan.popular
                        ? 'bg-[#4CAF50] hover:bg-[#45a049] text-white shadow-sm hover:shadow-md active:scale-98'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900 shadow-sm hover:shadow active:scale-98'
                    }`}
                  >
                    {loadingPlan === plan.planType ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 size={18} className="animate-spin" />
                        <span>Processing...</span>
                      </span>
                    ) : (
                      plan.cta
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* School Plans */}
        <div className="mb-12 sm:mb-16">
          <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-10 text-center">School Plans</h3>
          <p className="text-center text-gray-600 mb-10 max-w-2xl mx-auto">
            Custom pricing for primary schools. Each school typically has around 10 teachers on a LessonLift subscription.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 max-w-4xl mx-auto">
            {/* Monthly School Plan */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-md hover:shadow-xl transition-all duration-300 p-8 flex flex-col">
              <h4 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 text-center">Monthly</h4>
              <p className="text-center text-gray-600 mb-8 flex-grow">
                Flexible month-to-month billing for your school's teaching team.
              </p>
              <a
                href="#contact"
                className="block w-full py-3.5 px-6 rounded-lg font-semibold text-base transition-all duration-200 text-center bg-gray-100 hover:bg-gray-200 text-gray-900 shadow-sm hover:shadow active:scale-98"
              >
                Contact Us
              </a>
            </div>

            {/* Annual School Plan */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-md hover:shadow-xl transition-all duration-300 p-8 flex flex-col">
              <h4 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 text-center">Annual</h4>
              <p className="text-center text-gray-600 mb-8 flex-grow">
                Annual pricing with discounts for committing to the full year.
              </p>
              <a
                href="#contact"
                className="block w-full py-3.5 px-6 rounded-lg font-semibold text-base transition-all duration-200 text-center bg-gray-100 hover:bg-gray-200 text-gray-900 shadow-sm hover:shadow active:scale-98"
              >
                Contact Us
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="text-center mt-12 sm:mt-16 space-y-3 border-t border-gray-200 pt-8 sm:pt-12">
          <p className="text-base text-gray-600">
            All individual plans include a 7-day free trial. Cancel anytime, no hidden fees.
          </p>
          <p className="text-sm text-gray-500">
            Questions about pricing? <a href="#contact" className="text-[#4CAF50] hover:text-[#45a049] underline underline-offset-2 transition-colors">Get in touch</a> for more information.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing;