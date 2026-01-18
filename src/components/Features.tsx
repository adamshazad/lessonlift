import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, BookOpen, Target, Zap } from 'lucide-react';

const Features: React.FC = () => {
  const features = [
    {
      icon: Clock,
      title: "Time-Saving AI Lessons",
      description: "Generate comprehensive lesson plans in under 30 seconds, freeing up hours for what matters most - teaching."
    },
    {
      icon: BookOpen,
      title: "UK Curriculum Aligned",
      description: "Every lesson plan is perfectly aligned with the UK National Curriculum standards and assessment objectives."
    },
    {
      icon: Target,
      title: "Personalized Learning",
      description: "Tailor lessons to your students' needs with adaptive content that matches different learning styles and abilities."
    },
    {
      icon: Zap,
      title: "Instant Customization",
      description: "Easily modify and adapt any lesson plan with our intuitive editing tools and resource suggestions."
    }
  ];

  return (
    <section id="features" className="py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Why Teachers Choose LessonLift
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover how our AI-powered platform transforms the way you plan and deliver engaging lessons.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 border border-gray-100 group"
            >
              {/* Icon */}
              <div className="w-16 h-16 bg-[#4CAF50] rounded-full flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-8 h-8 text-white" />
              </div>

              {/* Content */}
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center">
          <Link 
            to="/explore-features"
            className="inline-block bg-[#4CAF50] hover:bg-[#45a049] text-white px-10 py-5 rounded-2xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Explore All Features
          </Link>
        </div>
      </div>
    </section>
  );
};

export default Features;