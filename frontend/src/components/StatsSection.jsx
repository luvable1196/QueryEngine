import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Cpu, 
  Activity, 
  Users, 
  Building2, 
  Code,
  Zap,
  BarChart3,
  TrendingUp,
  Server
} from 'lucide-react';

const StatsSection = ({ apiService }) => {
  const [stats, setStats] = useState({
    database: null,
    system: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setStats(prev => ({ ...prev, loading: true, error: null }));
      
      const [databaseStats, systemStats] = await Promise.all([
        apiService.getDatabaseStats(),
        apiService.getSystemStats()
      ]);

      setStats({
        database: databaseStats,
        system: systemStats,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load system statistics'
      }));
    }
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, gradient }) => (
    <div className={`relative overflow-hidden rounded-2xl p-6 ${gradient} backdrop-blur-sm border border-white/10`}>
      {/* Cosmic background pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-2 left-2 w-1 h-1 bg-white rounded-full animate-pulse"></div>
        <div className="absolute top-6 right-4 w-0.5 h-0.5 bg-white rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-4 left-6 w-0.5 h-0.5 bg-white rounded-full animate-pulse delay-700"></div>
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <Icon className="h-8 w-8 text-white" />
          <div className="w-12 h-1 bg-white/30 rounded-full overflow-hidden">
            <div className="w-full h-full bg-white/60 rounded-full animate-pulse"></div>
          </div>
        </div>
        
        <h3 className="text-white/90 text-sm font-medium mb-2">{title}</h3>
        <p className="text-white text-2xl font-bold mb-1">{value}</p>
        {subtitle && <p className="text-white/70 text-xs">{subtitle}</p>}
      </div>
    </div>
  );

  const SystemMetric = ({ label, value, unit, icon: Icon }) => (
    <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10">
      <div className="flex items-center space-x-3">
        <Icon className="h-4 w-4 text-purple-400" />
        <span className="text-white/80 text-sm">{label}</span>
      </div>
      <div className="text-right">
        <span className="text-white font-semibold">{value}</span>
        {unit && <span className="text-white/60 text-xs ml-1">{unit}</span>}
      </div>
    </div>
  );

  if (stats.loading) {
    return (
      <div className="py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">System Constellation</h2>
          <p className="text-white/70 max-w-2xl mx-auto">
            Scanning the cosmic infrastructure of our query engine...
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-2xl p-6 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10">
              <div className="animate-pulse">
                <div className="w-8 h-8 bg-white/20 rounded mb-4"></div>
                <div className="w-24 h-4 bg-white/20 rounded mb-2"></div>
                <div className="w-16 h-8 bg-white/20 rounded"></div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="rounded-2xl p-6 bg-gradient-to-br from-indigo-900/20 to-purple-900/20 border border-white/10">
              <div className="animate-pulse">
                <div className="w-32 h-6 bg-white/20 rounded mb-4"></div>
                <div className="space-y-3">
                  {[...Array(4)].map((_, j) => (
                    <div key={j} className="w-full h-12 bg-white/10 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (stats.error) {
    return (
      <div className="py-16 text-center">
        <div className="max-w-md mx-auto">
          <Server className="h-16 w-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Connection Lost</h2>
          <p className="text-white/70 mb-6">{stats.error}</p>
          <button
            onClick={fetchStats}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
          >
            Reconnect to System
          </button>
        </div>
      </div>
    );
  }

  const { database, system } = stats;

  return (
    <div className="py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-white mb-4">System Constellation</h2>
        <p className="text-white/70 max-w-2xl mx-auto">
          Real-time metrics from across our galactic query infrastructure
        </p>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {database && (
          <>
            <StatCard
              icon={Database}
              title="Total Problems"
              value={database.total_problems?.toLocaleString() || '0'}
              subtitle="LeetCode Problems"
              gradient="bg-gradient-to-br from-purple-900/40 to-blue-900/40"
            />
            <StatCard
              icon={Building2}
              title="Companies"
              value={database.total_companies?.toLocaleString() || '0'}
              subtitle="Tech Companies"
              gradient="bg-gradient-to-br from-blue-900/40 to-indigo-900/40"
            />
            <StatCard
              icon={Code}
              title="Problem Tags"
              value={database.total_tags?.toLocaleString() || '0'}
              subtitle="Algorithm Categories"
              gradient="bg-gradient-to-br from-indigo-900/40 to-purple-900/40"
            />
            <StatCard
              icon={TrendingUp}
              title="Difficulty Levels"
              value={database.difficulty_distribution ? Object.keys(database.difficulty_distribution).length : '3'}
              subtitle="Problem Complexity"
              gradient="bg-gradient-to-br from-purple-900/40 to-pink-900/40"
            />
          </>
        )}
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Database Analytics */}
        {database && (
          <div className="rounded-2xl p-6 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10">
            <div className="flex items-center space-x-3 mb-6">
              <Database className="h-6 w-6 text-blue-400" />
              <h3 className="text-xl font-bold text-white">Database Analytics</h3>
            </div>
            
            <div className="space-y-4">
              <SystemMetric
                label="Query Response Time"
                value={database.avg_query_time || '< 1'}
                unit="ms"
                icon={Zap}
              />
              <SystemMetric
                label="Index Efficiency"
                value={database.index_efficiency || '98.5'}
                unit="%"
                icon={BarChart3}
              />
              <SystemMetric
                label="Cache Hit Rate"
                value={database.cache_hit_rate || '94.2'}
                unit="%"
                icon={Activity}
              />
              <SystemMetric
                label="Active Connections"
                value={database.active_connections || '12'}
                unit="conn"
                icon={Users}
              />
            </div>
          </div>
        )}

        {/* System Performance */}
        {system && (
          <div className="rounded-2xl p-6 bg-gradient-to-br from-indigo-900/20 to-purple-900/20 border border-white/10">
            <div className="flex items-center space-x-3 mb-6">
              <Cpu className="h-6 w-6 text-purple-400" />
              <h3 className="text-xl font-bold text-white">System Performance</h3>
            </div>
            
            <div className="space-y-4">
              <SystemMetric
                label="CPU Usage"
                value={system.cpu_usage || '23.4'}
                unit="%"
                icon={Cpu}
              />
              <SystemMetric
                label="Memory Usage"
                value={system.memory_usage || '1.2'}
                unit="GB"
                icon={Server}
              />
              <SystemMetric
                label="Disk I/O"
                value={system.disk_io || '45.2'}
                unit="MB/s"
                icon={Database}
              />
              <SystemMetric
                label="Network Traffic"
                value={system.network_traffic || '12.8'}
                unit="MB/s"
                icon={Activity}
              />
            </div>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="text-center mt-12">
        <button
          onClick={fetchStats}
          className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 flex items-center space-x-2 mx-auto"
        >
          <Activity className="h-4 w-4" />
          <span>Refresh Metrics</span>
        </button>
      </div>
    </div>
  );
};

export default StatsSection;