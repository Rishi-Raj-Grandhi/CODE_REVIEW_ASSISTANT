import os
import io
import zipfile
import tempfile
import json
import shutil
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

# ---------------- LangChain Model ---------------- #

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=openai_api_key
)

# ---------------- Enhanced File Configuration ---------------- #

COMPREHENSIVE_REVIEWABLE_EXTS = {
    # Frontend
    ".jsx", ".tsx", ".js", ".ts", ".mjs", ".mts",
    ".vue", ".svelte",
    ".css", ".scss", ".sass", ".less",
    ".html", ".htm", ".xml",
    
    # Backend
    ".py", ".java", ".cpp", ".c", ".h", ".hpp",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt",
    ".cs", ".scala", ".clj", ".groovy",
    
    # Config & Data
    ".json", ".yaml", ".yml", ".toml", ".env",
    ".dockerfile", ".sql",
    
    # Markup
    ".md", ".mdx", ".rst",
}

IGNORE_DIRS = {
    "node_modules", "__pycache__", ".git", ".venv",
    "venv", ".env", "dist", "build", "out",
    ".next", ".nuxt", ".cache", "coverage",
    ".idea", ".vscode", "target", "bin", "obj"
}

IGNORE_FILES = {
    ".gitignore", ".env.example", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", ".DS_Store"
}

# Priority files that should be reviewed first
PRIORITY_FILES = {
    "app.jsx", "app.tsx", "index.jsx", "index.tsx",
    "main.py", "main.js", "app.py", "server.py",
    "config.py", "package.json", "requirements.txt",
    "dockerfile", "docker-compose.yml"
}

# ---------------- Graph State ---------------- #

class ReviewState(dict):
    code: str
    filename: str
    file_path: str
    result: dict

# ---------------- Enhanced LLM Node with Comprehensive Analysis ---------------- #

def analyze_code_node(state: ReviewState) -> ReviewState:
    """Enhanced LangChain-based code review node."""
    code = state["code"]
    filename = state["filename"]
    file_path = state.get("file_path", filename)

    # Determine file type for context
    _, ext = os.path.splitext(filename)
    
    prompt = f"""
You are a professional code reviewer. Review the following file: `{file_path}` (extension: {ext})

Provide ONLY valid JSON with this EXACT structure:
{{
  "filename": "{filename}",
  "file_path": "{file_path}",
  "file_type": "{ext}",
  "issues": [
      {{
          "line_range": [start, end],
          "type": "Bug Risk" | "Code Smell" | "Style" | "Security" | "Performance" | "Best Practice",
          "severity": "Minor" | "Major" | "Critical",
          "message": "Clear description of the issue",
          "recommendation": "Specific fix or improvement",
          "code_example": "Optional: show corrected code"
      }}
  ],
  "improvements": [
      {{
          "title": "Improvement title",
          "description": "What could be better",
          "impact": "Code quality improvement",
          "suggestion": "How to implement"
      }}
  ],
  "feedback": {{
      "strengths": ["List of good practices observed"],
      "weaknesses": ["Areas for improvement"],
      "best_practices_found": ["Best practices already in use"],
      "best_practices_missing": ["Industry best practices not found"]
  }},
  "file_score": {{
      "maintainability": 0-100,
      "readability": 0-100,
      "robustness": 0-100,
      "security": 0-100,
      "performance": 0-100,
      "best_practices": 0-100,
      "overall": 0-100
  }}
}}

IMPORTANT: 
- Be thorough and specific
- Include actual line numbers when possible
- Provide actionable recommendations
- Consider industry standards for {ext} files
- Flag security issues immediately
- Include performance optimization tips

Code to review:
```{ext}
{code[:8000]}
```
{"[... code truncated due to length ...]" if len(code) > 8000 else ""}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError as e:
        result = {
            "filename": filename,
            "file_path": file_path,
            "file_type": ext,
            "issues": [{"line_range": [0, 0], "type": "Code Smell", "severity": "Minor",
                       "message": "Could not parse response", "recommendation": "Manual review needed"}],
            "improvements": [],
            "feedback": {"strengths": [], "weaknesses": [], "best_practices_found": [], "best_practices_missing": []},
            "file_score": {"maintainability": 75, "readability": 75, "robustness": 75,
                          "security": 75, "performance": 75, "best_practices": 75, "overall": 75}
        }

    state["result"] = result
    return state

# ---------------- Graph Construction ---------------- #

graph = StateGraph(ReviewState)
graph.add_node("analyze_code", analyze_code_node)
graph.set_entry_point("analyze_code")
graph.set_finish_point("analyze_code")
review_graph = graph.compile()

# ---------------- Enhanced Helper Functions ---------------- #

def filter_reviewable_files(temp_dir: str) -> List[tuple]:
    """Filter and prioritize reviewable files."""
    reviewable_files = []

    for root, dirs, files in os.walk(temp_dir):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            # Skip ignored files
            if file in IGNORE_FILES:
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in COMPREHENSIVE_REVIEWABLE_EXTS or ext == "":
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, temp_dir)
                reviewable_files.append((full_path, relative_path, file))

    # Sort by priority (priority files first, then by path)
    reviewable_files.sort(
        key=lambda x: (
            x[2] not in PRIORITY_FILES,  # Priority files first (False < True)
            x[1]  # Then alphabetically by relative path
        )
    )
    
    return reviewable_files


def process_files(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process individual files."""
    results = []
    for file in files:
        file_name = file["filename"]
        code = file["content"].decode(errors="ignore")
        state = {
            "filename": file_name,
            "file_path": file.get("file_path", file_name),
            "code": code
        }
        review_result = review_graph.invoke(state)["result"]
        results.append(review_result)
    return aggregate_results(results)


def process_folder(zip_bytes: bytes) -> Dict[str, Any]:
    """Enhanced folder processing with better file detection."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract zip
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
            z.extractall(temp_dir)

        reviewable_files = filter_reviewable_files(temp_dir)
        
        if not reviewable_files:
            return {
                "metadata": {
                    "reviewed_by": "AI Code Review Engine (LangChain + LangGraph)",
                    "status": "warning",
                    "message": "No reviewable files found in the uploaded folder"
                },
                "files": [],
                "summary": {"total_files": 0, "average_score": 0}
            }

        results = []
        total_files = len(reviewable_files)
        
        print(f"Found {total_files} reviewable files. Starting review...")

        for idx, (file_path, relative_path, filename) in enumerate(reviewable_files, 1):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                
                print(f"[{idx}/{total_files}] Reviewing: {relative_path}")
                
                state = {
                    "filename": filename,
                    "file_path": relative_path,
                    "code": code
                }
                review_result = review_graph.invoke(state)["result"]
                results.append(review_result)
                
            except Exception as e:
                print(f"Error reviewing {filename}: {str(e)}")
                results.append({
                    "filename": filename,
                    "file_path": relative_path,
                    "error": str(e),
                    "file_score": {"overall": 0}
                })

        return aggregate_results(results)
        
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def aggregate_results(file_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced aggregation with comprehensive statistics."""
    valid_reviews = [f for f in file_reviews if "file_score" in f and not f.get("error")]
    
    if valid_reviews:
        avg_overall = sum(f["file_score"]["overall"] for f in valid_reviews) / len(valid_reviews)
        avg_maintainability = sum(f["file_score"].get("maintainability", 0) for f in valid_reviews) / len(valid_reviews)
        avg_security = sum(f["file_score"].get("security", 0) for f in valid_reviews) / len(valid_reviews)
        
        total_issues = sum(len(f.get("issues", [])) for f in valid_reviews)
        total_improvements = sum(len(f.get("improvements", [])) for f in valid_reviews)
        
        critical_issues = sum(
            len([i for i in f.get("issues", []) if i.get("severity") == "Critical"])
            for f in valid_reviews
        )
    else:
        avg_overall = avg_maintainability = avg_security = 0
        total_issues = total_improvements = critical_issues = 0

    return {
        "metadata": {
            "reviewed_by": "AI Code Review Engine (LangChain + LangGraph)",
            "status": "success",
            "total_files_scanned": len(file_reviews),
            "total_files_reviewed": len(valid_reviews)
        },
        "files": sorted(valid_reviews, key=lambda x: x["file_score"].get("overall", 0), reverse=True),
        "summary": {
            "total_files": len(valid_reviews),
            "average_score": round(avg_overall, 2),
            "average_maintainability": round(avg_maintainability, 2),
            "average_security": round(avg_security, 2),
            "total_issues_found": total_issues,
            "total_improvements_suggested": total_improvements,
            "critical_issues": critical_issues,
            "recommendation": generate_summary_recommendation(avg_overall, critical_issues)
        }
    }


def generate_summary_recommendation(avg_score: float, critical_issues: int) -> str:
    """Generate overall recommendation based on scores."""
    if critical_issues > 0:
        return "🔴 CRITICAL: Address critical issues immediately before deployment"
    elif avg_score >= 85:
        return "🟢 EXCELLENT: Code quality is very high"
    elif avg_score >= 70:
        return "🟡 GOOD: Code is acceptable but has areas for improvement"
    else:
        return "🔴 POOR: Significant refactoring recommended"


def route_input(input_type: str, data: Any) -> Dict[str, Any]:
    """Route input to appropriate processor."""
    if input_type == "file":
        return process_files([data])
    elif input_type == "files":
        return process_files(data)
    elif input_type == "zip":
        return process_folder(data)
    else:
        raise ValueError(f"Unknown input type: {input_type}")


def process_uploaded_input(input_type: str, data: Any):
    """Main entry point for processing uploads."""
    return route_input(input_type, data)