# 🎯 MCP Data Visualization Server

Transform natural language into beautiful, interactive data visualizations using Claude Desktop with **DuckDB** and **Databricks** support - one-command installation!

## ✨ Features

- 🚀 **One-Command Installation** - `pip install mcp-visualization-duckdb`
- 🔧 **Automatic Configuration** - Automatically sets up Claude Desktop
- 🗣️ **Natural Language Interface** - Chat with Claude to create visualizations
- 📊 **Interactive Charts** - Plotly-powered HTML widgets
- 🏢 **Databricks Integration** - Connect to Databricks SQL warehouses with secure credential management
- 🗃️ **DuckDB Support** - Local database with CSV import and interactive browser
- 🔄 **Multi-Database** - Seamlessly switch between DuckDB and Databricks
- 🧠 **Rule-Based Analysis** - Smart chart suggestions without external LLM dependencies
- 📈 **Multiple Chart Types** - Bar, line, scatter, pie, histogram, box plots, heatmaps, and area charts
- 🔍 **Smart Insights** - Automatic statistical analysis and pattern detection
- 🛡️ **Security First** - SQL injection protection, encrypted credential storage
- ⚡ **No External Dependencies** - Works entirely offline with Claude Desktop

## 🚀 Quick Installation

### Option A: DuckDB (Local Database)

```bash
# 1. Install the package (includes DuckDB and all dependencies)
pip install mcp-visualization-duckdb

# 2. Configure Claude Desktop automatically
mcp-viz configure

# 3. Restart Claude Desktop and start chatting!
```

That's it! No manual configuration needed.

> **Note**: DuckDB and all other dependencies are automatically installed with the package. No separate database installation required!

### Option B: Databricks (Enterprise Data Warehouse)

```bash
# 1. Install the package
pip install mcp-visualization-duckdb

# 2. Configure Databricks credentials (secure, interactive setup)
mcp-viz databricks configure

# 3. Configure Claude Desktop (auto-detects Databricks)
mcp-viz configure

# 4. Restart Claude Desktop and start chatting!
```

**For Databricks, you'll need:**
- Databricks workspace hostname (e.g., `your-company.cloud.databricks.com`)
- SQL warehouse HTTP path (e.g., `/sql/1.0/warehouses/abc123`)
- Personal access token (generated in Databricks User Settings > Developer > Access Tokens)

> **🔒 Security**: Credentials are stored securely using your system keyring or encrypted files. Tokens are never stored in plain text or command history.

### What the installer does automatically:

- ✅ **Detects your platform** (Windows/Mac/Linux)
- ✅ **Finds Claude Desktop config** automatically
- ✅ **Auto-detects database type** (DuckDB or Databricks)
- ✅ **Sets up database** with sample data (DuckDB)
- ✅ **Securely stores credentials** (Databricks)
- ✅ **Configures paths** correctly
- ✅ **Creates backups** of existing config
- ✅ **Validates setup** to ensure it works

### 🚀 **After Installation**

Once installed, you'll see detailed instructions with:
- Next steps for your chosen database type
- Quick start commands
- Sample database links
- Example queries to try

Run `mcp-viz-setup` anytime to see the post-installation guide again!

## 🔄 **Ongoing Usage (After Setup)**

### **✅ One-Time Setup Only**
```bash
# Run these commands ONCE:
mcp-viz databricks configure  # First time Databricks setup
mcp-viz configure             # Configure Claude Desktop  
# Restart Claude Desktop
```

### **📋 Daily Usage - No Reconfiguration Needed**
```bash
# Just open Claude Desktop and start chatting:
"What Databricks catalogs are available?"
"List tables in the sales catalog" 
"Create a chart of revenue by region"
```

### **🔍 Check Status Anytime**
```bash
mcp-viz databricks status    # Shows if credentials exist
mcp-viz databricks test      # Test connection and browse catalogs
mcp-viz status              # Shows MCP server configuration
```

### **🔄 When You Need to Reconfigure**
- ❌ **Token expires** (personal access tokens can have expiration dates)
- ❌ **Change workspaces** (different Databricks instance)  
- ❌ **Change SQL warehouses** (different HTTP path)
- ❌ **Credential issues** (run `mcp-viz databricks remove` then reconfigure)

### **💾 Secure Credential Storage**
- 🔒 **Encrypted on disk** or in system keyring
- 🔄 **Automatically loaded** when Claude Desktop starts
- ⚡ **No repeated authentication** needed

> **📝 Note**: After initial setup, you should be able to use Claude Desktop normally without any additional configuration steps!

## 🎮 Usage with Claude Desktop

After installation, simply chat with Claude using natural language:

### Data Analysis
- **"What tables are available?"** - List database tables
- **"What Databricks catalogs are available?"** - Browse Databricks catalogs 
- **"Show me schemas in the sales catalog"** - List schemas
- **"Analyze the sales table"** - Get table information
- **"Show me the top 10 products by revenue"** - Query data

### Creating Visualizations  
- **"Create a bar chart of sales by region"** - Generate charts
- **"Show me the correlation between price and quantity"** - Scatter plots
- **"Make a pie chart of customer segments"** - Category breakdowns
- **"Visualize sales trends over time"** - Time series analysis

### Database Management

**DuckDB:**
- **"Browse databases in my Downloads folder"** - Interactive database browser
- **"Connect to C:/path/to/mydata.duckdb"** - Switch databases
- **"Load CSV from Downloads/sales.csv as table 'sales'"** - Import data

**Databricks:**
- **"Switch to the marketing catalog"** - Navigate catalogs
- **"List schemas in the sales catalog"** - Browse schemas
- **"What database am I connected to?"** - Connection info

## 🔧 CLI Commands

The package includes a powerful CLI:

```bash
# Configuration
mcp-viz configure              # Interactive setup (auto-detects database type)
mcp-viz configure --auto       # Automatic setup with defaults
mcp-viz status                 # Check configuration status

# Management  
mcp-viz test                   # Test server functionality
mcp-viz remove                 # Remove server from Claude Desktop

# DuckDB Database
mcp-viz create-db              # Create sample database
mcp-viz create-db --path ./my-data.duckdb  # Create at specific path

# Databricks Integration
mcp-viz databricks configure   # Setup Databricks credentials (interactive)
mcp-viz databricks status      # Check Databricks connection status
mcp-viz databricks test        # Test connection and browse catalogs
mcp-viz databricks remove      # Remove stored credentials
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

### 🎯 **Built-in Sample Data**
The package automatically creates sample data including:

- **Sales Data** - 365 days of sales across regions and products
- **Customer Data** - 1000 customer records with demographics  
- **Product Data** - 100 products with categories and pricing

### 🌟 **Additional Sample Databases**
Want more data to explore? Check out these high-quality sample databases:

**[TimeStored Sample DuckDB Databases](https://www.timestored.com/data/sample/duckdb)**

Available datasets include:
- **Financial Data** - Stock prices, trading data, market analysis
- **NYC Taxi** - Real NYC taxi trip records with geospatial data
- **TPC-H Benchmark** - Standard database performance testing data
- **E-commerce** - Product catalogs, orders, customer behavior
- **IoT Sensor Data** - Time-series sensor readings and telemetry

Simply download any `.duckdb` file and load it:
```bash
# Download a sample database, then:
"Load database from Downloads/nyc-taxi.duckdb"
"What tables are available in this database?"
"Create a heatmap of taxi pickups by hour and day"
```

Perfect for testing, learning, and demonstrating data visualization capabilities!

## 🏗️ Development Setup

For developers who want to contribute:

```bash
# Clone repository
git clone https://github.com/your-github-username/mcp-visualization-duckdb.git
cd mcp-visualization-duckdb

# Install in development mode
pip install -e .

# Configure for development
mcp-viz configure

# Run tests
python test_package.py
```

See [Development Guide](docs/DEVELOPMENT.md) for detailed instructions.

## ❓ Frequently Asked Questions

### **Q: Do I need to run `mcp-viz databricks configure` every time?**
**A: No!** You only run it once during initial setup. After that:
- ✅ Credentials are stored securely and auto-loaded
- ✅ Just open Claude Desktop and start chatting
- ✅ No repeated authentication needed

### **Q: How do I know if my Databricks is still connected?**
**A:** Check anytime with:
```bash
mcp-viz databricks status    # Shows connection status
mcp-viz databricks test      # Tests connection and shows catalogs
```

### **Q: When do I need to reconfigure?**
**A:** Only when:
- Your access token expires
- You change Databricks workspaces
- You switch to a different SQL warehouse
- Credentials get corrupted (rare)

### **Q: Are my credentials safe?**
**A:** Yes! Credentials are:
- 🔒 Encrypted on disk or stored in system keyring
- 🚫 Never stored in plain text or command history
- ⚡ Automatically loaded when needed

### **Q: Can I use both DuckDB and Databricks?**
**A:** Yes! The server auto-detects which database type to use:
- Configure Databricks: `mcp-viz databricks configure`
- Configure DuckDB: `mcp-viz configure`
- Server automatically uses the appropriate one

## 📦 Package Information

- **PyPI**: https://pypi.org/project/mcp-visualization-duckdb/
- **Repository**: https://github.com/your-github-username/mcp-visualization-duckdb
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