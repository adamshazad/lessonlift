import React, { useState } from 'react';
import { Wand2, Loader2 } from 'lucide-react';
import { LessonRequest } from '../services/lessonService';

interface LessonFormProps {
  onGenerate: (request: LessonRequest) => Promise<void>;
  isGenerating: boolean;
}

const LessonForm: React.FC<LessonFormProps> = ({ onGenerate, isGenerating }) => {
  const [yearGroup, setYearGroup] = useState('Year 1');
  const [abilityLevel, setAbilityLevel] = useState('Mixed');
  const [lessonDuration, setLessonDuration] = useState(45);
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [learningObjective, setLearningObjective] = useState('');
  const [senEalNotes, setSenEalNotes] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const request: LessonRequest = {
      yearGroup,
      abilityLevel,
      lessonDuration,
      subject,
      topic,
      learningObjective: learningObjective || undefined,
      senEalNotes: senEalNotes || undefined,
    };

    await onGenerate(request);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-6 space-y-5">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New Lesson Plan</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Year Group
          </label>
          <select
            value={yearGroup}
            onChange={(e) => setYearGroup(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
            required
          >
            <option>Year 1</option>
            <option>Year 2</option>
            <option>Year 3</option>
            <option>Year 4</option>
            <option>Year 5</option>
            <option>Year 6</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Ability Level
          </label>
          <select
            value={abilityLevel}
            onChange={(e) => setAbilityLevel(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
            required
          >
            <option>Mixed</option>
            <option>Lower</option>
            <option>Higher</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Lesson Duration (minutes)
          </label>
          <select
            value={lessonDuration}
            onChange={(e) => setLessonDuration(Number(e.target.value))}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
            required
          >
            <option value={30}>30 minutes</option>
            <option value={45}>45 minutes</option>
            <option value={60}>60 minutes</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Subject
          </label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g., Mathematics, English, Science"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Topic
        </label>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., Fractions, Creative Writing, Plant Life Cycles"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Learning Objective (Optional)
        </label>
        <input
          type="text"
          value={learningObjective}
          onChange={(e) => setLearningObjective(e.target.value)}
          placeholder="e.g., Students will be able to identify and add simple fractions"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          SEN/EAL Notes (Optional)
        </label>
        <textarea
          value={senEalNotes}
          onChange={(e) => setSenEalNotes(e.target.value)}
          placeholder="e.g., Two students with dyslexia, one EAL student learning English"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#4CAF50] focus:ring-2 focus:ring-green-100 outline-none transition-all resize-none"
          rows={3}
        />
      </div>

      <button
        type="submit"
        disabled={isGenerating}
        className="w-full bg-[#4CAF50] hover:bg-[#45a049] disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 shadow-md hover:shadow-lg flex items-center justify-center gap-2 text-lg"
      >
        {isGenerating ? (
          <>
            <Loader2 size={24} className="animate-spin" />
            Generating Lesson Plan...
          </>
        ) : (
          <>
            <Wand2 size={24} />
            Generate Lesson Plan
          </>
        )}
      </button>
    </form>
  );
};

export default LessonForm;
