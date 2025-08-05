# Discord Knowledge Bot

A Discord bot that indexes server content and provides AI-powered chat functionality using ChromaDB and OpenAI.

## Features

- **Server Indexing**: Index all text channels in a Discord server
- **Channel Indexing**: Index specific channels with pagination support
- **AI Chat**: Natural language conversation with context from server content
- **Search**: Find relevant content from indexed messages
- **Reindexing**: Clear and rebuild indexes as needed
- **Rate Limiting**: Respects Discord API limits
- **Text-Only**: Focuses exclusively on text content

## Requirements

- Python 3.8 or higher
- Discord Bot Token
- OpenAI API Key

## Environment Variables

The bot requires the following environment variables to be set in a `.env` file:

- `DISCORD_TOKEN`: Your Discord bot token from the Discord Developer Portal
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
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Configure the bot**:
   Edit `config.yaml` to customize bot settings.

## Usage

### Testing Your Setup

Before running the bot, test your configuration:
```bash
python test_setup.py
```

This will validate your Discord token, environment variables, and dependencies.

### Starting the Bot

```bash
python main.py
```

### Bot Commands

#### Indexing Commands
- `!index-server` - Index all text channels in the server
- `!index-channel [channel]` - Index a specific channel (or current channel)
- `!reindex-server` - Clear and reindex all text channels
- `!reindex-channel [channel]` - Clear and reindex a specific channel

#### Management Commands
- `!status` - Show bot and indexing status
- `!stats` - Show detailed statistics
- `!clear` - Clear all indexed data
- `!help` - Show help information

#### Chat Commands
- `!ask <question>` - Ask a question and get AI response

#### Natural Chat
Simply send a message to chat with the AI! The bot will search through indexed content to provide relevant answers.

### Permissions

Indexing and management commands require "Manage Messages" permission.

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
  model: "gpt-3.5-turbo"
  embedding_model: "text-embedding-ada-002"
  max_tokens: 1000
  temperature: 0.7

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
   - Command handling
   - Event processing

2. **Indexing System** (`indexing/`)
   - Message collection with pagination
   - Text processing and chunking
   - ChromaDB storage management

3. **AI Chat System** (`chat/`)
   - OpenAI integration
   - Context building
   - Response generation

4. **Utilities** (`utils/`)
   - Configuration management
   - Text processing helpers

### Data Flow

1. **Indexing**: Messages → Text Processing → ChromaDB Storage
2. **Chat**: User Query → Search → Context Building → AI Response
3. **Search**: Query → ChromaDB Search → Formatted Results

## Technical Details

- **Text Processing**: MVP functionality with basic cleaning and chunking
- **Rate Limiting**: Built-in delays to respect Discord API limits
- **Pagination**: Handles multiple pages of message history
- **Error Handling**: Comprehensive error handling and logging
- **Local Storage**: ChromaDB for local vector storage

## Limitations

- Text-only content (no attachments, embeds, reactions)
- Single-server focus
- Local storage only
- Requires "Manage Messages" permission for indexing

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure `DISCORD_TOKEN` and `OPENAI_API_KEY` are set

2. **Invalid Discord Token**
   - Run `python test_setup.py` to validate your token
   - Check that your token is correct and not expired
   - Ensure the token is from a Discord bot application (not a user token)

3. **Permission Errors**
   - Bot needs "Manage Messages" permission for indexing commands

4. **Rate Limiting**
   - Bot includes built-in delays to respect Discord API limits

5. **Storage Issues**
   - Ensure write permissions for the `./data` directory

### Debugging

The bot now provides detailed error logging to help diagnose issues:

#### Test Setup Script
Run the test setup script to validate your configuration:
```bash
python test_setup.py
```

This will check:
- Environment variables
- Discord token format and validity
- Required dependencies
- Configuration files

#### Enhanced Error Logging
The bot now provides detailed error information including:
- Token validation and format checking
- Environment variable status
- Discord API error details
- Configuration loading issues

#### Common Token Issues
- **"Improper token has been passed"**: Usually means the token is invalid, expired, or malformed
- **Token too short/long**: Discord tokens are typically ~59 characters
- **Missing dots**: Discord tokens usually contain dots (.)
- **Wrong token type**: Make sure you're using a bot token, not a user token

### Logs

The bot provides detailed logging. Check console output for:
- Indexing progress
- Error messages with detailed context
- API rate limiting
- Storage operations
- Token validation results

## Development

### Project Structure

```
discord_knowledge_bot/
├── bot/
│   ├── main.py
│   └── commands/
├── indexing/
│   ├── collector.py
│   ├── processor.py
│   └── storage.py
├── chat/
│   ├── ai_interface.py
│   └── context_builder.py
├── utils/
│   ├── config.py
│   └── helpers.py
├── main.py
├── config.yaml
├── requirements.txt
└── README.md
```

### Adding Features

1. **New Commands**: Add to appropriate cog in `bot/commands/`
2. **New Processing**: Extend `indexing/processor.py`
3. **New Storage**: Extend `indexing/storage.py`
4. **New AI Features**: Extend `chat/ai_interface.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 