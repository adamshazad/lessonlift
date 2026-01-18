import React, { useState } from 'react';
import { Play } from 'lucide-react';

const DemoVideo: React.FC = () => {
  const [videoError, setVideoError] = useState(false);

  const handleFallbackClick = () => {
    window.open('https://youtu.be/Zzj9vEu5-fE', '_blank', 'noopener,noreferrer');
  };

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* KEEP - Demo (Top) */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            🎥 Watch LessonLift in Action
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how teachers generate complete lesson plans in seconds using AI.
          </p>
        </div>

        {/* Video Container */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            {!videoError ? (
              <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
                <iframe
                  className="absolute top-0 left-0 w-full h-full"
                  src="https://www.youtube.com/embed/Zzj9vEu5-fE"
                  title="LessonLift Demo Video"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                  onError={() => setVideoError(true)}
                ></iframe>
              </div>
            ) : (
              /* Fallback Thumbnail */
              <div 
                className="relative w-full bg-gray-100 cursor-pointer hover:bg-gray-200 transition-colors duration-200"
                style={{ paddingBottom: '56.25%' }}
                onClick={handleFallbackClick}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-20 h-20 bg-[#4CAF50] rounded-full flex items-center justify-center mb-4 mx-auto hover:bg-[#45a049] transition-colors duration-200">
                      <Play size={32} className="text-white ml-1" fill="currentColor" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      LessonLift Demo
                    </h3>
                    <p className="text-gray-600">
                      Click to watch on YouTube
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoVideo;