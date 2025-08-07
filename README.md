# Agento
 ai ai knock knock...

# Agentic Microservices Project

A full-stack microservices application with React frontend and Express.js backend, containerized with Docker.

## 🏗️ Architecture

```
agentic_fullstack/
├── agentic_backend/         # Express.js REST API
├── agentic_frontend/        # React.js Web Application  
├── docker-compose.yml       # Production deployment
├── docker-compose.dev.yml   # Development environment
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Node.js 18+ (for local development)
- Git

### Production Deployment

1. **Clone and navigate to the project:**
   ```bash
   cd agentic_fullstack
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - Health Check: http://localhost:3001/health

### Development Environment

1. **Run development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:5173 (Vite dev server)
   - Backend API: http://localhost:3001
   - Hot reload enabled for both services

### Local Development (without Docker)

1. **Backend setup:**
   ```bash
   cd agentic_backend
   cp .env.example .env
   npm install
   npm run dev
   ```

2. **Frontend setup:**
   ```bash
   cd agentic_frontend
   cp .env.example .env
   npm install
   npm run dev
   ```

## 📁 Services Overview

### Backend Service (`agentic_backend`)

- **Framework**: Express.js
- **Port**: 3001
- **Features**:
  - RESTful API endpoints
  - CORS configuration
  - Health check endpoint
  - Error handling middleware
  - Environment-based configuration

**API Endpoints:**
- `GET /health` - Health check
- `GET /api/test` - Test connection
- `GET /api/users` - Get users list
- `POST /api/users` - Create new user

### Frontend Service (`agentic_frontend`)

- **Framework**: React.js + Vite
- **Port**: 3000 (production), 5173 (development)
- **Features**:
  - Modern React with hooks
  - Responsive design
  - API integration
  - Environment-based configuration
  - Production-ready Nginx serving

## 🐳 Docker Configuration

### Production Images

- **Backend**: Node.js Alpine with multi-stage build
- **Frontend**: Nginx Alpine serving static files
- **Security**: Non-root users, health checks
- **Optimization**: Layer caching, minimal image size

### Development Images

- **Hot Reload**: Volume mounting for live development
- **Debugging**: Full development dependencies included
- **Fast Iteration**: Optimized for development workflow

## 🔧 Environment Variables

### Backend (.env)
```bash
PORT=3001
NODE_ENV=development
FRONTEND_URL=http://localhost:5173
# Add database and API configurations
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:3001
VITE_NODE_ENV=development
VITE_APP_NAME=Agentic Frontend
```

## 📊 Monitoring & Health Checks

Both services include health check endpoints:
- Backend: `GET /health`
- Frontend: `GET /health` (via Nginx)

Docker Compose includes health check configuration for service dependencies.

## 🔄 Development Workflow

1. **Feature Development:**
   ```bash
   # Start development environment
   docker-compose -f docker-compose.dev.yml up

   # Make changes to code (auto-reload enabled)
   # Test locally
   ```

2. **Production Testing:**
   ```bash
   # Build and test production images
   docker-compose up --build

   # Verify functionality
   ```

3. **Deployment:**
   ```bash
   # Deploy to production environment
   docker-compose -f docker-compose.yml up -d
   ```

## 📈 Scaling & Extensions

### Adding New Services

1. Create service directory
2. Add Dockerfile
3. Update docker-compose.yml
4. Configure networking

### Database Integration

Uncomment database service in docker-compose.yml:
```yaml
database:
  image: postgres:15-alpine
  # ... configuration
```

### Adding Redis Cache

Uncomment Redis service for session management and caching.

## 🔐 Security Features

- Non-root container users
- Security headers (Nginx)
- CORS configuration
- Environment variable isolation
- Health check monitoring

## 🧪 Testing

```bash
# Backend tests
cd agentic_backend
npm test

# Frontend tests  
cd agentic_frontend
npm test

# Integration tests with Docker
docker-compose -f docker-compose.test.yml up
```

## 📝 API Documentation

### Backend Endpoints

#### Health Check
```
GET /health
Response: { status: "OK", message: "Backend service is running" }
```

#### Test Connection
```
GET /api/test  
Response: { message: "Hello from Agentic Backend!", version: "1.0.0" }
```

#### Users Management
```
GET /api/users
Response: [{ id: 1, name: "John Doe", email: "john@example.com" }]

POST /api/users
Body: { name: "Jane", email: "jane@example.com" }
Response: { id: 123, name: "Jane", email: "jane@example.com", createdAt: "..." }
```

## 🚀 Production Deployment

### Using Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml agentic
```

### Using Kubernetes

Convert Docker Compose to Kubernetes manifests:
```bash
kompose convert
kubectl apply -f .
```

## 📚 Learning Resources

This project demonstrates:
- **Microservices Architecture**
- **Containerization with Docker**
- **React.js Frontend Development**  
- **Express.js Backend Development**
- **API Design and Integration**
- **Production-Ready Deployment**
- **Development Environment Setup**

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test with Docker
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.
