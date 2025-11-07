// components/Header.tsx
"use client";

import { useState } from 'react'
import Link from 'next/link'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false)

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-2xl font-bold text-primary">JobAssist</Link>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-primary">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-primary">How It Works</a>
            <a href="#pricing" className="text-gray-600 hover:text-primary">Pricing</a>
            <Link 
              href="/accounts/register" 
              className="bg-background-accent text-white px-4 py-2 rounded-full hover:bg-secondary transition-colors duration-200"
            >
              Sign up
            </Link>
            <Link 
              href="/accounts/login" 
              className="bg-background-maweu text-texts-primary px-4 py-2 rounded-full hover:bg-secondary transition-colors duration-200"
            >
              Login
            </Link>
          </div>

          <div className="md:hidden flex items-center">
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-primary hover:bg-gray-50"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t">
              <a href="#features" className="block px-3 py-2 text-gray-600 hover:text-primary hover:bg-gray-50 rounded-md">Features</a>
              <a href="#how-it-works" className="block px-3 py-2 text-gray-600 hover:text-primary hover:bg-gray-50 rounded-md">How It Works</a>
              <a href="#pricing" className="block px-3 py-2 text-gray-600 hover:text-primary hover:bg-gray-50 rounded-md">Pricing</a>
              <div className="pt-2 space-y-2">
                <Link 
                  href="/accounts/register" 
                  className="block w-full bg-background-accent text-white px-4 py-2 rounded-lg text-center hover:bg-secondary transition-colors duration-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign up
                </Link>
                <Link 
                  href="/accounts/login" 
                  className="block w-full bg-background-maweu text-texts-primary px-4 py-2 rounded-lg text-center hover:bg-secondary transition-colors duration-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Login
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}