# Browser Agent

Autonomous browser automation agent that mimics human-like actions and can execute complex tasks on the web. Built with FastAPI (Python) and React (TypeScript) for a modern, scalable architecture.

## Features

- 🤖 **Autonomous Browser Control**: Automate browser tasks with human-like interactions
- 🎯 **Flexible Actions**: Navigate, click, type, scroll, take screenshots, and execute JavaScript
- 🔄 **Session Management**: Create and manage multiple concurrent browser sessions
- 📸 **Visual Feedback**: Real-time screenshots of browser state
- 🚀 **RESTful API**: Well-documented API for all agent operations
- 💻 **Modern UI**: React-based responsive interface for session management
- 🔒 **Security**: Environment-based configuration, request validation, and error handling
- 📝 **Comprehensive Logging**: Structured logging for debugging and monitoring
- ✅ **Fully Tested**: Unit and integration tests with pytest
- 🐳 **Docker Ready**: Complete Docker configuration for containerization

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Playwright**: Cross-browser automation library
- **Pydantic**: Data validation and configuration
- **Structlog**: Structured logging
- **Pytest**: Testing framework

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: State management
- **Vite**: Fast build tool
- **React Router**: Client-side routing

## Architecture

```
browser-agent/
├── backend/
│   ├── app/
│   │   ├── core/              # Core logic
│   │   │   ├── browser.py     # Browser automation engine
│   │   │   ├── exceptions.py  # Custom exceptions
│   │   │   └── logging.py     # Logging configuration
│   │   ├── api/               # API endpoints
│   │   │   ├── sessions.py    # Session management routes
│   │   │   ├── actions.py     # Action execution routes
│   │   │   └── health.py      # Health check routes
│   │   ├── models/            # Data models
│   │   │   └── domain.py      # Domain models
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── requests.py    # Request/response schemas
│   │   ├── services/          # Business logic
│   │   │   ├── agent.py       # Main agent service
│   │   │   ├── session.py     # Session management
│   │   │   └── task.py        # Task management
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app factory
│   ├── tests/                 # Test suite
│   │   ├── unit/              # Unit tests
│   │   └── integration/       # Integration tests
│   ├── requirements.txt       # Python dependencies
│   └── server.py              # Server entry point
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── stores/            # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── vite.config.ts         # Vite config
│   └── tailwind.config.cjs    # Tailwind config
├── .github/
│   └── workflows/             # GitHub Actions
├── docs/                      # Documentation
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/browser-agent.git
cd browser-agent
```

2. Create a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Create `.env` file from template:
```bash
cp ../.env.example ../.env
```

6. Run the backend server:
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` and documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Configuration

Create a `.env` file in the project root:

```env
# Application
APP_NAME=Browser Agent
DEBUG=False
LOG_LEVEL=INFO

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Browser
HEADLESS_MODE=True
BROWSER_TIMEOUT=30000
MAX_BROWSER_INSTANCES=5
BROWSER_TYPE=chromium

# API
API_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Security
MAX_EXECUTION_TIME=300
```

## Usage

### Creating a Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00.000000",
  "is_active": true,
  "current_url": null
}
```

### Navigating to a URL

```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/actions/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Taking a Screenshot

```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/actions/screenshot
```

### Clicking an Element

```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/actions \
  -H "Content-Type: application/json" \
  -d '{"action_type": "click", "parameters": {"selector": ".button"}}'
```

### Typing Text

```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/actions \
  -H "Content-Type: application/json" \
  -d '{"action_type": "type", "parameters": {"selector": "input[name=search]", "text": "query"}}'
```

## API Documentation

Full API documentation is available at `http://localhost:8000/docs` (Swagger UI) when the server is running.

### Main Endpoints

#### Sessions
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions` - List all sessions
- `GET /api/v1/sessions/{session_id}` - Get session details
- `DELETE /api/v1/sessions/{session_id}` - Close session

#### Actions
- `POST /api/v1/sessions/{session_id}/actions` - Execute action
- `POST /api/v1/sessions/{session_id}/actions/navigate` - Navigate to URL
- `POST /api/v1/sessions/{session_id}/actions/screenshot` - Take screenshot

#### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/ready` - Readiness check

## Testing

### Run Unit Tests

```bash
cd backend
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run All Tests with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Frontend Tests

```bash
cd frontend
npm run test
```

## Deployment

### Docker

Build the Docker image:
```bash
docker build -t browser-agent .
```

Run the container:
```bash
docker run -p 8000:8000 -p 3000:3000 browser-agent
```

### Docker Compose (Coming Soon)

```bash
docker-compose up
```

### Production Deployment

1. Set `DEBUG=False` in environment
2. Configure CORS for your domain
3. Use a production WSGI server (Gunicorn)
4. Set up proper logging and monitoring
5. Use environment-based secrets management

## Error Handling

The application uses custom exception classes for different error scenarios:

- `BrowserException`: Browser automation failures
- `NavigationException`: Page navigation failures
- `InteractionException`: Element interaction failures
- `TimeoutException`: Operation timeouts
- `ValidationException`: Input validation errors
- `SecurityException`: Security policy violations

All errors are logged with structured logging for easy debugging.

## Logging

Structured logging is configured using `structlog`. All logs include:
- Timestamp
- Log level
- Logger name
- Relevant context
- Error details

Access logs at:
- Console output during development
- Log files in production (configurable)

## Security Considerations

1. **Input Validation**: All requests are validated using Pydantic
2. **CORS**: Configure CORS origins in `.env`
3. **Rate Limiting**: Implement rate limiting for production (not included)
4. **Authentication**: Add authentication layer for production
5. **Domain Whitelisting**: Restrict navigation to allowed domains (configurable)
6. **Timeout Protection**: All operations have timeout limits
7. **Resource Limits**: Max browser instances and execution time limits

## Extending the Application

### Adding New Actions

1. Define the action in `ActionType` enum in `models/domain.py`
2. Implement the action method in `BrowserAgent` class
3. Add corresponding service method in `AgentService`
4. Create API endpoint in `api/actions.py`
5. Add tests for the new action

### Adding New API Endpoints

1. Create handler function in appropriate module
2. Use FastAPI decorators (`@router.get()`, etc.)
3. Use Pydantic schemas for validation
4. Include proper error handling
5. Add comprehensive docstrings

### Custom Storage

Current implementation uses in-memory storage. For production:
1. Implement SQLAlchemy models
2. Add database migrations
3. Update services to use database queries
4. Add transaction management

## Development Workflow

1. Create a branch for your feature
2. Make changes following the code style
3. Write tests for new functionality
4. Run tests and linters
5. Create a pull request
6. Address review comments

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

- [ ] LLM integration for intelligent task planning
- [ ] Advanced element detection (OCR)
- [ ] Multi-page task execution
- [ ] Database storage for sessions and results
- [ ] Authentication and user management
- [ ] Rate limiting and throttling
- [ ] Performance metrics and analytics
- [ ] Mobile browser support
- [ ] API key management
- [ ] Webhook integration

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://github.com/pmndrs/zustand)

## Notes

- This is a v1.0.0 release with core functionality
- For production use, implement additional security measures
- Consider adding authentication and database persistence
- Monitor resource usage when scaling to multiple concurrent sessions
- Playwright browser installation is required after package installation
