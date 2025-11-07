// components/Hero.tsx
"use client";

import { useState, FormEvent } from 'react'

export default function Hero() {
  const [email, setEmail] = useState<string>('')

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    console.log('Email submitted:', email)
  }

  return (
    <section className="bg-gradient-brand text-texts-default">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Land Your Dream Job
            <span className="block text-accent">3x Faster</span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-text-secondary">
            AI-powered job application assistant that helps you craft perfect resumes, 
            write compelling cover letters, and track your applications.
          </p>
          
          <form onSubmit={handleSubmit} className="max-w-md mx-auto">
            <div className="flex flex-col sm:flex-row gap-4">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                className="flex-1 px-4 py-3 rounded-lg text-texts-default bg-background-maweu/35 border border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent"
                required
              />
              <button
                type="submit"
                className="bg-background-accent text-white px-6 py-3 rounded-lg hover:bg-background-hover transition-colors font-semibold"
              >
                Join Waitlist
              </button>
            </div>
            <p className="text-sm mt-3 text-text-secondary">
              Join 5,000+ job seekers who found their dream job with JobAssist
            </p>
          </form>
        </div>
        
        <div className="mt-16 grid md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-accent">87%</div>
            <p className="text-text-secondary">More interview calls</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-accent">2.5x</div>
            <p className="text-text-secondary">Faster job search</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-accent">$15K</div>
            <p className="text-text-secondary">Higher average salary</p>
          </div>
        </div>
      </div>
    </section>
  )
}