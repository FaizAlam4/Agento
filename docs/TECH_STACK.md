# Technology Stack Documentation

## 🎯 Overview

This document provides a comprehensive overview of the technology stack used in the Smart Customer Support RAG Chatbot system, including rationale for technology choices, configurations, and best practices.

## 🏗️ Architecture Layers

### Frontend Layer
```
React 18 + TypeScript → Vite → Tailwind CSS → WebSocket Client
```

### Backend Layer  
```
FastAPI + Pydantic → SQLAlchemy → AsyncIO → Uvicorn
```

### Data Layer
```
PostgreSQL → OpenSearch → Redis → Vector Embeddings
```

### AI/ML Layer
```
sentence-transformers → CLIP → OpenSearch → Local LLM
```

---

## 🎨 Frontend Stack

### Core Framework
**React 18 + TypeScript**
```json
{
  "react": "^19.1.1",
  "react-dom": "^19.1.1",
  "@types/react": "^19.1.9",
  "@types/react-dom": "^19.1.7"
}
```

**Why React 18?**
- **Concurrent Features**: Automatic batching, Suspense, useTransition
- **Performance**: React Server Components, Streaming SSR
- **Developer Experience**: Better dev tools, error boundaries
- **Ecosystem**: Largest component library ecosystem

**Why TypeScript?**
- **Type Safety**: Catch errors at compile time
- **Better IDE Support**: IntelliSense, refactoring
- **Self-Documenting**: Interfaces serve as documentation
- **Team Collaboration**: Clearer contracts between components

### Build Tool
**Vite**
```json
{
  "vite": "^5.4.0",
  "@vitejs/plugin-react": "^4.3.0"
}
```

**Advantages over Create React App:**
- **Faster Dev Server**: ES modules, no bundling in dev
- **Lightning Fast HMR**: <50ms hot reload
- **Smaller Bundle Size**: Tree shaking, code splitting
- **Modern Defaults**: ES2020, dynamic imports

### State Management
**Zustand + TanStack Query**
```typescript
// Zustand for client state
import { create } from 'zustand'

interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    // Implementation
  },
  logout: () => set({ user: null, isAuthenticated: false })
}))

// TanStack Query for server state
import { useQuery, useMutation } from '@tanstack/react-query'

export const useKnowledgeBases = () => {
  return useQuery({
    queryKey: ['knowledge-bases'],
    queryFn: () => api.getKnowledgeBases(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
```

**Why This Combination?**
- **Zustand**: Minimal boilerplate, TypeScript-first, no providers
- **TanStack Query**: Best server state management, caching, background updates
- **Separation of Concerns**: Client state vs server state
- **Performance**: Selective re-renders, automatic optimizations

### UI Components & Styling
**Tailwind CSS + Headless UI**
```json
{
  "tailwindcss": "^3.4.0",
  "@headlessui/react": "^1.7.17",
  "lucide-react": "^0.263.1"
}
```

**Component Library Strategy:**
```tsx
// Base components with Tailwind + Headless UI
import { Dialog, Transition } from '@headlessui/react'

const Modal = ({ isOpen, onClose, children }) => {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>
        
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                {children}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
```

**Benefits:**
- **No Runtime Cost**: Utility-first CSS, purged unused styles
- **Consistent Design**: Design system through configuration
- **Accessibility**: Headless UI components are accessible by default
- **Developer Experience**: IntelliSense for CSS classes

### Real-time Features
**WebSocket + Server-Sent Events**
```typescript
// WebSocket for bidirectional chat
class ChatWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  connect(token: string) {
    this.ws = new WebSocket(`ws://localhost:3001/ws/chat?token=${token}`)
    
    this.ws.onopen = () => {
      console.log('Chat connected')
      this.reconnectAttempts = 0
    }
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      this.handleMessage(message)
    }
    
    this.ws.onclose = () => {
      this.handleReconnect()
    }
  }
  
  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++
        this.connect()
      }, Math.pow(2, this.reconnectAttempts) * 1000) // Exponential backoff
    }
  }
}

// Server-Sent Events for notifications
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  
  useEffect(() => {
    const eventSource = new EventSource('/api/notifications/stream')
    
    eventSource.onmessage = (event) => {
      const notification = JSON.parse(event.data)
      setNotifications(prev => [notification, ...prev])
    }
    
    return () => eventSource.close()
  }, [])
  
  return notifications
}
```

---

## ⚡ Backend Stack

### Core Framework
**FastAPI + Pydantic v2**
```python
# requirements.txt
fastapi==0.104.1
pydantic==2.5.0
uvicorn[standard]==0.24.0
```

**Why FastAPI?**
- **Performance**: Comparable to Node.js and Go
- **Type Safety**: Pydantic models for request/response validation
- **Auto Documentation**: OpenAPI/Swagger generation
- **Modern Python**: Async/await, type hints, Python 3.7+
- **Developer Experience**: Great error messages, IDE support

**Example API Structure:**
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio

app = FastAPI(
    title="Smart Customer Support API",
    description="Multi-modal RAG chatbot for customer support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for type safety
class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: bool = Field(default=False)

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    document_count: int
    
    class Config:
        from_attributes = True

# Async endpoint with dependency injection
@app.post("/api/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Implementation
    pass
```

### Database ORM
**SQLAlchemy 2.0 + Alembic**
```python
# Modern SQLAlchemy 2.0 syntax
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base")
    conversations = relationship("Conversation", back_populates="knowledge_base")

# Async database operations
async def get_knowledge_bases(db: AsyncSession, user_id: str) -> List[KnowledgeBase]:
    result = await db.execute(
        select(KnowledgeBase)
        .options(selectinload(KnowledgeBase.documents))
        .where(KnowledgeBase.created_by == user_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    return result.scalars().all()
```

**Benefits of SQLAlchemy 2.0:**
- **Async Support**: Native async/await support
- **Better Type Safety**: Improved typing with modern Python
- **Performance**: Lazy loading, connection pooling
- **Migration Management**: Alembic for database versioning

### Authentication & Security
**JWT + bcrypt + Rate Limiting**
```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginCredentials):
    # Implementation with rate limiting
    pass
```

### Async Processing
**Celery + Redis**
```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    "smart_support",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks"]
)

# Task configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Background tasks
@celery_app.task(bind=True)
def scrape_website_task(self, url: str, knowledge_base_id: str):
    try:
        scraper = WebScraper()
        result = scraper.scrape_url(url)
        
        # Process and store results
        processor = ContentProcessor()
        documents = processor.process_content(result)
        
        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"processed": len(documents), "total": len(documents)}
        )
        
        return {"status": "completed", "documents_created": len(documents)}
    except Exception as exc:
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc)}
        )
        raise
```

---

## 🗄️ Data Layer

### Primary Database
**PostgreSQL 15**
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: smart_support
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
```

**Configuration for Performance:**
```sql
-- postgresql.conf optimizations
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

**Why PostgreSQL?**
- **ACID Compliance**: Strong consistency guarantees
- **JSON Support**: Native JSONB for flexible schemas
- **Full-Text Search**: Built-in text search capabilities
- **Extensions**: PostGIS, pg_vector for specialized use cases
- **Performance**: Mature optimizer, parallel queries

### Vector Database
**OpenSearch**
```yaml
# docker-compose.yml
services:
  opensearch:
    image: opensearchproject/opensearch:2.10.0
    environment:
      - cluster.name=smart-support-cluster
      - node.name=smart-support-node
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
      - "DISABLE_INSTALL_DEMO_CONFIG=true"
      - "DISABLE_SECURITY_PLUGIN=true"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - opensearch_data:/usr/share/opensearch/data
    ports:
      - "9200:9200"
      - "9600:9600"
```

**Index Configuration:**
```python
# Vector index mapping
EMBEDDING_INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 100
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "standard"
            },
            "embedding": {
                "type": "knn_vector",
                "dimension": 384,  # sentence-transformers dimension
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimilarity",
                    "engine": "lucene",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 24
                    }
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "source_url": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        }
    }
}
```

**Why OpenSearch over Alternatives?**
- **Performance**: Faster than Pinecone for self-hosted
- **Cost**: No per-vector pricing, unlimited storage
- **Hybrid Search**: Combine vector + keyword search
- **Flexibility**: Full control over indexing and search
- **Integration**: Works well with existing ELK stack

### Cache Layer
**Redis**
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
```

**Usage Patterns:**
```python
import redis.asyncio as redis
from typing import Optional
import json

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    
    async def get_cached_response(self, query_hash: str) -> Optional[dict]:
        """Get cached chat response"""
        cached = await self.redis.get(f"chat_response:{query_hash}")
        return json.loads(cached) if cached else None
    
    async def cache_response(self, query_hash: str, response: dict, ttl: int = 3600):
        """Cache chat response for 1 hour"""
        await self.redis.setex(
            f"chat_response:{query_hash}",
            ttl,
            json.dumps(response)
        )
    
    async def get_rate_limit(self, user_id: str) -> int:
        """Get current rate limit count"""
        count = await self.redis.get(f"rate_limit:{user_id}")
        return int(count) if count else 0
    
    async def increment_rate_limit(self, user_id: str, window: int = 60) -> int:
        """Increment rate limit counter"""
        key = f"rate_limit:{user_id}"
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        return results[0]
```

---

## 🤖 AI/ML Stack

### Text Embeddings
**sentence-transformers**
```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class TextEmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text chunks"""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32
        )
    
    def encode_query(self, query: str) -> np.ndarray:
        """Generate embedding for search query"""
        return self.model.encode([query], normalize_embeddings=True)[0]
```

**Model Selection Rationale:**
- **all-MiniLM-L6-v2**: Good balance of speed and quality
- **384 dimensions**: Reasonable storage requirements
- **Multilingual support**: Works with multiple languages
- **Fine-tuning ready**: Can be customized for domain

### Image Processing
**CLIP Model**
```python
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import requests

class ImageEmbeddingEngine:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def encode_image_from_url(self, image_url: str) -> np.ndarray:
        """Generate embedding for image from URL"""
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # Normalize embeddings
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
            return np.zeros(512)  # Return zero vector on error
    
    def encode_text_query(self, text: str) -> np.ndarray:
        """Generate embedding for text query to search images"""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        return text_features.cpu().numpy().flatten()
```

### Local LLM Integration
**Ollama Integration**
```python
import aiohttp
import json

class LocalLLMEngine:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama2:13b-chat"
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "",
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """Generate response using local LLM"""
        
        full_prompt = f"""Context: {context}

Question: {prompt}

Please provide a helpful and accurate response based on the context provided. If the context doesn't contain enough information, say so clearly.

Response:"""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "stop": ["Human:", "Assistant:"]
            },
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                result = await response.json()
                return result.get("response", "").strip()
    
    async def stream_response(
        self, 
        prompt: str, 
        context: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream response for real-time chat"""
        # Implementation for streaming responses
        pass
```

---

## 🔧 Development Tools

### Code Quality
```json
{
  "devDependencies": {
    "eslint": "^9.32.0",
    "prettier": "^3.0.3",
    "@typescript-eslint/eslint-plugin": "^6.7.2",
    "@typescript-eslint/parser": "^6.7.2"
  }
}
```

```python
# Python tools
black==23.11.0          # Code formatting
flake8==6.1.0           # Linting
isort==5.12.0           # Import sorting
mypy==1.6.1             # Type checking
pytest==7.4.3          # Testing
pytest-asyncio==0.21.1 # Async testing
httpx==0.25.2           # HTTP testing
```

### Testing Strategy
```typescript
// Frontend testing with Vitest + Testing Library
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import ChatInterface from '../ChatInterface'

describe('ChatInterface', () => {
  it('sends message when form is submitted', async () => {
    const mockSendMessage = vi.fn()
    
    render(<ChatInterface onSendMessage={mockSendMessage} />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    const submitButton = screen.getByRole('button', { name: 'Send' })
    
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.click(submitButton)
    
    expect(mockSendMessage).toHaveBeenCalledWith('Hello')
  })
})
```

```python
# Backend testing with pytest
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_knowledge_base():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/knowledge-bases",
            json={
                "name": "Test KB",
                "description": "Test description",
                "is_public": False
            },
            headers={"Authorization": "Bearer test_token"}
        )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test KB"
```

### Monitoring & Observability
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration'
)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_duration.observe(duration)
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🚀 Deployment Stack

### Containerization
```dockerfile
# Multi-stage production Dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY --from=frontend-builder /app/dist ./static

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Orchestration
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-support-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smart-support-api
  template:
    metadata:
      labels:
        app: smart-support-api
    spec:
      containers:
      - name: api
        image: smart-support:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

This technology stack provides a solid foundation for building a scalable, maintainable, and performant RAG chatbot system while keeping costs minimal through the use of open-source technologies and efficient resource utilization.