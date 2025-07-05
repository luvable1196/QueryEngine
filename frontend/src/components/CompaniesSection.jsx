import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Award, Users, Code, ArrowRight, Building2 } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import apiService from '../services/api';

const CompaniesSection = () => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const data = await apiService.getCompanies();
      setCompanies(data.companies || []);
    } catch (error) {
      console.error('Failed to fetch companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyClick = async (company) => {
    try {
      const data = await apiService.getCompanyDetails(company.name);
      setSelectedCompany(data);
    } catch (error) {
      console.error('Failed to fetch company details:', error);
    }
  };

  const handleSearchClick = async (companyName) => {
    if (companyName.trim()) {
      try {
        const data = await apiService.getCompanyDetails(companyName.trim());
        setSelectedCompany(data);
      } catch (error) {
        console.error('Failed to fetch company details:', error);
      }
    }
  };

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getColorClasses = (index) => {
    const colors = ['orange', 'blue', 'green', 'red'];
    const color = colors[index % colors.length];
    
    const colorMap = {
      orange: {
        bg: 'bg-orange-100 hover:bg-orange-200',
        border: 'border-orange-300 hover:border-orange-400',
        text: 'text-orange-700',
        icon: 'text-orange-600',
        gradient: 'from-orange-500 to-red-500'
      },
      blue: {
        bg: 'bg-blue-100 hover:bg-blue-200',
        border: 'border-blue-300 hover:border-blue-400',
        text: 'text-blue-700',
        icon: 'text-blue-600',
        gradient: 'from-blue-500 to-indigo-600'
      },
      green: {
        bg: 'bg-green-100 hover:bg-green-200',
        border: 'border-green-300 hover:border-green-400',
        text: 'text-green-700',
        icon: 'text-green-600',
        gradient: 'from-green-500 to-emerald-600'
      },
      red: {
        bg: 'bg-red-100 hover:bg-red-200',
        border: 'border-red-300 hover:border-red-400',
        text: 'text-red-700',
        icon: 'text-red-600',
        gradient: 'from-red-500 to-pink-600'
      }
    };
    return colorMap[color];
  };

  const getDifficultyData = (company) => [
    { name: 'Easy', value: company.easy_count, color: '#00af9b' },
    { name: 'Medium', value: company.medium_count, color: '#ffb800' },
    { name: 'Hard', value: company.hard_count, color: '#ff375f' },
  ];

  const getTopicsData = (company) => 
    company.most_common_topics?.slice(0, 5).map(topic => ({
      name: topic,
      value: Math.floor(Math.random() * 100) + 50, // Mock data for visualization
    })) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <span className="ml-3 text-gray-600">Loading companies...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gray-800 p-3 rounded-full shadow-lg">
              <Building2 className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-black mb-2">
            Company Explorer
          </h1>
          <p className="text-gray-600 text-lg">
            Explore LeetCode problems by company
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-2xl mx-auto mb-12">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search companies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearchClick(searchTerm);
                }
              }}
              className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-gray-500 focus:ring-4 focus:ring-gray-100 transition-all duration-300 shadow-lg"
            />
          </div>
        </div>

        {/* Company Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredCompanies.map((company, index) => {
            const colorClasses = getColorClasses(index);
            return (
              <div
                key={company.name}
                onClick={() => handleCompanyClick(company)}
                className={`group relative overflow-hidden rounded-3xl ${colorClasses.bg} ${colorClasses.border} border-2 shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-105 cursor-pointer`}
                style={{
                  animationDelay: `${index * 0.1}s`,
                  animation: 'fadeInUp 0.8s ease-out forwards'
                }}
              >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
                
                {/* Header */}
                <div className="relative p-8 pb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-3 rounded-xl ${colorClasses.bg} ${colorClasses.border} border shadow-sm`}>
                        <Building2 className={`h-6 w-6 ${colorClasses.icon}`} />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-800">{company.name}</h3>
                        <p className="text-sm text-gray-600">{company.problem_count} problems</p>
                      </div>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                </div>

                {/* Stats */}
                <div className="relative px-8 pb-6">
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center">
                      <div className="flex items-center justify-center mb-2">
                        <TrendingUp className={`h-5 w-5 ${colorClasses.icon} mr-2`} />
                        <span className="text-sm font-medium text-gray-600">Avg Frequency</span>
                      </div>
                      <div className="text-2xl font-bold text-gray-800">{company.avg_frequency?.toFixed(1)}</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center mb-2">
                        <Award className={`h-5 w-5 ${colorClasses.icon} mr-2`} />
                        <span className="text-sm font-medium text-gray-600">Acceptance Rate</span>
                      </div>
                      <div className="text-2xl font-bold text-gray-800">{(company.average_acceptance_rate * 100).toFixed(1)}%</div>
                    </div>
                  </div>

                  {/* Difficulty Breakdown */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between text-sm font-medium text-gray-600 mb-3">
                      <span>Difficulty Breakdown</span>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="text-center p-3 bg-white rounded-xl border border-gray-200 shadow-sm">
                        <div className="text-lg font-bold text-green-600">Easy: {company.easy_count}</div>
                      </div>
                      <div className="text-center p-3 bg-white rounded-xl border border-gray-200 shadow-sm">
                        <div className="text-lg font-bold text-yellow-600">Medium: {company.medium_count}</div>
                      </div>
                      <div className="text-center p-3 bg-white rounded-xl border border-gray-200 shadow-sm">
                        <div className="text-lg font-bold text-red-600">Hard: {company.hard_count}</div>
                      </div>
                    </div>
                  </div>

                  {/* Topics */}
                  <div>
                    <div className="flex items-center mb-3">
                      <Code className={`h-4 w-4 ${colorClasses.icon} mr-2`} />
                      <span className="text-sm font-medium text-gray-600">Popular Topics</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {company.most_common_topics?.slice(0, 3).map((topic, idx) => (
                        <span
                          key={idx}
                          className={`px-3 py-1 text-xs font-medium rounded-full ${colorClasses.text} ${colorClasses.bg} border ${colorClasses.border}`}
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Hover Effect */}
                <div className="absolute inset-0 rounded-3xl ring-4 ring-transparent group-hover:ring-gray-200 transition-all duration-500" />
              </div>
            );
          })}
        </div>

        {/* No Results */}
        {filteredCompanies.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Users className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No companies found</h3>
            <p className="text-gray-500">Try adjusting your search terms</p>
          </div>
        )}

        {/* Company Details Modal */}
        {selectedCompany && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <Building2 className="h-8 w-8 text-white" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{selectedCompany.name}</h2>
                      <p className="text-gray-600">{selectedCompany.problem_count} problems</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedCompany(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                  {/* Stats Cards */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-5 w-5 text-blue-600" />
                        <span className="text-sm text-blue-800">Avg Frequency</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-900">{selectedCompany.avg_frequency?.toFixed(1)}</p>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Users className="h-5 w-5 text-green-600" />
                        <span className="text-sm text-green-800">Acceptance Rate</span>
                      </div>
                      <p className="text-2xl font-bold text-green-900">{(selectedCompany.average_acceptance_rate * 100).toFixed(1)}%</p>
                    </div>
                  </div>

                  {/* Difficulty Distribution */}
                  <div className="bg-white border rounded-lg p-4">
                    <h3 className="text-lg font-semibold mb-3">Difficulty Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={getDifficultyData(selectedCompany)}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {getDifficultyData(selectedCompany).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Topics Chart */}
                <div className="bg-white border rounded-lg p-4 mb-6">
                  <h3 className="text-lg font-semibold mb-3">Most Common Topics</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={getTopicsData(selectedCompany)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Topics List */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">All Topics</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCompany.most_common_topics?.map((topic, idx) => (
                      <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default CompaniesSection;