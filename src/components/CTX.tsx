// components/CTA.tsx
"use client";

import { useState, FormEvent } from 'react'

export default function CTA() {
  const [email, setEmail] = useState<string>('')

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    console.log('Email submitted:', email)
  }

  return (
    <section className="py-20 bg-background-icons text-texts-default">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Ready to Transform Your Job Search?
        </h2>
        <p className="text-xl mb-8 text-blue-100">
          Join thousands of successful job seekers today. Start your 14-day free trial.
        </p>
        
        <form onSubmit={handleSubmit} className="max-w-md mx-auto">
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              className="flex-1 px-4 py-3 rounded-lg bg-background-maweu text-texts-primary"
              required
            />
            <button
              type="submit"
              className="bg-background-accent text-white px-6 py-3 rounded-lg hover:bg-background-hover transition-colors font-semibold"
            >
              Start Free Trial
            </button>
          </div>
          <p className="text-sm mt-3 text-blue-200">
            No credit card required • Cancel anytime
          </p>
        </form>
      </div>
    </section>
  )
}