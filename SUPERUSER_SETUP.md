# Superuser Permission System

The Discord Knowledge Bot now supports a superuser permission system that allows maintainers to have full bot permissions regardless of their server role.

## Setup

1. **Get your Discord User ID**
   - Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
   - Right-click on your username and select "Copy ID"

2. **Add to Environment Variables**
   - Add your Discord ID to the `.env` file:
   ```
   SUPERUSER_DISCORD_ID=your_discord_user_id_here
   ```

## How It Works

- **Superusers** have access to all bot commands regardless of their server permissions
- **Regular users** still need appropriate server permissions (like Administrator) to use restricted commands
- The system is optional - if no `SUPERUSER_DISCORD_ID` is set, the bot operates normally

## Commands Available to Superusers

Superusers have access to all bot commands, including:

### Indexing Commands
- `/index-server` - Index all text channels in the server
- `/index-channel` - Index a specific channel
- `/reindex-server` - Clear and reindex all text channels
- `/reindex-channel` - Clear and reindex a specific channel

### Management Commands
- `/clear` - Clear all indexed data
- `/status` - Show bot and indexing status
- `/stats` - Show detailed statistics


### Chat Commands
- All chat functionality works normally for everyone

## Security Notes

- The superuser ID is stored in environment variables, not in the bot's code
- Only the Discord user ID specified will have superuser privileges
- The system is designed for maintainers and should be used sparingly
- Regular server administrators still need appropriate server permissions

## Testing

Run the test suite to verify the superuser system works correctly:

```bash
PYTHONPATH=. python3 test/test_superuser_permissions.py
``` 