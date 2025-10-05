import { Bot, ChartBar, Clipboard, CloudLightning, Pencil, Target } from "lucide-react"

// components/Features.jsx
export default function Features() {
  const features = [
    {
      icon: Clipboard,
      title: 'Smart Resume Builder',
      description: 'AI-powered resume optimization tailored to each job description'
    },
    {
      icon: Pencil,
      title: 'Cover Letter Generator',
      description: 'Create personalized cover letters in minutes, not hours'
    },
    {
      icon: Target,
      title: 'Job Matching',
      description: 'Find the perfect jobs that match your skills and preferences'
    },
    {
      icon: ChartBar,
      title: 'Application Tracker',
      description: 'Track all your applications in one place with smart reminders'
    },
    {
      icon: Bot,
      title: 'AI Interview Prep',
      description: 'Practice with AI-powered mock interviews and get instant feedback'
    },
    {
      icon: CloudLightning,
      title: 'Quick Apply',
      description: 'Apply to multiple jobs with one-click using your optimized profiles'
    }
  ]

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Everything You Need for Your Job Search
          </h2>
          <p className="text-xl text-gray-600">
            Streamline your job application process with our powerful AI tools
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
              <div className="w-12 h-12 bg-background-maweu rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 " />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}