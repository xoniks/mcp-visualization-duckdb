# 🎯 MCP Data Visualization Server

Transform natural language into beautiful, interactive data visualizations using the Model Context Protocol (MCP) with Claude Desktop integration.

## ✨ Features

- 🗣️ **Natural Language Interface** - Chat with Claude to describe what you want to visualize
- 📊 **Interactive Charts** - Generate HTML widgets with Plotly for rich, interactive visualizations  
- 🗃️ **Flexible Database Management** - Easy database switching with interactive browser
- 🧠 **Local LLM** - Privacy-focused processing with Ollama integration
- 📈 **Multiple Chart Types** - Bar, line, scatter, pie, histogram, box plots, heatmaps, and area charts
- 🔍 **Smart Insights** - Automatic statistical analysis and pattern detection
- 🔧 **Modular Design** - Clean, extensible architecture with comprehensive configuration
- 🛡️ **Security First** - SQL injection protection and input validation
- 🎮 **Claude Desktop Integration** - Seamless experience through Claude's interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- [Claude Desktop](https://claude.ai/download) installed

### Installation

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd mcp-visualization-duckdb
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# Linux/Mac
source .venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install mcp duckdb pandas matplotlib seaborn plotly pydantic pydantic-settings pyyaml rich requests ollama numpy scikit-learn
```

3. **Install and start Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a lightweight model (in another terminal)
ollama pull qwen2:0.5b
```

4. **Configure Claude Desktop:**

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-viz-server": {
      "command": "C:/Github/mcp-visualization-duckdb/.venv/Scripts/python.exe",
      "args": ["C:/Github/mcp-visualization-duckdb/mcp_server.py"],
      "cwd": "C:/Github/mcp-visualization-duckdb",
      "env": {
        "DUCKDB_DATABASE_PATH": "C:/Github/mcp-visualization-duckdb/data/mcp.duckdb",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

5. **Create the launcher script:**
```bash
# Create mcp_server.py in your project root
cat > mcp_server.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("DUCKDB_DATABASE_PATH", str(project_root / "data" / "mcp.duckdb"))

async def main():
    try:
        from code.main import main as code_main
        return await code_main()
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
EOF
```

6. **Restart Claude Desktop** and start chatting!

## 🎮 Usage with Claude Desktop

Simply chat with Claude using natural language:

### Database Management
- **"What data tables are available?"** - List all tables
- **"Browse databases in my Downloads folder"** - Interactive database browser
- **"Connect to C:/path/to/mydata.duckdb"** - Switch databases
- **"Load CSV from Downloads/sales.csv as table 'sales'"** - Import data

### Data Analysis
- **"Analyze the sales table"** - Get detailed table information
- **"Show me the top 10 products by price"** - Query data
- **"What are the column statistics for sales_amount?"** - Statistical analysis

### Creating Visualizations
- **"Create a bar chart showing sales by region"** - Generate charts
- **"Show me the relationship between price and quantity"** - Scatter plots
- **"Make a pie chart of customer segments"** - Category breakdowns
- **"Visualize sales trends over time"** - Time series analysis

### Advanced Features
- **"Create a heatmap of correlations in the sales data"** - Correlation analysis
- **"Show me outliers in the pricing data"** - Outlier detection
- **"Compare sales performance across regions with insights"** - Statistical insights

## 📋 Available Tools

### Database Management 🗃️
- `change_database` - Connect to a different DuckDB database file
- `browse_databases` - Browse database files in a directory
- `browse_and_select_database` - Interactive browser with numbered selection
- `select_database_by_number` - Quick database selection by number
- `list_recent_databases` - Show database management options

### Data Management 📊
- `list_tables` - List all available database tables
- `analyze_table` - Get detailed table information and sample data
- `load_csv_data` - Import CSV files into the database
- `query_data` - Execute SQL queries with safety validation
- `get_column_stats` - Get statistical analysis for specific columns

### Visualization 📈
- `create_visualization` - Start creating a chart from natural language
- `configure_chart` - Configure chart parameters through guided questions
- `suggest_visualizations` - Get chart type recommendations for your data
- `validate_chart_config` - Validate column mappings for chart types

### Utilities 🔧
- `explain_chart_types` - Learn about available chart types and their uses
- `create_sample_chart` - Generate sample charts for testing
- `server_status` - Check server health and component status

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

## 🔍 Statistical Insights

Get automatic insights with any visualization:

- **Basic Stats**: max, min, mean, median, distinct_count, total_count
- **Advanced Analysis**: correlation, trend, outliers, distribution
- **Pattern Detection**: Automatically detect data patterns and relationships
- **Narrative Explanations**: Human-readable summaries of findings

## 💾 Database Switching Made Easy

### Interactive Database Browser
```
You: "Browse databases in Downloads folder"

Claude: 📁 Database Browser: C:/Users/You/Downloads/

🗃️ Available Databases:
1. sales_data.duckdb (2.3MB, modified: 2024-06-18 10:30)
2. customer_analysis.duckdb (5.1MB, modified: 2024-06-17 15:45)
3. inventory.duckdb (1.8MB, modified: 2024-06-16 09:20)

💡 To connect: Use select_database_by_number with a number (1-3)

You: "Select database number 2"

Claude: ✅ Successfully connected to database: C:/Users/You/Downloads/customer_analysis.duckdb
Available tables: customers, orders, products
```

### Quick Database Actions
- **In-Memory Database**: "Switch to in-memory database"
- **Specific Path**: "Connect to C:/data/myproject.duckdb"  
- **Browse Folders**: "Browse databases in Documents folder"
- **Current Status**: "What database am I currently connected to?"

## ⚙️ Configuration

The server uses a layered configuration system:

1. **Environment Variables** (recommended for database path)
2. **YAML Configuration** (`code/config/config.yaml`)
3. **Command Line Arguments**

### Key Environment Variables

```bash
export DUCKDB_DATABASE_PATH="C:/path/to/your/database.duckdb"
export OLLAMA_MODEL="qwen2:0.5b"
export DEBUG_MODE="true"
export LOG_LEVEL="INFO"
```

### Configuration Options

```yaml
# Database settings
database:
  path: "./data/mcp.duckdb"
  memory_limit: "1GB"
  threads: 4

# LLM settings  
llm:
  ollama:
    model: "qwen2:0.5b"
    base_url: "http://localhost:11434"
    timeout: 30

# Visualization settings
visualization:
  default_theme: "plotly_white"
  width: 800
  height: 600
```

## 🏗️ Architecture

```
mcp-visualization-duckdb/
├── mcp_server.py        # Main launcher for Claude Desktop
├── code/
│   ├── config/          # Configuration management
│   ├── database/        # DuckDB operations and queries  
│   ├── llm/             # Ollama client and prompts
│   ├── visualization/   # Chart generation and insights
│   ├── mcp_server/      # MCP protocol implementation
│   ├── utils/           # Logging and validation utilities
│   └── main.py          # Core entry point
├── data/                # Database files and sample data
│   ├── mcp.duckdb      # Default database
│   └── samples/        # Sample CSV files
└── README.md
```

## 🧪 Development & Testing

### Manual Testing
```bash
# Run the server directly for debugging
export DUCKDB_DATABASE_PATH="./data/mcp.duckdb"
python -m code.main
```

### Sample Data
The server automatically generates sample data on startup:
- **sales** table - 50 sales records with regions, products, dates
- **customers** table - 1000 customer records with demographics  
- **products** table - 100 products with categories and pricing

### Create Your Own Sample Data
Save this as `sample_data.csv` and load it:

```csv
name,age,city,salary,department
Alice,28,New York,75000,Engineering
Bob,35,San Francisco,85000,Sales
Carol,42,Chicago,65000,Marketing
```

Then: "Load CSV from Downloads/sample_data.csv as table 'employees'"

## 🛡️ Security Features

- **SQL Injection Protection** - Query validation and sanitization
- **Input Validation** - Comprehensive argument and data validation  
- **File Access Control** - Restricted file system access
- **Query Limits** - Configurable query size and execution limits
- **Local Processing** - All data stays on your machine
- **Environment Isolation** - Sandboxed execution environment

## 🔧 Troubleshooting

### Claude Desktop Connection Issues

**Server not appearing in Claude:**
1. Check the config file path and JSON syntax
2. Restart Claude Desktop completely
3. Verify the Python path and working directory
4. Check logs in Claude Desktop Developer Tools

**"Unknown tool" errors:**
```bash
# Check if server is running
python -m code.main

# Verify all imports work
python -c "from code.main import main; print('✅ Imports OK')"

# Test database connection
python -c "from code.database.manager import DatabaseManager; dm = DatabaseManager(); print(f'✅ DB OK: {dm.db_path}')"
```

### Common Issues

**Ollama Connection Failed:**
```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list

# Pull required model if missing
ollama pull qwen2:0.5b
```

**Database Lock Errors:**
```bash
# Kill any running Python processes
taskkill /F /IM python.exe  # Windows
pkill python                # Linux/Mac

# Or use a different database file
export DUCKDB_DATABASE_PATH="./data/new_database.duckdb"
```

**Import/Path Errors:**
1. Ensure you're in the correct directory
2. Check Python path in launcher script  
3. Verify all dependencies are installed
4. Use absolute paths in Claude Desktop config

### Debugging Tips

**Enable detailed logging:**
```bash
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
python -m code.main
```

**Test individual components:**
```bash
# Test database
python -c "from code.database.manager import DatabaseManager; print('DB ✅')"

# Test LLM  
python -c "from code.llm.ollama_client import OllamaClient; print('LLM ✅')"

# Test charts
python -c "from code.visualization.chart_generator import ChartGenerator; print('Charts ✅')"
```

## 📚 Examples and Use Cases

### Business Analytics
- Sales performance dashboards
- Customer segmentation analysis  
- Inventory management insights
- Regional performance comparisons

### Data Science
- Exploratory data analysis
- Statistical correlation studies
- Outlier detection and analysis
- Distribution visualizations

### Research
- Survey data analysis
- Experimental results visualization
- Publication-ready charts
- Statistical significance testing

## 🤝 Contributing

We welcome contributions! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `python -m pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/mcp-visualization-duckdb.git
cd mcp-visualization-duckdb

# Create development environment
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort mypy

# Run tests
pytest tests/

# Format code
black code/
isort code/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://github.com/anthropics/mcp) by Anthropic
- [DuckDB](https://duckdb.org/) for fast analytical processing
- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Plotly](https://plotly.com/) for interactive visualizations
- [Claude Desktop](https://claude.ai/) for the amazing AI interface

---

**Ready to transform your data into insights with Claude?** Set up the server and start chatting! 🚀💬

*"Show me a visualization of sales by region"* → Beautiful interactive charts  
*"What's the correlation between price and customer satisfaction?"* → Statistical insights  
*"Browse databases in my project folder"* → Easy database management  

The future of data analysis is conversational! 🎯