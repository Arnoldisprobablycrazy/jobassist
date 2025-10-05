import { Laptop, ShoppingBasket, User, Quote, Award, Briefcase, LucideProps } from "lucide-react"

// components/Testimonials.tsx
export default function Testimonials() {
  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Software Engineer at Google',
      icon: Laptop,
      content: 'JobAssist helped me land my dream job at Google. The AI resume optimization increased my interview calls by 300%.',
      rating: 5
    },
    {
      name: 'Michael Rodriguez',
      role: 'Product Manager at Airbnb',
      icon: Briefcase,
      content: 'I went from 0 interviews to 5 offers in 2 months. The cover letter generator saved me hours each week.',
      rating: 5
    },
    {
      name: 'Emily Johnson',
      role: 'Marketing Director at Shopify',
      icon: Award,
      content: 'The application tracker kept me organized and the AI interview prep made me confident for every meeting.',
      rating: 5
    }
  ]

  return (
    <section className="py-20 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium mb-4">
            Testimonials
          </span>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Success Stories
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            See how JobAssist has transformed job searches for professionals worldwide
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <TestimonialCard key={index} testimonial={testimonial} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}

interface Testimonial {
  name: string;
  role: string;
  icon: React.ComponentType<LucideProps>;
  content: string;
  rating: number;
}

interface TestimonialCardProps {
  testimonial: Testimonial;
  index: number;
}

function TestimonialCard({ testimonial, index }: TestimonialCardProps) {
  const IconComponent = testimonial.icon;

  return (
    <div className="bg-gray-800 p-8 rounded-xl hover:bg-gray-750 transition-all duration-300 hover:transform hover:scale-105 group relative">
      {/* Quote Icon */}
      <Quote className="w-8 h-8 text-primary/30 absolute top-6 right-6" />
      
      {/* Rating Stars */}
      <div className="flex justify-center mb-4">
        {[...Array(testimonial.rating)].map((_, i) => (
          <span key={i} className="text-yellow-400">★</span>
        ))}
      </div>``

      {/* Icon */}
      <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
        <IconComponent className="w-10 h-10 text-white" />
      </div>

      {/* Content */}
      <p className="text-gray-300 mb-6 text-lg leading-relaxed text-center">
        &ldquo;{testimonial.content}&rdquo;
      </p>

      {/* Author */}
      <div className="text-center">
        <div className="font-semibold text-white text-xl">{testimonial.name}</div>
        <div className="text-gray-400 text-sm">{testimonial.role}</div>
      </div>
    </div>
  );
}