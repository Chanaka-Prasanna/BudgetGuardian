"use client";
import Link from "next/link";
import { useState } from "react";

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState("");

  const features = [
    {
      icon: "🤖",
      title: "AI-Powered Planning",
      description: "Intelligent recommendations using advanced RAG technology and multi-agent systems"
    },
    {
      icon: "🗺️",
      title: "Comprehensive Research",
      description: "Detailed information on destinations, attractions, weather, costs, and local insights"
    },
    {
      icon: "💰",
      title: "Budget Optimization",
      description: "Smart budget tracking and cost estimates to help you make the most of your money"
    },
    {
      icon: "📍",
      title: "Interactive Maps",
      description: "Visualize your trip with interactive maps showing all your planned destinations"
    },
    {
      icon: "🎯",
      title: "Personalized Itineraries",
      description: "Custom day-by-day plans tailored to your interests, budget, and travel style"
    },
    {
      icon: "✨",
      title: "Human-in-the-Loop",
      description: "Review, adjust, and perfect your itinerary at every step with full control"
    }
  ];

  const popularDestinations = [
    { name: "Tokyo", image: "🗼", budget: "$2,500" },
    { name: "Paris", image: "🗼", budget: "$3,000" },
    { name: "Bali", image: "🏝️", budget: "$1,800" },
    { name: "New York", image: "🗽", budget: "$3,500" },
    { name: "Dubai", image: "🏙️", budget: "$2,800" },
    { name: "Thailand", image: "🏖️", budget: "$1,500" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🛡️</span>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                BudgetGuardian
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link 
                href="#features" 
                className="text-gray-700 hover:text-blue-600 transition-colors text-sm font-medium"
              >
                Features
              </Link>
              <Link 
                href="#how-it-works" 
                className="text-gray-700 hover:text-blue-600 transition-colors text-sm font-medium"
              >
                How It Works
              </Link>
              <Link 
                href="/plan-your-trip"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
              >
                Start Planning
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Plan Your Perfect Trip with
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {" "}AI Intelligence
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            One-stop platform for comprehensive travel planning. No bookings, no pressure—just intelligent,
            personalized itineraries powered by advanced AI technology.
          </p>

          {/* Quick Search */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Where do you want to go? (e.g., Paris, Tokyo, Bali)"
                className="w-full px-6 py-4 pr-32 rounded-full border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none text-lg transition-all"
              />
              <Link
                href={`/plan-your-trip${searchQuery ? `?destination=${encodeURIComponent(searchQuery)}` : ''}`}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-full font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-md"
              >
                Explore →
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto mb-16">
            <div>
              <div className="text-3xl font-bold text-blue-600">1000+</div>
              <div className="text-sm text-gray-600">Destinations</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">AI-Powered</div>
              <div className="text-sm text-gray-600">Smart Planning</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">100%</div>
              <div className="text-sm text-gray-600">Free to Use</div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Popular Destinations
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {popularDestinations.map((dest) => (
            <Link
              key={dest.name}
              href={`/plan-your-trip?destination=${dest.name}`}
              className="group bg-white rounded-xl p-6 text-center hover:shadow-xl transition-all cursor-pointer border-2 border-transparent hover:border-blue-300"
            >
              <div className="text-5xl mb-3 group-hover:scale-110 transition-transform">
                {dest.image}
              </div>
              <div className="font-semibold text-gray-900 mb-1">{dest.name}</div>
              <div className="text-sm text-gray-500">{dest.budget}</div>
            </Link>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Plan
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Comprehensive tools and AI-powered features to make travel planning effortless
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 hover:shadow-lg transition-all border border-gray-100"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Simple, intelligent, and personalized travel planning in 4 easy steps
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-lg font-semibold mb-2">Enter Details</h3>
              <p className="text-gray-600 text-sm">
                Tell us your destination, budget, and preferences
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-lg font-semibold mb-2">AI Discovers</h3>
              <p className="text-gray-600 text-sm">
                Our AI finds the best places matching your interests
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-lg font-semibold mb-2">Review Research</h3>
              <p className="text-gray-600 text-sm">
                Get detailed information about each location
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                4
              </div>
              <h3 className="text-lg font-semibold mb-2">Get Itinerary</h3>
              <p className="text-gray-600 text-sm">
                Receive a personalized day-by-day travel plan
              </p>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              href="/plan-your-trip"
              className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl text-lg"
            >
              Start Planning Your Trip →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Plan Your Dream Trip?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of travelers using AI-powered planning to create perfect itineraries
          </p>
          <Link
            href="/plan-your-trip"
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl text-lg"
          >
            Get Started Free →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🛡️</span>
                <span className="text-white font-bold">BudgetGuardian</span>
              </div>
              <p className="text-sm">
                AI-powered travel planning platform. No bookings, just intelligent recommendations.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/plan-your-trip" className="hover:text-white transition-colors">Plan Trip</Link></li>
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#how-it-works" className="hover:text-white transition-colors">How It Works</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Travel Guides</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-sm">
            <p>&copy; 2024 BudgetGuardian. All rights reserved. Made with ❤️ for travelers.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
