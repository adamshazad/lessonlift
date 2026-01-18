import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Wand2, Download, Share2 } from 'lucide-react';

const HowItWorks: React.FC = () => {
  const steps = [
    {
      icon: MessageSquare,
      title: "Describe Your Lesson",
      description: "Tell us your subject, topic, year group, and any specific requirements in natural language."
    },
    {
      icon: Wand2,
      title: "AI Creates Your Plan",
      description: "Our advanced AI generates a comprehensive, curriculum-aligned lesson plan in seconds."
    },
    {
      icon: Download,
      title: "Review & Customize",
      description: "Edit, adapt, and personalize the lesson plan to perfectly fit your teaching style."
    },
    {
      icon: Share2,
      title: "Save & Share",
      description: "Export your lesson plan and share it with colleagues or save it to your personal library."
    }
  ];

  return (
    <section className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            How LessonLift Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Creating professional lesson plans has never been easier. Follow these simple steps to transform your teaching.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line - Hidden on mobile */}
          <div className="hidden lg:block absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 -translate-y-1/2"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Step Card */}
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 text-center relative z-10 border border-gray-100 group">
                  {/* Step Number */}
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 bg-[#4CAF50] rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {index + 1}
                  </div>

                  {/* Icon */}
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-6 mx-auto mt-4 group-hover:bg-[#4CAF50] transition-colors duration-300">
                    <step.icon className="w-8 h-8 text-[#4CAF50] group-hover:text-white" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Arrow for large screens */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                    <div className="w-8 h-8 bg-[#4CAF50] rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <Link
            to="/how-it-works"
            className="inline-block bg-[#4CAF50] hover:bg-[#45a049] text-white px-10 py-5 rounded-2xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Discover How LessonLift Works
          </Link>
          <p className="text-gray-500 mt-4">No credit card required • Free 7-day trial</p>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;