import React, { useState } from 'react';
import { Search, Filter, Zap, Database, Code, Target } from 'lucide-react';

const SearchSection = ({ onSearch, isLoading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    difficulty: '',
    company: '',
    topics: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  const difficulties = ['Easy', 'Medium', 'Hard'];
  const popularCompanies = ['Google', 'Amazon', 'Microsoft', 'Apple', 'Facebook', 'Netflix', 'Uber', 'Tesla'];
  const popularTopics = ['Array', 'String', 'Hash Table', 'Dynamic Programming', 'Tree', 'Graph', 'Binary Search', 'Sorting'];

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim() || Object.values(filters).some(f => f)) {
      onSearch(searchTerm.trim(), filters);
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
    { label: 'Array Problems', query: 'array', icon: Code, color: 'from-blue-500 to-blue-600', bgColor: 'bg-blue-50', textColor: 'text-blue-600' },
    { label: 'Dynamic Programming', query: 'dynamic programming', icon: Target, color: 'from-green-500 to-green-600', bgColor: 'bg-green-50', textColor: 'text-green-600' },
    { label: 'Tree Traversal', query: 'tree traversal', icon: Database, color: 'from-red-500 to-red-600', bgColor: 'bg-red-50', textColor: 'text-red-600' },
    { label: 'Google Questions', query: '', company: 'Google', icon: Zap, color: 'from-orange-500 to-orange-600', bgColor: 'bg-orange-50', textColor: 'text-orange-600' }
  ];

  return (
    <div className="space-y-12 py-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold leading-tight">
          <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Query Engine
          </span>
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
              onClick={() => {
                if (quick.query) {
                  setSearchTerm(quick.query);
                  onSearch(quick.query, quick.company ? { company: quick.company } : {});
                } else if (quick.company) {
                  setFilters({...filters, company: quick.company});
                  onSearch('', { company: quick.company });
                }
              }}
              disabled={isLoading}
              className={`p-4 ${quick.bgColor} border border-gray-200 rounded-xl hover:shadow-lg hover:border-gray-300 transition-all duration-300 text-left group disabled:opacity-50 transform hover:scale-105`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 bg-gradient-to-r ${quick.color} rounded-lg shadow-md group-hover:shadow-lg transition-all duration-300`}>
                  <quick.icon className="h-5 w-5 text-white" />
                </div>
                <span className={`${quick.textColor} font-medium`}>{quick.label}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SearchSection;