import os
import io
import zipfile
import tempfile
import json
import shutil
import bcrypt
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env")) 

# connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["code_review_app"]
users = db["users"]
uploads_collection=db["review_data"]


openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

# ==================== VALID ISSUE TYPES ====================

VALID_ISSUE_TYPES = [
    "Bug Risk",
    "Logic Error",
    "Code Smell",
    "Poor Naming",
    "Overcomplicated",
    "Style",
    "Documentation",
    "Performance",
    "Resource Leak",
    "Security",
    "Authentication",
    "Unsafe Operation",
    "Best Practice",
    "Error Handling",
    "Testing",
    "Compatibility",
    "Dependency",
    "Type Safety",
    "Concurrency"
]

VALID_SEVERITIES = ["Minor", "Major", "Critical"]

# ==================== LANGCHAIN MODEL ====================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=openai_api_key
)

# ==================== FILE CONFIGURATION ====================

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

# ==================== GRAPH STATE ====================

class ReviewState(dict):
    code: str
    filename: str
    file_path: str
    result: dict

# ==================== VALIDATION FUNCTIONS ====================

def validate_issue(issue: Dict[str, Any]) -> bool:
    """Validate that issue has correct type and severity."""
    if issue.get("type") not in VALID_ISSUE_TYPES:
        return False
    if issue.get("severity") not in VALID_SEVERITIES:
        return False
    return True


def fix_invalid_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove or fix invalid issues."""
    fixed_issues = []
    for issue in issues:
        if validate_issue(issue):
            fixed_issues.append(issue)
        else:
            # Try to fix invalid type
            if issue.get("type") not in VALID_ISSUE_TYPES:
                issue["type"] = "Code Smell"  # Default fallback
            if issue.get("severity") not in VALID_SEVERITIES:
                issue["severity"] = "Minor"  # Default fallback
            if validate_issue(issue):
                fixed_issues.append(issue)
    return fixed_issues


def count_issues_by_type(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count issues grouped by type."""
    type_counts = {issue_type: 0 for issue_type in VALID_ISSUE_TYPES}
    for issue in issues:
        issue_type = issue.get("type", "Code Smell")
        if issue_type in type_counts:
            type_counts[issue_type] += 1
    return {k: v for k, v in type_counts.items() if v > 0}


# ==================== LLM NODE ====================

def analyze_code_node(state: ReviewState) -> ReviewState:
    """Enhanced LangChain-based code review node."""
    code = state["code"]
    filename = state["filename"]
    file_path = state.get("file_path", filename)

    _, ext = os.path.splitext(filename)
    
    valid_types_str = ", ".join(VALID_ISSUE_TYPES)
    valid_severities_str = ", ".join(VALID_SEVERITIES)
    
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
          "type": "{valid_types_str}",
          "severity": "{valid_severities_str}",
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
  }},
  "issue_distribution": {{
      "Bug Risk": 0,
      "Logic Error": 0,
      "Code Smell": 0,
      "Poor Naming": 0,
      "Overcomplicated": 0,
      "Style": 0,
      "Documentation": 0,
      "Performance": 0,
      "Resource Leak": 0,
      "Security": 0,
      "Authentication": 0,
      "Unsafe Operation": 0,
      "Best Practice": 0,
      "Error Handling": 0,
      "Testing": 0,
      "Compatibility": 0,
      "Dependency": 0,
      "Type Safety": 0,
      "Concurrency": 0
  }}
}}

CRITICAL INSTRUCTIONS:
- ONLY use issue types from: {valid_types_str}
- ONLY use severity levels from: {valid_severities_str}
- Include actual line numbers when possible
- Be thorough and specific
- Provide actionable recommendations
- Consider industry standards for {ext} files
- Flag security issues immediately
- Include performance optimization tips
- Count each issue by type in the issue_distribution field

Code to review:
```{ext}
{code[:8000]}
```
{"[... code truncated due to length ...]" if len(code) > 8000 else ""}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(response.content)
        # Validate and fix issues
        if "issues" in result:
            result["issues"] = fix_invalid_issues(result.get("issues", []))
        # Calculate issue distribution
        result["issue_distribution"] = count_issues_by_type(result.get("issues", []))
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
                          "security": 75, "performance": 75, "best_practices": 75, "overall": 75},
            "issue_distribution": {"Code Smell": 1}
        }

    state["result"] = result
    return state

# ==================== GRAPH CONSTRUCTION ====================

graph = StateGraph(ReviewState)
graph.add_node("analyze_code", analyze_code_node)
graph.set_entry_point("analyze_code")
graph.set_finish_point("analyze_code")
review_graph = graph.compile()

# ==================== HELPER FUNCTIONS ====================

def filter_reviewable_files(temp_dir: str) -> List[tuple]:
    """Filter and prioritize reviewable files."""
    reviewable_files = []

    for root, dirs, files in os.walk(temp_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in COMPREHENSIVE_REVIEWABLE_EXTS or ext == "":
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, temp_dir)
                reviewable_files.append((full_path, relative_path, file))

    reviewable_files.sort(
        key=lambda x: (
            x[2] not in PRIORITY_FILES,
            x[1]
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
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def aggregate_results(file_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced aggregation with comprehensive statistics and issue distribution."""
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
        
        # Aggregate issue distribution across all files
        overall_issue_distribution = {issue_type: 0 for issue_type in VALID_ISSUE_TYPES}
        for file_review in valid_reviews:
            file_dist = file_review.get("issue_distribution", {})
            for issue_type, count in file_dist.items():
                if issue_type in overall_issue_distribution:
                    overall_issue_distribution[issue_type] += count
        
        overall_issue_distribution = {k: v for k, v in overall_issue_distribution.items() if v > 0}
    else:
        avg_overall = avg_maintainability = avg_security = 0
        total_issues = total_improvements = critical_issues = 0
        overall_issue_distribution = {}

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
            "issue_distribution": overall_issue_distribution,
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
def register_user(username: str, password: str):
    """
    Registers a new user with a unique auto-generated user ID and hashed password.
    """
    # Check if username already exists
    if users.find_one({"username": username}):
        return {"status": "error", "message": "Username already exists"}

    # Generate a random unique user ID
    userid = str(uuid.uuid4())

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_data = {
        "username": username,
        "userid": userid,
        "password": hashed_pw.decode('utf-8'),
    }

    users.insert_one(user_data)
    return {
        "status": "success",
        "message": "User registered successfully",
        "user": {"username": username, "userid": userid}
    }


def login_user(username: str, password: str):
    """
    Verifies login credentials using username and password.
    """
    user = users.find_one({"username": username})
    if not user:
        return {"status": "error", "message": "User not found"}

    if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return {
            "status": "success",
            "message": "Login successful",
            "user": {"username": user["username"], "userid": user["userid"]}
        }
    else:
        return {"status": "error", "message": "Invalid password"}


def save_to_db(user_id: str, upload_type: str, result: dict):
    """Save upload response in DB with user_id and timestamp."""
    uploads_collection.insert_one({
        "user_id": user_id,
        "upload_type": upload_type,
        "result": result,
        "timestamp": datetime.utcnow()
    })

def get_user_uploads(user_id: str):
    """
    Fetch all uploads associated with a given user_id.
    Converts timestamp to ISO format for JSON serialization.
    """
    uploads = list(uploads_collection.find({"user_id": user_id}, {"_id": 0}))
    
    if not uploads:
        return {
            "status": "error",
            "message": "No uploads found for this user."
        }

    # Convert timestamp to string
    for upload in uploads:
        if "timestamp" in upload and isinstance(upload["timestamp"], datetime):
            upload["timestamp"] = upload["timestamp"].isoformat()

    return {
        "status": "success",
        "message": "Uploads retrieved successfully.",
        "data": uploads
    }