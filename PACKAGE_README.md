# 🎯 MCP Data Visualization Server - Pip Package

Transform natural language into beautiful data visualizations using Claude Desktop and DuckDB with one-command installation!

## ✨ Key Features

- **🚀 One-Command Installation**: `pip install mcp-visualization-duckdb`
- **🔧 Automatic Configuration**: Automatically configures Claude Desktop 
- **💬 Natural Language Interface**: Chat with Claude to create visualizations
- **📊 Interactive Charts**: Plotly-powered HTML widgets
- **🗃️ DuckDB Integration**: Fast analytical database
- **⚡ No External Dependencies**: Works entirely offline with Claude Desktop

## 🚀 Quick Installation

### Method 1: Pip Install (Recommended)

```bash
# Install the package
pip install mcp-visualization-duckdb

# Configure Claude Desktop automatically
mcp-viz configure

# Restart Claude Desktop and start chatting!
```

### Method 2: Interactive Setup

```bash
pip install mcp-visualization-duckdb
mcp-viz configure

# Follow the interactive prompts to customize your setup
```

### Method 3: Automatic Setup

```bash
pip install mcp-visualization-duckdb
mcp-viz configure --auto

# Uses default settings without prompts
```

## 🔧 CLI Commands

Once installed, you have access to the `mcp-viz` command:

```bash
# Configuration
mcp-viz configure              # Interactive setup
mcp-viz configure --auto       # Automatic setup with defaults
mcp-viz configure --force      # Update existing configuration

# Management  
mcp-viz status                 # Check configuration status
mcp-viz test                   # Test server functionality
mcp-viz list-servers          # List configured MCP servers
mcp-viz remove                # Remove server from Claude Desktop

# Database
mcp-viz create-db             # Create sample database
mcp-viz create-db --path ./my-data.duckdb  # Create at specific path
```

## 🎮 Usage with Claude Desktop

After installation and configuration, simply chat with Claude:

### Data Analysis
- **"What tables are available?"** - List database tables
- **"Analyze the sales table"** - Get table information
- **"Show me the top 10 products by revenue"** - Query data

### Creating Visualizations  
- **"Create a bar chart of sales by region"** - Generate charts
- **"Show me the correlation between price and quantity"** - Scatter plots
- **"Make a pie chart of customer segments"** - Category breakdowns
- **"Visualize sales trends over time"** - Time series analysis

## 📋 What the Installation Does

The `mcp-viz configure` command automatically:

1. **🔍 Detects Your Platform**: Finds Claude Desktop config on Windows/Mac/Linux
2. **📁 Creates Directories**: Sets up database and config directories
3. **⚙️ Configures Claude Desktop**: Adds MCP server to your config
4. **🗃️ Sets Up Database**: Creates default database with sample data
5. **✅ Validates Setup**: Tests that everything works correctly

## 🖥️ Cross-Platform Configuration

The package automatically detects and configures the correct Claude Desktop config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## 📊 Configuration Example

After running `mcp-viz configure`, your Claude Desktop config will include:

```json
{
  "mcpServers": {
    "data-viz-server": {
      "command": "/path/to/your/python",
      "args": ["-m", "mcp_visualization.server"],
      "cwd": "/path/to/package",
      "env": {
        "DUCKDB_DATABASE_PATH": "/home/user/.mcp-visualization/data.duckdb"
      }
    }
  }
}
```

## 🔍 Troubleshooting

### "Server not found" in Claude Desktop

```bash
# Check configuration status
mcp-viz status

# Test server functionality  
mcp-viz test

# Reconfigure if needed
mcp-viz configure --force
```

### "Unknown tool" errors

```bash
# Verify server is properly configured
mcp-viz status

# Check if Claude Desktop config is valid
cat ~/.config/claude/claude_desktop_config.json  # Linux
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json  # Mac
```

### Permission issues

```bash
# On Linux/Mac, ensure config directory exists
mkdir -p ~/.config/claude  # Linux
mkdir -p ~/Library/Application\ Support/Claude  # Mac

# Re-run configuration
mcp-viz configure
```

## 🎯 Example Installation Session

```bash
$ pip install mcp-visualization-duckdb
Successfully installed mcp-visualization-duckdb-0.1.0

$ mcp-viz configure
🎯 MCP Data Visualization Server
🔧 Setting up Claude Desktop integration...

📋 Current Configuration Status:
┌──────────────────┬────────────────────────────────────────┐
│ Setting          │ Value                                  │
├──────────────────┼────────────────────────────────────────┤
│ Platform         │ Linux                                  │
│ Config Path      │ /home/user/.config/claude/...         │
│ Config Exists    │ ✅ Yes                                 │
│ Config Valid     │ ✅ Yes                                 │
│ Existing Servers │ None                                   │
└──────────────────┴────────────────────────────────────────┘

📁 Configuration Options:
Database path [/home/user/.mcp-visualization/data.duckdb]: 
Python executable [/home/user/.venv/bin/python]:

📝 Configuration Preview:
┌──────────────┬──────────────────────────────────────────┐
│ Setting      │ Value                                    │
├──────────────┼──────────────────────────────────────────┤
│ Server Name  │ data-viz-server                          │
│ Database     │ /home/user/.mcp-visualization/data.duckdb│
│ Python Path  │ /home/user/.venv/bin/python              │
│ Config File  │ /home/user/.config/claude/...            │
└──────────────┴──────────────────────────────────────────┘

Proceed with configuration? [Y/n]: Y

🚀 Applying configuration...
✅ Successfully configured 'data-viz-server' for Claude Desktop

🔄 Next steps:
   1. Restart Claude Desktop completely
   2. Open a new conversation  
   3. Try: 'What MCP servers are available?'
   4. Try: 'List available tables'

ℹ️ Your MCP Data Visualization Server is ready! 🎉
```

## 🛠️ Development Installation

For development or contributing:

```bash
# Clone repository
git clone https://github.com/your-username/mcp-visualization-duckdb.git
cd mcp-visualization-duckdb

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Configure for development
mcp-viz configure --python-path $(which python)
```

## 📦 PyPI Package Information

- **Package Name**: `mcp-visualization-duckdb`
- **PyPI URL**: `https://pypi.org/project/mcp-visualization-duckdb/`
- **Source Code**: `https://github.com/your-username/mcp-visualization-duckdb`
- **Documentation**: Available in README and package docstrings

## 🤝 Contributing

We welcome contributions! The package is structured for easy development:

```
mcp-visualization-duckdb/
├── mcp_visualization/        # Main package
│   ├── cli.py               # Command-line interface  
│   ├── claude_config.py     # Claude Desktop integration
│   ├── server.py            # MCP server entry point
│   ├── mcp_server/          # MCP protocol implementation
│   ├── database/            # Database management
│   ├── visualization/       # Chart generation
│   └── config/              # Configuration management
├── pyproject.toml           # Package configuration
└── README.md                # Documentation
```

---

**Ready to transform your data analysis with Claude Desktop?** 

```bash
pip install mcp-visualization-duckdb && mcp-viz configure
```

🎉 **That's it!** Start chatting with Claude about your data!