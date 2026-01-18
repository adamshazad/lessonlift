import React from 'react';
import { Clock, Trash2, BookOpen, ChevronRight } from 'lucide-react';
import { Lesson, deleteLesson } from '../services/lessonService';

interface LessonHistoryProps {
  lessons: Lesson[];
  onSelectLesson: (lesson: Lesson) => void;
  onDeleteLesson: (lessonId: string) => void;
  selectedLessonId?: string;
}

const LessonHistory: React.FC<LessonHistoryProps> = ({
  lessons,
  onSelectLesson,
  onDeleteLesson,
  selectedLessonId,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      });
    }
  };

  const handleDelete = async (e: React.MouseEvent, lessonId: string) => {
    e.stopPropagation();

    if (confirm('Are you sure you want to delete this lesson?')) {
      const success = await deleteLesson(lessonId);
      if (success) {
        onDeleteLesson(lessonId);
      }
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 h-full overflow-hidden flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen size={24} className="text-[#4CAF50]" />
        <h2 className="text-xl font-bold text-gray-900">Lesson History</h2>
      </div>

      {lessons.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <BookOpen size={48} className="mx-auto mb-3 opacity-50" />
            <p className="text-sm">No lessons yet</p>
            <p className="text-xs mt-1">Generate your first lesson to get started</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-2 pr-2 -mr-2">
          {lessons.map((lesson) => (
            <div
              key={lesson.id}
              onClick={() => onSelectLesson(lesson)}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all group ${
                selectedLessonId === lesson.id
                  ? 'border-[#4CAF50] bg-green-50'
                  : 'border-gray-200 hover:border-[#4CAF50] hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-gray-900 text-sm truncate mb-1">
                    {lesson.subject}: {lesson.topic}
                  </h3>
                  <div className="flex flex-wrap gap-2 text-xs text-gray-600 mb-2">
                    <span className="bg-gray-100 px-2 py-0.5 rounded">
                      {lesson.year_group}
                    </span>
                    <span className="bg-gray-100 px-2 py-0.5 rounded">
                      {lesson.ability_level}
                    </span>
                    <span className="bg-gray-100 px-2 py-0.5 rounded">
                      {lesson.lesson_duration} min
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock size={12} />
                    <span>{formatDate(lesson.created_at)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={(e) => handleDelete(e, lesson.id)}
                    className="p-1.5 hover:bg-red-100 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                    title="Delete lesson"
                  >
                    <Trash2 size={16} className="text-red-500" />
                  </button>
                  <ChevronRight
                    size={20}
                    className={`transition-all ${
                      selectedLessonId === lesson.id ? 'text-[#4CAF50]' : 'text-gray-400'
                    }`}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LessonHistory;
