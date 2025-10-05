// components/Header.tsx
"use client";

import { useState } from 'react'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false)

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-primary">JobAssist</span>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-primary">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-primary">How It Works</a>
            <a href="#pricing" className="text-gray-600 hover:text-primary">Pricing</a>
            <button className="bg-background-accent text-white px-4 py-2 rounded-full hover:bg-secondary">
              Sign up
            </button>
            <button className="bg-background-maweu text-texts-primary px-4 py-2 rounded-full hover:bg-secondary">
              Login
            </button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <a href="#features" className="block px-3 py-2 text-gray-600">Features</a>
              <a href="#how-it-works" className="block px-3 py-2 text-gray-600">How It Works</a>
              <a href="#pricing" className="block px-3 py-2 text-gray-600">Pricing</a>
              <button className="w-full bg-primary text-white px-4 py-2 rounded-lg">Get Started</button>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}