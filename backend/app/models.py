from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Association tables
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', String, ForeignKey('teams.id')),
    Column('user_id', String, ForeignKey('users.id')),
    Column('role', String, default='member'),  # owner, admin, member
    Column('joined_at', DateTime, default=func.now())
)

experiment_shares = Table(
    'experiment_shares',
    Base.metadata,
    Column('experiment_id', String, ForeignKey('experiments.id')),
    Column('team_id', String, ForeignKey('teams.id')),
    Column('shared_at', DateTime, default=func.now())
)

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())

    # Settings
    theme = Column(String, default='dark')
    notifications = Column(Boolean, default=True)
    default_cancer_type = Column(String)
    openai_api_key = Column(String)
    anthropic_api_key = Column(String)

    # Relationships
    experiments = relationship('Experiment', back_populates='user')
    teams = relationship('Team', secondary=team_members, back_populates='members')

class Experiment(Base):
    __tablename__ = 'experiments'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    cancer_type = Column(String, nullable=False)
    user_id = Column(String, ForeignKey('users.id'))
    is_public = Column(Boolean, default=False)
    share_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Analysis status
    status = Column(String, default='pending')  # pending, processing, completed, failed

    # Relationships
    user = relationship('User', back_populates='experiments')
    layers = relationship('Layer', back_populates='experiment', cascade='all, delete-orphan')
    results = relationship('AnalysisResult', back_populates='experiment', uselist=False)
    teams = relationship('Team', secondary=experiment_shares, back_populates='shared_experiments')

class Layer(Base):
    __tablename__ = 'layers'

    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey('experiments.id'), nullable=False)
    layer_type = Column(String, nullable=False)  # expression, mutation, methylation, cnv, protein, metabolomics, single_cell
    file_name = Column(String, nullable=False)
    file_path = Column(String)
    gene_count = Column(Integer)
    sample_count = Column(Integer)
    uploaded_at = Column(DateTime, default=func.now())

    # Store data as JSON for now (could be moved to separate storage)
    data_summary = Column(JSON)

    # Relationships
    experiment = relationship('Experiment', back_populates='layers')

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'

    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey('experiments.id'), unique=True, nullable=False)

    # Metrics
    layers_count = Column(Integer)
    novel_genes_count = Column(Integer)
    known_alterations_count = Column(Integer)
    multi_omics_hits = Column(Integer)
    pathways_count = Column(Integer)
    hypotheses_count = Column(Integer)

    # Results stored as JSON
    novel_findings = Column(JSON)
    known_genes = Column(JSON)
    pathways = Column(JSON)
    subtype_prediction = Column(JSON)
    hypotheses = Column(JSON)
    narrative = Column(Text)

    # Survival analysis
    survival_data = Column(JSON)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    experiment = relationship('Experiment', back_populates='results')

class Team(Base):
    __tablename__ = 'teams'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    members = relationship('User', secondary=team_members, back_populates='teams')
    shared_experiments = relationship('Experiment', secondary=experiment_shares, back_populates='teams')

class GEODataset(Base):
    __tablename__ = 'geo_datasets'

    id = Column(String, primary_key=True, default=generate_uuid)
    accession = Column(String, unique=True, index=True, nullable=False)
    title = Column(String)
    summary = Column(Text)
    organism = Column(String)
    samples_count = Column(Integer)
    platform = Column(String)
    pubmed_id = Column(String)
    cached_at = Column(DateTime, default=func.now())

class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey('experiments.id'), nullable=False)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
