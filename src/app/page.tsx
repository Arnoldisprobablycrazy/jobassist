// pages/index.js
import Head from 'next/head'
import Header from '../components/header'
import Hero from '../components/Hero'
import Features from '../components/Features'
import HowItWorks from '../components/HowItWorks'
import Testimonials from '../components/Testimonials'
import Pricing from '../components/Pricing'
import CTA from '../components/CTX'
import Footer from '../components/Footer'

export default function Home() {
  return (
    <div>
      <Head>
        <title>JobAssist - AI-Powered Job Application Assistant</title>
        <meta name="description" content="Land your dream job 3x faster with AI-powered resume optimization, cover letter generation, and application tracking." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header />
      <Hero />
      <Features />
      <HowItWorks />
      <Testimonials />
      <Pricing />
    
      <Footer />
    </div>
  )
}