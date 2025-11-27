"use client";
import React, { useState } from "react";
import AuthButton from "./AuthButton";
import LoginFacebook from "./LoginFacebook";
import { useRouter } from "next/navigation";
import { signIn } from "../../actions/auth";
import Link from "next/link";
import Image from "next/image";
import Toast from "./toast";

const LoginForm = () => {
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(false);
  const [showSuccess, setShowSuccess] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(event.currentTarget);

    const email = formData.get('email') as string;

    console.log('Login attempt with:', { email });

    const result = await signIn(formData);
    console.log('Login result:', result);

    if (result.status === "success") {
      console.log('Login successful, showing toast...');
      setShowSuccess(true);
      setTimeout(() => {
        console.log('Redirecting to dashboard...');
        router.push("/dashboard");
      }, 2000);
    } else if (result.status === "Email not confirmed") {
      setError(`Please verify your email address before signing in. We sent a verification link to ${email}.`);
    } else if (result.status === "Invalid login credentials") {
      setError("Invalid email or password. If you just signed up, please check your email for the verification link.");
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

      {/* Add Toast component */}
      <Toast
        message="Login successful! Redirecting to dashboard..."
        type="success"
        isVisible={showSuccess}
        onClose={() => setShowSuccess(false)}
        duration={2000}
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

                <span className="font-bold text-3xl">JobAssist</span>
              </div>
              <h1 className="text-5xl font-bold mb-6 leading-tight">
                Welcome Back to
                <span className="block bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
                  Your Job Application Assistant
                </span>
              </h1>
            </div>

            {/* Features with Animations */}
            <div className="space-y-6">
              <div className="flex items-center gap-4 group">
                
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Smart Recommendations</h3>
                  <p className="text-text-secondary">Get personalized job matches based on your profile</p>
                </div>
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Quick Applications</h3>
                  <p className="text-text-secondary">Apply to jobs faster with your saved information</p>
                </div>
              </div>
            </div>

            {/* Testimonial */}
            <div className="mt-12 p-6 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
              <p className="text-lg italic mb-4">"I landed 3 interviews in my first week using JobAssist! The platform made creating Compelling Cover letters easier."</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                  <span className="font-bold text-white">JD</span>
                </div>
                <div>
                  <p className="font-semibold">John Doe</p>
                  <p className="text-text-secondary text-sm">Product Manager at Meta</p>
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
              Welcome Back
            </h1>
            <p className="text-text-secondary">
              Sign in to continue your job search journey
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-background-default rounded-3xl shadow-2xl p-6 sm:p-8 lg:p-10 border border-gray-100">
            {/* Header */}
            <div className="text-center mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-texts-default to-primary bg-clip-text text-transparent">
                Sign In
              </h2>
              <p className="text-text-secondary mt-2 text-sm sm:text-base">
                Continue your journey to your dream job
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
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
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-300 bg-white text-texts-primary placeholder-gray-500 shadow-sm"
                    disabled={loading}
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="block text-sm font-medium text-texts-primary">
                    Password
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-sm font-medium text-primary hover:text-accent transition-colors duration-200"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
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
              </div>

              {/* Enhanced Error Message */}
              {error && (
                <div className={`flex items-start p-4 rounded-lg border ${error.includes('verify your email') || error.includes('Email not confirmed')
                    ? 'bg-yellow-50 border-yellow-200 text-yellow-800'
                    : 'bg-red-50 border-red-200 text-red-800'
                  }`}>
                  <svg className="flex-shrink-0 w-5 h-5 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    {error.includes('verify your email') || error.includes('Email not confirmed') ? (
                      // Info icon for verification required
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    ) : (
                      // X icon for other errors
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                    )}
                  </svg>
                  <div className="flex-1">
                    <p className="font-medium">
                      {error.includes('verify your email') || error.includes('Email not confirmed')
                        ? 'Email Verification Required'
                        : 'Login Error'}
                    </p>
                    <p className="text-sm mt-1">{error}</p>
                    {(error.includes('verify your email') || error.includes('Email not confirmed')) && (
                      <div className="mt-3 space-y-2">
                        <p className="text-sm font-medium">Need help?</p>
                        <div className="flex space-x-3">
                          <Link
                            href="/accounts/signup"
                            className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded hover:bg-yellow-200 transition-colors"
                          >
                            Sign up again
                          </Link>
                          <Link
                            href="/contact"
                            className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded hover:bg-yellow-200 transition-colors"
                          >
                            Contact support
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Login Button */}
              <div className="pt-2">
                <AuthButton type="login" loading={loading} />
              </div>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-background-default text-text-secondary">Or continue with</span>
              </div>
            </div>

            

            {/* Sign Up Link */}
            <div className="mt-6 text-center">
              <p className="text-text-primary">
                Don't have an account?{" "}
                <Link
                  href="/accounts/register"
                  className="font-semibold text-primary hover:text-accent transition-colors duration-200"
                >
                  Sign Up
                </Link>
              </p>
            </div>
          </div>

          {/* Security Badge */}
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-text-secondary">
            <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Secure & Encrypted</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;