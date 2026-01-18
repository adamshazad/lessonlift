import React from 'react';
import { Link } from 'react-router-dom';
import { XCircle, ArrowRight, HelpCircle } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';

const PaymentCancelPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-white">
      <Header />

      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 text-center"
          >
            {/* Cancel Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-24 h-24 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-8"
            >
              <XCircle className="w-16 h-16 text-orange-600" />
            </motion.div>

            {/* Heading */}
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Payment Cancelled
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Your payment was not processed. No charges have been made.
            </p>

            {/* Info Box */}
            <div className="bg-gray-50 border-2 border-gray-200 rounded-2xl p-6 mb-8">
              <p className="text-gray-700 leading-relaxed">
                It looks like you cancelled the payment process or the transaction didn't complete.
                Don't worry — you can try again whenever you're ready!
              </p>
            </div>

            {/* Why Choose LessonLift */}
            <div className="text-left mb-8 bg-blue-50 rounded-2xl p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <HelpCircle className="w-6 h-6 text-[#4CAF50] mr-2" />
                Why Choose LessonLift?
              </h3>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="text-[#4CAF50] font-bold mr-3">✓</span>
                  <span>7-day free trial — generate up to 5 lesson plans</span>
                </li>
                <li className="flex items-start">
                  <span className="text-[#4CAF50] font-bold mr-3">✓</span>
                  <span>Plans starting from £4.99/month (Starter: 1/day, Standard: 3/day, Pro: 5/day)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-[#4CAF50] font-bold mr-3">✓</span>
                  <span>Cancel anytime — no long-term commitment required</span>
                </li>
                <li className="flex items-start">
                  <span className="text-[#4CAF50] font-bold mr-3">✓</span>
                  <span>UK curriculum-aligned, instantly generated lesson plans</span>
                </li>
              </ul>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/get-started"
                className="inline-flex items-center justify-center space-x-2 bg-[#4CAF50] text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-[#45a049] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <span>Try Again</span>
                <ArrowRight className="w-5 h-5" />
              </Link>

              <Link
                to="/"
                className="inline-flex items-center justify-center space-x-2 bg-white text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg border-2 border-gray-300 hover:border-gray-400 transition-all duration-300 shadow-md hover:shadow-lg"
              >
                <span>Back to Home</span>
              </Link>
            </div>

            <p className="text-gray-500 text-sm mt-8">
              Have questions? Contact us at{' '}
              <a href="mailto:support@lessonlift.com" className="text-[#4CAF50] hover:underline">
                support@lessonlift.com
              </a>
            </p>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default PaymentCancelPage;
