# 🎯 MCP Data Visualization Server

Transform natural language into beautiful, interactive data visualizations using Claude Desktop and DuckDB with **one-command installation**!

## ✨ Features

- 🚀 **One-Command Installation** - `pip install mcp-visualization-duckdb`
- 🔧 **Automatic Configuration** - Automatically sets up Claude Desktop
- 🗣️ **Natural Language Interface** - Chat with Claude to create visualizations
- 📊 **Interactive Charts** - Plotly-powered HTML widgets
- 🗃️ **Flexible Database Management** - Easy database switching with interactive browser
- 🧠 **Rule-Based Analysis** - Smart chart suggestions without external LLM dependencies
- 📈 **Multiple Chart Types** - Bar, line, scatter, pie, histogram, box plots, heatmaps, and area charts
- 🔍 **Smart Insights** - Automatic statistical analysis and pattern detection
- 🛡️ **Security First** - SQL injection protection and input validation
- ⚡ **No External Dependencies** - Works entirely offline with Claude Desktop

## 🚀 Quick Installation

### For End Users (Recommended)

```bash
# 1. Install the package
pip install mcp-visualization-duckdb

# 2. Configure Claude Desktop automatically
mcp-viz configure

# 3. Restart Claude Desktop and start chatting!
```

That's it! No manual configuration needed.

### What the installer does automatically:

- ✅ **Detects your platform** (Windows/Mac/Linux)
- ✅ **Finds Claude Desktop config** automatically
- ✅ **Sets up database** with sample data
- ✅ **Configures paths** correctly
- ✅ **Creates backups** of existing config
- ✅ **Validates setup** to ensure it works

## 🎮 Usage with Claude Desktop

After installation, simply chat with Claude using natural language:

### Data Analysis
- **"What tables are available?"** - List database tables
- **"Analyze the sales table"** - Get table information
- **"Show me the top 10 products by revenue"** - Query data

### Creating Visualizations  
- **"Create a bar chart of sales by region"** - Generate charts
- **"Show me the correlation between price and quantity"** - Scatter plots
- **"Make a pie chart of customer segments"** - Category breakdowns
- **"Visualize sales trends over time"** - Time series analysis

### Database Management
- **"Browse databases in my Downloads folder"** - Interactive database browser
- **"Connect to C:/path/to/mydata.duckdb"** - Switch databases
- **"Load CSV from Downloads/sales.csv as table 'sales'"** - Import data

## 🔧 CLI Commands

The package includes a powerful CLI:

```bash
# Configuration
mcp-viz configure              # Interactive setup
mcp-viz configure --auto       # Automatic setup with defaults
mcp-viz status                 # Check configuration status

# Management  
mcp-viz test                   # Test server functionality
mcp-viz remove                 # Remove server from Claude Desktop

# Database
mcp-viz create-db              # Create sample database
mcp-viz create-db --path ./my-data.duckdb  # Create at specific path
```

## 📊 Supported Chart Types

| Chart Type | Use Case | Example Request |
|------------|----------|-----------------|
| **Bar** | Compare categories | "Show sales by region" |
| **Line** | Show trends over time | "Plot revenue over months" |
| **Scatter** | Explore relationships | "Price vs quantity relationship" |
| **Pie** | Show proportions | "Customer segment breakdown" |
| **Histogram** | Analyze distributions | "Distribution of order values" |
| **Box** | Compare distributions | "Price ranges by category" |
| **Heatmap** | Show correlations | "Correlation matrix of metrics" |
| **Area** | Cumulative trends | "Cumulative sales over time" |

## 🛠️ Troubleshooting

### "Server not found" in Claude Desktop

```bash
# Check configuration status
mcp-viz status

# Reconfigure if needed
mcp-viz configure --force

# Restart Claude Desktop completely
```

### "Unknown tool" errors

```bash
# Test server functionality
mcp-viz test

# Check if all dependencies are installed
pip install --upgrade mcp-visualization-duckdb
```

### Database issues

```bash
# Create a fresh database with sample data
mcp-viz create-db

# Check current configuration
mcp-viz status
```

## 🔧 Advanced Configuration

### Custom Database Path

The installer will prompt you for a database location, or you can specify it:

```bash
# During configuration
mcp-viz configure
# Database path [/home/user/.mcp-visualization/data.duckdb]: /path/to/my/data.duckdb
```

### Multiple Databases

You can easily switch between databases using Claude Desktop:

- **"Browse databases in Documents folder"**
- **"Connect to /path/to/another/database.duckdb"**
- **"What database am I currently connected to?"**

## 💾 Sample Data

The package automatically creates sample data including:

- **Sales Data** - 365 days of sales across regions and products
- **Customer Data** - 1000 customer records with demographics
- **Product Data** - 100 products with categories and pricing

Perfect for testing and learning!

## 🏗️ Development Setup

For developers who want to contribute:

```bash
# Clone repository
git clone https://github.com/your-username/mcp-visualization-duckdb.git
cd mcp-visualization-duckdb

# Install in development mode
pip install -e .

# Configure for development
mcp-viz configure

# Run tests
python test_package.py
```

See [Development Guide](docs/DEVELOPMENT.md) for detailed instructions.

## 📦 Package Information

- **PyPI**: https://pypi.org/project/mcp-visualization-duckdb/
- **Repository**: https://github.com/your-username/mcp-visualization-duckdb
- **License**: MIT

## 🤝 Contributing

We welcome contributions! The package is structured for easy development:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_package.py`
5. Submit a pull request

## 🙏 Acknowledgments

- [Model Context Protocol](https://github.com/anthropics/mcp) by Anthropic
- [DuckDB](https://duckdb.org/) for fast analytical processing
- [Plotly](https://plotly.com/) for interactive visualizations
- [Claude Desktop](https://claude.ai/) for the amazing AI interface

---

**Ready to transform your data analysis with Claude Desktop?** 

```bash
pip install mcp-visualization-duckdb && mcp-viz configure
```

🎉 **That's it!** Start chatting with Claude about your data!