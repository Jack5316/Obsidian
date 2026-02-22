```mermaid
graph TB
    subgraph "User Interface"
        Obsidian[Obsidian Vault]
        ClaudeCode[Claude Code]
        RalphLoop[Ralph Loop Plugin]
    end

    subgraph "Automation Layer"
        Scripts["_scripts/*.py"]
        Templates["Templates/"]
        Config["config.py"]
    end

    subgraph "Data Sources"
        ArXiv[ArXiv API]
        YouTube[YouTube API]
        Bilibili[Bilibili API]
        Reddit[Reddit API]
        Twitter[Twitter API]
        HN[Hacker News API]
        PDFs[PDF Documents]
        Kindle[Kindle Clippings]
    end

    subgraph "AI Processing"
        Volcengine[Volcengine Ark API]
        Summarization[Summarization]
        Analysis[Analysis]
        Generation[Generation]
    end

    subgraph "Obsidian Plugins"
        Dataview[Dataview]
        Templater[Templater]
    end

    subgraph "Output Destinations"
        Sources["Sources/"]
        BearBlog[BearBlog]
        Logs["_logs/"]
    end

    %% User to Obsidian
    ClaudeCode --> Obsidian
    RalphLoop --> ClaudeCode
    ClaudeCode --> Scripts

    %% Obsidian to Plugins
    Obsidian --> Dataview
    Obsidian --> Templater
    Templater --> Templates

    %% Scripts configuration
    Scripts --> Config
    Config --> Volcengine

    %% Data sources
    Scripts --> ArXiv
    Scripts --> YouTube
    Scripts --> Bilibili
    Scripts --> Reddit
    Scripts --> Twitter
    Scripts --> HN
    Scripts --> PDFs
    Scripts --> Kindle

    %% AI processing
    Scripts --> Volcengine
    Volcengine --> Summarization
    Volcengine --> Analysis
    Volcengine --> Generation

    %% Output
    Scripts --> Sources
    Scripts --> BearBlog
    Scripts --> Logs

    %% Note creation
    Templater --> Obsidian
    Scripts --> Obsidian

    %% Querying
    Dataview --> Obsidian
    Obsidian --> Dataview
```

## System Architecture Diagram

This diagram shows the high-level architecture of your AI-powered Obsidian vault:

### 1. User Interface Layer
- **Obsidian**: Main knowledge base interface
- **Claude Code**: AI assistant for script execution and agent management
- **Ralph Loop Plugin**: Automated task execution system

### 2. Automation Layer
- **Scripts**: Python automation scripts for content acquisition and processing
- **Templates**: Note templates for consistency
- **Config**: Central configuration file

### 3. Data Sources
External content sources accessed by scripts:
- ArXiv, YouTube, Bilibili, Reddit, Twitter, Hacker News
- PDF documents, Kindle clippings

### 4. AI Processing Layer
Volcengine Ark API for:
- Content summarization
- Analysis and classification
- Text generation

### 5. Obsidian Plugins
- **Dataview**: Advanced query and relational database capabilities
- **Templater**: Note creation automation

### 6. Output Destinations
- **Sources/**: External content storage
- **BearBlog**: Publishing platform
- **_logs/**: Script execution logs

The system uses a bidirectional flow:
1. Content flows from sources → AI processing → Obsidian
2. Notes in Obsidian can be enhanced by AI
3. Automation scripts are controlled through Claude Code or Ralph Loop
4. Dataview and Templater provide enhanced usability

This architecture ensures that your knowledge base remains up-to-date, well-organized, and continuously improved through automation and AI assistance.
