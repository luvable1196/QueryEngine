import React, { useState } from 'react';
import { 
  ExternalLink, 
  Building2, 
  Tag, 
  Clock, 
  TrendingUp,
  Star,
  Code,
  Filter,
  Search,
  ChevronLeft,
  ChevronRight,
  Target,
  Zap
} from 'lucide-react';

const ResultsSection = ({ results, isLoading, onSearch, searchTerm }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('relevance');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const itemsPerPage = 10;

  if (isLoading) {
    return (
      <div className="py-16">
        <div className="text-center mb-12">
          <Search className="h-12 w-12 text-purple-400 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-white mb-2">Scanning the Galaxy</h2>
          <p className="text-white/70">Searching through cosmic problem database...</p>
        </div>
        
        <div className="space-y-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="rounded-2xl p-6 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10">
              <div className="animate-pulse">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-white/20 rounded-lg"></div>
                  <div className="flex-1">
                    <div className="w-48 h-5 bg-white/20 rounded mb-2"></div>
                    <div className="w-32 h-4 bg-white/20 rounded"></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="w-full h-4 bg-white/20 rounded"></div>
                  <div className="w-3/4 h-4 bg-white/20 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="py-16 text-center">
        <div className="max-w-md mx-auto">
          <Target className="h-16 w-16 text-purple-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">No Results Found</h2>
          <p className="text-white/70 mb-6">
            {searchTerm ? 
              `No problems found matching "${searchTerm}". Try adjusting your search terms.` :
              'Enter a search term to explore our problem database.'
            }
          </p>
          <button
            onClick={() => onSearch('')}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
          >
            Browse All Problems
          </button>
        </div>
      </div>
    );
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'text-green-400 bg-green-400/20';
      case 'medium': return 'text-yellow-400 bg-yellow-400/20';
      case 'hard': return 'text-red-400 bg-red-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  const getDifficultyIcon = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return '⭐';
      case 'medium': return '⭐⭐';
      case 'hard': return '⭐⭐⭐';
      default: return '⭐';
    }
  };

  // Filter and sort results
  const filteredResults = results.filter(result => {
    if (filterDifficulty === 'all') return true;
    return result.difficulty?.toLowerCase() === filterDifficulty;
  });

  const sortedResults = [...filteredResults].sort((a, b) => {
    switch (sortBy) {
      case 'difficulty':
        const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 };
        return (difficultyOrder[a.difficulty?.toLowerCase()] || 0) - (difficultyOrder[b.difficulty?.toLowerCase()] || 0);
      case 'title':
        return a.title?.localeCompare(b.title) || 0;
      case 'companies':
        return (b.companies?.length || 0) - (a.companies?.length || 0);
      default:
        return 0;
    }
  });

  // Pagination
  const totalPages = Math.ceil(sortedResults.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedResults = sortedResults.slice(startIndex, startIndex + itemsPerPage);

  const ProblemCard = ({ problem, index }) => (
    <div className="group rounded-2xl p-6 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10 hover:border-purple-400/30 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10">
      {/* Cosmic background effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className="absolute top-2 right-2 w-1 h-1 bg-purple-400 rounded-full animate-pulse"></div>
        <div className="absolute bottom-2 left-2 w-0.5 h-0.5 bg-blue-400 rounded-full animate-pulse delay-300"></div>
      </div>
      
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
              {startIndex + index + 1}
            </div>
            <div>
              <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors">
                {problem.title || 'Untitled Problem'}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(problem.difficulty)}`}>
                  {getDifficultyIcon(problem.difficulty)} {problem.difficulty || 'Unknown'}
                </span>
                {problem.id && (
                  <span className="text-white/60 text-xs">#{problem.id}</span>
                )}
              </div>
            </div>
          </div>
          
          {problem.leetcode_url && (
            <a
              href={problem.leetcode_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors group"
            >
              <ExternalLink className="h-4 w-4 text-white/70 group-hover:text-white" />
            </a>
          )}
        </div>

        {/* Description */}
        {problem.description && (
          <p className="text-white/80 mb-4 line-clamp-2 text-sm leading-relaxed">
            {problem.description}
          </p>
        )}

        {/* Tags */}
        {problem.tags && problem.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {problem.tags.slice(0, 4).map((tag, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-white/10 text-white/80 rounded-full text-xs flex items-center space-x-1"
              >
                <Tag className="h-3 w-3" />
                <span>{tag}</span>
              </span>
            ))}
            {problem.tags.length > 4 && (
              <span className="px-2 py-1 bg-white/10 text-white/60 rounded-full text-xs">
                +{problem.tags.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Companies */}
        {problem.companies && problem.companies.length > 0 && (
          <div className="flex items-center space-x-2 mb-4">
            <Building2 className="h-4 w-4 text-white/60" />
            <div className="flex flex-wrap gap-2">
              {problem.companies.slice(0, 3).map((company, i) => (
                <span
                  key={i}
                  className="px-2 py-1 bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white/90 rounded-full text-xs font-medium"
                >
                  {company}
                </span>
              ))}
              {problem.companies.length > 3 && (
                <span className="px-2 py-1 bg-white/10 text-white/60 rounded-full text-xs">
                  +{problem.companies.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="flex items-center justify-between pt-4 border-t border-white/10">
          <div className="flex items-center space-x-4 text-sm text-white/60">
            {problem.acceptance_rate && (
              <div className="flex items-center space-x-1">
                <TrendingUp className="h-4 w-4" />
                <span>{problem.acceptance_rate}% acceptance</span>
              </div>
            )}
            {problem.frequency && (
              <div className="flex items-center space-x-1">
                <Zap className="h-4 w-4" />
                <span>Frequency: {problem.frequency}</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Star className="h-4 w-4 text-yellow-400" />
            <span className="text-white/80 text-sm">
              {Math.floor(Math.random() * 5) + 1}/5
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="py-16">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Search Results
          </h2>
          <p className="text-white/70">
            Found {sortedResults.length} problems 
            {searchTerm && ` matching "${searchTerm}"`}
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Filter */}
          <select
            value={filterDifficulty}
            onChange={(e) => {
              setFilterDifficulty(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
          
          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="relevance">Sort by Relevance</option>
            <option value="title">Sort by Title</option>
            <option value="difficulty">Sort by Difficulty</option>
            <option value="companies">Sort by Companies</option>
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-6 mb-8">
        {paginatedResults.map((problem, index) => (
          <ProblemCard key={problem.id || index} problem={problem} index={index} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4 text-white" />
          </button>
          
          <div className="flex items-center space-x-2">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                    currentPage === pageNum
                      ? 'bg-purple-500 text-white'
                      : 'bg-white/10 text-white/80 hover:bg-white/20'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-4 w-4 text-white" />
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultsSection;