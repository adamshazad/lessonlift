import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, loading, signOut } = useAuth();

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
    setIsMenuOpen(false);
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Handle scrolling to pricing section after navigation
    if (location.pathname === '/' && location.hash === '#pricing') {
      setTimeout(() => {
        const pricingSection = document.getElementById('pricing');
        if (pricingSection) {
          pricingSection.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  }, [location]);


  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
      className={`bg-white sticky top-0 z-50 transition-all duration-300 ${
        isScrolled ? 'shadow-lg border-b border-gray-100' : 'shadow-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <img
              src="/20250913_141827376_iOS.jpg"
              alt="LessonLift Logo"
              className="h-12 w-auto transition-transform duration-300 group-hover:scale-110"
            />
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-[#4CAF50] transition-all duration-300 font-semibold text-base relative group">
              Home
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#4CAF50] transition-all duration-300 group-hover:w-full"></span>
            </Link>
            <Link to="/how-it-works" className="text-gray-700 hover:text-[#4CAF50] transition-all duration-300 font-semibold text-base relative group">
              How It Works
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#4CAF50] transition-all duration-300 group-hover:w-full"></span>
            </Link>
            <Link to="/explore-features" className="text-gray-700 hover:text-[#4CAF50] transition-all duration-300 font-semibold text-base relative group">
              Features
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#4CAF50] transition-all duration-300 group-hover:w-full"></span>
            </Link>
            <Link to="/get-started" className="text-gray-700 hover:text-[#4CAF50] transition-all duration-300 font-semibold text-base relative group">
              Pricing
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#4CAF50] transition-all duration-300 group-hover:w-full"></span>
            </Link>
            {!loading && (
              user ? (
                <>
                  <Link to="/lesson-generator" className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-6 py-2.5 rounded-lg font-bold text-base transition-all duration-300 shadow-sm hover:shadow-md inline-block">
                    Go to Generator
                  </Link>
                  <button
                    onClick={handleSignOut}
                    className="flex items-center gap-2 text-gray-700 hover:text-red-600 transition-all duration-300 font-semibold text-base"
                  >
                    <LogOut size={18} />
                    Sign Out
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-gray-700 hover:text-[#4CAF50] transition-all duration-300 font-semibold text-base">
                    Log in
                  </Link>
                  <Link to="/signup" className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-6 py-2.5 rounded-lg font-bold text-base transition-all duration-300 shadow-sm hover:shadow-md inline-block">
                    Sign up
                  </Link>
                </>
              )
            )}
          </nav>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2.5 rounded-xl hover:bg-gray-100 transition-all duration-300"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={26} /> : <Menu size={26} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="md:hidden border-t border-gray-100 overflow-hidden"
            >
              <nav className="flex flex-col space-y-1 py-4">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-[#4CAF50] hover:bg-gray-50 transition-all duration-300 font-semibold py-3 px-4 rounded-xl"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Home
                </Link>
                <Link
                  to="/how-it-works"
                  className="text-gray-700 hover:text-[#4CAF50] hover:bg-gray-50 transition-all duration-300 font-semibold py-3 px-4 rounded-xl"
                  onClick={() => setIsMenuOpen(false)}
                >
                  How It Works
                </Link>
                <Link
                  to="/explore-features"
                  className="text-gray-700 hover:text-[#4CAF50] hover:bg-gray-50 transition-all duration-300 font-semibold py-3 px-4 rounded-xl"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Features
                </Link>
                <Link
                  to="/get-started"
                  className="text-gray-700 hover:text-[#4CAF50] hover:bg-gray-50 transition-all duration-300 font-semibold py-3 px-4 rounded-xl"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Pricing
                </Link>
                {!loading && (
                  <div className="pt-2 space-y-2">
                    {user ? (
                      <>
                        <Link
                          to="/lesson-generator"
                          className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-4 py-3 rounded-xl font-bold w-full transition-all duration-300 shadow-sm hover:shadow-md block text-center"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          Go to Generator
                        </Link>
                        <button
                          onClick={handleSignOut}
                          className="flex items-center justify-center gap-2 border-2 border-red-300 hover:border-red-500 text-red-600 hover:text-red-700 px-4 py-3 rounded-xl font-semibold w-full transition-all duration-300"
                        >
                          <LogOut size={18} />
                          Sign Out
                        </button>
                      </>
                    ) : (
                      <>
                        <Link
                          to="/login"
                          className="border-2 border-gray-300 hover:border-[#4CAF50] text-gray-700 hover:text-[#4CAF50] px-4 py-3 rounded-xl font-semibold w-full transition-all duration-300 block text-center"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          Log in
                        </Link>
                        <Link
                          to="/signup"
                          className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-4 py-3 rounded-xl font-bold w-full transition-all duration-300 shadow-sm hover:shadow-md block text-center"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          Sign up
                        </Link>
                      </>
                    )}
                  </div>
                )}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.header>
  );
};

export default Header;