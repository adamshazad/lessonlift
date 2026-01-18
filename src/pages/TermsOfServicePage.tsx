import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const TermsOfServicePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />

      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Terms of Service
          </h1>
          <p className="text-gray-600 mb-8">
            Last updated: January 2025
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                By accessing and using LessonLift, you accept and agree to be bound by the terms and provision of this
                agreement. If you do not agree to these Terms of Service, please do not use our service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                LessonLift is an AI-powered lesson planning platform designed for UK teachers. We provide tools to
                generate, customize, and export curriculum-aligned lesson plans. The service includes:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>AI-generated lesson plan creation based on UK National Curriculum</li>
                <li>Customization and editing tools for lesson plans</li>
                <li>Export functionality in multiple formats (PDF, DOCX)</li>
                <li>Daily plan limits based on subscription tier</li>
                <li>Resource suggestions and teaching materials</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Accounts</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                To access certain features of LessonLift, you must register for an account. You agree to:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>Provide accurate, current, and complete information during registration</li>
                <li>Maintain and promptly update your account information</li>
                <li>Maintain the security of your password and account</li>
                <li>Accept all responsibility for activities that occur under your account</li>
                <li>Notify us immediately of any unauthorized use of your account</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Subscription and Payment</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                LessonLift offers both free trial and paid subscription plans:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>Free trials are limited to 7 days with up to 5 lesson plans per day</li>
                <li>Paid subscriptions provide higher daily limits and additional features</li>
                <li>Payment is processed monthly and automatically renews unless cancelled</li>
                <li>Cancellations take effect at the end of the current billing period</li>
                <li>No refunds are provided for partial months of service</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Usage Limits and Fair Use</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Each subscription tier includes specific daily lesson plan generation limits. These limits are designed
                to ensure fair use and maintain service quality for all users. Attempting to circumvent these limits
                may result in account suspension or termination.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Intellectual Property</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                The lesson plans you create using LessonLift are yours to use for your teaching purposes. However:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>You retain ownership of your customized lesson plans</li>
                <li>LessonLift retains all rights to the platform, software, and underlying technology</li>
                <li>You may not resell or commercially distribute AI-generated content without authorization</li>
                <li>You grant us a license to use anonymized data to improve our service</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Prohibited Uses</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You agree not to use LessonLift to:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe upon intellectual property rights</li>
                <li>Share your account credentials with unauthorized users</li>
                <li>Attempt to reverse engineer or copy our software</li>
                <li>Use automated systems to access the service beyond normal usage</li>
                <li>Generate content that is harmful, offensive, or inappropriate for educational settings</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Service Availability</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                While we strive to maintain continuous service availability, we do not guarantee uninterrupted access.
                We may temporarily suspend service for maintenance, updates, or unforeseen technical issues. We will
                provide advance notice when possible.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Disclaimer of Warranties</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                LessonLift is provided "as is" without warranties of any kind. While our AI generates lesson plans
                aligned with UK curriculum standards, teachers are responsible for reviewing and adapting content
                to ensure it meets their specific classroom needs and complies with their school's policies.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                To the fullest extent permitted by law, LessonLift shall not be liable for any indirect, incidental,
                special, consequential, or punitive damages resulting from your use of or inability to use the service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Termination</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may terminate or suspend your account and access to the service immediately, without prior notice,
                for conduct that we believe violates these Terms of Service or is harmful to other users, us, or
                third parties, or for any other reason.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Changes to Terms</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We reserve the right to modify these Terms of Service at any time. We will notify users of any
                material changes via email or through the service. Continued use of LessonLift after changes
                constitutes acceptance of the modified terms.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Governing Law</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                These Terms shall be governed by and construed in accordance with the laws of England and Wales,
                without regard to its conflict of law provisions.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have any questions about these Terms of Service, please contact us at:
              </p>
              <p className="text-gray-700 leading-relaxed">
                Email: lessonliftapp@gmail.com<br />
                Address: London, United Kingdom
              </p>
            </section>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default TermsOfServicePage;
