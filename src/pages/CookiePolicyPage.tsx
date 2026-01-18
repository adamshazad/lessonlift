import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const CookiePolicyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />

      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Cookie Policy
          </h1>
          <p className="text-gray-600 mb-8">
            Last updated: January 2025
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. What Are Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Cookies are small text files that are placed on your computer or mobile device when you visit a website.
                They are widely used to make websites work more efficiently and provide information to the website owners.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                LessonLift uses cookies to enhance your experience, understand how you use our service, and improve
                our platform based on your preferences and usage patterns.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. How We Use Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We use cookies for the following purposes:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li><strong>Essential Cookies:</strong> These are necessary for the website to function properly and cannot be disabled. They enable core functionality like security, account authentication, and service accessibility.</li>
                <li><strong>Performance Cookies:</strong> These help us understand how visitors interact with our website by collecting anonymous information about page visits and user behavior.</li>
                <li><strong>Functional Cookies:</strong> These remember your preferences and choices to provide enhanced, personalized features.</li>
                <li><strong>Analytics Cookies:</strong> These help us improve our service by analyzing how users navigate and interact with LessonLift.</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Types of Cookies We Use</h2>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Session Cookies</h3>
                <p className="text-gray-700 leading-relaxed mb-4">
                  These are temporary cookies that remain in your browser only until you leave our website. They are
                  essential for maintaining your login session and ensuring smooth navigation through the site.
                </p>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Persistent Cookies</h3>
                <p className="text-gray-700 leading-relaxed mb-4">
                  These cookies remain on your device for a set period or until you delete them. They help us remember
                  your preferences and provide a more personalized experience when you return to LessonLift.
                </p>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">First-Party Cookies</h3>
                <p className="text-gray-700 leading-relaxed mb-4">
                  These are set directly by LessonLift and are used to operate and improve our service.
                </p>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Third-Party Cookies</h3>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We may use third-party services like analytics providers that set their own cookies. These help us
                  understand user behavior and improve our service. Common third-party cookies include:
                </p>
                <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                  <li>Google Analytics for website traffic analysis</li>
                  <li>Authentication providers for secure login</li>
                  <li>Payment processors for subscription management</li>
                </ul>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Managing Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                You have the right to decide whether to accept or reject cookies. You can exercise your cookie preferences by:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li><strong>Browser Settings:</strong> Most web browsers automatically accept cookies, but you can modify your browser settings to decline cookies if you prefer. Please note that disabling cookies may affect the functionality of our website.</li>
                <li><strong>Cookie Consent Tool:</strong> When you first visit LessonLift, you can choose which types of cookies to accept through our cookie consent banner.</li>
                <li><strong>Opt-Out Links:</strong> For third-party cookies, you can use opt-out mechanisms provided by the respective services.</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. How to Control Cookies in Your Browser</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Most browsers allow you to control cookies through their settings. Here are links to cookie management
                information for popular browsers:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2 mb-4">
                <li><strong>Google Chrome:</strong> Settings → Privacy and security → Cookies and other site data</li>
                <li><strong>Mozilla Firefox:</strong> Settings → Privacy & Security → Cookies and Site Data</li>
                <li><strong>Safari:</strong> Preferences → Privacy → Cookies and website data</li>
                <li><strong>Microsoft Edge:</strong> Settings → Privacy, search, and services → Cookies and site permissions</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mb-4">
                Please note that if you choose to block all cookies, you may not be able to access all or parts of our service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Cookies and Personal Data</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Some cookies may collect personal data about you. We treat all data collected through cookies in accordance
                with our Privacy Policy. The information collected through cookies may be combined with other information
                we collect about you to improve our service and provide personalized features.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Updates to This Cookie Policy</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We may update this Cookie Policy from time to time to reflect changes in our practices or for other
                operational, legal, or regulatory reasons. We encourage you to review this policy periodically to stay
                informed about our use of cookies.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Contact Us</h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                If you have any questions about our use of cookies or this Cookie Policy, please contact us at:
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

export default CookiePolicyPage;
