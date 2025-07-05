import React, { useState, useEffect } from 'react';
import { Search, Database, BarChart3, Building2, Menu, X, Github, Zap, Filter, Code, Target, ExternalLink, Clock, TrendingUp, Star } from 'lucide-react';
import apiService from '../services/api';

// SearchSection Component
const SearchSection = ({ onSearchStart, onSearchComplete }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    difficulty: '',
    company: '',
    topics: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const difficulties = ['Easy', 'Medium', 'Hard'];
  const popularCompanies = ['Google', 'Amazon', 'Microsoft', 'Apple', 'Facebook', 'Netflix', 'Uber', 'Tesla'];
  const popularTopics = ['Array', 'String', 'Hash Table', 'Dynamic Programming', 'Tree', 'Graph', 'Binary Search', 'Sorting'];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchTerm.trim() || Object.values(filters).some(f => f)) {
      try {
        setIsLoading(true);
        onSearchStart();
        
        const response = await apiService.searchProblems(searchTerm.trim(), filters);
        console.log('API Response:', response);
        
        const results = response.results || response || [];
        console.log('Extracted results:', results);
        
        onSearchComplete(results, searchTerm.trim());
      } catch (error) {
        console.error('Search failed:', error);
        onSearchComplete([]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const clearFilters = () => {
    setFilters({
      difficulty: '',
      company: '',
      topics: ''
    });
  };

  const quickSearches = [
    { label: 'Array Problems', query: 'array', icon: Code, color: 'from-blue-500 to-blue-600', bgColor: 'bg-blue-50 hover:bg-blue-100', textColor: 'text-blue-600 hover:text-blue-700' },
    { label: 'Dynamic Programming', query: 'dynamic programming', icon: Target, color: 'from-green-500 to-green-600', bgColor: 'bg-green-50 hover:bg-green-100', textColor: 'text-green-600 hover:text-green-700' },
    { label: 'Tree Traversal', query: 'tree traversal', icon: Database, color: 'from-red-500 to-red-600', bgColor: 'bg-red-50 hover:bg-red-100', textColor: 'text-red-600 hover:text-red-700' },
    { label: 'Google Questions', query: '', company: 'Google', icon: Zap, color: 'from-orange-500 to-orange-600', bgColor: 'bg-orange-50 hover:bg-orange-100', textColor: 'text-orange-600 hover:text-orange-700' }
  ];

  const handleQuickSearch = async (quick) => {
    try {
      setIsLoading(true);
      onSearchStart();
      
      let response;
      if (quick.query) {
        setSearchTerm(quick.query);
        const searchFilters = quick.company ? { company: quick.company } : {};
        response = await apiService.searchProblems(quick.query, searchFilters);
      } else if (quick.company) {
        setFilters({...filters, company: quick.company});
        response = await apiService.searchProblems('', { company: quick.company });
      }
      
      console.log('Quick search response:', response);
      
      const results = response.results || response || [];
      console.log('Quick search results:', results);
      
      onSearchComplete(results, quick.query || quick.company);
    } catch (error) {
      console.error('Quick search failed:', error);
      onSearchComplete([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-12 py-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold leading-tight text-gray-800">
          Query Engine
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Explore the cosmic database of coding problems. Search through thousands of LeetCode problems using natural language or advanced filters.
        </p>
      </div>

      {/* Search Form */}
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          {/* Main Search Input */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for coding problems... (e.g., 'two sum', 'binary tree', 'dynamic programming')"
              className="w-full pl-12 pr-32 py-4 bg-white/80 backdrop-blur-md border-2 border-gray-200 rounded-2xl text-gray-800 placeholder-gray-500 focus:outline-none focus:border-blue-400 focus:bg-white transition-all duration-300 text-lg shadow-lg"
              disabled={isLoading}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch(e)}
            />
            <div className="absolute inset-y-0 right-0 flex items-center space-x-2 pr-4">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800 transition-colors duration-200"
                disabled={isLoading}
              >
                <Filter className="h-5 w-5" />
              </button>
              <button
                type="submit"
                onClick={handleSearch}
                disabled={isLoading}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-4 p-6 bg-white/80 backdrop-blur-md border border-gray-200 rounded-2xl space-y-4 shadow-lg">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">Advanced Filters</h3>
                <button
                  type="button"
                  onClick={clearFilters}
                  className="text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
                >
                  Clear All
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Difficulty Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select
                    value={filters.difficulty}
                    onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
                    className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg text-gray-800 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200"
                  >
                    <option value="">All Difficulties</option>
                    {difficulties.map(diff => (
                      <option key={diff} value={diff}>{diff}</option>
                    ))}
                  </select>
                </div>

                {/* Company Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
                  <select
                    value={filters.company}
                    onChange={(e) => setFilters({...filters, company: e.target.value})}
                    className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg text-gray-800 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200"
                  >
                    <option value="">All Companies</option>
                    {popularCompanies.map(company => (
                      <option key={company} value={company}>{company}</option>
                    ))}
                  </select>
                </div>

                {/* Topics Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Topics</label>
                  <select
                    value={filters.topics}
                    onChange={(e) => setFilters({...filters, topics: e.target.value})}
                    className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-lg text-gray-800 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200"
                  >
                    <option value="">All Topics</option>
                    {popularTopics.map(topic => (
                      <option key={topic} value={topic}>{topic}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Search Suggestions */}
      <div className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold text-gray-800 mb-6">Quick Searches</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickSearches.map((quick, index) => (
            <button
              key={index}
              onClick={() => handleQuickSearch(quick)}
              disabled={isLoading}
              className={`p-4 ${quick.bgColor} border border-gray-200 rounded-xl hover:shadow-lg hover:border-gray-300 transition-all duration-300 text-left group disabled:opacity-50 transform hover:scale-105`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 bg-gradient-to-r ${quick.color} rounded-lg shadow-md group-hover:shadow-lg transition-all duration-300`}>
                  <quick.icon className="h-5 w-5 text-white" />
                </div>
                <span className={`${quick.textColor} font-medium transition-colors duration-200`}>{quick.label}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// ProblemResults Component
const ProblemResults = ({ results, searchQuery, onBackToSearch }) => {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'hard': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatAcceptanceRate = (rate) => {
    return `${(rate * 100).toFixed(1)}%`;
  };

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-12">
        <Database className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-600">No problems found</h3>
        <p className="text-gray-500 mt-2">Try adjusting your search query or filters</p>
        <button
          onClick={onBackToSearch}
          className="mt-4 px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors duration-200"
        >
          Back to Search
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 py-6">
      {/* Results Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Search Results</h2>
          <p className="text-gray-600">
            {searchQuery && `Found ${results.length} problems for "${searchQuery}"`}
            {!searchQuery && `Found ${results.length} problems`}
          </p>
        </div>
        <button
          onClick={onBackToSearch}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200"
        >
          New Search
        </button>
      </div>

      {/* Results Grid */}
      <div className="grid gap-4">
        {results.map((problem, index) => (
          <div key={problem.question_number || index} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
            <div className="p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-500">#{problem.question_number}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(problem.difficulty)}`}>
                      {problem.difficulty}
                    </span>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors duration-200">
                    {problem.title}
                  </h3>
                  
                  <div className="flex flex-wrap gap-2">
                    {problem.topics && problem.topics.map((topic, topicIndex) => (
                      <span key={topicIndex} className="px-2 py-1 bg-blue-50 text-blue-700 rounded-md text-sm">
                        {topic}
                      </span>
                    ))}
                  </div>
                  
                  {problem.companies && problem.companies.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {problem.companies.map((company, companyIndex) => (
                        <span key={companyIndex} className="px-2 py-1 bg-purple-50 text-purple-700 rounded-md text-sm flex items-center gap-1">
                          <Building2 className="h-3 w-3" />
                          {company}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Acceptance</div>
                    <div className="text-lg font-semibold text-green-600">
                      {formatAcceptanceRate(problem.acceptance_rate)}
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Frequency</div>
                    <div className="text-lg font-semibold text-orange-600 flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      {problem.frequency}
                    </div>
                  </div>
                  
                  <a
                    href={problem.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                  >
                    <span>Solve</span>
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// LoadingSection Component
const LoadingSection = () => (
  <div className="flex flex-col items-center justify-center py-20">
    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
    <h3 className="text-xl font-semibold text-gray-700">Searching...</h3>
    <p className="text-gray-500 mt-2">Exploring the cosmic database</p>
  </div>
);

// Main App Component
const App = () => {
  const [currentSection, setCurrentSection] = useState('search');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSearchTerm, setCurrentSearchTerm] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle search operations
  const handleSearchStart = () => {
    console.log('Search started');
    setIsLoading(true);
    setCurrentSection('loading');
  };

  const handleSearchComplete = (results, searchTerm = '') => {
    console.log('Search completed with results:', results);
    setSearchResults(results);
    setCurrentSearchTerm(searchTerm);
    setIsLoading(false);
    setCurrentSection('results');
  };

  // Navigation handlers
  const handleBackToSearch = () => {
    setCurrentSection('search');
    setSearchResults([]);
    setCurrentSearchTerm('');
  };

  const handleNavigateToResults = () => {
    if (searchResults.length > 0) {
      setCurrentSection('results');
    }
  };

  // Fixed Navigation Bar Component
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
          <div className="hidden md:flex items-center space-x-4">
            {/* Search Button */}
            <button
              onClick={handleBackToSearch}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                currentSection === 'search' || currentSection === 'loading'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                  : 'bg-blue-50 text-blue-700 hover:bg-gradient-to-r hover:from-blue-500 hover:to-blue-600 hover:text-white hover:shadow-md'
              }`}
            >
              <Search className="h-4 w-4" />
              <span>Search</span>
            </button>

            {/* Results Button */}
            <button
              onClick={handleNavigateToResults}
              disabled={searchResults.length === 0}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                currentSection === 'results' && searchResults.length > 0
                  ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg'
                  : searchResults.length > 0
                  ? 'bg-green-50 text-green-700 hover:bg-gradient-to-r hover:from-green-500 hover:to-green-600 hover:text-white hover:shadow-md'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Database className="h-4 w-4" />
              <span>Results</span>
              {searchResults.length > 0 && (
                <span className="ml-1 px-2 py-1 bg-white/20 rounded-full text-xs">
                  {searchResults.length}
                </span>
              )}
            </button>

            {/* Stats Button */}
            <button
              className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 bg-purple-50 text-purple-700 hover:bg-gradient-to-r hover:from-purple-500 hover:to-purple-600 hover:text-white hover:shadow-md"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Stats</span>
            </button>
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
              <button
                onClick={() => {
                  handleBackToSearch();
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                  currentSection === 'search' || currentSection === 'loading'
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                    : 'bg-blue-50 text-blue-700'
                }`}
              >
                <Search className="h-4 w-4" />
                <span>Search</span>
              </button>

              <button
                onClick={() => {
                  handleNavigateToResults();
                  setMobileMenuOpen(false);
                }}
                disabled={searchResults.length === 0}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                  currentSection === 'results' && searchResults.length > 0
                    ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg'
                    : searchResults.length > 0
                    ? 'bg-green-50 text-green-700'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                <Database className="h-4 w-4" />
                <span>Results</span>
                {searchResults.length > 0 && (
                  <span className="ml-auto px-2 py-1 bg-white/20 rounded-full text-xs">
                    {searchResults.length}
                  </span>
                )}
              </button>

              <button
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 bg-purple-50 text-purple-700"
                onClick={() => setMobileMenuOpen(false)}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Stats</span>
              </button>
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
          />
        );
      
      case 'results':
        return (
          <ProblemResults
            results={searchResults}
            searchQuery={currentSearchTerm}
            onBackToSearch={handleBackToSearch}
          />
        );
      
      case 'loading':
        return <LoadingSection />;
      
      default:
        return (
          <SearchSection
            onSearchStart={handleSearchStart}
            onSearchComplete={handleSearchComplete}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/50"></div>
        <div className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-blue-300/30 to-blue-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-gradient-to-br from-green-300/30 to-green-500/30 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute bottom-40 left-1/3 w-20 h-20 bg-gradient-to-br from-red-300/30 to-red-500/30 rounded-full blur-2xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <NavigationBar />

      {/* Main Content */}
      <main className="relative z-10 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {renderContent()}
        </div>
      </main>

      {/* Single Footer */}
      {/* <footer className="relative z-10 mt-20 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
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
            </div>
          </div>
        </div>
      </footer> */}
    </div>
  );
};

export default App;