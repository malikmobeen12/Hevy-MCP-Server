# Hevy Trainer MCP Server

Have you ever wanted your own personal AI fitness coach that actually knows your workout history? Hevy Trainer is an MCP (Model Context Protocol) server that connects your AI assistant directly to your Hevy workout data. 

Instead of guessing what you lifted last week or trying to manually explain your current program to your AI assistant, this server feeds your actual Hevy CSV export straight into the AI. It can analyze your volume, track your strength progression, and even search the web for reliable form guides and hypertrophy research.

## Features

- **Local & Private Database**: Your `workouts.csv` is parsed into a local SQLite database on your machine. Your data never leaves your computer unless the AI needs to answer your specific question.
- **Premium Progress Visualizations**: The AI can instantly generate beautiful, sleek progress charts (powered by Seaborn) showing your 1RM or total volume progression over time.
- **Fitness Web Search**: Built-in integration with DuckDuckGo allows the AI to fetch the latest hypertrophy research or form guides when giving you advice, ensuring you get accurate, up-to-date information.
- **Few-Shot SQL Intelligence**: The server is pre-configured with complex SQL examples, meaning the AI knows exactly how to query your data without making mistakes.

## Prerequisites

- Python 3.10+
- An AI assistant that supports MCP (like Claude Desktop or the Antigravity IDE)
- A CSV export of your workout data from the Hevy app

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Hevy-Trainer.git
   cd Hevy-Trainer
   ```

2. **Install the dependencies:**
   We recommend using `uv` or `pip` to install the requirements.
   ```bash
   pip install .
   ```

3. **Add your data:**
   Export your workout data from the Hevy app (usually found in Settings > Export Data). Save the file as `workouts.csv` in the root directory of this project.

## Usage

You can run the server directly using FastMCP:

```bash
python src/hevy_trainer/server.py
```

### Adding to your AI Chat

This server works universally with any MCP-compatible client (including Claude Desktop, Cursor, Windsurf, LibreChat, Goose, and the Antigravity IDE). 

Most MCP clients allow you to configure servers via a JSON file (like `claude_desktop_config.json` or `mcp.json`) or directly within their settings UI. 

**Generic JSON Configuration:**
```json
{
  "mcpServers": {
    "hevy-trainer": {
      "command": "python",
      "args": [
        "/absolute/path/to/Hevy-Trainer/src/hevy_trainer/server.py"
      ]
    }
  }
}
```

*Note: If you use `uv` for python dependency management, you can replace `"command": "python"` with `"command": "uv", "args": ["run", "python", "/absolute/path/to/..."]`.*

Once connected, simply ask your AI:
- *"Act as my personal trainer. Based on my workout history, how is my bench press progressing?"*
- *"Can you chart my total volume for squats over the last 3 months?"*
- *"Search the web for the optimal hypertrophy rep range and tell me if my current program matches it."*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
