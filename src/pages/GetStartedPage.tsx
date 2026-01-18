import React from 'react';
import { Check, Shield, Lock } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Pricing from '../components/Pricing';

const GetStartedPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-cyan-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Get Started with
              <span className="text-[#4CAF50] block mt-2">LessonLift</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Choose your plan and start generating AI-powered lesson plans in seconds.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Component */}
      <Pricing />

      {/* Security and Guarantee Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gray-50 rounded-2xl shadow-lg p-8 lg:p-12">
            <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
              Secure & Trusted Payment Processing
            </h2>
            <div className="flex flex-col md:flex-row items-center justify-center space-y-6 md:space-y-0 md:space-x-12">
              {/* Security Icon */}
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-[#4CAF50] bg-opacity-10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Shield className="w-8 h-8 text-[#4CAF50]" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">Secure Payments</h3>
                  <p className="text-gray-600 text-sm">Powered by Stripe</p>
                </div>
              </div>

              {/* Lock Icon */}
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-[#4CAF50] bg-opacity-10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Lock className="w-8 h-8 text-[#4CAF50]" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">256-bit Encryption</h3>
                  <p className="text-gray-600 text-sm">Your data is safe</p>
                </div>
              </div>

              {/* Check Icon */}
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-[#4CAF50] bg-opacity-10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Check className="w-8 h-8 text-[#4CAF50]" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">Cancel Anytime</h3>
                  <p className="text-gray-600 text-sm">No long-term commitment</p>
                </div>
              </div>
            </div>

            <p className="text-center text-gray-700 mt-8 text-base">
              All payments are processed securely via Stripe. Start your free trial today with no credit card required.
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default GetStartedPage;
