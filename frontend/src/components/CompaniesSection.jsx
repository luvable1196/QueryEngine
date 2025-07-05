import { useState, useEffect } from 'react';
import { Building2, TrendingUp, Users, Code, ChevronRight } from 'lucide-react';
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

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
        <div className="loading-spinner" />
        <span className="ml-3 text-gray-600">Loading companies...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Company Analysis</h2>
        <p className="text-gray-600">Explore LeetCode problems by company</p>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search companies..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Companies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCompanies.map((company) => (
          <div
            key={company.name}
            onClick={() => handleCompanyClick(company)}
            className="card cursor-pointer hover:shadow-lg hover:scale-105 transform transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
                  <p className="text-sm text-gray-600">{company.problem_count} problems</p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-gray-400" />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Avg Frequency</span>
                <span className="font-semibold text-gray-900">{company.avg_frequency.toFixed(1)}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Acceptance Rate</span>
                <span className="font-semibold text-gray-900">{(company.average_acceptance_rate * 100).toFixed(1)}%</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-easy">Easy: {company.easy_count}</span>
                <span className="text-medium">Medium: {company.medium_count}</span>
                <span className="text-hard">Hard: {company.hard_count}</span>
              </div>

              <div className="flex flex-wrap gap-1 mt-2">
                {company.most_common_topics?.slice(0, 3).map((topic, idx) => (
                  <span key={idx} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Company Details Modal */}
      {selectedCompany && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
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
                    <span key={idx} className="topic-tag">
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
  );
};

export default CompaniesSection;