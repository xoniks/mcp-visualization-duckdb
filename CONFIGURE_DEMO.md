# 🔧 `mcp-viz configure` Interactive Demo

## What happens when you run `mcp-viz configure`

Here's the complete interactive experience users get:

```bash
$ mcp-viz configure
```

## 🎨 Interactive Setup Flow

### Step 1: Welcome & Status Check
```
🎯 MCP Data Visualization Server
Transform natural language into beautiful charts with Claude Desktop

🔧 Setting up Claude Desktop integration...

📋 Current Configuration Status:
┌──────────────────┬────────────────────────────────────────┐
│ Setting          │ Value                                  │
├──────────────────┼────────────────────────────────────────┤
│ Platform         │ Windows                                │
│ Config Path      │ C:\Users\YourName\AppData\Roaming\... │
│ Config Exists    │ ✅ Yes                                 │
│ Config Valid     │ ✅ Yes                                 │
│ Existing Servers │ None                                   │
└──────────────────┴────────────────────────────────────────┘
```

### Step 2: Database Location Selection
```
📁 Configuration Options:

💾 Database Location Options:
   1. C:\Users\YourName\.mcp-visualization\data.duckdb ✅ (recommended)
   2. C:\Users\YourName\Documents\mcp-viz.duckdb
   3. C:\Users\YourName\Desktop\data.duckdb
   4. C:\Github\mcp-visualization-duckdb\data.duckdb
   5. Custom path

Choose database location [1]: 1
```

### Step 3: Python Path Detection
```
Python executable [C:\Github\mcp-visualization-duckdb\.venv\Scripts\python.exe]: 
(Press Enter to use detected path, or type custom path)
```

### Step 4: Configuration Preview
```
📝 Configuration Preview:
┌──────────────┬──────────────────────────────────────────────────────┐
│ Setting      │ Value                                                │
├──────────────┼──────────────────────────────────────────────────────┤
│ Server Name  │ data-viz-server                                      │
│ Database     │ C:\Users\YourName\.mcp-visualization\data.duckdb     │
│ Python Path  │ C:\Github\mcp-visualization-duckdb\.venv\Scripts\... │
│ Config File  │ C:\Users\YourName\AppData\Roaming\Claude\...        │
└──────────────┴──────────────────────────────────────────────────────┘

Proceed with configuration? [Y/n]: Y
```

### Step 5: Automatic Setup
```
🚀 Applying configuration...
✅ Created directory: C:\Users\YourName\.mcp-visualization
✅ Created backup: claude_desktop_config.json.backup
✅ Successfully configured 'data-viz-server' for Claude Desktop
✅ Created sample database with 3 tables

🔄 Next steps:
   1. Restart Claude Desktop completely
   2. Open a new conversation
   3. Try: "What MCP servers are available?"
   4. Try: "List available tables"

ℹ️ Your MCP Data Visualization Server is ready! 🎉
```

## 🎯 What This Replaces

### Before (Manual Setup)
Users had to manually:
1. Find Claude Desktop config file location
2. Edit JSON configuration by hand
3. Figure out correct paths for their system
4. Set environment variables
5. Create database manually

### After (Interactive Setup)
The CLI automatically:
1. **Detects platform** (Windows/Mac/Linux)
2. **Finds Claude config** file location
3. **Suggests smart paths** based on platform
4. **Creates directories** as needed
5. **Backs up existing** configuration
6. **Validates setup** before finishing
7. **Creates sample data** for immediate use

## 🔧 CLI Options

### Quick Setup (No Prompts)
```bash
mcp-viz configure --auto
# Uses all defaults, perfect for scripts
```

### Force Reconfiguration
```bash
mcp-viz configure --force
# Updates existing configuration
```

### Custom Parameters
```bash
mcp-viz configure --database-path ./my-data.duckdb --python-path /usr/bin/python3
# Pre-specify options
```

## 🛠️ Other CLI Commands

### Check Status
```bash
$ mcp-viz status

📊 MCP Data Visualization Server Status

🖥️ Platform Information:
┌──────────────────┬────────────────────────────────────────┐
│ Setting          │ Value                                  │
├──────────────────┼────────────────────────────────────────┤
│ Operating System │ Windows                                │
│ Config Path      │ C:\Users\YourName\AppData\Roaming\... │
│ Config Directory │ ✅ Exists                             │
│ Config File      │ ✅ Exists                             │
└──────────────────┴────────────────────────────────────────┘

🔍 Configuration Validation:
✅ Configuration valid with 1 server(s)

🔧 Configured MCP Servers:
  1. data-viz-server

🧪 Server Import Test:
✅ Server code can be imported successfully
```

### Test Functionality
```bash
$ mcp-viz test

🧪 Testing MCP Data Visualization Server

Running: Import server module... ✅ PASS
Running: Claude Desktop config detection... ✅ PASS
Running: Database path creation... ✅ PASS

✅ All 3 tests passed! 🎉
```

### Create Sample Database
```bash
$ mcp-viz create-db

🗃️ Creating new database with sample data...
✅ Database created: C:\Users\YourName\.mcp-visualization\data.duckdb
ℹ️ Database includes sample tables: sales, customers, products
```

### Remove Configuration
```bash
$ mcp-viz remove

🗑️ Removing MCP server configuration...

Remove server 'data-viz-server' from Claude Desktop configuration? (y/N): y
✅ Successfully removed 'data-viz-server' from Claude Desktop
ℹ️ Please restart Claude Desktop to apply changes
```

## 🎨 Rich Terminal UI

The CLI uses the **Rich** library for beautiful terminal output:
- **Colored text** and emojis for better UX
- **Tables** for organized information display  
- **Progress indicators** during setup
- **Interactive prompts** with smart defaults
- **Error handling** with helpful suggestions

## 🔄 Complete User Flow

```bash
# 1. Install package
pip install mcp-visualization-duckdb

# 2. Run interactive setup
mcp-viz configure
# (Beautiful interactive prompts guide user through setup)

# 3. Restart Claude Desktop

# 4. Start chatting with Claude:
# "What tables are available?"
# "Create a bar chart of sales by region"
# "Show me customer demographics"
```

**That's it!** No manual configuration, no environment variables, no complex setup. The CLI handles everything automatically with a beautiful, user-friendly interface. 🎉