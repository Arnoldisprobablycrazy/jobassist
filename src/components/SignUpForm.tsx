"use client";
import React, { useState } from "react";
import AuthButton from "./AuthButton";
import { useRouter } from "next/navigation";
import { signUp } from "../../actions/auth";
import Link from "next/link";
import Image from "next/image";
import Toast from "./toast";

const SignUpForm = () => {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showSuccess, setShowSuccess] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: ""
  });
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(event.currentTarget);
    const email = formData.get('email') as string;
    
    console.log('Signup attempt with:', { 
      email: email,
      username: formData.get('username')
    });

    const result = await signUp(formData);
    console.log('Signup result:', result);

    if (result.status === "success") {
      setSuccessMessage(`Account created successfully! We've sent a verification link to ${email}. Please check your email to verify your account before signing in.`);
      setShowSuccess(true);
      // Clear form
      setFormData({ username: "", email: "", password: "" });
    } else {
      setError(result.status);
    }

    setLoading(false);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Success Toast for email verification */}
      <Toast
        message={successMessage}
        type="info"
        isVisible={showSuccess}
        onClose={() => setShowSuccess(false)}
        duration={8000} // Longer duration for important message
      />

      {/* Left Side - Visual Section (Hidden on mobile) */}
      <div className="hidden lg:flex lg:flex-1 relative bg-gradient-brand overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          {/* Floating Shapes */}
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-bounce delay-1000"></div>
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-primary/15 rounded-full blur-3xl animate-pulse delay-500"></div>
          
          {/* Grid Pattern */}
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: `linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }}></div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-16 text-texts-default">
          <div className="max-w-lg">
            {/* Logo */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="relative w-12 h-12">
                  <Image
                    src="/logo.svg"
                    alt="JobAssist Logo"
                    fill
                    className="object-contain filter brightness-0 invert"
                  />
                </div>
                <span className="font-bold text-3xl">JobAssist</span>
              </div>
              <h1 className="text-5xl font-bold mb-6 leading-tight">
                Land Your
                <span className="block bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
                  Dream Job Faster
                </span>
              </h1>
            </div>

            {/* Features with Animations */}
            <div className="space-y-6">
              <div className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">AI Resume Parsing</h3>
                  <p className="text-text-secondary">Smart extraction of skills and experience from your resume</p>
                </div>
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Smart Matching</h3>
                  <p className="text-text-secondary">AI-powered job-resume compatibility scoring</p>
                </div>
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Cover Letter Generator</h3>
                  <p className="text-text-secondary">Personalized cover letters tailored to each job</p>
                </div>
              </div>
            </div>

            {/* Testimonial */}
            <div className="mt-12 p-6 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
              <p className="text-lg italic mb-4">"JobAssist helped me land my dream job in 3 weeks! The AI matching was incredibly accurate."</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                  <span className="font-bold text-white">SJ</span>
                </div>
                <div>
                  <p className="font-semibold">Sarah Johnson</p>
                  <p className="text-text-secondary text-sm">Software Engineer at Google</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Animated Elements */}
        <div className="absolute top-10 right-10 w-4 h-4 bg-accent rounded-full animate-ping"></div>
        <div className="absolute bottom-20 left-20 w-3 h-3 bg-primary rounded-full animate-bounce delay-300"></div>
      </div>

      {/* Right Side - Form Section (Full width on mobile, half on desktop) */}
      <div className="flex-1 flex items-center justify-center px-4 py-8 lg:py-12 bg-gradient-to-br from-background-maweu to-background-default">
        <div className="w-full max-w-md lg:max-w-lg">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative w-12 h-12">
                <Image
                  src="/logo.svg"
                  alt="JobAssist Logo"
                  fill
                  className="object-contain transition-transform group-hover:scale-110"
                  priority
                />
              </div>
              <span className="font-bold text-2xl text-texts-default group-hover:text-primary transition-colors">
                JobAssist
              </span>
            </Link>
          </div>

          {/* Mobile Hero Section (Only shown on mobile) */}
          <div className="lg:hidden mb-8 text-center">
            <h1 className="text-3xl font-bold text-texts-default mb-4">
              Start Your Job Search
            </h1>
            <p className="text-text-secondary">
              Create your account and let AI help you land your dream job
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-background-default rounded-3xl shadow-2xl p-6 sm:p-8 lg:p-10 border border-gray-100">
            {/* Header */}
            <div className="text-center mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-texts-default to-primary bg-clip-text text-transparent">
                Create Account
              </h2>
              <p className="text-text-secondary mt-2 text-sm sm:text-base">
                Join thousands of successful job seekers
              </p>
            </div>

            {/* Email Verification Notice - Shows after successful signup */}
            {showSuccess && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-blue-800">Verify Your Email</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      We've sent a verification link to your email address. Please check your inbox and click the link to verify your account before signing in.
                    </p>
                    <div className="mt-3 flex space-x-3">
                      <Link
                        href="/accounts/login"
                        className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
                      >
                        Go to Login
                      </Link>
                      <button
                        onClick={() => setShowSuccess(false)}
                        className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username Field */}
              <div className="space-y-2">
                <label htmlFor="username" className="block text-sm font-medium text-texts-primary">
                  Username
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Choose a username"
                    id="username"
                    name="username"
                    required
                    value={formData.username}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 bg-white text-texts-default placeholder-gray-500 shadow-sm"
                    disabled={loading}
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium text-texts-primary">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    id="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 bg-white text-texts-default placeholder-gray-500 shadow-sm"
                    disabled={loading}
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium text-texts-primary">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    name="password"
                    id="password"
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 bg-white text-texts-primary placeholder-gray-500 shadow-sm"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 transition-colors"
                    disabled={loading}
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L9 9m4.242 4.242L15 15m-5.122-5.122a3 3 0 000-4.243m0 4.243a3 3 0 010-4.243m4.242 4.242l-4.242-4.242" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
                <p className="text-xs text-text-secondary">Use 8+ characters with mix of letters, numbers & symbols</p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="flex items-start p-4 rounded-lg border bg-red-50 border-red-200 text-red-800">
                  <svg className="flex-shrink-0 w-5 h-5 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd"/>
                  </svg>
                  <div className="flex-1">
                    <p className="font-medium">Sign Up Error</p>
                    <p className="text-sm mt-1">{error}</p>
                  </div>
                </div>
              )}

              {/* Sign Up Button */}
              <div className="pt-2">
                <AuthButton type="register" loading={loading} />
              </div>

              {/* Terms */}
              <p className="text-center text-xs text-text-secondary">
                By signing up, you agree to our{" "}
                <Link href="/terms" className="text-primary hover:underline">Terms</Link> and{" "}
                <Link href="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
              </p>
            </form>

            {/* Sign In Link */}
            <div className="mt-6 text-center">
              <p className="text-text-primary">
                Already have an account?{" "}
                <Link
                  href="/accounts/login"
                  className="font-semibold text-primary hover:text-accent transition-colors duration-200"
                >
                  Sign In
                </Link>
              </p>
            </div>
          </div>

          {/* Security Badge */}
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-text-secondary">
            <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
            </svg>
            <span>Secure & Encrypted</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpForm;