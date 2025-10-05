// components/Pricing.tsx
"use client";

import { useState } from 'react'

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState<boolean>(false)

  const plans = [
    {
      name: 'Starter',
      price: isAnnual ? '$8' : '$10',
      period: isAnnual ? '/month billed annually' : '/month',
      description: 'Perfect for casual job seekers',
      features: [
        '5 resume optimizations per month',
        '10 cover letter generations',
        'Basic job matching',
        'Application tracker',
        'Email support'
      ],
      cta: 'Start Free Trial',
      popular: false
    },
    {
      name: 'Professional',
      price: isAnnual ? '$20' : '$25',
      period: isAnnual ? '/month billed annually' : '/month',
      description: 'Ideal for active job seekers',
      features: [
        'Unlimited resume optimizations',
        'Unlimited cover letters',
        'Advanced job matching',
        'AI interview preparation',
        'Priority support',
        'Quick apply feature'
      ],
      cta: 'Get Started',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For career coaches and teams',
      features: [
        'All Professional features',
        'Multiple user accounts',
        'Custom AI training',
        'Dedicated account manager',
        'API access',
        'White-label options'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ]

  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Start free. No credit card required.
          </p>
          
          <div className="flex items-center justify-center space-x-4">
            <span className={!isAnnual ? 'font-semibold' : 'text-gray-500'}>Monthly</span>
            <button 
              onClick={() => setIsAnnual(!isAnnual)}
              className="w-12 h-6 flex items-center bg-primary rounded-full p-1"
            >
              <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                isAnnual ? 'translate-x-6' : 'translate-x-0'
              }`} />
            </button>
            <span className={isAnnual ? 'font-semibold' : 'text-gray-500'}>Annual (Save 20%)</span>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <div key={index} className={`bg-white rounded-xl shadow-sm border-2 ${
              plan.popular ? 'border-primary transform scale-105' : 'border-gray-200'
            }`}>
              {plan.popular && (
                <div className="bg-primary text-white text-center py-2 rounded-t-xl">
                  Most Popular
                </div>
              )}
              <div className="p-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>
                <p className="text-gray-600 mb-6">{plan.description}</p>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <svg className="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <button className={`w-full py-3 rounded-lg font-semibold ${
                  plan.popular 
                    ? 'bg-primary text-white hover:bg-secondary' 
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}>
                  {plan.cta}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}