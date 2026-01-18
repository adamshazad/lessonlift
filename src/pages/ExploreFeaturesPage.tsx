import React from 'react';
import { Clock, BookOpen, Settings, Download, Lightbulb, History, Target, FileText, Users, Gauge, ArrowRight } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const ExploreFeaturesPage: React.FC = () => {
  const features = [
    {
      icon: Clock,
      title: "AI-Powered Lesson Generation",
      description: "Generate comprehensive, curriculum-aligned lesson plans in under 30 seconds using advanced AI technology."
    },
    {
      icon: BookOpen,
      title: "UK Curriculum Alignment",
      description: "Every lesson plan is aligned with the latest UK National Curriculum standards to make teaching simpler and compliant."
    },
    {
      icon: Settings,
      title: "Customizable Plans",
      description: "Edit, adapt, and personalize each generated lesson plan to suit your teaching style and classroom needs."
    },
    {
      icon: Download,
      title: "Multiple Export Formats",
      description: "Download your plans as PDF or DOCX for easy use in the classroom or when sharing with colleagues."
    },
    {
      icon: Lightbulb,
      title: "Smart Resource Suggestions",
      description: "Receive tailored ideas for resources, activities, and materials to enhance your lessons."
    },
    {
      icon: History,
      title: "Lesson History",
      description: "Easily access your previously generated lesson plans to review, download, or update them anytime."
    },
    {
      icon: Target,
      title: "Differentiated Learning",
      description: "Generate materials for different ability levels to support all students in your classroom."
    },
    {
      icon: FileText,
      title: "Assessment Integration",
      description: "Add assessment criteria and questions directly within your lesson plans."
    },
    {
      icon: Gauge,
      title: "Daily Plan Limit System",
      description: "Free Trial: 5 plans total. Starter: 1/day, Standard: 3/day, Pro: 5/day. Choose the plan that fits your needs."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-cyan-50 to-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-5 leading-tight">
              Explore All
              <span className="text-[#4CAF50] block mt-2">LessonLift Features</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Discover the tools designed to make lesson planning effortless,
              engaging, and perfectly aligned with your teaching needs.
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid Section */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 group"
              >
                {/* Icon */}
                <div className="w-16 h-16 bg-[#4CAF50] rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 group-hover:text-[#4CAF50] transition-colors duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Visual Demonstration Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              See These Features in Action
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience how these features work together to create an efficient lesson planning workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Feature Highlights */}
            <div className="space-y-8">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-[#4CAF50] rounded-full flex items-center justify-center flex-shrink-0">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Lightning Fast Generation</h3>
                  <p className="text-gray-600">Create comprehensive lesson plans in under 30 seconds with our advanced AI technology.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-[#4CAF50] rounded-full flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Curriculum Perfect</h3>
                  <p className="text-gray-600">Every lesson automatically aligns with UK National Curriculum standards and objectives.</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-[#4CAF50] rounded-full flex items-center justify-center flex-shrink-0">
                  <Settings className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Fully Customizable</h3>
                  <p className="text-gray-600">Adapt and personalize every aspect to match your unique teaching style and classroom needs.</p>
                </div>
              </div>
            </div>

            {/* Visual Mockup */}
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border">
                {/* Header */}
                <div className="bg-[#4CAF50] px-6 py-4">
                  <h3 className="text-white font-semibold text-lg">LessonLift Dashboard</h3>
                </div>
                
                {/* Content */}
                <div className="p-6 space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-[#4CAF50] rounded-full flex items-center justify-center">
                        <BookOpen className="w-4 h-4 text-white" />
                      </div>
                      <span className="font-medium text-gray-900">Year 4 Mathematics</span>
                    </div>
                    <span className="text-sm text-gray-500">Generated in 28s</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-[#4CAF50] rounded-full flex items-center justify-center">
                        <FileText className="w-4 h-4 text-white" />
                      </div>
                      <span className="font-medium text-gray-900">Science - Plants</span>
                    </div>
                    <span className="text-sm text-gray-500">Generated in 31s</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-[#4CAF50] rounded-full flex items-center justify-center">
                        <Users className="w-4 h-4 text-white" />
                      </div>
                      <span className="font-medium text-gray-900">English - Creative Writing</span>
                    </div>
                    <span className="text-sm text-gray-500">Generated in 25s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Start your free trial today and discover how LessonLift can transform your lesson planning experience.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
            <a href="/signup" className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg flex items-center space-x-2">
              <span>Start Free Trial</span>
              <ArrowRight size={20} />
            </a>
            <p className="text-gray-500 text-sm">
              No credit card required • 7-day free trial
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default ExploreFeaturesPage;