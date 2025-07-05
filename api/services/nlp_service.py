import re
import nltk
from typing import Dict, List, Any, Optional, Set
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

class NLPService:
    """
    Natural Language Processing service for query parsing and intent recognition
    """
    
    def __init__(self):
        self.topics = None
        self.companies = None
        self.difficulty_patterns = None
        self.intent_patterns = None
        self.stop_words = None
        self.topic_aliases = None
        self.company_aliases = None
        self.tfidf_vectorizer = None

    async def initialize(self):
        """Initialize the NLP service with required data and models"""
        try:
            # Define topics
            self.topics = [
                "Array", "String", "Hash Table", "Dynamic Programming", "Math",
                "Sorting", "Greedy", "Depth-First Search", "Binary Search", "Tree",
                "Breadth-First Search", "Matrix", "Two Pointers", "Bit Manipulation",
                "Stack", "Design", "Heap", "Graph", "Prefix Sum", "Simulation",
                "Counting", "Sliding Window", "Union Find", "Linked List", "Recursion",
                "Trie", "Divide and Conquer", "Backtracking", "Monotonic Stack",
                "Queue", "Binary Tree", "Binary Search Tree", "Segment Tree",
                "Topological Sort", "Dijkstra", "BFS", "DFS", "Priority Queue",
                "Monotonic Queue", "Game Theory", "Minimax", "Rolling Hash",
                "Reservoir Sampling", "Rejection Sampling", "Quick Select",
                "Merge Sort", "Heap Sort", "Counting Sort", "Radix Sort",
                "Bucket Sort", "Shell Sort", "Insertion Sort", "Selection Sort",
                "Bubble Sort", "Pancake Sort", "Cycle Sort", "Pigeonhole Sort"
            ]
            
            # Define companies - Updated with your comprehensive list
            self.companies = [
                "Accenture", "Accolite", "Acko", "Activision", "Adobe", "Affirm", "Agoda", 
                "Airbnb", "Airbus SE", "Airtel", "Airwallex", "Akamai", "Akuna Capital", 
                "Alibaba", "Altimetrik", "Amadeus", "Amazon", "AMD", "Amdocs", 
                "American Express", "Analytics quotient", "Anduril", "Aon", "Apollo.io", 
                "AppDynamics", "AppFolio", "Apple", "Applied Intuition", "AQR Capital Management", 
                "Arcesium", "Arista Networks", "Asana", "athenahealth", "Atlassian", 
                "Attentive", "Audible", "Aurora", "Autodesk", "Avalara", "Avito", "Axon",
                "Baidu", "Bank of America", "Barclays", "Bentley Systems", "BharatPe", 
                "BILL Holdings", "BitGo", "BlackRock", "BlackStone", "blinkit", "Blizzard", 
                "Block", "Bloomberg", "BNY Mellon", "Bolt", "Booking.com", "Bosch", "Box", 
                "BP", "Braze", "Brex", "Bridgewater Associates", "ByteDance",
                "Cadence", "Canonical", "Capgemini", "Capital One", "Careem", "CARS24", 
                "carwale", "Cashfree", "CEDCOSS", "Celigo", "Chewy", "Chime", "ciena", 
                "Circle", "Cisco", "Citadel", "Citigroup", "Citrix", "Clari", "Cleartrip", 
                "Cloudera", "Cloudflare", "CME Group", "Coforge", "Cognizant", "Cohesity", 
                "Coinbase", "Comcast", "Commvault", "Compass", "Confluent", "ConsultAdd", 
                "Coupang", "Coursera", "Coveo", "CRED", "Credit Karma", "Criteo", 
                "CrowdStrike", "Cruise", "CTC", "CureFit", "CVENT",
                "Darwinbox", "Databricks", "Datadog", "Dataminr", "DE Shaw", "Delhivery", 
                "Deliveroo", "Dell", "Deloitte", "DeltaX", "Deutsche Bank", "DevRev", 
                "Devsinc", "Devtron", "Directi", "Disney", "Docusign", "DoorDash", 
                "DP world", "Dream11", "Dropbox", "Druva", "DRW", "Dunzo", "Duolingo", 
                "DXC Technology",
                "EarnIn", "eBay", "Edelweiss Group", "Electronic Arts", "EPAM Systems", 
                "Epic Systems", "Expedia", "EY",
                "FactSet", "Faire", "Fastenal", "Fidelity", "Fiverr", "Flexera", 
                "Flexport", "Flipkart", "Fortinet", "fourkites", "FPT", "Freecharge", 
                "FreshWorks",
                "Gameskraft", "Garmin", "GE Digital", "GE Healthcare", "Geico", 
                "General Motors", "Genpact", "GoDaddy", "Gojek", "Goldman Sachs", 
                "Google", "Grab", "Grammarly", "Graviton", "Groupon", "Groww", 
                "Grubhub", "GSA Capital", "GSN Games", "Guidewire", "Gusto",
                "Harness", "HashedIn", "HCL", "Hertz", "Highspot", "HiLabs", "Hive", 
                "Hiver", "Honeywell", "Hotstar", "Houzz", "HP", "HPE", "HSBC", 
                "Huawei", "Hubspot", "Hudson River Trading", "Hulu",
                "IBM", "IIT Bombay", "IMC", "Indeed", "INDmoney", "Info Edge", 
                "Informatica", "Infosys", "InMobi", "instabase", "Instacart", "Intel", 
                "Intuit", "IVP", "IXL",
                "J.P. Morgan", "Jane Street", "jio", "josh technology", "Jump Trading", 
                "Juniper Networks", "Juspay",
                "Kakao", "Karat", "KLA", "Komprise",
                "Larsen & Toubro", "Lendingkart Technologies", "Lenskart", "Licious", 
                "Liftoff", "LINE", "LinkedIn", "LiveRamp", "Lowe's", "LTI", "Lucid", 
                "Luxoft", "Lyft",
                "Machine Zone", "MakeMyTrip", "Mapbox", "MAQ Software", "Mastercard", 
                "MathWorks", "McKinsey", "Media.net", "Meesho", "Mercari", "Meta", 
                "Microsoft", "Microstrategy", "Millennium", "Mindtickle", "MindTree", 
                "Miro", "Mitsogo", "Mixpanel", "Mobileye", "Moengage", "Moloco", 
                "MongoDB", "Morgan Stanley", "Mountblue", "Moveworks", "MSCI", "Myntra",
                "Nagarro", "National Instruments", "National Payments Corporation of India", 
                "Navan", "Navi", "NCR", "NetApp", "NetEase", "Netflix", "Netskope", 
                "Netsuite", "Nextdoor", "Niantic", "Nielsen", "Nike", "NinjaCart", 
                "Nokia", "Nordstrom", "Notion", "Nuro", "Nutanix", "Nvidia", "Nykaa",
                "Odoo", "Okta", "OKX", "Ola Cabs", "OpenAI", "Opendoor", "opentext", 
                "Optiver", "Optum", "Oracle", "Otter.ai", "oyo", "Ozon",
                "Palantir Technologies", "Palo Alto Networks", "Patreon", "Paycom", 
                "PayPal", "PayPay", "Paytm", "PayU", "peak6", "Peloton", 
                "persistent systems", "PhonePe", "Pinterest", "Pocket Gems", "Point72", 
                "Pony.ai", "PornHub", "Poshmark", "Postmates", "Publicis Sapient", 
                "PubMatic", "Pure Storage", "Pwc",
                "QBurst", "Qualcomm", "Qualtrics", "Quora",
                "Rakuten", "razorpay", "RBC", "redbus", "Reddit", "Remitly", "Revolut", 
                "Riot Games", "Ripple", "Rippling", "Rivian", "Robinhood", "Roblox", 
                "Roche", "Rokt", "Roku", "Rubrik",
                "Salesforce", "Samsara", "Samsung", "SAP", "Scale AI", "Sentry", 
                "ServiceNow", "ShareChat", "Shopee", "Shopify", "Siemens", "SIG", 
                "Sigmoid", "Slice", "smartnews", "Smartsheet", "Snap", "Snapdeal", 
                "Snowflake", "Societe Generale", "SoFi", "Softwire", "Sony", "SOTI", 
                "SoundHound", "Splunk", "Spotify", "Sprinklr", "Squarepoint Capital", 
                "Squarespace", "StackAdapt", "Stackline", "Stripe", "Sumo Logic", 
                "Swiggy", "Synopsys",
                "Tanium", "Target", "tcs", "Tech Mahindra", "Tejas Networks", "Tekion", 
                "Tencent", "Teradata", "Tesco", "Tesla", "Texas Instruments", 
                "The Trade Desk", "Thomson Reuters", "thoughtspot", "ThoughtWorks", 
                "ThousandEyes", "Tiger Analytics", "TikTok", "Tinder", "Tinkoff", 
                "Toast", "Toptal", "Tower Research Capital", "Trexquant", "Trilogy", 
                "Tripadvisor", "Turing", "Turo", "Turvo", "TuSimple", "Twilio", 
                "Twitch", "Two Sigma",
                "Uber", "UBS", "UiPath", "UKG", "Unity", "Upstart", "Urban Company", 
                "USAA",
                "Valve", "Vanguard", "Veeva Systems", "Verily", "Veritas", "Verkada", 
                "Vimeo", "Virtu Financial", "Virtusa", "Visa", "VK", "VMware",
                "Walmart Labs", "Warnermedia", "WatchGuard", "Wayfair", "Waymo", 
                "Wealthfront", "Wells Fargo", "WeRide", "Western Digital", "Whatnot", 
                "WinZO", "Wipro", "Wise", "Wish", "Wissen Technology", "Wix", 
                "Workday", "Works Applications", "WorldQuant",
                "X", "Yahoo", "Yandex", "Yelp", "Yext",
                "Zalando", "Zendesk", "Zenefits", "Zepto", "Zeta", "zeta suite", 
                "Zillow", "ZipRecruiter", "Zluri", "Zoho", "Zomato", "Zoom", "Zoox", 
                "Zopsmart", "ZS Associates", "ZScaler", "Zynga"
            ]
            
            # Define difficulty patterns
            self.difficulty_patterns = {
                "easy": ["easy", "simple", "basic", "beginner", "trivial", "straightforward"],
                "medium": ["medium", "intermediate", "moderate", "average", "standard"],
                "hard": ["hard", "difficult", "challenging", "advanced", "expert", "complex", "tough"]
            }
            
            # Define intent patterns
            self.intent_patterns = {
                "find_problems": [
                    "give me", "show me", "find", "get", "list", "what are",
                    "I want", "I need", "can you give", "please show", "display"
                ],
                "most_frequent": [
                    "most frequent", "most common", "popular", "top", "frequent",
                    "commonly asked", "often asked", "repeated", "most asked"
                ],
                "company_specific": [
                    "asked by", "from", "interview", "company", "at", "by",
                    "interview questions", "hiring", "recruitment"
                ],
                "topic_specific": [
                    "problems", "questions", "exercises", "challenges", "algorithms",
                    "data structures", "coding", "programming"
                ],
                "statistics": [
                    "stats", "statistics", "analysis", "distribution", "count",
                    "how many", "number of", "frequency"
                ],
                "comparison": [
                    "compare", "vs", "versus", "difference", "better", "worse",
                    "similar", "related"
                ]
            }
            
            # Initialize stopwords
            self.stop_words = set(stopwords.words('english'))
            
            # Create aliases
            self.topic_aliases = self._create_topic_aliases()
            self.company_aliases = self._create_company_aliases()
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Fit vectorizer with topics for better similarity matching
            self.tfidf_vectorizer.fit(self.topics + list(self.topic_aliases.keys()))
            
            logger.info("NLPService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLPService: {e}")
            raise

    def _create_topic_aliases(self) -> Dict[str, str]:
        """Create aliases for topics to handle variations"""
        aliases = {}
        aliases_mapping = {
            "array": "Array",
            "arrays": "Array",
            "list": "Array",
            "lists": "Array",
            "string": "String",
            "strings": "String",
            "str": "String",
            "hashtable": "Hash Table",
            "hashmap": "Hash Table",
            "hash": "Hash Table",
            "map": "Hash Table",
            "dict": "Hash Table",
            "dictionary": "Hash Table",
            "dp": "Dynamic Programming",
            "dynamic programming": "Dynamic Programming",
            "tree": "Tree",
            "trees": "Tree",
            "binary tree": "Binary Tree",
            "bst": "Binary Search Tree",
            "binary search tree": "Binary Search Tree",
            "graph": "Graph",
            "graphs": "Graph",
            "dfs": "Depth-First Search",
            "depth first search": "Depth-First Search",
            "bfs": "Breadth-First Search",
            "breadth first search": "Breadth-First Search",
            "two pointer": "Two Pointers",
            "two pointers": "Two Pointers",
            "sliding window": "Sliding Window",
            "stack": "Stack",
            "stacks": "Stack",
            "queue": "Queue",
            "queues": "Queue",
            "heap": "Heap",
            "heaps": "Heap",
            "priority queue": "Priority Queue",
            "linked list": "Linked List",
            "linkedlist": "Linked List",
            "trie": "Trie",
            "prefix tree": "Trie",
            "union find": "Union Find",
            "disjoint set": "Union Find"
        }
        return aliases_mapping

    def _create_company_aliases(self) -> Dict[str, str]:
        """Create aliases for companies to handle variations"""
        aliases = {}
        aliases_mapping = {
            # Tech Giants
            "fb": "Meta",
            "facebook": "Meta",
            "goog": "Google",
            "googl": "Google",
            "alphabet": "Google",
            "amzn": "Amazon",
            "aws": "Amazon",
            "msft": "Microsoft",
            "aapl": "Apple",
            "nflx": "Netflix",
            "tsla": "Tesla",
            
            # Financial Services
            "goldman": "Goldman Sachs",
            "gs": "Goldman Sachs",
            "jpmorgan": "J.P. Morgan",
            "jp morgan": "J.P. Morgan",
            "jpm": "J.P. Morgan",
            "morgan stanley": "Morgan Stanley",
            "ms": "Morgan Stanley",
            "bofa": "Bank of America",
            "boa": "Bank of America",
            "citi": "Citigroup",
            "wells": "Wells Fargo",
            "amex": "American Express",
            "american express": "American Express",
            
            # Ride Sharing & Delivery
            "uber": "Uber",
            "lyft": "Lyft",
            "doordash": "DoorDash",
            "grubhub": "Grubhub",
            "airbnb": "Airbnb",
            
            # Social Media & Entertainment
            "twitter": "X",
            "linkedin": "LinkedIn",
            "snap": "Snap",
            "snapchat": "Snap",
            "tiktok": "TikTok",
            "bytedance": "ByteDance",
            "pinterest": "Pinterest",
            "reddit": "Reddit",
            "discord": "Discord",
            
            # Enterprise Software
            "salesforce": "Salesforce",
            "oracle": "Oracle",
            "sap": "SAP",
            "ibm": "IBM",
            "vmware": "VMware",
            "servicenow": "ServiceNow",
            "workday": "Workday",
            "atlassian": "Atlassian",
            
            # Semiconductor & Hardware
            "intel": "Intel",
            "nvidia": "Nvidia",
            "amd": "AMD",
            "qualcomm": "Qualcomm",
            "texas instruments": "Texas Instruments",
            "ti": "Texas Instruments",
            
            # Streaming & Media
            "spotify": "Spotify",
            "netflix": "Netflix",
            "disney": "Disney",
            "twitch": "Twitch",
            "hulu": "Hulu",
            
            # E-commerce & Retail
            "ebay": "eBay",
            "shopify": "Shopify",
            "walmart": "Walmart Labs",
            "target": "Target",
            "booking": "Booking.com",
            "expedia": "Expedia",
            
            # Gaming
            "activision": "Activision",
            "blizzard": "Blizzard",
            "riot": "Riot Games",
            "roblox": "Roblox",
            "zynga": "Zynga",
            "ea": "Electronic Arts",
            "electronic arts": "Electronic Arts",
            
            # Financial Technology
            "robinhood": "Robinhood",
            "coinbase": "Coinbase",
            "stripe": "Stripe",
            "square": "Block",
            "paypal": "PayPal",
            "visa": "Visa",
            "mastercard": "Mastercard",
            "capital one": "Capital One",
            "sofi": "SoFi",
            
            # Indian Companies
            "tcs": "tcs",
            "infosys": "Infosys",
            "wipro": "Wipro",
            "hcl": "HCL",
            "tech mahindra": "Tech Mahindra",
            "flipkart": "Flipkart",
            "paytm": "Paytm",
            "phonepe": "PhonePe",
            "swiggy": "Swiggy",
            "zomato": "Zomato",
            "ola": "Ola Cabs",
            "bharatpe": "BharatPe",
            "razorpay": "razorpay",
            "cred": "CRED",
            "dream11": "Dream11",
            "nykaa": "Nykaa",
            "myntra": "Myntra",
            "zepto": "Zepto",
            "blinkit": "blinkit",
            "urban company": "Urban Company",
            "groww": "Groww",
            "delhivery": "Delhivery",
            "lenskart": "Lenskart",
            "cars24": "CARS24",
            "freshworks": "FreshWorks",
            "zoho": "Zoho",
            "jio": "jio",
            "airtel": "Airtel",
            
            # Consulting & Professional Services
            "mckinsey": "McKinsey",
            "deloitte": "Deloitte",
            "accenture": "Accenture",
            "capgemini": "Capgemini",
            "cognizant": "Cognizant",
            "ey": "EY",
            "pwc": "Pwc",
            "epam": "EPAM Systems",
            
            # Cloud & Infrastructure
            "cloudflare": "Cloudflare",
            "databricks": "Databricks",
            "snowflake": "Snowflake",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "elastic": "Elastic",
            "splunk": "Splunk",
            "okta": "Okta",
            "crowdstrike": "CrowdStrike",
            "palo alto": "Palo Alto Networks",
            "palo alto networks": "Palo Alto Networks",
            
            # Trading & Finance
            "citadel": "Citadel",
            "two sigma": "Two Sigma",
            "jane street": "Jane Street",
            "de shaw": "DE Shaw",
            "bridgewater": "Bridgewater Associates",
            "millennium": "Millennium",
            "jump trading": "Jump Trading",
            "optiver": "Optiver",
            "akuna": "Akuna Capital",
            "akuna capital": "Akuna Capital",
            "tower research": "Tower Research Capital",
            "hudson river trading": "Hudson River Trading",
            "hrt": "Hudson River Trading",
            
            # Other Notable Companies
            "palantir": "Palantir Technologies",
            "zoom": "Zoom",
            "slack": "Slack",
            "dropbox": "Dropbox",
            "adobe": "Adobe",
            "intuit": "Intuit",
            "coursera": "Coursera",
            "duolingo": "Duolingo",
            "notion": "Notion",
            "figma": "Figma",
            "canva": "Canva",
            "github": "GitHub",
            "gitlab": "GitLab",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "openai": "OpenAI"
        }
        return aliases_mapping

    async def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Enhanced NLP-based query parsing with semantic understanding
        """
        try:
            # Preprocess query
            processed_query = self._preprocess_query(query)
            
            # Extract entities using NLP
            entities = await self._extract_entities_nlp(processed_query)
            
            # Build structured query
            parsed = {
                "original_query": query,
                "processed_query": processed_query,
                "intent": entities.get("intent", "find_problems"),
                "difficulty": entities.get("difficulty", []),
                "topics": entities.get("topics", []),
                "companies": entities.get("companies", []),
                "filters": entities.get("filters", {}),
                "sort_preferences": entities.get("sort_preferences", {"sort_by": "frequency", "sort_order": "desc"}),
                "limit": entities.get("limit", 50),
                "confidence_score": entities.get("confidence", 0.0)
            }
            
            logger.info(f"Parsed query with confidence {parsed['confidence_score']:.2f}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing query '{query}': {e}")
            return self._get_default_response(query)

    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for better NLP understanding"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Handle common abbreviations
        abbreviations = {
            'dp': 'dynamic programming',
            'bfs': 'breadth first search',
            'dfs': 'depth first search',
            'bst': 'binary search tree',
            'fb': 'facebook',
            'amzn': 'amazon',
            'msft': 'microsoft',
            'goog': 'google',
        }
        
        for abbr, full in abbreviations.items():
            query = re.sub(r'\b' + abbr + r'\b', full, query)
        
        return query

    async def _extract_entities_nlp(self, query: str) -> Dict[str, Any]:
        """Extract entities using advanced NLP techniques"""
        entities = {
            "intent": "find_problems",
            "difficulty": [],
            "topics": [],
            "companies": [],
            "filters": {},
            "sort_preferences": {"sort_by": "frequency", "sort_order": "desc"},
            "limit": 50,
            "confidence": 0.0
        }
        
        # Tokenize query
        tokens = word_tokenize(query)
        tokens_clean = [t for t in tokens if t not in self.stop_words and t.isalpha()]
        
        # Extract intent with confidence
        intent_result = self._extract_intent_with_confidence(query, tokens_clean)
        entities["intent"] = intent_result["intent"]
        
        # Extract topics using semantic similarity
        topics_result = self._extract_topics_semantic(query, tokens_clean)
        entities["topics"] = topics_result["topics"]
        
        # Extract companies using fuzzy matching
        companies_result = self._extract_companies_fuzzy(query, tokens_clean)
        entities["companies"] = companies_result["companies"]
        
        # Extract difficulty with context
        entities["difficulty"] = self._extract_difficulty_contextual(query, tokens_clean)
        
        # Extract numerical filters
        entities["filters"] = self._extract_numerical_filters(query)
        
        # Extract sorting preferences
        entities["sort_preferences"] = self._extract_sorting_semantic(query)
        
        # Extract limit intelligently
        entities["limit"] = self._extract_limit_intelligent(query)
        
        # Calculate overall confidence
        entities["confidence"] = self._calculate_confidence(
            intent_result, topics_result, companies_result, entities
        )
        
        return entities

    def _extract_intent_with_confidence(self, query: str, tokens: List[str]) -> Dict[str, Any]:
        """Extract intent with confidence scoring"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query:
                    score += 1
            # Normalize score
            intent_scores[intent] = score / len(patterns) if patterns else 0
        
        # Default intent if no strong match
        best_intent = max(intent_scores, key=intent_scores.get) if intent_scores else "find_problems"
        confidence = intent_scores.get(best_intent, 0.0)
        
        return {"intent": best_intent, "confidence": confidence}

    def _extract_topics_semantic(self, query: str, tokens: List[str]) -> Dict[str, Any]:
        """Extract topics using semantic similarity - FIXED VERSION"""
        topics = []
        confidence_scores = []
        
        # Make query lowercase for consistent matching
        query_lower = query.lower()
        
        # Direct matching first (case-insensitive) - FIXED: Use word boundaries
        for topic in self.topics:
            topic_lower = topic.lower()
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(topic_lower) + r'\b', query_lower):
                topics.append(topic)
                confidence_scores.append(1.0)
        
        # Alias matching - FIXED: Use word boundaries
        for alias, topic in self.topic_aliases.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', query_lower) and topic not in topics:
                topics.append(topic)
                confidence_scores.append(0.9)
        
        # Token-based matching for better word boundary detection - FIXED
        query_tokens = [token.lower() for token in tokens]
        for topic in self.topics:
            topic_words = [word.lower() for word in topic.split()]
            # For single word topics, check if the word exists in tokens
            if len(topic_words) == 1:
                if topic_words[0] in query_tokens and topic not in topics:
                    topics.append(topic)
                    confidence_scores.append(0.95)
            # For multi-word topics, check if all words exist
            else:
                if all(word in query_lower for word in topic_words) and topic not in topics:
                    topics.append(topic)
                    confidence_scores.append(0.8)
        
        # Remove duplicates while preserving order
        unique_topics = []
        seen = set()
        for topic in topics:
            if topic not in seen:
                unique_topics.append(topic)
                seen.add(topic)
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return {"topics": unique_topics, "confidence": avg_confidence}

    def _extract_companies_fuzzy(self, query: str, tokens: List[str]) -> Dict[str, Any]:
        """Extract companies using fuzzy matching - FIXED VERSION"""
        companies = []
        confidence_scores = []
        
        # Convert query to lowercase for comparison
        query_lower = query.lower()
        
        # Direct matching with word boundaries - FIXED
        for company in self.companies:
            company_lower = company.lower()
            if re.search(r'\b' + re.escape(company_lower) + r'\b', query_lower):
                companies.append(company)
                confidence_scores.append(1.0)
        
        # Alias matching with word boundaries - FIXED
        for alias, company in self.company_aliases.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', query_lower) and company not in companies:
                companies.append(company)
                confidence_scores.append(0.9)
        
        # Token-based matching - FIXED
        query_tokens = [token.lower() for token in tokens]
        for company in self.companies:
            company_words = [word.lower() for word in company.split()]
            if len(company_words) == 1:
                if company_words[0] in query_tokens and company not in companies:
                    companies.append(company)
                    confidence_scores.append(0.95)
            else:
                # For multi-word companies, check if majority of words match
                matches = sum(1 for word in company_words if word in query_tokens)
                if matches >= len(company_words) * 0.6 and company not in companies:
                    companies.append(company)
                    confidence_scores.append(matches / len(company_words))
        
        # Remove duplicates while preserving order
        unique_companies = []
        seen = set()
        for company in companies:
            if company not in seen:
                unique_companies.append(company)
                seen.add(company)
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return {"companies": unique_companies, "confidence": avg_confidence}

    def _extract_difficulty_contextual(self, query: str, tokens: List[str]) -> List[str]:
        """Extract difficulty with contextual understanding - FIXED VERSION"""
        difficulties = []
        query_lower = query.lower()
        
        # Direct pattern matching with word boundaries - FIXED
        for difficulty, patterns in self.difficulty_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query_lower):
                    if difficulty not in difficulties:
                        difficulties.append(difficulty)
        
        # Additional contextual patterns
        difficulty_context = {
            "easy": ["easy", "simple", "basic", "beginner", "trivial", "straightforward", "level 1"],
            "medium": ["medium", "intermediate", "moderate", "average", "standard", "level 2"],
            "hard": ["hard", "difficult", "challenging", "advanced", "expert", "complex", "tough", "level 3"]
        }
        
        # Check for contextual difficulty indicators
        for difficulty, patterns in difficulty_context.items():
            for pattern in patterns:
                if pattern in query_lower and difficulty not in difficulties:
                    difficulties.append(difficulty)
        
        # Special handling for "level" patterns
        level_match = re.search(r'level\s*(\d+)', query_lower)
        if level_match:
            level_num = int(level_match.group(1))
            if level_num == 1 and "easy" not in difficulties:
                difficulties.append("easy")
            elif level_num == 2 and "medium" not in difficulties:
                difficulties.append("medium")
            elif level_num == 3 and "hard" not in difficulties:
                difficulties.append("hard")
        
        return difficulties

    # Debug method to test the fixes
    def debug_entity_extraction(self, query: str) -> Dict[str, Any]:
        """Debug method to see what's being extracted - ENHANCED VERSION"""
        processed_query = self._preprocess_query(query)
        tokens = word_tokenize(processed_query)
        tokens_clean = [t for t in tokens if t not in self.stop_words and t.isalpha()]
        
        debug_info = {
            "original_query": query,
            "processed_query": processed_query,
            "tokens": tokens,
            "clean_tokens": tokens_clean,
            "word_boundaries_test": {},
            "step_by_step": {}
        }
        
        # Test word boundary patterns for debugging
        query_lower = processed_query.lower()
        
        # Test topic matching
        debug_info["word_boundaries_test"]["topics"] = {}
        for topic in self.topics[:5]:  # Test first 5 topics
            topic_lower = topic.lower()
            direct_match = re.search(r'\b' + re.escape(topic_lower) + r'\b', query_lower)
            debug_info["word_boundaries_test"]["topics"][topic] = {
                "found": bool(direct_match),
                "pattern": r'\b' + re.escape(topic_lower) + r'\b'
            }
        
        # Test company matching
        debug_info["word_boundaries_test"]["companies"] = {}
        for company in ["Google", "Amazon", "Meta", "Apple", "Microsoft"]:
            company_lower = company.lower()
            direct_match = re.search(r'\b' + re.escape(company_lower) + r'\b', query_lower)
            debug_info["word_boundaries_test"]["companies"][company] = {
                "found": bool(direct_match),
                "pattern": r'\b' + re.escape(company_lower) + r'\b'
            }
        
        # Test difficulty matching
        debug_info["word_boundaries_test"]["difficulty"] = {}
        for difficulty, patterns in self.difficulty_patterns.items():
            for pattern in patterns:
                match = re.search(r'\b' + re.escape(pattern) + r'\b', query_lower)
                if match:
                    debug_info["word_boundaries_test"]["difficulty"][difficulty] = {
                        "found": True,
                        "pattern": pattern
                    }
        
        # Test each extraction method
        debug_info["step_by_step"]["intent"] = self._extract_intent_with_confidence(processed_query, tokens_clean)
        debug_info["step_by_step"]["topics"] = self._extract_topics_semantic(processed_query, tokens_clean)
        debug_info["step_by_step"]["companies"] = self._extract_companies_fuzzy(processed_query, tokens_clean)
        debug_info["step_by_step"]["difficulty"] = self._extract_difficulty_contextual(processed_query, tokens_clean)
        debug_info["step_by_step"]["filters"] = self._extract_numerical_filters(processed_query)
        debug_info["step_by_step"]["sort_preferences"] = self._extract_sorting_semantic(processed_query)
        debug_info["step_by_step"]["limit"] = self._extract_limit_intelligent(processed_query)
        
        return debug_info

    def _extract_numerical_filters(self, query: str) -> Dict[str, Any]:
        """Extract numerical filters with better pattern recognition"""
        filters = {}
        
        # Enhanced frequency patterns
        freq_patterns = [
            r'frequency\s*(?:>=|>|above|at\s*least)\s*(\d+)',
            r'(?:>=|>|above|at\s*least)\s*(\d+)\s*frequency',
            r'frequency\s*(\d+)\s*(?:or\s*more|plus)',
            r'more\s*than\s*(\d+)\s*(?:times|frequency)'
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                filters['min_frequency'] = int(match.group(1))
                break
        
        # Enhanced acceptance rate patterns
        acc_patterns = [
            r'acceptance\s*rate\s*(?:>=|>|above)\s*(\d+(?:\.\d+)?)',
            r'success\s*rate\s*(?:>=|>|above)\s*(\d+(?:\.\d+)?)',
            r'(?:>=|>|above)\s*(\d+(?:\.\d+)?)\s*%?\s*acceptance'
        ]
        
        for pattern in acc_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                rate = float(match.group(1))
                if rate > 1:
                    rate = rate / 100
                filters['min_acceptance_rate'] = rate
                break
        
        return filters

    def _extract_sorting_semantic(self, query: str) -> Dict[str, str]:
        """Extract sorting preferences with semantic understanding"""
        sort_prefs = {"sort_by": "frequency", "sort_order": "desc"}
        
        # Sort by field
        if any(word in query for word in ["frequent", "popularity", "common", "asked"]):
            sort_prefs["sort_by"] = "frequency"
        elif any(word in query for word in ["acceptance", "success", "solve"]):
            sort_prefs["sort_by"] = "acceptance_rate"
        elif any(word in query for word in ["alphabetical", "name", "title"]):
            sort_prefs["sort_by"] = "title"
        elif any(word in query for word in ["difficulty", "level"]):
            sort_prefs["sort_by"] = "difficulty"
        elif any(word in query for word in ["number", "id", "leetcode"]):
            sort_prefs["sort_by"] = "question_number"
        
        # Sort order
        if any(word in query for word in ["ascending", "asc", "lowest", "easiest", "smallest"]):
            sort_prefs["sort_order"] = "asc"
        elif any(word in query for word in ["descending", "desc", "highest", "hardest", "largest", "most"]):
            sort_prefs["sort_order"] = "desc"
        
        return sort_prefs

    def _extract_limit_intelligent(self, query: str) -> int:
        """Intelligently extract result limit"""
        # Explicit number patterns
        limit_patterns = [
            r'(?:top|first|give\s*me|show\s*me|get\s*me|find\s*me)\s*(\d+)',
            r'(\d+)\s*(?:problems?|questions?|challenges?)',
            r'limit\s*(?:to\s*)?(\d+)',
            r'maximum\s*(\d+)'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                limit = int(match.group(1))
                return min(limit, 1000)  # Cap at 1000
        
        # Contextual limits
        if any(word in query for word in ["few", "some", "couple"]):
            return 5
        elif any(word in query for word in ["many", "lots", "bunch", "plenty"]):
            return 100
        elif any(word in query for word in ["all", "every", "complete"]):
            return 1000
        elif "top" in query:
            return 10
        
        return 50

    def _calculate_confidence(self, intent_result: Dict, topics_result: Dict, 
                            companies_result: Dict, entities: Dict) -> float:
        """Calculate overall confidence score"""
        scores = []
        
        # Intent confidence
        scores.append(intent_result.get("confidence", 0.0))
        
        # Topics confidence
        scores.append(topics_result.get("confidence", 0.0))
        
        # Companies confidence
        scores.append(companies_result.get("confidence", 0.0))
        
        # Bonus for having multiple entity types
        entity_types = sum([
            1 if entities["difficulty"] else 0,
            1 if entities["topics"] else 0,
            1 if entities["companies"] else 0,
            1 if entities["filters"] else 0
        ])
        
        diversity_bonus = min(entity_types * 0.1, 0.3)
        
        base_confidence = np.mean(scores) if scores else 0.0
        return min(base_confidence + diversity_bonus, 1.0)

    def _get_default_response(self, query: str) -> Dict[str, Any]:
        """Get default response for failed parsing"""
        return {
            "original_query": query,
            "intent": "find_problems",
            "difficulty": [],
            "topics": [],
            "companies": [],
            "filters": {},
            "sort_preferences": {"sort_by": "frequency", "sort_order": "desc"},
            "limit": 50,
            "confidence_score": 0.0
        }

    def debug_query_parsing(self, query: str) -> Dict[str, Any]:
        """Debug method to see what's being extracted at each step"""
        processed_query = self._preprocess_query(query)
        tokens = word_tokenize(processed_query)
        tokens_clean = [t for t in tokens if t not in self.stop_words and t.isalpha()]
        
        debug_info = {
            "original_query": query,
            "processed_query": processed_query,
            "tokens": tokens,
            "clean_tokens": tokens_clean,
            "step_by_step": {}
        }
        
        # Test each extraction method
        debug_info["step_by_step"]["intent"] = self._extract_intent_with_confidence(processed_query, tokens_clean)
        debug_info["step_by_step"]["topics"] = self._extract_topics_semantic(processed_query, tokens_clean)
        debug_info["step_by_step"]["companies"] = self._extract_companies_fuzzy(processed_query, tokens_clean)
        debug_info["step_by_step"]["difficulty"] = self._extract_difficulty_contextual(processed_query, tokens_clean)
        debug_info["step_by_step"]["filters"] = self._extract_numerical_filters(processed_query)
        debug_info["step_by_step"]["sort_preferences"] = self._extract_sorting_semantic(processed_query)
        debug_info["step_by_step"]["limit"] = self._extract_limit_intelligent(processed_query)
        
        return debug_info