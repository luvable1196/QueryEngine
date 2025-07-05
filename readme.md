┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│ React Frontend (Port 3000)                                     │
│ ├── Query Input Interface                                       │
│ ├── Results Visualization                                       │
│ └── Real-time WebSocket Updates                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│ FastAPI Backend (Port 8000)                                    │
│ ├── /api/query (POST) - Main query endpoint                    │
│ ├── /api/companies (GET) - List companies                      │
│ ├── /api/health (GET) - Health check                           │
│ └── /ws/query - WebSocket for real-time updates                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│ │   NLP ENGINE    │  │  CACHE LAYER    │  │ DATABASE ENGINE │ │
│ │                 │  │                 │  │                 │ │
│ │ • Query Parser  │  │ • Redis Cache   │  │ • DuckDB Engine │ │
│ │ • Intent Recog  │  │ • Query Cache   │  │ • SQL Execution │ │
│ │ • SQL Generator │  │ • Result Cache  │  │ • Query Optimizer│ │
│ │ • Validation    │  │ • Session Cache │  │ • Analytics     │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│ File System Storage                                             │
│ /data/                                                          │
│ ├── Amazon/                                                     │
│ │   ├── last1month.csv                                          │
│ │   ├── last6months.csv                                         │
│ │   └── last1year.csv                                           │
│ ├── Google/                                                     │
│ ├── Microsoft/                                                  │
│ └── [100+ companies...]                                         │
└─────────────────────────────────────────────────────────────────┘




leetcode-query-system/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── query.py
│   │   └── companies.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py
│   │   ├── database_service.py
│   │   └── cache_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py
│   │   └── response_models.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── db/
│   ├── __init__.py
│   ├── models.py
│   ├── connection.py
│   └── migrations/
│       └── __init__.py
├── data/
│   ├── Amazon/
│   │   ├── last1month.csv
│   │   ├── last6months.csv
│   │   └── last1year.csv
│   ├── Google/
│   ├── Microsoft/
│   └── [other companies...]
├── requirements.txt
├── .env
├── docker-compose.yml
└── README.md