# 🔍 Code Review Assistant

An intelligent code review tool that leverages AI to analyze codebases for quality issues, security vulnerabilities, and best practices. Built with FastAPI and React, powered by OpenAI's GPT models.

![Project Screenshot](images/dashboard-screenshot.png)
*Dashboard displaying comprehensive code analysis results*

## Demo Video

[▶️ Watch on Loom](https://www.loom.com/share/29c86bda634d4ef198db2291ab0630b1?sid=b33edfc3-b9ef-4708-8563-2f8041b2c395)
## Overview

Code Review Assistant provides automated, comprehensive code analysis to help development teams maintain high code quality standards. The system analyzes uploaded code files or entire projects, identifying potential issues across 19 different categories and providing actionable recommendations for improvement.

## Features

### Core Functionality

- **Flexible Upload System**: Support for single files, multiple files, or complete project folders (ZIP format)
- **AI-Powered Analysis**: Comprehensive code review using OpenAI's GPT-4o-mini model
- **Issue Classification**: 19 distinct issue categories including Bug Risk, Security, Performance, and Code Quality
- **Severity Assessment**: Three-tier severity system (Minor, Major, Critical) for prioritizing fixes
- **Quality Metrics**: Detailed scoring across five dimensions: maintainability, readability, robustness, security, and performance
- **User Authentication**: Secure authentication system with persistent sessions
- **Review History**: Complete audit trail of all code reviews with temporal tracking
- **Modern Interface**: Responsive React-based UI with data visualizations and intuitive navigation
- **Multi-Language Support**: Compatibility with 20+ programming languages and frameworks

![Upload Interface](images/upload-interface.png)
*Streamlined file upload interface*

## Technical Architecture

The application follows a modern full-stack architecture:

- **Backend** (`backend/`): FastAPI-based REST API handling file processing, AI integration, and data persistence
- **Frontend** (`frontend/frontend/`): React SPA with Vite build system for optimal performance
- **Database**: MongoDB for flexible document storage and efficient querying
- **AI Integration**: OpenAI GPT-4o-mini via LangChain for structured code analysis



## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 16+
- MongoDB (local installation or cloud instance)
- OpenAI API key

### Backend Configuration

1. **Clone the repository and navigate to backend:**

```bash
git clone <repository-url>
cd code_review_assistant/backend
```

2. **Create and activate virtual environment:**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the `backend` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017

# For MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```



### Frontend Configuration

1. **Navigate to frontend directory:**

```bash
cd ../frontend/frontend
```

2. **Install dependencies:**

```bash
npm install
```

### Database Setup

Ensure MongoDB is running:

```bash
# Local MongoDB instance:
mongod

# MongoDB Atlas requires no additional local setup
```

![Database Setup](images/mongodb-setup.png)
*MongoDB connection configuration*

### Running the Application

Start both servers in separate terminal instances:

**Terminal 1 - Backend Server:**
```bash
cd backend
# Activate virtual environment if not already active
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Development Server:**
```bash
cd frontend/frontend
npm run dev
```

![Running the Application](images/startup-screens1.png)
*Backend*
![Running the Application](images/startup-screens2.png)
*Frontend*

Access points:
- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### Authentication

![Authentication](images/auth-screens.png)
*User authentication interface*

1. Access the application at http://localhost:5173
2. Register a new account or authenticate with existing credentials
3. Session persistence maintains authentication across browser sessions

### Code Upload

![Upload Options](images/upload-interface.png)
*Multiple upload method options*

**Single File Upload:**
- Select individual files through the file picker
- Supported formats include: .py, .js, .jsx, .ts, .tsx, .java, .cpp, .go, .rs, .php, .rb, .swift, .kt, .cs, .scala, .vue, .svelte, .css, .scss, .html, .json, .yaml, .md

**Multiple File Upload:**
- Select multiple files simultaneously for batch analysis
- All files are processed and analyzed collectively

**Project Folder Upload:**
- Compress project directory as ZIP archive
- Upload for comprehensive project-wide analysis

### Analysis Results

![Review Results](images/dashboard-screenshot.png)
*Comprehensive analysis results display*

Results include:

- **Summary Statistics**: Aggregate metrics for overall project health
- **Issue Distribution**: Categorization by type and severity level
- **File-Level Analysis**: Detailed findings for each file with specific line references
- **Recommendations**: Concrete improvement suggestions with implementation guidance
- **Quality Scores**: Quantitative ratings across five key dimensions

### Review History

![Review History](images/history-view.png)
*Historical review tracking interface*

- Access complete history of previous code reviews
- Compare results across different time periods
- Track quality improvements and identify recurring patterns

## Development

### Backend Structure

The FastAPI backend is organized into modular components:

- **`app/main.py`**: Application initialization and CORS configuration
- **`app/routes.py`**: RESTful API endpoint definitions
- **`app/services.py`**: Business logic and AI integration layer
- **`app/utils.py`**: Utility functions and helper methods

### Frontend Structure

React application built with modern best practices:

- **`src/App.jsx`**: Root component with authentication flow management
- **`src/Dashboard.jsx`**: Main application interface for uploads and results
- **`src/AuthPage.jsx`**: Authentication and registration interface
- **`src/components/`**: Reusable component library

### Development Workflow



1. Implement changes in respective components
2. Leverage hot-reload functionality for rapid iteration
3. Test locally using development servers
4. Validate functionality before deployment

## Supported Technologies

### Programming Languages

**Frontend:**
- JavaScript/TypeScript: .js, .jsx, .ts, .tsx, .mjs, .mts
- Framework-specific: .vue, .svelte
- Styling: .css, .scss, .sass, .less
- Markup: .html, .htm, .xml

**Backend:**
- Python (.py)
- Java (.java)
- C/C++ (.cpp, .c, .h, .hpp)
- Go (.go)
- Rust (.rs)
- PHP (.php)
- Ruby (.rb)
- Swift (.swift)
- Kotlin (.kt)
- C# (.cs)
- Scala (.scala)
- Clojure (.clj)
- Groovy (.groovy)

**Configuration & Data:**
- .json, .yaml, .yml, .toml, .env
- .dockerfile, .sql
- .md, .mdx, .rst

### Issue Categories



The analysis engine evaluates code across 19 distinct categories:

- **Bug Risk**: Potential runtime errors and edge cases
- **Logic Error**: Incorrect program logic and algorithm issues
- **Code Smell**: Anti-patterns and design quality issues
- **Poor Naming**: Unclear or inconsistent naming conventions
- **Overcomplicated**: Unnecessary complexity and over-engineering
- **Style**: Code formatting and style guide compliance
- **Documentation**: Documentation quality and completeness
- **Performance**: Optimization opportunities and bottlenecks
- **Resource Leak**: Memory leaks and resource management issues
- **Security**: Security vulnerabilities and attack vectors
- **Authentication**: Authentication and authorization issues
- **Unsafe Operation**: Potentially dangerous operations
- **Best Practice**: Deviation from industry standards
- **Error Handling**: Exception handling and error propagation
- **Testing**: Test coverage and quality assessment
- **Compatibility**: Cross-platform and compatibility issues
- **Dependency**: Dependency management and versioning
- **Type Safety**: Type-related issues and type system usage
- **Concurrency**: Threading, synchronization, and async issues

## Troubleshooting

### Common Issues

**OpenAI API Configuration Error**
```
ValueError: OPENAI_API_KEY not found in .env file.
```
**Resolution:** Verify `.env` file exists in `backend` directory with valid OpenAI API key.

**MongoDB Connection Failure**
```
pymongo.errors.ServerSelectionTimeoutError
```
**Resolution:** Ensure MongoDB service is running locally or verify cloud connection string is correct.

**CORS Policy Errors**
```
Access to fetch blocked by CORS policy
```
**Resolution:** Confirm frontend is accessed via `localhost:5173` and backend via `localhost:8000`. CORS is pre-configured for these origins.

**Dependency Resolution Issues**
```
Module not found: Can't resolve 'react'
```
**Resolution:** Execute `npm install` in `frontend/frontend` directory to install all dependencies.



### Performance Considerations

- **Large Files**: Files exceeding 8000 characters are automatically truncated to optimize API usage
- **Batch Processing**: For projects with numerous files, consider batch uploads for improved performance
- **Network Requirements**: Stable internet connection required for OpenAI API communication

## API Documentation

The backend provides interactive API documentation via FastAPI's automatic documentation generation.

Access at: http://localhost:8000/docs

**Primary Endpoints:**

- `POST /upload/file/` - Single file upload and analysis
- `POST /upload/files/` - Multiple file upload and analysis
- `POST /upload/folder/` - ZIP folder upload and analysis
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User authentication
- `POST /user/uploads/` - Retrieve user's review history

![API Documentation](images/api-docs.png)
*Interactive API documentation interface*

## Technical Decisions & Implementation

### Why These Technologies?

**FastAPI** was chosen for its:
- High performance and async capabilities
- Automatic API documentation generation
- Type validation with Pydantic
- Modern Python syntax support

**React + Vite** provides:
- Fast development experience with hot module replacement
- Optimized production builds
- Modern JavaScript tooling
- Component-based architecture

**MongoDB** offers:
- Flexible schema for varying code analysis results
- Efficient document storage and retrieval
- Horizontal scalability
- Rich query capabilities

**OpenAI GPT-4o-mini** enables:
- Context-aware code analysis
- Natural language explanations
- Cost-effective API usage
- Consistent analysis quality

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Implement changes with appropriate tests
4. Submit a pull request with detailed description



## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- OpenAI for GPT model access
- FastAPI framework and community
- React and Vite development teams
- MongoDB database system
- LangChain for AI workflow management

---

**Support & Documentation**
- Troubleshooting guide available in this README
- Interactive API documentation at `/docs`
- Issue tracking available on GitHub


