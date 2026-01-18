@@ .. @@
 import { LessonForm } from '../components/LessonForm';
 import { LessonDisplay } from '../components/LessonDisplay';
 import { LimitReachedModal } from '../components/LimitReachedModal';
+import { SubscriptionStatus } from '../components/SubscriptionStatus';
 import { supabase } from '../lib/supabase';
 import { useAuth } from '../contexts/AuthContext';
@@ .. @@
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
           <div className="grid lg:grid-cols-3 gap-8">
             <div className="lg:col-span-1 space-y-6">
+              <SubscriptionStatus />
               <LessonForm 
                 onGenerate={handleGenerate} 
                 isGenerating={isGenerating}
@@ .. @@