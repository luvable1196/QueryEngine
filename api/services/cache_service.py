import redis.asyncio as redis
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CompanyDataCacheManager:
    def __init__(self, max_queries: int = 20, frequency_threshold: int = 3, 
                 recency_threshold_hours: int = 24):
        self.max_queries = max_queries
        self.frequency_threshold = frequency_threshold  # Min frequency to consider "frequent"
        self.recency_threshold = recency_threshold_hours * 3600  # Convert to seconds
        self.redis = None
        
        # Redis keys for different data structures
        self.QUERY_DATA_KEY = "smart_query_data"        # Hash: query_key -> result_data
        self.QUERY_METADATA_KEY = "smart_query_metadata" # Hash: query_key -> metadata
        self.FREQUENCY_SCORE_KEY = "smart_query_frequency" # Sorted Set: query_key -> frequency_score
        self.LAST_ACCESS_KEY = "smart_query_last_access"  # Sorted Set: query_key -> last_access_time
    
    async def initialize(self, redis_client):
        """Initialize with existing Redis client"""
        self.redis = redis_client
        logger.info("Smart LRU Query Cache Manager initialized")
    
    async def get_cached_query(self, query_params: Dict[str, Any], limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached query result and update frequency + recency
        """
        if not self.redis:
            return None
        
        try:
            query_key = self._generate_query_key(query_params, limit)
            
            # Check if query exists in cache
            cached_data = await self.redis.hget(self.QUERY_DATA_KEY, query_key)
            
            if cached_data:
                current_time = time.time()
                
                # Update access metadata
                await self._update_query_access(query_key, current_time)
                
                logger.info(f"Smart Cache hit for query: {query_key}")
                return json.loads(cached_data)
            
            logger.info(f"Smart Cache miss for query: {query_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached query: {e}")
            return None
    
    async def cache_query_result(self, query_params: Dict[str, Any], companies: List[Dict[str, Any]], limit: int = 100):
        """
        Cache query result with smart frequency-based eviction
        """
        if not self.redis:
            return
        
        try:
            query_key = self._generate_query_key(query_params, limit)
            current_time = time.time()
            
            # Check if we need to evict based on smart criteria
            await self._smart_eviction_check(query_key)
            
            # Store the query data
            await self.redis.hset(self.QUERY_DATA_KEY, query_key, json.dumps(companies))
            
            # Initialize or update metadata
            await self._initialize_query_metadata(query_key, query_params, len(companies), current_time)
            
            # Update frequency and recency scores
            await self._update_query_access(query_key, current_time)
            
            logger.info(f"Query cached with Smart LRU: {query_key}, result count: {len(companies)}")
            
        except Exception as e:
            logger.error(f"Error caching query result: {e}")
    
    async def _smart_eviction_check(self, new_query_key: str):
        """
        Smart eviction based on frequency and recency
        """
        try:
            current_count = await self.redis.hlen(self.QUERY_DATA_KEY)
            is_new_query = not await self.redis.hexists(self.QUERY_DATA_KEY, new_query_key)
            
            if is_new_query and current_count >= self.max_queries:
                # Find candidates for eviction
                eviction_candidate = await self._find_eviction_candidate()
                
                if eviction_candidate:
                    await self._evict_query(eviction_candidate)
                    logger.info(f"Smart eviction: removed {eviction_candidate}")
                else:
                    logger.warning("No suitable eviction candidate found")
            
        except Exception as e:
            logger.error(f"Error in smart eviction check: {e}")
    
    async def _find_eviction_candidate(self) -> Optional[str]:
        """
        Find the best candidate for eviction based on frequency and recency
        Priority: Low frequency + Old access time
        """
        try:
            current_time = time.time()
            all_queries = await self.redis.hkeys(self.QUERY_DATA_KEY)
            
            candidates = []
            
            for query_key in all_queries:
                # Get metadata
                metadata_str = await self.redis.hget(self.QUERY_METADATA_KEY, query_key)
                if not metadata_str:
                    continue
                
                metadata = json.loads(metadata_str)
                access_count = metadata.get("access_count", 0)
                last_accessed = metadata.get("last_accessed", 0)
                
                # Calculate time since last access
                time_since_access = current_time - last_accessed
                
                # Calculate eviction score (higher = more likely to evict)
                eviction_score = self._calculate_eviction_score(access_count, time_since_access)
                
                candidates.append({
                    "query_key": query_key,
                    "access_count": access_count,
                    "time_since_access": time_since_access,
                    "eviction_score": eviction_score
                })
            
            if not candidates:
                return None
            
            # Sort by eviction score (highest first)
            candidates.sort(key=lambda x: x["eviction_score"], reverse=True)
            
            # Log eviction reasoning
            best_candidate = candidates[0]
            logger.info(f"Eviction candidate: {best_candidate['query_key']}, "
                       f"access_count: {best_candidate['access_count']}, "
                       f"hours_since_access: {best_candidate['time_since_access']/3600:.1f}")
            
            return best_candidate["query_key"]
            
        except Exception as e:
            logger.error(f"Error finding eviction candidate: {e}")
            return None
    
    def _calculate_eviction_score(self, access_count: int, time_since_access: float) -> float:
        """
        Calculate eviction score based on frequency and recency
        Higher score = more likely to be evicted
        """
        # Frequency component (lower frequency = higher eviction score)
        frequency_score = max(0, self.frequency_threshold - access_count) * 10
        
        # Recency component (older = higher eviction score)
        recency_score = min(time_since_access / self.recency_threshold, 2) * 5
        
        # Combined score
        total_score = frequency_score + recency_score
        
        # Bonus penalty for very low frequency queries
        if access_count == 1:
            total_score += 5
        
        return total_score
    
    async def _evict_query(self, query_key: str):
        """Remove query from all cache structures"""
        try:
            await self.redis.hdel(self.QUERY_DATA_KEY, query_key)
            await self.redis.hdel(self.QUERY_METADATA_KEY, query_key)
            await self.redis.zrem(self.FREQUENCY_SCORE_KEY, query_key)
            await self.redis.zrem(self.LAST_ACCESS_KEY, query_key)
            
        except Exception as e:
            logger.error(f"Error evicting query {query_key}: {e}")
    
    async def _initialize_query_metadata(self, query_key: str, query_params: Dict[str, Any], 
                                       result_count: int, current_time: float):
        """Initialize metadata for new query"""
        try:
            existing_metadata = await self.redis.hget(self.QUERY_METADATA_KEY, query_key)
            
            if existing_metadata:
                # Update existing
                metadata = json.loads(existing_metadata)
            else:
                # Create new
                metadata = {
                    "query_params": query_params,
                    "result_count": result_count,
                    "first_cached": current_time,
                    "access_count": 0,
                    "last_accessed": current_time
                }
            
            await self.redis.hset(self.QUERY_METADATA_KEY, query_key, json.dumps(metadata))
            
        except Exception as e:
            logger.error(f"Error initializing metadata: {e}")
    
    async def _update_query_access(self, query_key: str, current_time: float):
        """Update frequency and recency scores"""
        try:
            # Get current metadata
            metadata_str = await self.redis.hget(self.QUERY_METADATA_KEY, query_key)
            if not metadata_str:
                return
            
            metadata = json.loads(metadata_str)
            metadata["access_count"] = metadata.get("access_count", 0) + 1
            metadata["last_accessed"] = current_time
            
            # Update metadata
            await self.redis.hset(self.QUERY_METADATA_KEY, query_key, json.dumps(metadata))
            
            # Update frequency score (access count)
            await self.redis.zadd(self.FREQUENCY_SCORE_KEY, {query_key: metadata["access_count"]})
            
            # Update last access time
            await self.redis.zadd(self.LAST_ACCESS_KEY, {query_key: current_time})
            
        except Exception as e:
            logger.error(f"Error updating query access: {e}")
    
    def _generate_query_key(self, query_params: Dict[str, Any], limit: int) -> str:
        """Generate a unique cache key for the query"""
        query_str = json.dumps(query_params, sort_keys=True) + f"_limit_{limit}"
        query_hash = hashlib.md5(query_str.encode()).hexdigest()
        return f"smart_query_{query_hash}"
    
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """Get comprehensive cache analytics"""
        if not self.redis:
            return {"error": "Redis not available"}
        
        try:
            # Get all queries
            all_queries = await self.redis.hkeys(self.QUERY_DATA_KEY)
            current_time = time.time()
            
            query_stats = []
            total_access_count = 0
            
            for query_key in all_queries:
                metadata_str = await self.redis.hget(self.QUERY_METADATA_KEY, query_key)
                if metadata_str:
                    metadata = json.loads(metadata_str)
                    access_count = metadata.get("access_count", 0)
                    last_accessed = metadata.get("last_accessed", 0)
                    
                    total_access_count += access_count
                    
                    query_stats.append({
                        "query_key": query_key,
                        "query_params": metadata.get("query_params", {}),
                        "access_count": access_count,
                        "result_count": metadata.get("result_count", 0),
                        "hours_since_access": (current_time - last_accessed) / 3600,
                        "eviction_score": self._calculate_eviction_score(access_count, current_time - last_accessed),
                        "is_frequent": access_count >= self.frequency_threshold,
                        "is_recent": (current_time - last_accessed) < self.recency_threshold
                    })
            
            # Sort by access count (most frequent first)
            query_stats.sort(key=lambda x: x["access_count"], reverse=True)
            
            # Calculate distribution
            frequent_queries = [q for q in query_stats if q["is_frequent"]]
            recent_queries = [q for q in query_stats if q["is_recent"]]
            
            return {
                "total_cached_queries": len(all_queries),
                "max_queries": self.max_queries,
                "cache_utilization": f"{(len(all_queries) / self.max_queries) * 100:.1f}%",
                "total_access_count": total_access_count,
                "frequent_queries_count": len(frequent_queries),
                "recent_queries_count": len(recent_queries),
                "frequency_threshold": self.frequency_threshold,
                "recency_threshold_hours": self.recency_threshold / 3600,
                "query_distribution": {
                    "high_frequency": len([q for q in query_stats if q["access_count"] >= 5]),
                    "medium_frequency": len([q for q in query_stats if 2 <= q["access_count"] < 5]),
                    "low_frequency": len([q for q in query_stats if q["access_count"] < 2])
                },
                "top_queries": query_stats[:10],
                "eviction_candidates": sorted(query_stats, key=lambda x: x["eviction_score"], reverse=True)[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting cache analytics: {e}")
            return {"error": str(e)}
    
    async def clear_cache(self):
        """Clear all cache data"""
        if not self.redis:
            return {"error": "Redis not available"}
        
        try:
            await self.redis.delete(self.QUERY_DATA_KEY)
            await self.redis.delete(self.QUERY_METADATA_KEY)
            await self.redis.delete(self.FREQUENCY_SCORE_KEY)
            await self.redis.delete(self.LAST_ACCESS_KEY)
            
            logger.info("Smart cache cleared successfully")
            return {"success": True, "message": "Smart cache cleared"}
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"error": str(e)}
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        if not self.redis:
            return {"error": "Redis not available"}
        
        try:
            # Get Redis info
            info = await self.redis.info("memory")
            
            # Calculate cache-specific memory usage
            cache_keys = [
                self.QUERY_DATA_KEY,
                self.QUERY_METADATA_KEY,
                self.FREQUENCY_SCORE_KEY,
                self.LAST_ACCESS_KEY
            ]
            
            cache_memory = 0
            for key in cache_keys:
                try:
                    # Estimate memory usage per key
                    key_memory = await self.redis.memory_usage(key)
                    if key_memory:
                        cache_memory += key_memory
                except:
                    pass  # Key might not exist
            
            return {
                "total_redis_memory": info.get("used_memory_human", "Unknown"),
                "total_redis_memory_bytes": info.get("used_memory", 0),
                "cache_memory_bytes": cache_memory,
                "cache_memory_mb": cache_memory / (1024 * 1024),
                "allocated_limit_mb": 128,
                "memory_utilization": f"{(cache_memory / (128 * 1024 * 1024)) * 100:.2f}%"
            }
            
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {"error": str(e)}

    async def health_check(self):
        """Health check method for the cache manager"""
        try:
            # Check if Redis is accessible and can perform operations
            if hasattr(self, 'redis') and self.redis is not None:
                # Test Redis connection with a simple operation
                await self.redis.ping()
                return {"status": "healthy", "redis": "accessible"}
            else:
                return {"status": "degraded", "redis": "not_initialized"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Usage example with your existing cache manager
async def example_smart_cache_usage():
    """Example usage of the smart cache"""
    
    # Initialize cache manager
    cache_manager = CompanyDataCacheManager(
        max_queries=20,
        frequency_threshold=3,  # Queries with 3+ accesses are considered frequent
        recency_threshold_hours=24  # Queries accessed within 24 hours are recent
    )
    
    # Simulate Redis connection (use your existing Redis client)
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    await cache_manager.initialize(redis_client)
    
    # Example: Simulate query patterns
    queries = [
        {"industry": "technology"},           # Will be accessed 5 times
        {"location": "bangalore"},           # Will be accessed 3 times  
        {"industry": "healthcare"},          # Will be accessed 1 time
        {"size": "large"},                   # Will be accessed 2 times
        {"industry": "fintech", "location": "mumbai"}  # Will be accessed 1 time
    ]
    
    # Simulate access patterns
    for i in range(10):
        for j, query in enumerate(queries):
            # Different access frequencies
            if j == 0 and i < 5:  # First query accessed 5 times
                await cache_manager.cache_query_result(query, [{"dummy": "data"}])
            elif j == 1 and i < 3:  # Second query accessed 3 times
                await cache_manager.cache_query_result(query, [{"dummy": "data"}])
            elif j == 2 and i < 1:  # Third query accessed 1 time
                await cache_manager.cache_query_result(query, [{"dummy": "data"}])
            elif j == 3 and i < 2:  # Fourth query accessed 2 times
                await cache_manager.cache_query_result(query, [{"dummy": "data"}])
            elif j == 4 and i < 1:  # Fifth query accessed 1 time
                await cache_manager.cache_query_result(query, [{"dummy": "data"}])
    
    # Get analytics
    analytics = await cache_manager.get_cache_analytics()
    memory_usage = await cache_manager.get_memory_usage()
    
    print("Smart Cache Analytics:")
    print(f"- Total queries: {analytics['total_cached_queries']}")
    print(f"- Frequent queries: {analytics['frequent_queries_count']}")
    print(f"- Memory usage: {memory_usage['cache_memory_mb']:.2f} MB")
    print(f"- Top queries: {analytics['top_queries'][:3]}")
    
    await redis_client.aclose()



# Run example
# asyncio.run(example_smart_cache_usage())