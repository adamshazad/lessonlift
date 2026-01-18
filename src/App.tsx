import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import ScrollToTop from './components/ScrollToTop';
import { Pricing } from './pages/Pricing';
import { Success } from './pages/Success';
import LandingPage from './pages/LandingPage';
import FeaturesPage from './pages/FeaturesPage';
import ExploreFeaturesPage from './pages/ExploreFeaturesPage';
import HowItWorksPage from './pages/HowItWorksPage';
import GetStartedPage from './pages/GetStartedPage';
import { LoginPage } from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import LessonGeneratorPage from './pages/LessonGeneratorPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import DataProtectionPage from './pages/DataProtectionPage';
import PaymentSuccessPage from './pages/PaymentSuccessPage';
import PaymentCancelPage from './pages/PaymentCancelPage';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <ScrollToTop />
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/success" element={<Success />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/explore-features" element={<ExploreFeaturesPage />} />
            <Route path="/get-started" element={<GetStartedPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route
              path="/lesson-generator"
              element={
                <ProtectedRoute requireActivePlan={true}>
                  <LessonGeneratorPage />
                </ProtectedRoute>
              }
            />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="/terms-of-service" element={<TermsOfServicePage />} />
            <Route path="/cookie-policy" element={<CookiePolicyPage />} />
            <Route path="/data-protection" element={<DataProtectionPage />} />
            <Route path="/payment-success" element={<PaymentSuccessPage />} />
            <Route path="/payment-cancel" element={<PaymentCancelPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App;