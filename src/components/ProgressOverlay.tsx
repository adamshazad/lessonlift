import React, { useEffect, useState } from 'react';
import { Wand2 } from 'lucide-react';

interface ProgressOverlayProps {
  isVisible: boolean;
}

const ProgressOverlay: React.FC<ProgressOverlayProps> = ({ isVisible }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isVisible) {
      setProgress(0);
      return;
    }

    const intervals: NodeJS.Timeout[] = [];

    const startTime = Date.now();

    const updateProgress = () => {
      const elapsed = Date.now() - startTime;

      let targetProgress = 0;

      if (elapsed < 2000) {
        targetProgress = (elapsed / 2000) * 30;
      } else if (elapsed < 10000) {
        targetProgress = 30 + ((elapsed - 2000) / 8000) * 40;
      } else if (elapsed < 15000) {
        targetProgress = 70 + ((elapsed - 10000) / 5000) * 25;
      } else {
        targetProgress = 95;
      }

      setProgress(Math.min(targetProgress, 95));
    };

    const interval = setInterval(updateProgress, 100);
    intervals.push(interval);

    return () => {
      intervals.forEach(clearInterval);
    };
  }, [isVisible]);

  useEffect(() => {
    if (!isVisible && progress > 0) {
      setProgress(100);
      const timeout = setTimeout(() => {
        setProgress(0);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [isVisible, progress]);

  if (progress === 0) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm transition-opacity">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all">
        <div className="flex flex-col items-center">
          <div className="mb-6 relative">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center animate-pulse">
              <Wand2 className="text-[#4CAF50]" size={32} />
            </div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-[#4CAF50] border-t-transparent rounded-full animate-spin"></div>
          </div>

          <h3 className="text-2xl font-bold text-gray-900 mb-2">Generating Lesson Plan...</h3>
          <p className="text-gray-600 text-center mb-6">
            Creating your customised lesson plan with AI
          </p>

          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden mb-3">
            <div
              className="bg-gradient-to-r from-[#4CAF50] to-[#66BB6A] h-full rounded-full transition-all duration-300 ease-out relative overflow-hidden"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>
            </div>
          </div>

          <p className="text-sm font-semibold text-gray-700">
            {Math.round(progress)}% Complete
          </p>
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
};

export default ProgressOverlay;
