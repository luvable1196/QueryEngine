import React, { useState } from 'react';
import { 
  MapPin, Users, Calendar, ExternalLink, Star, Briefcase, 
  TrendingUp, Filter, Grid, List, Heart, Share2, BookmarkPlus,
  Building2, Globe, DollarSign, Award
} from 'lucide-react';
import { useStaggeredAnimation, useHoverAnimation } from '../hooks/useAnimations';

const CompanyResults = ({ results, query, onSearch }) => {
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('relevance');
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const [elementRef, visibleItems] = useStaggeredAnimation(results, 150);

  const sortedResults = [...results].sort((a, b) => {
    switch (sortBy) {
      case 'rating':
        return b.rating - a.rating;
      case 'employees':
        return parseInt(b.employees.split('-')[1]) - parseInt(a.employees.split('-')[1]);
      case 'founded':
        return b.founded - a.founded;
      default:
        return 0;
    }
  });

  const toggleFavorite = (id) => {
    setFavoriteIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const CompanyCard = ({ company, index }) => {
    const [cardRef, isHovered] = useHoverAnimation();
    const isFavorite = favoriteIds.has(company.id);
    const isVisible = visibleItems.has(index);

    return (
      <div
        ref={cardRef}
        className={`
          relative overflow-hidden rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 
          transition-all duration-500 hover:shadow-neon hover:bg-white/20 group
          ${isVisible ? 'animate-slide-up opacity-100' : 'opacity-0 translate-y-10'}
          ${isHovered ? 'transform scale-105' : ''}
        `}
        style={{ animationDelay: `${index * 0.1}s` }}
      >
        {/* Background gradient effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Hiring badge */}
        {company.isHiring && (
          <div className="absolute top-4 right-4 z-10">
            <div className="bg-gradient-to-r from-green-400 to-emerald-500 text-white px-3 py-1 rounded-full text-sm font-semibold animate-pulse">
              Hiring
            </div>
          </div>
        )}

        <div className="relative z-10 p-6">
          {/* Company Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-400 to-purple-500 rounded-2xl flex items-center justify-center text-2xl">
                {company.logo}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white group-hover:text-gradient-rainbow transition-all duration-300">
                  {company.name}
                </h3>
                <p className="text-white/70 flex items-center space-x-2">
                  <Building2 className="h-4 w-4" />
                  <span>{company.industry}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => toggleFavorite(company.id)}
                className={`p-2 rounded-full transition-all duration-300 ${
                  isFavorite 
                    ? 'bg-red-500 text-white shadow-glow' 
                    : 'bg-white/10 text-white/70 hover:bg-white/20 hover:text-white'
                }`}
              >
                <Heart className={`h-5 w-5 ${isFavorite ? 'fill-current' : ''}`} />
              </button>
              <button className="p-2 rounded-full bg-white/10 text-white/70 hover:bg-white/20 hover:text-white transition-all duration-300">
                <Share2 className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Company Info */}
          <div className="space-y-3 mb-4">
            <p className="text-white/80 text-sm leading-relaxed">
              {company.description}
            </p>

            <div className="flex flex-wrap gap-2">
              {company.tags.map((tag, tagIndex) => (
                <span
                  key={tagIndex}
                  className="px-3 py-1 bg-white/10 text-white/80 rounded-full text-xs hover:bg-white/20 cursor-pointer transition-all duration-200"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center space-x-2 text-white/70">
              <MapPin className="h-4 w-4" />
              <span className="text-sm">{company.location}</span>
            </div>
            <div className="flex items-center space-x-2 text-white/70">
              <Users className="h-4 w-4" />
              <span className="text-sm">{company.employees}</span>
            </div>
            <div className="flex items-center space-x-2 text-white/70">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">Founded {company.founded}</span>
            </div>
            <div className="flex items-center space-x-2 text-white/70">
              <DollarSign className="h-4 w-4" />
              <span className="text-sm">{company.funding}</span>
            </div>
          </div>

          {/* Rating and Jobs */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < Math.floor(company.rating) 
                        ? 'text-yellow-400 fill-current' 
                        : 'text-white/30'
                    }`}
                  />
                ))}
              </div>
              <span className="text-white/80 text-sm font-medium">{company.rating}</span>
            </div>
            
            {company.isHiring && (
              <div className="flex items-center space-x-2 text-green-400">
                <Briefcase className="h-4 w-4" />
                <span className="text-sm font-medium">{company.openPositions} open roles</span>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <button className="flex-1 btn-primary py-3 px-6 rounded-xl font-medium transition-all duration-300 hover:shadow-neon group">
              <span className="flex items-center justify-center space-x-2">
                <ExternalLink className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                <span>View Company</span>
              </span>
            </button>
            
            <button className="p-3 bg-white/10 rounded-xl text-white/70 hover:bg-white/20 hover:text-white transition-all duration-300">
              <BookmarkPlus className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Hover effect overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
      </div>
    );
  };

  const CompanyListItem = ({ company, index }) => {
    const isVisible = visibleItems.has(index);
    const isFavorite = favoriteIds.has(company.id);

    return (
      <div
        className={`
          flex items-center space-x-6 p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 
          hover:bg-white/20 transition-all duration-300 group
          ${isVisible ? 'animate-slide-right opacity-100' : 'opacity-0 translate-x-10'}
        `}
        style={{ animationDelay: `${index * 0.1}s` }}
      >
        <div className="w-16 h-16 bg-gradient-to-br from-pink-400 to-purple-500 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0">
          {company.logo}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-4 mb-2">
            <h3 className="text-lg font-bold text-white group-hover:text-gradient-rainbow transition-all duration-300">
              {company.name}
            </h3>
            <div className="flex items-center space-x-1">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-4 w-4 ${
                    i < Math.floor(company.rating) 
                      ? 'text-yellow-400 fill-current' 
                      : 'text-white/30'
                  }`}
                />
              ))}
            </div>
          </div>
          
          <p className="text-white/70 text-sm mb-2 line-clamp-2">
            {company.description}
          </p>
          
          <div className="flex items-center space-x-4 text-white/60 text-sm">
            <span className="flex items-center space-x-1">
              <Building2 className="h-3 w-3" />
              <span>{company.industry}</span>
            </span>
            <span className="flex items-center space-x-1">
              <MapPin className="h-3 w-3" />
              <span>{company.location}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Users className="h-3 w-3" />
              <span>{company.employees}</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {company.isHiring && (
            <div className="flex items-center space-x-2 text-green-400">
              <Briefcase className="h-4 w-4" />
              <span className="text-sm font-medium">{company.openPositions}</span>
            </div>
          )}
          
          <button
            onClick={() => toggleFavorite(company.id)}
            className={`p-2 rounded-full transition-all duration-300 ${
              isFavorite 
                ? 'bg-red-500 text-white shadow-glow' 
                : 'bg-white/10 text-white/70 hover:bg-white/20 hover:text-white'
            }`}
          >
            <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
          
          <button className="btn-primary py-2 px-4 rounded-lg text-sm">
            View
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6" ref={elementRef}>
      {/* Results Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Found {results.length} companies
          </h2>
          {query && (
            <p className="text-white/70">
              Showing results for "{query.term}"
              {query.filters && query.filters.length > 0 && (
                <span> with filters: {query.filters.join(', ')}</span>
              )}
            </p>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="relevance">Sort by Relevance</option>
            <option value="rating">Sort by Rating</option>
            <option value="employees">Sort by Size</option>
            <option value="founded">Sort by Founded</option>
          </select>

          {/* View Mode */}
          <div className="flex items-center bg-white/10 backdrop-blur-sm rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-all duration-300 ${
                viewMode === 'grid' 
                  ? 'bg-white/20 text-white' 
                  : 'text-white/70 hover:text-white'
              }`}
            >
              <Grid className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-all duration-300 ${
                viewMode === 'list' 
                  ? 'bg-white/20 text-white' 
                  : 'text-white/70 hover:text-white'
              }`}
            >
              <List className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className={`
        ${viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
        }
      `}>
        {sortedResults.map((company, index) => (
          viewMode === 'grid' ? (
            <CompanyCard key={company.id} company={company} index={index} />
          ) : (
            <CompanyListItem key={company.id} company={company} index={index} />
          )
        ))}
      </div>

      {/* Load More */}
      {results.length > 0 && (
        <div className="text-center">
          <button className="btn-ghost py-3 px-8 rounded-xl font-medium transition-all duration-300 hover:shadow-glow">
            Load More Companies
          </button>
        </div>
      )}
    </div>
  );
};

export default CompanyResults;