#!/bin/bash

# Create directories in current directory
mkdir -p {code,code/config,code/database,code/llm,code/visualization,code/mcp_server,code/utils}
mkdir -p {data,data/samples,data/database}
mkdir -p {tests,scripts,docs}

# Create files with basic content
touch code/{__init__.py,main.py}
echo "# Main entry point for the MCP Data Viz Server" > code/main.py

touch code/config/{__init__.py,settings.py,config.yaml}
echo "# Configuration settings" > code/config/settings.py
echo "# Configuration file" > code/config/config.yaml

touch code/database/{__init__.py,manager.py,queries.py}
echo "# Database management operations" > code/database/manager.py
echo "# Database queries" > code/database/queries.py

touch code/llm/{__init__.py,ollama_client.py,prompts.py}
echo "# Ollama LLM client integration" > code/llm/ollama_client.py
echo "# LLM prompts" > code/llm/prompts.py

touch code/visualization/{__init__.py,chart_generator.py,chart_types.py,insights.py}
echo "# Chart generation logic" > code/visualization/chart_generator.py
echo "# Chart type definitions" > code/visualization/chart_types.py
echo "# Data visualization insights" > code/visualization/insights.py

touch code/mcp_server/{__init__.py,server.py,tools.py,handlers.py}
echo "# MCP server implementation" > code/mcp_server/server.py
echo "# Server tools and utilities" > code/mcp_server/tools.py
echo "# Request handlers" > code/mcp_server/handlers.py

touch code/utils/{__init__.py,logger.py,validators.py}
echo "# Logging utilities" > code/utils/logger.py
echo "# Data validation utilities" > code/utils/validators.py

touch data/samples/{sales_data.csv,customers.csv,products.csv}
echo "id,date,amount" > data/samples/sales_data.csv
echo "id,name,email" > data/samples/customers.csv
echo "id,name,price" > data/samples/products.csv

touch data/database/.gitkeep

touch tests/{__init__.py,test_database.py,test_visualization.py,test_llm.py}
echo "# Database tests" > tests/test_database.py
echo "# Visualization tests" > tests/test_visualization.py
echo "# LLM integration tests" > tests/test_llm.py

touch scripts/{setup_environment.py,install_ollama.sh,load_sample_data.py}
echo "# Environment setup script" > scripts/setup_environment.py
echo "#!/bin/bash\n# Ollama installation script" > scripts/install_ollama.sh
echo "# Sample data loading script" > scripts/load_sample_data.py

touch docs/{setup.md,usage.md,api.md}
echo "# Setup Instructions" > docs/setup.md
echo "# Usage Guide" > docs/usage.md
echo "# API Documentation" > docs/api.md

touch .env.example
echo "# Environment variables template" > .env.example

touch .gitignore
echo ".venv/\n*.pyc\n__pycache__/\n.env" > .gitignore

touch requirements.txt
echo "# Python dependencies" > requirements.txt

touch README.md
echo "# MCP Data Viz Server" > README.md

touch pyproject.toml
echo "# Project configuration" > pyproject.toml

# Set executable permissions for shell script
chmod +x scripts/install_ollama.sh

echo "Project structure created successfully!"