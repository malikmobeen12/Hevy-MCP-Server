from mcp.server.fastmcp import FastMCP
from hevy_trainer.database import HevyDatabase
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from pathlib import Path
from duckduckgo_search import DDGS

workspace_dir = Path(__file__).parent.parent.parent.resolve()
csv_path = workspace_dir / "workouts.csv"

db = HevyDatabase(csv_path)
if not db.load():
    print(f"Warning: Could not load {csv_path}", file=sys.stderr)

mcp = FastMCP("Hevy Personal Trainer")

# Set seaborn theme for premium charts
sns.set_theme(style="darkgrid")

@mcp.tool()
def get_database_schema() -> str:
    """Returns the DDL schema of the SQLite database containing workouts, exercises, and sets."""
    return db.get_schema()

@mcp.tool()
def query_workout_database(sql_query: str) -> str:
    """Execute a read-only SQL SELECT query against the workout database and return the rows.
    
    Args:
        sql_query: A valid SQLite SELECT query.
    """
    try:
        rows = db.query(sql_query)
        if not rows:
            return "No results found."
        
        # Format rows nicely
        output = []
        for row in rows:
            output.append(str(row))
        return "\n".join(output)
    except Exception as e:
        return f"SQL Error: {str(e)}"

@mcp.tool()
def generate_progress_chart(exercise_name: str, metric: str = "max_weight") -> str:
    """Generates a line chart for an exercise's progress over time and returns a viewable image.
    
    Args:
        exercise_name: The exact name of the exercise in the database (e.g. "Bench Press (Smith Machine)")
        metric: The metric to plot. Either "max_weight" or "total_volume".
    """
    if metric == "max_weight":
        sql = f'''
            SELECT w.start_time, MAX(s.weight_kg) as value
            FROM workouts w
            JOIN exercises e ON e.workout_id = w.id
            JOIN sets s ON s.exercise_id = e.id
            WHERE e.title = ?
            GROUP BY w.id
            ORDER BY w.id ASC
        '''
    else:
        sql = f'''
            SELECT w.start_time, SUM(s.weight_kg * s.reps) as value
            FROM workouts w
            JOIN exercises e ON e.workout_id = w.id
            JOIN sets s ON s.exercise_id = e.id
            WHERE e.title = ?
            GROUP BY w.id
            ORDER BY w.id ASC
        '''
        
    rows = db.query(sql, (exercise_name,))
    if not rows:
        return f"No data found to plot for {exercise_name}."
        
    dates = []
    values = []
    for row in rows:
        try:
            dt = datetime.datetime.strptime(row['start_time'], "%b %d, %Y, %I:%M %p")
            dates.append(dt)
            values.append(row['value'])
        except Exception:
            continue
            
    if not dates:
        return "Could not parse dates for charting."
        
    plt.figure(figsize=(10, 6), facecolor="#1e1e2e")
    ax = plt.gca()
    ax.set_facecolor("#1e1e2e")
    ax.tick_params(colors="#cdd6f4")
    ax.xaxis.label.set_color("#cdd6f4")
    ax.yaxis.label.set_color("#cdd6f4")
    ax.title.set_color("#cdd6f4")

    # Use a nice modern color for the line
    plt.plot(dates, values, marker='o', linestyle='-', color='#8caaee', linewidth=2, markersize=8)
    
    plt.title(f"{exercise_name} - {metric.replace('_', ' ').title()}", fontsize=14, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
    plt.grid(True, color="#313244", alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    charts_dir = workspace_dir / "charts"
    charts_dir.mkdir(exist_ok=True)
    
    chart_filename = f"chart_{exercise_name.replace(' ', '_').replace('(', '').replace(')', '')}.png"
    chart_path = charts_dir / chart_filename
    plt.savefig(chart_path, dpi=300, facecolor="#1e1e2e")
    plt.close()
    
    markdown_link = f"![{exercise_name} Progress Chart]({chart_path.as_posix()})"
    return f"Chart generated successfully at {chart_path}. You MUST display it to the user by outputting exactly this markdown: {markdown_link}"

@mcp.tool()
def search_fitness_guidance(query: str) -> str:
    """Searches the web for reliable workout, hypertrophy, and fitness guidance.
    
    Args:
        query: The topic or question to search for (e.g. 'proper squat form', 'hypertrophy rep ranges').
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No web results found."
        
        output = []
        for r in results:
            output.append(f"Title: {r.get('title')}\\nSnippet: {r.get('body')}\\nLink: {r.get('href')}\\n")
        return "\\n".join(output)
    except Exception as e:
        return f"Search failed: {str(e)}"

@mcp.prompt()
def personal_trainer() -> str:
    """A specialized prompt that instructs the agent to adopt the persona of an expert personal trainer."""
    return (
        "You are an expert personal trainer, highly knowledgeable in hypertrophy, strength training, "
        "and progressive overload. You have access to the user's Hevy workout history via your SQL MCP tools.\\n\\n"
        "Instructions:\\n"
        "1. Adopt a motivational, encouraging, but scientifically-grounded tone.\\n"
        "2. When the user asks for advice, ALWAYS use `get_database_schema` to understand the tables.\\n"
        "3. Write precise SQL queries using `query_workout_database` to analyze their volume, frequency, and strength.\\n"
        "4. Proactively use `generate_progress_chart` to show them a visual chart for their lifts.\\n"
        "5. Use `search_fitness_guidance` if you need to fetch external research or form guides.\\n\\n"
        "Few-Shot SQL Examples for Complex Queries:\\n"
        "- Total volume for an exercise across workouts:\\n"
        "  SELECT w.start_time, SUM(s.weight_kg * s.reps) as total_volume\\n"
        "  FROM workouts w JOIN exercises e ON e.workout_id = w.id JOIN sets s ON s.exercise_id = e.id\\n"
        "  WHERE e.title = 'Squat (Barbell)' GROUP BY w.id ORDER BY w.id ASC;\\n\\n"
        "- Finding the 1RM (Max Weight) progression over time:\\n"
        "  SELECT w.start_time, MAX(s.weight_kg) as max_weight\\n"
        "  FROM workouts w JOIN exercises e ON e.workout_id = w.id JOIN sets s ON s.exercise_id = e.id\\n"
        "  WHERE e.title = 'Deadlift (Barbell)' GROUP BY w.id ORDER BY w.id ASC;\\n"
    )

if __name__ == "__main__":
    mcp.run(transport='stdio')
