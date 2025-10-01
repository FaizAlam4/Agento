from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    __table_args__ = {'schema': 'agentic'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    settings = Column(Text)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    
    # Relationships
    created_by_user = relationship("User", back_populates="knowledge_bases")
    organization = relationship("Organization", back_populates="knowledge_bases")
    scraped_urls = relationship("ScrapedUrl", back_populates="knowledge_base")
    conversations = relationship("Conversation", back_populates="knowledge_base")

class ScrapedUrl(Base):
    __tablename__ = "scraped_urls"
    __table_args__ = {'schema': 'agentic'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(2048), nullable=False)
    title = Column(String(500))
    content_hash = Column(String(64))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    scraped_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    scrape_metadata = Column(Text)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="scraped_urls")
    created_by_user = relationship("User")
    documents = relationship("Document", back_populates="scraped_url")

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {'schema': 'agentic'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # text, image, metadata
    chunk_index = Column(Integer, default=0)
    embedding_id = Column(String(255))  # Reference to vector store
    source_url = Column(String(2048))
    doc_metadata = Column(Text)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scraped_url_id = Column(UUID(as_uuid=True), ForeignKey("scraped_urls.id"))
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"))
    
    # Relationships
    scraped_url = relationship("ScrapedUrl", back_populates="documents")

class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {'schema': 'agentic'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id"))
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    knowledge_base = relationship("KnowledgeBase", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {'schema': 'agentic'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON array of source URLs/documents
    msg_metadata = Column(Text)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")