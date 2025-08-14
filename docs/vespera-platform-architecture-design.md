# Vespera Scriptorium Platform Architecture Design

**Document Purpose**: Detailed technical architecture for transforming MCP Task Orchestrator into Vespera Scriptorium - "An IDE for Ideas" - maintaining clean architecture principles while adding comprehensive document-centric, creative, and knowledge management capabilities.

## Architecture Overview

### Extended Clean Architecture Layers

The existing clean architecture foundation expands to support the full "IDE for Ideas" vision:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Web UI        │  MCP Server     │  CLI Tools    │  APIs     │
│  • Document    │  • Task Tools   │  • Setup      │  • REST   │
│    Editor      │  • Doc Tools    │  • Import     │  • GraphQL│
│  • Workspace   │  • Creative     │  • Export     │  • WebSockets │
│  • Dashboard   │    Tools        │               │           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│         Use Cases & Orchestration Services                 │
│                                                             │
│  Task Orchestration  │  Document Lifecycle  │  Creative    │
│  • Task Management   │  • Document CRUD     │    Workflows │
│  • Agent Spawning    │  • Version Control   │  • Story     │
│  • State Management  │  • Multi-format      │    Planning  │
│                      │    Export            │  • Character │
│                      │                      │    Dev       │
│                      │                      │              │
│  Knowledge Management│  Research Tools      │  Professional│
│  • Wiki Management   │  • Source Collection │    Workflows │
│  • Note Linking      │  • Citation Mgmt     │  • Report    │
│  • Semantic Search   │  • Research Coord    │    Generation│
│                      │                      │  • Collab    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                            │
├─────────────────────────────────────────────────────────────┤
│                   Entities & Value Objects                  │
│                                                             │
│  Task Domain         │  Document Domain     │  Creative     │
│  • Task              │  • Document          │    Domain     │
│  • Specialist        │  • Section           │  • Story      │
│  • Session           │  • Version           │  • Character  │
│  • Artifact          │  • Template          │  • Scene      │
│                      │                      │  • Chapter    │
│                      │                      │              │
│  Knowledge Domain    │  Research Domain     │  Collab       │
│  • Note              │  • Source            │    Domain     │
│  • Topic             │  • Citation          │  • Review     │
│  • Link              │  • Reference         │  • Comment    │
│  • Wiki              │  • Research Project  │  • Discussion │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  Database           │  External Services   │  Processing   │
│  • SQLite Core      │  • MCP Protocol      │    Engines    │
│  • Document Store   │  • Version Control   │  • Text       │
│  • Search Index     │  • Export Services   │    Processing │
│  • Media Storage    │  • Collaboration     │  • Semantic   │
│                     │    APIs              │    Analysis   │
│                     │                      │  • AI/LLM     │
│                     │                      │    Integration│
└─────────────────────────────────────────────────────────────┘
```

## Extended Domain Model

### Core Document Domain

#### Document Entity
```python
class Document(Entity):
    """Central document entity supporting all content types."""
    
    # Core properties
    document_id: DocumentId
    title: str
    content: DocumentContent  # Rich content with multiple formats
    document_type: DocumentType  # Article, Story, Research, Report, etc.
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: DocumentVersion
    author: Author
    collaborators: List[Collaborator]
    
    # Structure
    sections: List[DocumentSection]
    attachments: List[Attachment]
    references: List[Reference]
    
    # Executive dysfunction support
    last_edit_position: EditPosition
    session_context: SessionContext
    momentum_markers: List[MomentumMarker]
    
    # Relationships
    parent_document: Optional[DocumentId]
    child_documents: List[DocumentId]
    linked_documents: List[DocumentLink]
    related_tasks: List[TaskId]
```

#### Document Content System
```python
class DocumentContent:
    """Multi-format content representation."""
    
    # Primary content
    markdown: str  # Source of truth
    html: str     # Rich display format
    plain_text: str  # Searchable format
    
    # Structure
    outline: DocumentOutline
    metadata: ContentMetadata
    
    # Multi-modal elements
    images: List[Image]
    diagrams: List[Diagram]
    code_blocks: List[CodeBlock]
    tables: List[Table]
    
    # Interactive elements
    tasks: List[EmbeddedTask]
    comments: List[Comment]
    annotations: List[Annotation]
```

### Creative Domain Extensions

#### Story Planning System
```python
class Story(Document):
    """Extended document for creative writing projects."""
    
    # Story structure
    genre: List[Genre]
    premise: StoryPremise
    themes: List[Theme]
    
    # Narrative structure
    plot_structure: PlotStructure  # Three-act, Hero's Journey, etc.
    story_beats: List[StoryBeat]
    chapters: List[Chapter]
    scenes: List[Scene]
    
    # Creative elements
    characters: List[Character]
    settings: List[Setting]
    world_building: WorldBuilding
    
    # Writing progress
    word_count_target: int
    current_word_count: int
    writing_schedule: WritingSchedule
    momentum_tracking: WritingMomentum

class Character(Entity):
    """Character development and tracking."""
    
    # Basic info
    name: str
    role: CharacterRole  # Protagonist, Antagonist, Supporting, etc.
    
    # Development
    background: CharacterBackground
    personality: PersonalityProfile
    goals: List[CharacterGoal]
    conflicts: List[CharacterConflict]
    
    # Story integration
    character_arcs: List[CharacterArc]
    relationships: List[CharacterRelationship]
    scenes_appeared: List[SceneId]
    
    # Creative continuity
    physical_description: PhysicalDescription
    voice_notes: List[VoiceNote]
    dialogue_samples: List[DialogueSample]
```

### Knowledge Management Domain

#### Personal Wiki System
```python
class Wiki(Entity):
    """Personal knowledge wiki with interconnected notes."""
    
    wiki_id: WikiId
    name: str
    description: str
    
    # Structure
    pages: List[WikiPage]
    categories: List[WikiCategory]
    tags: List[WikiTag]
    
    # Navigation
    index_page: WikiPageId
    navigation_structure: WikiNavigation
    
    # Knowledge graph
    topic_graph: TopicGraph
    link_graph: LinkGraph

class WikiPage(Document):
    """Individual wiki page with enhanced linking."""
    
    # Wiki-specific properties
    wiki_id: WikiId
    page_type: WikiPageType  # Concept, Person, Event, Process, etc.
    
    # Linking system
    backlinks: List[WikiLink]
    forward_links: List[WikiLink]
    related_pages: List[WikiPageId]
    
    # Knowledge structure
    topics: List[Topic]
    concepts: List[Concept]
    definitions: List[Definition]
    
    # Research integration
    sources: List[Source]
    citations: List[Citation]
    research_questions: List[ResearchQuestion]
```

#### Research Coordination System
```python
class ResearchProject(Entity):
    """Comprehensive research project management."""
    
    # Project basics
    project_id: ResearchProjectId
    title: str
    research_questions: List[ResearchQuestion]
    methodology: ResearchMethodology
    
    # Source management
    sources: List[Source]
    citations: List[Citation]
    bibliography: Bibliography
    
    # Research process
    research_phases: List[ResearchPhase]
    current_phase: ResearchPhase
    progress_tracking: ResearchProgress
    
    # Knowledge synthesis
    findings: List[Finding]
    themes: List[ResearchTheme]
    conclusions: List[Conclusion]
    
    # Output integration
    output_documents: List[DocumentId]
    presentations: List[PresentationId]

class Source(Entity):
    """Research source with automatic metadata extraction."""
    
    # Source identification
    source_id: SourceId
    source_type: SourceType  # Book, Article, Website, Interview, etc.
    
    # Metadata
    title: str
    authors: List[Author]
    publication_date: datetime
    publisher: Publisher
    
    # Content
    abstract: str
    key_points: List[KeyPoint]
    quotes: List[Quote]
    
    # Research integration
    relevance_score: float
    research_projects: List[ResearchProjectId]
    related_sources: List[SourceId]
    
    # Accessibility features
    summary: str
    accessibility_notes: List[AccessibilityNote]
```

### Professional Workflow Domain

#### Report Generation System
```python
class Report(Document):
    """Professional report with automated generation features."""
    
    # Report structure
    report_type: ReportType  # Status, Analysis, Proposal, etc.
    template: ReportTemplate
    sections: List[ReportSection]
    
    # Data integration
    data_sources: List[DataSource]
    charts: List[Chart]
    tables: List[DataTable]
    
    # Collaboration
    review_cycle: ReviewCycle
    approval_workflow: ApprovalWorkflow
    stakeholders: List[Stakeholder]
    
    # Professional formatting
    style_guide: StyleGuide
    branding: BrandingSettings
    export_formats: List[ExportFormat]

class Presentation(Entity):
    """Presentation creation and coordination."""
    
    # Presentation basics
    presentation_id: PresentationId
    title: str
    presentation_type: PresentationType
    
    # Structure
    slides: List[Slide]
    speaker_notes: List[SpeakerNote]
    handouts: List[Handout]
    
    # Content integration
    source_documents: List[DocumentId]
    research_references: List[SourceId]
    
    # Delivery support
    practice_sessions: List[PracticeSession]
    audience_analysis: AudienceAnalysis
    timing_analysis: TimingAnalysis
```

## Extended Application Layer Services

### Document Lifecycle Management

#### Document Service
```python
class DocumentLifecycleService:
    """Comprehensive document lifecycle management."""
    
    async def create_document(
        self, 
        document_type: DocumentType,
        template: Optional[DocumentTemplate] = None,
        initial_content: Optional[str] = None
    ) -> Document:
        """Create new document with executive dysfunction support."""
        
        # Apply template with intelligent defaults
        # Set up momentum preservation markers
        # Initialize collaboration if needed
        # Create initial version
    
    async def edit_document(
        self,
        document_id: DocumentId,
        changes: DocumentChangeset,
        preserve_momentum: bool = True
    ) -> Document:
        """Edit document with momentum preservation."""
        
        # Apply changes with conflict resolution
        # Update momentum markers
        # Trigger automatic saves
        # Notify collaborators if needed
    
    async def version_document(
        self,
        document_id: DocumentId,
        version_type: VersionType = VersionType.AUTO
    ) -> DocumentVersion:
        """Version control with automatic snapshots."""
        
        # Create version snapshot
        # Update version history
        # Preserve edit context
        # Clean up old versions if needed
```

### Creative Workflow Services

#### Story Development Service
```python
class StoryDevelopmentService:
    """Executive dysfunction-aware creative writing support."""
    
    async def create_story_project(
        self,
        premise: StoryPremise,
        structure_template: PlotStructureTemplate
    ) -> Story:
        """Initialize story project with structure."""
        
        # Create story document
        # Initialize plot structure
        # Set up character development framework
        # Create writing schedule with buffer zones
    
    async def develop_character(
        self,
        story_id: StoryId,
        character_concept: CharacterConcept
    ) -> Character:
        """Character development with continuity tracking."""
        
        # Create character profile
        # Generate character arc framework
        # Set up relationship tracking
        # Initialize dialogue voice consistency
    
    async def track_writing_momentum(
        self,
        story_id: StoryId
    ) -> WritingMomentumReport:
        """Monitor and support writing momentum."""
        
        # Analyze writing patterns
        # Identify momentum breaks
        # Suggest recovery strategies
        # Update writing goals if needed
```

### Knowledge Management Services

#### Knowledge Graph Service
```python
class KnowledgeGraphService:
    """Semantic knowledge management and discovery."""
    
    async def build_knowledge_graph(
        self,
        wiki_id: WikiId
    ) -> TopicGraph:
        """Construct knowledge graph from wiki content."""
        
        # Extract topics and concepts
        # Identify relationships
        # Build semantic connections
        # Create navigation pathways
    
    async def discover_connections(
        self,
        topic: Topic,
        context: Optional[WikiContext] = None
    ) -> List[TopicConnection]:
        """Discover implicit knowledge connections."""
        
        # Semantic analysis of content
        # Identify related concepts
        # Suggest new connections
        # Highlight knowledge gaps
    
    async def search_semantically(
        self,
        query: SearchQuery,
        context: SearchContext
    ) -> SemanticSearchResults:
        """Executive dysfunction-friendly semantic search."""
        
        # Natural language query processing
        # Context-aware results
        # Cognitive load optimization
        # Progressive disclosure of results
```

## Infrastructure Layer Extensions

### Document Storage and Processing

#### Document Repository
```python
class DocumentRepository:
    """High-performance document storage with full-text search."""
    
    # Core storage
    async def store_document(self, document: Document) -> DocumentId
    async def retrieve_document(self, document_id: DocumentId) -> Document
    async def update_document(self, document: Document) -> None
    async def delete_document(self, document_id: DocumentId) -> None
    
    # Version management
    async def create_version(self, document_id: DocumentId) -> DocumentVersion
    async def get_version_history(self, document_id: DocumentId) -> List[DocumentVersion]
    async def restore_version(self, document_id: DocumentId, version: DocumentVersion) -> Document
    
    # Search and discovery
    async def full_text_search(self, query: str) -> List[Document]
    async def semantic_search(self, query: SemanticQuery) -> List[Document]
    async def find_related_documents(self, document_id: DocumentId) -> List[Document]
```

#### Rich Text Processing Engine
```python
class RichTextProcessor:
    """Multi-format document processing with executive dysfunction support."""
    
    async def parse_markdown(self, markdown: str) -> DocumentContent:
        """Parse markdown with enhanced structure extraction."""
        
        # Extract document outline
        # Identify embedded elements
        # Process cross-references
        # Generate accessibility metadata
    
    async def render_html(self, content: DocumentContent) -> str:
        """Render accessible HTML with executive dysfunction support."""
        
        # Apply accessibility optimizations
        # Implement progressive disclosure
        # Add momentum preservation markers
        # Include navigation aids
    
    async def export_format(
        self, 
        document: Document, 
        format: ExportFormat
    ) -> bytes:
        """Export to multiple formats with professional styling."""
        
        # Apply format-specific styling
        # Include metadata and references
        # Optimize for target audience
        # Maintain accessibility features
```

### Collaborative Infrastructure

#### Collaboration Engine
```python
class CollaborationEngine:
    """Real-time collaboration with executive dysfunction awareness."""
    
    async def enable_collaboration(
        self,
        document_id: DocumentId,
        collaborators: List[Collaborator]
    ) -> CollaborationSession:
        """Set up collaborative editing session."""
        
        # Initialize conflict resolution
        # Set up real-time sync
        # Configure access controls
        # Enable communication channels
    
    async def handle_concurrent_edits(
        self,
        document_id: DocumentId,
        changes: List[DocumentChange]
    ) -> DocumentMergeResult:
        """Handle concurrent edits with intelligent conflict resolution."""
        
        # Analyze change conflicts
        # Apply automatic resolution where possible
        # Flag complex conflicts for human review
        # Preserve all contributors' momentum
    
    async def support_async_collaboration(
        self,
        document_id: DocumentId,
        review_cycle: ReviewCycle
    ) -> ReviewWorkflow:
        """Support asynchronous review and approval workflows."""
        
        # Set up review assignments
        # Track review progress
        # Handle review consolidation
        # Maintain review history
```

## Integration Strategy

### Unified Workflow Architecture

The integration maintains existing task orchestration while extending it to support document-centric workflows:

```python
class UnifiedWorkflowOrchestrator:
    """Orchestrator supporting both task and document workflows."""
    
    def __init__(
        self,
        task_orchestrator: TaskOrchestrator,
        document_service: DocumentLifecycleService,
        creative_service: CreativeWorkflowService,
        knowledge_service: KnowledgeManagementService
    ):
        self.task_orchestrator = task_orchestrator
        self.document_service = document_service
        self.creative_service = creative_service
        self.knowledge_service = knowledge_service
    
    async def orchestrate_document_workflow(
        self,
        workflow_type: DocumentWorkflowType,
        context: WorkflowContext
    ) -> WorkflowResult:
        """Orchestrate document-centric workflows using existing task system."""
        
        # Create master coordination task
        master_task = await self.task_orchestrator.create_task(
            title=f"{workflow_type} Coordination",
            task_type=TaskType.COORDINATION,
            specialist_type=SpecialistType.COORDINATOR
        )
        
        # Decompose into document and creative subtasks
        subtasks = await self._decompose_document_workflow(
            workflow_type, context, master_task.task_id
        )
        
        # Execute using existing orchestration system
        results = await self.task_orchestrator.execute_coordinated_workflow(
            master_task.task_id, subtasks
        )
        
        # Synthesize results into document outputs
        return await self._synthesize_document_results(results)
```

### Executive Dysfunction Integration

All new features implement the pressure-lid-vent system:

```python
class ExecutiveDysfunctionSupport:
    """Comprehensive executive dysfunction support across all features."""
    
    async def preserve_momentum(
        self,
        user_context: UserContext,
        current_activity: Activity
    ) -> MomentumPreservationStrategy:
        """Analyze and preserve user momentum across interruptions."""
        
        # Detect interruption patterns
        # Identify momentum markers
        # Create resumption context
        # Suggest optimal restart points
    
    async def reduce_cognitive_load(
        self,
        interface_context: InterfaceContext,
        user_capacity: CognitiveCapacity
    ) -> InterfaceAdaptation:
        """Adapt interface to current cognitive capacity."""
        
        # Assess current capacity indicators
        # Apply progressive disclosure
        # Reduce decision fatigue
        # Optimize information hierarchy
    
    async def prevent_overwhelm(
        self,
        workflow_context: WorkflowContext,
        user_stress_indicators: StressIndicators
    ) -> OverwhelmPrevention:
        """Detect and prevent cognitive overwhelm."""
        
        # Monitor stress indicators
        # Provide escape hatches
        # Suggest break points
        # Implement graceful degradation
```

## Technical Implementation Specifications

### Database Schema Extensions

The existing SQLite foundation extends to support new entities:

```sql
-- Document domain tables
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL,
    content_markdown TEXT,
    content_html TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_id TEXT,
    parent_document_id TEXT,
    session_context TEXT,
    momentum_markers TEXT,
    FOREIGN KEY (parent_document_id) REFERENCES documents(document_id)
);

-- Creative domain tables  
CREATE TABLE stories (
    story_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    genre TEXT,
    premise TEXT,
    plot_structure TEXT,
    word_count_target INTEGER,
    current_word_count INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

CREATE TABLE characters (
    character_id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    background TEXT,
    personality_profile TEXT,
    character_arcs TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);

-- Knowledge domain tables
CREATE TABLE wikis (
    wiki_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    index_page_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wiki_pages (
    page_id TEXT PRIMARY KEY,
    wiki_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    page_type TEXT,
    topics TEXT,
    backlinks TEXT,
    forward_links TEXT,
    FOREIGN KEY (wiki_id) REFERENCES wikis(wiki_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Research domain tables
CREATE TABLE research_projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    research_questions TEXT,
    methodology TEXT,
    current_phase TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    publication_date DATE,
    content_summary TEXT,
    relevance_score REAL
);
```

### MCP Tool Extensions

New MCP tools for document-centric workflows:

```python
# Document management tools
DOCUMENT_TOOLS = [
    types.Tool(
        name="vespera_create_document",
        description="Create a new document with intelligent templates",
        inputSchema={
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "enum": ["article", "story", "research", "report", "wiki_page"]
                },
                "title": {"type": "string"},
                "template": {"type": "string"},
                "initial_content": {"type": "string"}
            },
            "required": ["document_type", "title"]
        }
    ),
    
    types.Tool(
        name="vespera_edit_document",
        description="Edit document with momentum preservation",
        inputSchema={
            "type": "object", 
            "properties": {
                "document_id": {"type": "string"},
                "changes": {"type": "object"},
                "preserve_context": {"type": "boolean", "default": True}
            },
            "required": ["document_id", "changes"]
        }
    )
]

# Creative workflow tools
CREATIVE_TOOLS = [
    types.Tool(
        name="vespera_create_story",
        description="Initialize a creative writing project",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "premise": {"type": "string"},
                "genre": {"type": "array", "items": {"type": "string"}},
                "plot_structure": {"type": "string"}
            },
            "required": ["title", "premise"]
        }
    ),
    
    types.Tool(
        name="vespera_develop_character",
        description="Create and develop story characters",
        inputSchema={
            "type": "object",
            "properties": {
                "story_id": {"type": "string"},
                "character_name": {"type": "string"},
                "role": {"type": "string"},
                "background": {"type": "string"}
            },
            "required": ["story_id", "character_name"]
        }
    )
]

# Knowledge management tools
KNOWLEDGE_TOOLS = [
    types.Tool(
        name="vespera_create_wiki",
        description="Create personal knowledge wiki",
        inputSchema={
            "type": "object",
            "properties": {
                "wiki_name": {"type": "string"},
                "description": {"type": "string"},
                "initial_structure": {"type": "object"}
            },
            "required": ["wiki_name"]
        }
    ),
    
    types.Tool(
        name="vespera_semantic_search",
        description="Search knowledge base semantically",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "context": {"type": "object"},
                "search_scope": {"type": "array"}
            },
            "required": ["query"]
        }
    )
]
```

This architecture design provides a comprehensive foundation for implementing the Vespera Scriptorium transformation while maintaining the executive dysfunction accessibility principles and clean architecture that make the current system valuable.

---

*Next: Detailed implementation specifications for each major feature area, starting with Phase 1 foundation extensions.*