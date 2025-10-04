# From Seeds to Blockchain: Growing the Future of Environmental Education and Citizen Science

<div align="center">

**A Living Science Initiative at Freie Waldorfschule Frankfurt (Oder)**

*An Anthroposophical Approach to Environmental Monitoring, Citizen Science & Reciprocity*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

</div>

---

## 🌱 Project Philosophy

> *"As we learn to think like a plant, we discover that technology and nature are not opposites but complementary expressions of the same creative forces that shape our world."*

> *"You never change things by fighting the existing reality. To change something, build a new model that makes the existing model obsolete."* — R. Buckminster Fuller

This project embodies these principles by creating a next-generation platform that operates as a living system - where environmental monitoring, educational engagement, and technological innovation converge to create regenerative futures.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Living Lab - Erdpuls Müllrose](#living-lab---erdpuls-müllrose)
- [Architecture](#architecture)
- [Design Principles](#design-principles)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
- [Contributing](#contributing)
- [Attribution](#attribution)
- [License](#license)
- [Contact](#contact)

---

## 🌍 Overview

**From Seeds to Blockchain** is an innovative integration of environmental science, educational technology, and blockchain-based citizen science. Rooted in anthroposophical principles and hosted at the Freie Waldorfschule Frankfurt (Oder), this project creates a living laboratory where students, educators, and community members engage in real-time environmental monitoring while learning about regenerative systems.

### Key Components

- **Environmental Monitoring**: Real-time data collection from sensors tracking soil, air, water, and biodiversity metrics
- **Citizen Science Platform**: Engaging interface for community participation in scientific observation
- **Educational Integration**: Curriculum-aligned activities connecting theory with hands-on environmental stewardship
- **Blockchain Integration**: Transparent, immutable records of environmental data and citizen contributions
- **API Portal**: Robust service architecture for data access, visualization, and third-party integration

### Goals

1. **Educate**: Foster environmental literacy through direct engagement with living systems
2. **Monitor**: Create comprehensive, longitudinal environmental datasets
3. **Empower**: Enable citizens to participate meaningfully in environmental science
4. **Innovate**: Demonstrate how technology can enhance rather than replace connection with nature
5. **Regenerate**: Contribute to local and global regenerative practices

---

## 🌳 Living Lab - Erdpuls Müllrose

### Ein Lebendiges Labor für Regenerative Zukunft

The Erdpuls Müllrose site serves as our primary field laboratory - a living ecosystem where students and community members conduct ongoing environmental research. This regenerative space demonstrates:

- **Permaculture Design Principles**: Working with natural patterns and cycles
- **Biodiversity Enhancement**: Creating habitats and monitoring species diversity
- **Soil Regeneration**: Tracking soil health metrics over time
- **Water Stewardship**: Managing and monitoring water systems
- **Community Engagement**: Regular workshops, field days, and citizen science events

**Location**: Müllrose, Brandenburg, Germany  
**Established**: [Year]  
**Size**: [Area] hectares  
**Partners**: Freie Waldorfschule Frankfurt (Oder), local community groups, research institutions

---

## 🏗️ Architecture

This project is built as a **service-oriented, modular system** where each component operates as a self-contained holon - interconnected yet independent. The architecture prioritizes precision, scalability, and maintainability.

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       main.py (Orchestrator)                 │
│                    Single Entry Point                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Registry                         │
│              Central Dependency Management                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Sensor     │    │   Citizen    │    │  Blockchain  │
│   Service    │    │   Science    │    │   Service    │
│   Module     │    │   Module     │    │   Module     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │    Database      │
                    │ (Single Source   │
                    │   of Truth)      │
                    └──────────────────┘
```

### Technology Stack

- **Backend**: Python 3.11+ with async/await patterns
- **API Framework**: FastAPI for modern, async REST APIs
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **Blockchain**: stellar for data integrity
- **Messaging**: Redis for real-time data streaming
- **Monitoring**: Prometheus + Grafana for system observability
- **Deployment**: Docker + Kubernetes for containerized orchestration

---

## 🎯 Design Principles

### Core Principle: Precision in Implementation

**Coding is an exact science.** This system focuses exclusively on what it can ACTUALLY execute, not theoretical best-case scenarios. Every component is implementable, testable, and production-ready.

### The 12 Principles

#### 1. **Modular Design and Architecture**
- Each module operates as a self-contained holon with clearly defined boundaries
- Modules interact through well-defined interfaces only
- Components can be developed, tested, and deployed independently

#### 2. **Service Pattern with Centralized Execution**
- All modules implement the service pattern - no standalone execution except `main.py`
- `main.py` serves as the sole orchestrator and entry point
- Services expose functionality through standardized interfaces

#### 3. **Service Registry for Dependencies**
- All inter-module dependencies managed through a central service registry
- No direct module imports outside of the registry pattern
- Enables dynamic service discovery and loose coupling

#### 4. **Single Source of Truth**
- Database serves as the authoritative data source
- Each piece of information has exactly one canonical location
- No data duplication across modules or configuration files

#### 5. **Strict Async Operations**
- ALL I/O operations use async/await patterns
- No blocking operations in any code path
- Concurrent operations leveraged for maximum efficiency

#### 6. **No Sync Fallbacks or Backward Compatibility**
- Clean, forward-looking codebase only
- No legacy support code
- Breaking changes handled through module updates, not compatibility layers

#### 7. **Per-Asset Monitoring with Execution Minimums**
- Individual asset tracking and limits
- Minimum thresholds for execution to prevent micro-transactions
- Real-time monitoring of each system component

#### 8. **No Duplicate Configuration**
- Each configuration parameter defined exactly once
- Centralized configuration management
- Environment-specific overrides through a single mechanism

#### 9. **Integrated Rate Limiting**
- Built-in rate limiting for all external API calls
- Prevents service abuse and ensures compliance with provider limits
- Graceful degradation under load

#### 10. **Clear Separation of Concerns**
- Active processing clearly separated from passive monitoring
- Business logic isolated from infrastructure code
- Data access layer distinct from business rules

#### 11. **Comprehensive Documentation**
- Docstrings at the top of every file explaining purpose and usage
- Inline comments for complex or non-obvious logic
- API documentation for all public interfaces

#### 12. **Method Singularity (No Redundancy)**
- Each method implemented exactly once in the entire codebase
- Shared functionality extracted to common modules
- Methods available system-wide through service registry
- Zero tolerance for copy-paste programming

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ with TimescaleDB extension
- Redis 6.0+
- Docker and Docker Compose (optional, for containerized deployment)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/[your-org]/seeds-to-blockchain.git
   cd seeds-to-blockchain
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

### Docker Deployment

```bash
docker-compose up -d
```

This will start all required services: API server, PostgreSQL, Redis, and monitoring stack.

---

## 📡 API Documentation

### Base URL

```
https://living-labs.ubec.network
```

### Authentication

All API requests require authentication using JWT tokens:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.seeds-blockchain.org/v1/sensors
```

### Core Endpoints

#### Sensor Data

**Get All Sensors**
```http
GET /api/v1/sensors
```

**Get Sensor Readings**
```http
GET /api/v1/sensors/{sensor_id}/readings?start_time={ISO8601}&end_time={ISO8601}
```

**Submit Sensor Reading** (IoT devices)
```http
POST /api/v1/sensors/{sensor_id}/readings
Content-Type: application/json

{
  "timestamp": "2025-10-04T12:00:00Z",
  "value": 23.5,
  "unit": "celsius",
  "metadata": {}
}
```

#### Citizen Science

**Submit Observation**
```http
POST /api/v1/observations
Content-Type: application/json

{
  "observer_id": "user123",
  "type": "biodiversity",
  "species": "Quercus robur",
  "location": {"lat": 52.3547, "lon": 14.5431},
  "timestamp": "2025-10-04T14:30:00Z",
  "images": ["base64_encoded_image"],
  "notes": "Healthy oak tree, approximately 20m tall"
}
```

**Get Observation History**
```http
GET /api/v1/observations?observer_id={user_id}&start_date={date}
```

#### Blockchain

**Verify Data Integrity**
```http
GET /api/v1/blockchain/verify/{record_id}
```

**Get Transaction History**
```http
GET /api/v1/blockchain/transactions?type={sensor|observation}
```

### Response Format

All API responses follow this structure:

```json
{
  "status": "success",
  "data": { },
  "timestamp": "2025-10-04T12:00:00Z",
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 1247
  }
}
```

### Error Handling

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid sensor ID format",
    "details": {}
  },
  "timestamp": "2025-10-04T12:00:00Z"
}
```

### Rate Limits

- **Anonymous requests**: 100 requests/hour
- **Authenticated users**: 1,000 requests/hour
- **IoT devices**: 10,000 requests/hour
- **Enterprise**: Custom limits

### Interactive Documentation

Full API documentation with interactive testing available at:
- Swagger UI: `https://api.seeds-blockchain.org/docs`
- ReDoc: `https://api.seeds-blockchain.org/redoc`

---

## 📁 Project Structure

```
seeds-to-blockchain/
├── main.py                    # Single entry point and orchestrator
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
├── docker-compose.yml        # Container orchestration
├── README.md                 # This file
│
├── src/
│   ├── __init__.py
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py       # Centralized settings (single source)
│   │   └── registry.py       # Service registry
│   │
│   ├── services/             # Service modules (holons)
│   │   ├── __init__.py
│   │   ├── sensor_service.py
│   │   ├── citizen_science_service.py
│   │   ├── blockchain_service.py
│   │   ├── notification_service.py
│   │   └── analytics_service.py
│   │
│   ├── api/                  # API layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── sensors.py
│   │   │   ├── observations.py
│   │   │   └── blockchain.py
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   └── logging.py
│   │   └── schemas/
│   │       ├── sensor.py
│   │       └── observation.py
│   │
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── sensor.py
│   │   ├── observation.py
│   │   └── blockchain.py
│   │
│   ├── utils/                # Shared utilities (method singularity)
│   │   ├── __init__.py
│   │   ├── async_helpers.py
│   │   ├── validators.py
│   │   └── formatters.py
│   │
│   └── database/             # Database layer
│       ├── __init__.py
│       ├── connection.py
│       └── migrations/
│
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                  # Utility scripts
│   ├── init_db.py
│   ├── seed_data.py
│   └── backup.py
│
├── docs/                     # Additional documentation
│   ├── api/
│   ├── architecture/
│   └── deployment/
│
└── monitoring/               # Monitoring configuration
    ├── prometheus/
    └── grafana/
```

---

## 💻 Development Guidelines

### Python Code Best Practices

#### Function Design
- **Keep functions short**: Maximum 20-30 lines per function
- **Single responsibility**: Each function does one thing well
- **Clear naming**: Function names explicitly describe their action

Example:
```python
async def fetch_sensor_reading(sensor_id: str, timestamp: datetime) -> SensorReading:
    """
    Fetch a single sensor reading from the database.
    
    Args:
        sensor_id: Unique identifier for the sensor
        timestamp: Exact timestamp of the reading
        
    Returns:
        SensorReading object with the requested data
        
    Raises:
        SensorNotFoundError: If sensor_id doesn't exist
        ReadingNotFoundError: If no reading exists for timestamp
    """
    # Implementation here (< 30 lines)
```

#### Module Organization
- **One primary purpose per file/module**
- **Logical grouping** of related functionality
- **Clear module boundaries** with minimal cross-dependencies

#### Documentation Standards
- **File-level docstrings**: Purpose, usage examples, and module dependencies
- **Function docstrings**: Parameters, return values, and exceptions
- **Inline comments**: Only for complex algorithms or business logic
- **Update documentation** with code changes in the same commit

#### Code Quality Metrics
- **Testability**: Every function independently testable
- **Maintainability**: Code readable by team members without extensive context
- **Scalability**: Design supports 10x growth without architectural changes

### Git Workflow

1. **Branch naming**: `feature/`, `bugfix/`, `hotfix/`
2. **Commit messages**: Clear, descriptive, present tense
3. **Pull requests**: Include description, tests, and documentation updates
4. **Code review**: Required for all merges to main branch

### Testing Requirements

- **Minimum 80% code coverage**
- **All async functions must have async tests**
- **Integration tests for all API endpoints**
- **E2E tests for critical user flows**

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_sensor_service.py

# Run tests matching pattern
pytest -k "sensor"
```

---

## 🤝 Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### How to Contribute

1. **Fork the repository**
2. **Create your feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution

- 🔬 New sensor integrations
- 📊 Data visualization tools
- 📱 Mobile applications
- 🌐 Translations and localization
- 📚 Documentation improvements
- 🐛 Bug fixes and optimizations
- 🎨 UI/UX enhancements

---

## 🙏 Attribution

**This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.**

### Acknowledgments

- **Ubuntu Economic Commons**: Host institution and educational partner
- **Erdpuls Müllrose Community**: Living lab location and active participants
- **Open Source Community**: For the incredible tools and libraries that make this possible
- **Anthropic PBC and Claude**: For AI-assisted development and decision support
- **All Contributors**: Students, teachers, community scientists, and developers who make this project thrive

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

**Project Lead**: Farmer John]  
**Email**: living-labs@ubec.network  
**Website**: https://living-labs.ubec.network  


### Social Media

- **Twitter**: [@SeedsBlockchain](https://twitter.com/seedsblockchain)
- **LinkedIn**: [Seeds to Blockchain Project](https://linkedin.com/company/seeds-blockchain)
- **GitHub**: [@seeds-blockchain](https://github.com/seeds-blockchain)

### Community

- **Discussion Forum**: https://community.seeds-blockchain.org
- **Discord Server**: [Join our Discord](https://discord.gg/seeds-blockchain)
- **Monthly Meetups**: Every first Saturday at Erdpuls Müllrose

---

## 🌟 Roadmap

### Phase 1: Foundation (Q4 2025)
- ✅ Core API infrastructure
- ✅ Basic sensor integration
- 🔄 Initial blockchain implementation
- 🔄 Citizen science mobile app (beta)

### Phase 2: Expansion (Q1 2026)
- 📅 Advanced analytics dashboard
- 📅 Machine learning for pattern detection
- 📅 Multi-school network expansion
- 📅 Public data portal launch

### Phase 3: Ecosystem (Q2-Q4 2026)
- 📅 Open API for third-party developers
- 📅 Educational curriculum packages
- 📅 Research partnerships
- 📅 International pilot programs

---

## 📊 Project Status

![GitHub issues](https://img.shields.io/github/issues/seeds-blockchain/api-portal)
![GitHub pull requests](https://img.shields.io/github/issues-pr/seeds-blockchain/api-portal)
![GitHub contributors](https://img.shields.io/github/contributors/seeds-blockchain/api-portal)
![Last commit](https://img.shields.io/github/last-commit/seeds-blockchain/api-portal)

---

<div align="center">

**🌱 Growing Together, Learning Together, Regenerating Together 🌍**

*Made with 💚 at Living Lab · Erdpuls Müllrose*

</div>
