import React, { useState, useEffect } from 'react';
import { Search, Database, BarChart3, Building2, Menu, X, Github, Zap } from 'lucide-react';

// Import your existing components
import SearchSection from './components/SearchSection';
import ResultsSection from './components/ResultsSection';
import CompaniesSection from './components/CompaniesSection';
import CompanyResults from './components/CompanyResults';
import StatsSection from './components/StatsSection';
import LoadingSection from './components/LoadingSection';

const App = () => {
  const [currentSection, setCurrentSection] = useState('search');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSearchTerm, setCurrentSearchTerm] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [selectedCompanyData, setSelectedCompanyData] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle search operations
  const handleSearchStart = () => {
    setIsLoading(true);
    setCurrentSection('loading');
  };

  const handleSearchComplete = (results, searchTerm = '') => {
    setSearchResults(results);
    setCurrentSearchTerm(searchTerm);
    setIsLoading(false);
    setCurrentSection('results');
  };

  // Handle company selection
  const handleCompanySelect = (companyName, companyData) => {
    setSelectedCompany(companyName);
    setSelectedCompanyData(companyData);
    setCurrentSection('companyResults');
  };

  // Navigation handlers
  const handleViewCompanies = () => {
    setCurrentSection('companies');
  };

  const handleViewStats = () => {
    setCurrentSection('stats');
  };

  const handleBackToSearch = () => {
    setCurrentSection('search');
    setSelectedCompany(null);
    setSelectedCompanyData(null);
    setSearchResults([]);
    setCurrentSearchTerm('');
  };

  const handleBackToCompanies = () => {
    setCurrentSection('companies');
    setSelectedCompany(null);
    setSelectedCompanyData(null);
  };

  // Navigation items for the menu
  const navigationItems = [
    { id: 'search', label: 'Query Engine', icon: Search, color: 'from-blue-500 to-blue-600', bgColor: 'bg-blue-50', textColor: 'text-blue-700' },
    { id: 'results', label: 'Results', icon: Database, color: 'from-green-500 to-green-600', bgColor: 'bg-green-50', textColor: 'text-green-700' },
    { id: 'companies', label: 'Companies', icon: Building2, color: 'from-red-500 to-red-600', bgColor: 'bg-red-50', textColor: 'text-red-700' },
    { id: 'stats', label: 'System Stats', icon: BarChart3, color: 'from-orange-500 to-orange-600', bgColor: 'bg-orange-50', textColor: 'text-orange-700' },
  ];

  // Get current section title for navigation
  const getCurrentSectionTitle = () => {
    switch (currentSection) {
      case 'search':
        return 'Query Engine';
      case 'results':
        return 'Results';
      case 'companies':
        return 'Companies';
      case 'companyResults':
        return `${selectedCompany} Problems`;
      case 'stats':
        return 'System Stats';
      case 'loading':
        return 'Searching...';
      default:
        return 'Query Engine';
    }
  };

  const NavigationBar = () => (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">LeetCode Query System</h1>
              <p className="text-blue-600 text-sm font-medium">Problem Explorer Engine</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentSection === item.id || 
                             (currentSection === 'companyResults' && item.id === 'companies') ||
                             (currentSection === 'loading' && item.id === 'search');
              
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    if (item.id === 'search') handleBackToSearch();
                    else if (item.id === 'companies') handleViewCompanies();
                    else if (item.id === 'stats') handleViewStats();
                    else if (item.id === 'results' && searchResults.length > 0) setCurrentSection('results');
                  }}
                  disabled={item.id === 'results' && searchResults.length === 0}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    isActive
                      ? `bg-gradient-to-r ${item.color} text-white shadow-lg transform scale-105`
                      : `${item.bgColor} ${item.textColor} hover:bg-gradient-to-r hover:${item.color} hover:text-white hover:shadow-md hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed`
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white/95 backdrop-blur-md">
            <nav className="px-4 py-4 space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentSection === item.id || 
                               (currentSection === 'companyResults' && item.id === 'companies') ||
                               (currentSection === 'loading' && item.id === 'search');
                
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      if (item.id === 'search') handleBackToSearch();
                      else if (item.id === 'companies') handleViewCompanies();
                      else if (item.id === 'stats') handleViewStats();
                      else if (item.id === 'results' && searchResults.length > 0) setCurrentSection('results');
                      setMobileMenuOpen(false);
                    }}
                    disabled={item.id === 'results' && searchResults.length === 0}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                      isActive
                        ? `bg-gradient-to-r ${item.color} text-white shadow-lg`
                        : `${item.bgColor} ${item.textColor} hover:bg-gradient-to-r hover:${item.color} hover:text-white hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed`
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        )}
      </div>
    </nav>
  );

  // Render the appropriate section based on current state
  const renderContent = () => {
    switch (currentSection) {
      case 'search':
        return (
          <SearchSection
            onSearchStart={handleSearchStart}
            onSearchComplete={handleSearchComplete}
            onViewCompanies={handleViewCompanies}
            onViewStats={handleViewStats}
          />
        );
      
      case 'results':
        return (
          <ResultsSection
            results={searchResults}
            searchTerm={currentSearchTerm}
            onBackToSearch={handleBackToSearch}
            onViewCompanies={handleViewCompanies}
          />
        );
      
      case 'companies':
        return (
          <CompaniesSection
            onCompanySelect={handleCompanySelect}
            onBackToSearch={handleBackToSearch}
          />
        );
      
      case 'companyResults':
        return (
          <CompanyResults
            company={selectedCompany}
            data={selectedCompanyData}
            onBackToSearch={handleBackToSearch}
            onBackToCompanies={handleBackToCompanies}
          />
        );
      
      case 'stats':
        return (
          <StatsSection
            onBackToSearch={handleBackToSearch}
          />
        );
      
      case 'loading':
        return (
          <LoadingSection />
        );
      
      default:
        return (
          <SearchSection
            onSearchStart={handleSearchStart}
            onSearchComplete={handleSearchComplete}
            onViewCompanies={handleViewCompanies}
            onViewStats={handleViewStats}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 relative overflow-hidden">
      {/* Subtle decorative elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Soft gradient overlays */}
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/50"></div>
        
        {/* Colorful floating shapes */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-blue-300/30 to-blue-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-gradient-to-br from-green-300/30 to-green-500/30 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute bottom-40 left-1/3 w-20 h-20 bg-gradient-to-br from-red-300/30 to-red-500/30 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute bottom-20 right-1/4 w-28 h-28 bg-gradient-to-br from-orange-300/30 to-orange-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-gradient-to-br from-purple-300/30 to-purple-500/30 rounded-full blur-2xl animate-pulse"></div>
        
        {/* Colorful pattern dots */}
        <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-blue-400/50 rounded-full animate-bounce"></div>
        <div className="absolute top-1/3 right-1/3 w-2 h-2 bg-green-400/50 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
        <div className="absolute bottom-1/3 left-1/5 w-2 h-2 bg-red-400/50 rounded-full animate-bounce" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-1/4 right-1/5 w-3 h-3 bg-orange-400/50 rounded-full animate-bounce" style={{animationDelay: '1.5s'}}></div>
        <div className="absolute top-1/2 left-1/2 w-2 h-2 bg-purple-400/50 rounded-full animate-bounce" style={{animationDelay: '2s'}}></div>
        
        {/* Colorful gradient lines */}
        <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-blue-300/40 to-transparent"></div>
        <div className="absolute top-0 left-1/2 w-px h-full bg-gradient-to-b from-transparent via-green-300/40 to-transparent"></div>
        <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-red-300/30 to-transparent"></div>
        <div className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-orange-300/30 to-transparent"></div>
      </div>

      {/* Navigation */}
      <NavigationBar />

      {/* Main Content */}
      <main className="relative z-10 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {renderContent()}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-20 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-md flex items-center justify-center">
                <Zap className="h-4 w-4 text-white" />
              </div>
              <span className="text-gray-700 font-medium">Explore the universe of coding problems</span>
            </div>
            <div className="flex items-center space-x-6 text-gray-600">
              <a href="#" className="hover:text-blue-600 transition-colors duration-200 flex items-center space-x-2 group">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 group-hover:from-blue-600 group-hover:to-blue-700 transition-all duration-200 shadow-md">
                  <Github className="h-4 w-4 text-white" />
                </div>
                <span className="font-medium">GitHub</span>
              </a>
              <a href="#" className="hover:text-green-600 transition-colors duration-200 hover:underline font-medium px-3 py-1 rounded-md hover:bg-green-50">Documentation</a>
              <a href="#" className="hover:text-red-600 transition-colors duration-200 hover:underline font-medium px-3 py-1 rounded-md hover:bg-red-50">API</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;