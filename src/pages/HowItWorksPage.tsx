import React from 'react';
import { BookOpen, Wand2, CreditCard as Edit3, Save, TrendingUp, Clock, CheckCircle, Download, Lightbulb, ArrowRight } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const HowItWorksPage: React.FC = () => {
  const steps = [
    {
      number: 1,
      icon: BookOpen,
      title: "Enter Your Topic or Lesson Title",
      description: "Simply type in your subject, topic, and year group to get started."
    },
    {
      number: 2,
      icon: Wand2,
      title: "AI Generates a Full UK Curriculum-Aligned Plan",
      description: "LessonLift creates a complete lesson plan with objectives, activities, differentiation, and assessments in under 30 seconds."
    },
    {
      number: 3,
      icon: Edit3,
      title: "Edit or Adapt to Your Teaching Style",
      description: "Customize any section to match your classroom needs and preferences."
    },
    {
      number: 4,
      icon: Download,
      title: "Export in PDF or Word Format",
      description: "Download your finished lesson plan ready to use or share with colleagues."
    },
    {
      number: 5,
      icon: TrendingUp,
      title: "Repeat Within Your Daily Plan Limit",
      description: "Free Trial: up to 5 plans total. Starter: 1/day, Standard: 3/day, Pro: 5/day"
    }
  ];

  const benefits = [
    {
      icon: Clock,
      title: "Saves Hours of Planning",
      description: "Generate complete lesson plans in seconds instead of spending hours creating them from scratch."
    },
    {
      icon: CheckCircle,
      title: "UK Curriculum Focused",
      description: "Every lesson plan aligns with the latest UK National Curriculum standards and objectives."
    },
    {
      icon: Download,
      title: "Easy to Export & Share",
      description: "Download your plans as PDF or DOCX and share them with colleagues effortlessly."
    },
    {
      icon: Lightbulb,
      title: "Inspires Better Lessons",
      description: "Get fresh ideas, activities, and resources to make your teaching more engaging and effective."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-cyan-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              How
              <span className="text-[#4CAF50] block mt-2">LessonLift Works</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Your AI-powered assistant for creating structured, curriculum-aligned lesson plans — fast.
            </p>
          </div>

          {/* Video Section */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
                <iframe
                  className="absolute top-0 left-0 w-full h-full"
                  src="https://www.youtube.com/embed/Zzj9vEu5-fE"
                  title="LessonLift Demo Video"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
            <p className="text-center text-gray-600 mt-4 text-sm sm:text-base">
              Watch LessonLift in action: generating a full UK curriculum lesson plan in seconds.
            </p>
          </div>
        </div>
      </section>

      {/* Step-by-Step Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple Steps to Better Lesson Plans
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From idea to fully-formed lesson plan in seconds.
            </p>
          </div>

          <div className="space-y-8">
            {steps.map((step, index) => (
              <div
                key={index}
                className="flex flex-col md:flex-row items-start md:items-center gap-6 bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
              >
                {/* Step Number & Icon */}
                <div className="flex-shrink-0">
                  <div className="relative">
                    <div className="w-20 h-20 bg-[#4CAF50] rounded-full flex items-center justify-center">
                      <step.icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {step.number}
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed text-lg">
                    {step.description}
                  </p>
                </div>

                {/* Arrow for desktop (except last item) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block flex-shrink-0">
                    <ArrowRight className="w-6 h-6 text-gray-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Why Teachers Love LessonLift
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Focus on teaching while LessonLift handles the planning.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 text-center"
              >
                {/* Icon */}
                <div className="w-16 h-16 bg-[#4CAF50] rounded-full flex items-center justify-center mb-6 mx-auto">
                  <benefit.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {benefit.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {benefit.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
            Ready to Experience LessonLift?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join teachers who are saving time and creating better lessons with AI-powered planning.
          </p>

          <div className="flex flex-col items-center space-y-6">
            <a href="/signup" className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-12 py-6 rounded-2xl font-semibold text-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-2xl flex items-center space-x-3">
              <span>Start Your Free Trial</span>
              <ArrowRight size={24} />
            </a>

            <a
              href="/get-started"
              className="text-[#4CAF50] hover:text-[#45a049] font-medium text-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <span>See Example Plans</span>
              <ArrowRight size={18} />
            </a>

            <p className="text-gray-500 text-sm mt-4">
              No credit card required • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default HowItWorksPage;
