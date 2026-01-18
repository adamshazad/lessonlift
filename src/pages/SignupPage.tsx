import React from 'react'
import { SignupForm } from '../components/auth/SignupForm'

export function SignupPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="text-center text-3xl font-bold text-gray-900 mb-8">
          Join LessonLift today
        </h1>
      </div>
      <SignupForm />
    </div>
  )
}