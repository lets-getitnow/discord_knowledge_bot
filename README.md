# Discord Knowledge Bot
**Demo Video**: [https://www.youtube.com/watch?v=2LhrUmU_F2E](https://www.youtube.com/watch?v=2LhrUmU_F2E)

<iframe 
  width="560" 
  height="315" 
  src="https://www.youtube.com/embed/2LhrUmU_F2E" 
  frameborder="0" 
  allowfullscreen>
</iframe>

A Discord bot that indexes server content and provides AI-powered chat functionality using **local vectorDB**, **local embeddings**, and **OpenAI** for final chat completion (other model support coming soon).

## Key Features

- **Local Vector Database**: Uses [ChromaDB](https://github.com/chroma-core/chroma) for local vector storage - no external database required
- **Local Embeddings**: Uses [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for local embedding generation - no external embedding API needed
- **OpenAI Integration**: Only external dependency is OpenAI API for final chat completion (other model support coming soon)
- **Self-Contained**: Runs entirely locally to the host machine except for OpenAI chat completion

## Features

- **Server Indexing**: Index all text channels in a Discord server
- **Channel Indexing**: Index specific channels with pagination support
- **AI Chat**: Natural language conversation with context from server content
- **Context-Aware Search**: Channel-specific or server-wide search capabilities
- **Reindexing**: Clear and rebuild indexes as needed
- **Rate Limiting**: Respects Discord API limits
- **Text-Only**: Focuses exclusively on text content

## Requirements

- Python 3.8 or higher
- Discord Bot Token
- OpenAI API Key (required today for response generation)

## Environment Variables

The bot requires the following environment variables to be set in a `.env` file:

- `DISCORD_TOKEN`: Your Discord bot token from the Discord Developer Portal
- `DISCORD_APP_ID`: Your Discord application ID from the Discord Developer Portal
- `OPENAI_API_KEY`: Your OpenAI API key from the OpenAI platform

These are loaded automatically when the bot starts.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd discord_knowledge_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Copy the example environment file and configure it:
   ```bash
   cp env.example .env
   ```
   
   Then edit `.env` and add your actual values:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   DISCORD_APP_ID=your_discord_application_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Configure the bot**:
   Edit `config.yaml` to customize bot settings.

## Usage

### Starting the Bot

```bash
python main.py
```

### Bot Commands

All commands are now slash commands (`/`) that appear in Discord's command interface.

#### Indexing Commands (Admin Only)
- `/index-server` - Index all text channels in the server
- `/index-channel [channel]` - Index a specific channel (or current channel)
- `/reindex-server` - Clear and reindex all text channels
- `/reindex-channel [channel]` - Clear and reindex a specific channel

#### Management Commands
- `/help` - Show help information and available commands
- `/status` - Show bot and indexing status
- `/stats` - Show detailed statistics
- `/clear` - Clear all indexed data (Admin only)


#### Chat Commands
- `/ask <question>` - Ask a question about **this channel's** content
- `/ask-server <question>` - Ask a question about the **entire server's** content

#### Direct Mentions
Mention the bot with `@bot_name` to chat directly! The bot will search through indexed content to provide relevant answers.

### Context-Aware Search

The bot now provides two types of search:

1. **Channel-Specific Search** (`/ask`):
   - Searches only within the current channel's indexed content
   - Provides more focused, relevant responses
   - Use when asking about channel-specific topics

2. **Server-Wide Search** (`/ask-server`):
   - Searches across all indexed channels in the server
   - Provides broader context from the entire server
   - Use when asking about server-wide topics or cross-channel information

### Permissions

The bot needs "Read Message History" permission to index channels.

## Configuration

The bot can be configured through `config.yaml`:

```yaml
# Bot Configuration
bot:
  prefix: "!"
  intents:
    message_content: true
    guilds: true
    messages: true

# OpenAI Configuration
openai:
  model: "gpt-4o-mini"
  max_tokens: 1000
  temperature: 0.7

# Local Embeddings Configuration
embeddings:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"

# ChromaDB Configuration
chromadb:
  persist_directory: "./data"
  collection_name: "discord_knowledge"

# Indexing Configuration
indexing:
  chunk_size: 1000
  max_messages_per_request: 100
  rate_limit_delay: 1.0
```

## Architecture

### Components

1. **Discord Bot Core** (`bot/`)
   - Main bot functionality
   - Slash command handling
   - Event processing

2. **Indexing System** (`indexing/`)
   - Message collection with pagination
   - Text processing and chunking
   - ChromaDB storage management

3. **AI Chat System** (`chat/`)
   - OpenAI integration
   - Context building with channel filtering
   - Response generation

4. **Utilities** (`utils/`)
   - Configuration management
   - Text processing helpers

### Data Flow

1. **Indexing**: Messages → Text Processing → ChromaDB Storage
2. **Chat**: User Query → Context-Aware Search → AI Response
3. **Search**: Query → ChromaDB Search (with optional filtering) → Formatted Results

## Data Flow & Privacy

- **Stays local**: Discord message data, embeddings (vector representations), and the vector database (Chroma) all reside on your machine.
- **Sent to OpenAI (required today)**: For each response, the bot sends the user's prompt plus a small, selected set of retrieved context snippets to OpenAI for final response generation.
- **Planned**: Support for selecting alternative model providers via LlamaIndex so responses can be generated without OpenAI.

## Technical Details

- **Local Vector Database**: [ChromaDB](https://github.com/chroma-core/chroma) provides local vector storage - no external database required
- **Local Embeddings**: Uses [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for local embedding generation - no external embedding API needed
- **OpenAI Integration**: Only external dependency is OpenAI API for final chat completion (required today)
- **Text Processing**: MVP functionality with basic cleaning and chunking
- **Vector Search**: ChromaDB with LlamaIndex for semantic search
- **Context Filtering**: Channel-specific search with metadata filtering
- **Slash Commands**: Modern Discord slash command interface
- **Permission System**: Admin-only commands for destructive operations

## Model Providers (Planned)

We plan to support selecting among multiple LLM providers supported by LlamaIndex for response generation. See the official LlamaIndex documentation for provider options:

- [LlamaIndex LLMs (model providers)](https://docs.llamaindex.ai/en/stable/module_guides/models/llms/)

Once implemented, you will be able to choose a provider in configuration; until then, OpenAI is required.

## FAQ

- **Do you send our data to OpenAI?**
  - Yes, today the bot sends the user prompt and selected retrieved context to OpenAI to generate the final response. Raw server data and the full vector database remain local.
- **Does OpenAI train on our API data?**
  - No. Per OpenAI's API data usage policy, data submitted via the API is not used to train OpenAI models unless you explicitly opt in. See: [OpenAI API Data Usage Policy](https://openai.com/policies/api-data-usage)
- **What is “final chat completion”?**
  - The last step where an LLM takes your prompt plus retrieved context and generates the natural-language reply.
- **Can I avoid OpenAI?**
  - Not yet. OpenAI is required today. Planned support will allow selecting other providers via LlamaIndex; see the link above.
- **How long does indexing take?**
  - Depends on server size and rate limits. For a mid-size server (thousands of users, dozens of channels, multiple years), initial indexing can take hours.

## Command Examples

### Indexing
```
/index-server
/index-channel #general
/reindex-server
```

### Chat
```
/ask What was discussed about the new feature?
/ask-server Who mentioned the meeting yesterday?
```

### Management
```
/status
/stats

```

## Security

- **Admin-Only Commands**: Indexing and destructive operations require Administrator permissions
- **Permission Checks**: All commands verify user permissions before execution
- **Confirmation Dialogs**: Destructive operations require explicit confirmation
- **Error Handling**: Comprehensive error handling and logging 
