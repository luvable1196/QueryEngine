// Use relative URLs to leverage Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiService {
  async request(endpoint, options = {}) {
    // In development, use proxy path; in production, use full URL
    const url = import.meta.env.DEV ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      console.log('Making API request to:', url, 'with config:', config);
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async getHealth() {
    return this.request('/health');
  }

  async getDetailedHealth() {
    return this.request('/health/detailed');
  }

  // API Info
  async getApiInfo() {
    return this.request('/info');
  }

  // Companies
  async getCompanies() {
    return this.request('/api/v1/companies/');
  }

  async getCompanyDetails(companyName) {
    return this.request(`/api/v1/companies/${companyName}`);
  }

  // Query Problems - Main search functionality
  async searchProblems(query, filters = {}) {
    const requestBody = {};
    
    if (query) requestBody.query = query;
    if (filters.difficulty) requestBody.difficulty = filters.difficulty;
    if (filters.company) requestBody.company = filters.company;
    if (filters.topics) requestBody.topics = filters.topics;
    if (filters.limit) requestBody.limit = filters.limit;
    if (filters.offset) requestBody.offset = filters.offset;

    return this.request('/api/v1/query/', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  // Natural language query
  async naturalLanguageQuery(query) {
    return this.request('/api/v1/query/nl', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Stats
  async getDatabaseStats() {
    return this.request('/stats/database');
  }

  async getSystemStats() {
    return this.request('/stats/system');
  }

  // Utility methods for the frontend
  async searchWithFilters(searchTerm, difficulty = null, company = null, topics = null, limit = 20, offset = 0) {
    const filters = {
      difficulty,
      company,
      topics,
      limit,
      offset
    };

    // Remove null/undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key] === null || filters[key] === undefined) {
        delete filters[key];
      }
    });

    return this.searchProblems(searchTerm, filters);
  }

  // Quick search for common use cases
  async quickSearch(term) {
    return this.searchProblems(term, { limit: 10 });
  }

  // Get trending problems (mock implementation - you might want to add this endpoint to your backend)
  async getTrendingProblems() {
    // This would be a real endpoint in your backend
    // For now, we'll use a regular search with popular companies
    return this.searchProblems('', { 
      company: 'Google,Amazon,Microsoft,Apple,Facebook', 
      limit: 10 
    });
  }
}

export default new ApiService();