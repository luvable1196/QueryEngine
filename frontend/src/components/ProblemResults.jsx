import React, { useState } from 'react';
import { ExternalLink, Star, Clock, Users, Code, Filter, TrendingUp, CheckCircle } from 'lucide-react';

const ProblemResults = ({ results, isLoading, searchQuery }) => {
  const [sortBy, setSortBy] = useState('frequency');
  const [sortOrder, setSortOrder] = useState('desc');
  const [difficultyFilter, setDifficultyFilter] = useState('all');

  // Remove duplicates based on question_number and title
  const uniqueResults = results.reduce((acc, current) => {
    const existing = acc.find(item => 
      item.question_number === current.question_number && 
      item.title === current.title
    );
    if (!existing) {
      acc.push(current);
    }
    return acc;
  }, []);

  // Filter by difficulty
  const filteredResults = difficultyFilter === 'all' 
    ? uniqueResults 
    : uniqueResults.filter(problem => problem.difficulty.toLowerCase() === difficultyFilter.toLowerCase());

  // Sort results
  const sortedResults = [...filteredResults].sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'frequency':
        aValue = a.frequency || 0;
        bValue = b.frequency || 0;
        break;
      case 'acceptance':
        aValue = a.acceptance_rate || 0;
        bValue = b.acceptance_rate || 0;
        break;
      case 'difficulty':
        const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 };
        aValue = difficultyOrder[a.difficulty?.toLowerCase()] || 0;
        bValue = difficultyOrder[b.difficulty?.toLowerCase()] || 0;
        break;
      case 'title':
        aValue = a.title || '';
        bValue = b.title || '';
        break;
      default:
        return 0;
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'hard':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getFrequencyColor = (frequency) => {
    if (frequency >= 80) return 'text-red-600';
    if (frequency >= 60) return 'text-orange-600';
    if (frequency >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatAcceptanceRate = (rate) => {
    return rate ? `${(rate * 100).toFixed(1)}%` : 'N/A';
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Searching for problems...</p>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <Code className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No Problems Found</h3>
          <p className="text-gray-600">Try adjusting your search terms or filters to find more problems.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Results Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              Search Results {searchQuery && `for "${searchQuery}"`}
            </h2>
            <p className="text-gray-600 mt-1">
              Found {sortedResults.length} problems {uniqueResults.length !== results.length && `(${results.length - uniqueResults.length} duplicates removed)`}
            </p>
          </div>
          
          {/* Sort and Filter Controls */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <select
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="frequency">Frequency</option>
                <option value="acceptance">Acceptance Rate</option>
                <option value="difficulty">Difficulty</option>
                <option value="title">Title</option>
              </select>
              
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid gap-6">
        {sortedResults.map((problem, index) => (
          <div
            key={`${problem.question_number}-${problem.title}-${index}`}
            className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-gray-300 transition-all duration-300 group"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {/* Problem Title and Link */}
                <div className="flex items-center space-x-3 mb-3">
                  <h3 className="text-xl font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
                    {problem.title}
                  </h3>
                  <a
                    href={problem.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <ExternalLink className="h-5 w-5" />
                  </a>
                </div>

                {/* Problem Stats */}
                <div className="flex items-center space-x-6 mb-4">
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getDifficultyColor(problem.difficulty)}`}>
                      {problem.difficulty ? problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1) : 'Unknown'}
                    </span>
                  </div>
                  
                  {problem.frequency && (
                    <div className="flex items-center space-x-2">
                      <Star className={`h-4 w-4 ${getFrequencyColor(problem.frequency)}`} />
                      <span className={`text-sm font-medium ${getFrequencyColor(problem.frequency)}`}>
                        {problem.frequency.toFixed(1)}% frequency
                      </span>
                    </div>
                  )}
                  
                  {problem.acceptance_rate && (
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-gray-600">
                        {formatAcceptanceRate(problem.acceptance_rate)} acceptance
                      </span>
                    </div>
                  )}
                </div>

                {/* Topics */}
                {problem.topics && problem.topics.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {problem.topics.map((topic, topicIndex) => (
                      <span
                        key={topicIndex}
                        className="px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full border border-blue-200"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                )}

                {/* Companies */}
                {problem.companies && problem.companies.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <Users className="h-4 w-4 text-gray-500" />
                    <div className="flex flex-wrap gap-2">
                      {problem.companies.map((company, companyIndex) => (
                        <span
                          key={companyIndex}
                          className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full border border-gray-200"
                        >
                          {company}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Results Summary */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{sortedResults.length}</div>
            <div className="text-sm text-gray-600">Total Problems</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {sortedResults.filter(p => p.difficulty?.toLowerCase() === 'easy').length}
            </div>
            <div className="text-sm text-gray-600">Easy</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">
              {sortedResults.filter(p => p.difficulty?.toLowerCase() === 'medium').length}
            </div>
            <div className="text-sm text-gray-600">Medium</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">
              {sortedResults.filter(p => p.difficulty?.toLowerCase() === 'hard').length}
            </div>
            <div className="text-sm text-gray-600">Hard</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProblemResults;