# 🎯 MCP Data Visualization Server

Transform natural language into beautiful, interactive data visualizations using the Model Context Protocol (MCP).

## ✨ Features

- 🗣️ **Natural Language Interface** - Describe what you want to visualize in plain English
- 📊 **Interactive Charts** - Generate HTML widgets with Plotly for rich, interactive visualizations  
- 🗃️ **Local Database** - Fast analytics with DuckDB, no external dependencies
- 🧠 **Local LLM** - Privacy-focused processing with Ollama integration
- 📈 **Multiple Chart Types** - Bar, line, scatter, pie, histogram, box plots, heatmaps, and area charts
- 🔍 **Smart Insights** - Automatic statistical analysis and pattern detection
- 🔧 **Modular Design** - Clean, extensible architecture with comprehensive configuration
- 🛡️ **Security First** - SQL injection protection and input validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running

### Installation

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd mcp-data-viz-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install and start Ollama:**
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull codellama:7b
```

4. **Run the server:**
```bash
python code/main.py
```

The server will start with sample data loaded and be ready for MCP client connections.

## 🎮 Usage Examples

### Loading Data
```python
# Load CSV data
{
  "tool": "load_csv_data",
  "arguments": {
    "file_path": "./data/samples/sales_data.csv",
    "table_name": "sales"
  }
}
```

### Creating Visualizations

#### Step 1: Request a visualization
```python
{
  "tool": "create_visualization", 
  "arguments": {
    "request": "Show me sales trends over time by region",
    "table_name": "sales"
  }
}
```

#### Step 2: Configure the chart
```python
{
  "tool": "configure_chart",
  "arguments": {
    "request_id": "req_0",
    "x_axis": "date",
    "y_axis": "sales_amount", 
    "color": "region",
    "insights": "max, min, mean, trend"
  }
}
```

The server returns an interactive HTML widget with statistical insights!

## 📋 Available Tools

### Data Management
- `list_tables` - List all available database tables
- `analyze_table` - Get detailed table information and sample data
- `load_csv_data` - Import CSV files into the database
- `query_data` - Execute SQL queries with safety validation
- `get_column_stats` - Get statistical analysis for specific columns

### Visualization
- `create_visualization` - Start creating a chart from natural language
- `configure_chart` - Configure chart parameters through guided questions
- `suggest_visualizations` - Get chart type recommendations for your data
- `validate_chart_config` - Validate column mappings for chart types

### Utilities  
- `explain_chart_types` - Learn about available chart types and their uses
- `create_sample_chart` - Generate sample charts for testing
- `server_status` - Check server health and component status

## 📊 Supported Chart Types

| Chart Type | Use Case | Required Columns |
|------------|----------|------------------|
| **Bar** | Compare categories | x_axis (categorical), y_axis (numeric) |
| **Line** | Show trends over time | x_axis (temporal/numeric), y_axis (numeric) |
| **Scatter** | Explore relationships | x_axis (numeric), y_axis (numeric) |
| **Pie** | Show proportions | category (categorical), values (numeric) |
| **Histogram** | Analyze distributions | column (numeric) |
| **Box** | Compare distributions | column (numeric), groupby (optional) |
| **Heatmap** | Show correlations | x_axis, y_axis, values (optional) |
| **Area** | Cumulative trends | x_axis (temporal/numeric), y_axis (numeric) |

## 🔍 Statistical Insights

Request automatic insights with any visualization:

- **Basic Stats**: max, min, mean, median, distinct_count, total_count
- **Advanced Analysis**: correlation, trend, outliers, distribution
- **Pattern Detection**: Automatically detect data patterns and relationships
- **Narrative Explanations**: Human-readable summaries of findings

## ⚙️ Configuration

The server uses a layered configuration system:

1. **YAML Configuration** (`code/config/config.yaml`)
2. **Environment Variables** (`.env`)
3. **Command Line Arguments**

### Key Configuration Options

```yaml
# Database settings
database:
  path: "./data/database/main.db"
  memory_limit: "1GB"

# LLM settings  
llm:
  ollama:
    model: "codellama:7b"
    base_url: "http://localhost:11434"

# Visualization settings
visualization:
  default_theme: "plotly_white"
  width: 800
  height: 600
```

## 🏗️ Architecture

```
mcp-data-viz-server/
├── code/
│   ├── config/           # Configuration management
│   ├── database/         # DuckDB operations and queries  
│   ├── llm/             # Ollama client and prompts
│   ├── visualization/   # Chart generation and insights
│   ├── mcp_server/      # MCP protocol implementation
│   ├── utils/           # Logging and validation utilities
│   └── main.py          # Entry point
├── data/                # Sample data and database files
├── tests/               # Test suite
└── docs/                # Documentation
```

## 🧪 Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black code/
isort code/  
mypy code/
```

### Sample Data Generation
```bash
python code/main.py  # Generates sample data automatically
```

### Create Test Charts
```bash
python code/main.py sample  # Creates sample_chart.html
```

## 🛡️ Security Features

- **SQL Injection Protection** - Query validation and sanitization
- **Input Validation** - Comprehensive argument and data validation  
- **File Access Control** - Restricted file system access
- **Query Limits** - Configurable query size and execution limits
- **Local Processing** - No data leaves your machine

## 🔧 Troubleshooting

### Common Issues

**Ollama Connection Failed:**
```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list

# Pull required model if missing
ollama pull codellama:7b
```

**Import Errors:**
```bash
# Install all dependencies
pip install -r requirements.txt

# For development features
pip install -r requirements.txt[dev]
```

**Database Issues:**
- Check file permissions in `./data/database/`
- Verify CSV file paths are correct
- Use `server_status` tool to check database connection

## 📚 Examples and Tutorials

Check out the `/docs` folder for:
- Detailed API documentation
- Advanced usage examples  
- Integration guides
- Custom chart type development

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://github.com/anthropics/mcp) by Anthropic
- [DuckDB](https://duckdb.org/) for fast analytical processing
- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Plotly](https://plotly.com/) for interactive visualizations

---

**Ready to transform your data into insights?** Start the server and begin visualizing! 🚀