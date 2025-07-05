import React from 'react';
import { Search, Zap, Database, Cpu } from 'lucide-react';

const LoadingSection = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-8">
      {/* Central Loading Animation */}
      <div className="relative">
        {/* Orbiting Planets */}
        <div className="relative w-32 h-32">
          {/* Central Core */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full animate-pulse shadow-2xl shadow-purple-500/50"></div>
          </div>
          
          {/* Orbit 1 */}
          <div className="absolute inset-0 animate-spin-slow">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-full shadow-lg shadow-blue-500/50"></div>
          </div>
          
          {/* Orbit 2 */}
          <div className="absolute inset-2 animate-spin-reverse">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gradient-to-r from-green-400 to-teal-400 rounded-full shadow-lg shadow-green-500/50"></div>
          </div>
          
          {/* Orbit 3 */}
          <div className="absolute inset-4 animate-spin-slow">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full shadow-lg shadow-yellow-500/50"></div>
          </div>
        </div>
        
        {/* Outer Ring */}
        <div className="absolute inset-0 border-2 border-purple-500/30 rounded-full animate-ping"></div>
      </div>

      {/* Loading Text */}
      <div className="text-center space-y-4">
        <h3 className="text-2xl font-bold text-white">
          <span className="inline-block animate-pulse">Searching the Galaxy</span>
        </h3>
        <p className="text-purple-300 text-lg">
          Querying the cosmic database...
        </p>
      </div>

      {/* Loading Steps */}
      <div className="flex flex-col sm:flex-row gap-6 max-w-2xl">
        {[
          { icon: Search, label: 'Scanning', delay: '0ms' },
          { icon: Database, label: 'Processing', delay: '500ms' },
          { icon: Cpu, label: 'Analyzing', delay: '1000ms' },
          { icon: Zap, label: 'Finalizing', delay: '1500ms' }
        ].map((step, index) => (
          <div key={index} className="flex items-center space-x-3 text-white/70">
            <div 
              className="p-2 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-lg backdrop-blur-sm border border-purple-500/30"
              style={{ animationDelay: step.delay }}
            >
              <step.icon className="w-5 h-5 animate-pulse" />
            </div>
            <span className="text-sm font-medium">{step.label}</span>
          </div>
        ))}
      </div>

      {/* Progress Bar */}
      <div className="w-full max-w-md">
        <div className="h-2 bg-gray-800/50 rounded-full overflow-hidden backdrop-blur-sm">
          <div className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 rounded-full animate-loading-bar"></div>
        </div>
      </div>

      {/* Fun Loading Messages */}
      <div className="text-center">
        <p className="text-purple-300/80 text-sm animate-pulse">
          {/* Random loading message */}
          Traversing through {Math.floor(Math.random() * 1000) + 100} stellar systems...
        </p>
      </div>
    </div>
  );
};

export default LoadingSection;