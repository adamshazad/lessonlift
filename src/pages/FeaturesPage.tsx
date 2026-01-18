import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, BookOpen, Settings, Download, Lightbulb, Headphones as HeadphonesIcon, ArrowRight, Play, Zap, Target, FileText, Users } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const FeaturesPage: React.FC = () => {
  const features = [
    {
      icon: Clock,
      title: "Unlimited Lesson Plan Generation",
      description: "Create as many lesson plans as you need without restrictions. Generate comprehensive plans in under 30 seconds."
    },
    {
      icon: BookOpen,
      title: "UK Curriculum Alignment",
      description: "Every lesson plan is perfectly aligned with UK National Curriculum standards and assessment objectives."
    },
    {
      icon: Settings,
      title: "Customizable Plans",
      description: "Easily modify and adapt any lesson plan with our intuitive editing tools to match your teaching style."
    },
    {
      icon: Download,
      title: "Multiple Export Formats",
      description: "Export your lesson plans in PDF, DOCX, or other formats for easy sharing and printing."
    },
    {
      icon: Lightbulb,
      title: "Resource Suggestions",
      description: "Get intelligent recommendations for teaching materials, activities, and supplementary resources."
    },
    {
      icon: HeadphonesIcon,
      title: "Priority Support",
      description: "Access dedicated customer support with faster response times and personalized assistance."
    },
    {
      icon: Target,
      title: "Differentiated Learning",
      description: "Automatically generate content for different ability levels and learning styles in your classroom."
    },
    {
      icon: FileText,
      title: "Assessment Integration",
      description: "Include formative and summative assessments that align with your lesson objectives."
    },
    {
      icon: Users,
      title: "Collaboration Tools",
      description: "Share lesson plans with colleagues and build a collaborative teaching community."
    },
    {
      icon: Zap,
      title: "Smart Templates",
      description: "Choose from pre-built templates or create your own custom formats for consistent planning."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-white to-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Why Teachers Love
              <span className="text-[#4CAF50] block mt-2">LessonLift</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed">
              Designed to save time, spark creativity, and align with the curriculum. 
              Discover the features that make lesson planning effortless.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Teachers
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to create engaging, curriculum-aligned lesson plans that inspire learning.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
              >
                <div className="w-12 h-12 bg-[#4CAF50] rounded-full flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* Call to Action */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your Teaching?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Discover how LessonLift can make lesson planning easier with AI-assisted tools.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link to="/signup" className="bg-[#4CAF50] hover:bg-[#45a049] text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg flex items-center space-x-2">
              <span>Start Free Trial</span>
              <ArrowRight size={20} />
            </Link>
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

export default FeaturesPage;