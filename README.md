# Legal Intake Assistant Agent API

An intelligent AI-powered legal intake assistant that helps gather comprehensive information about legal cases through interactive questioning. Built with LangGraph and FastAPI, this system uses conversational AI to transform initial case descriptions into professional, structured legal summaries.

## 🎯 Overview

The Legal Intake Assistant automates the initial client intake process by:
- Asking targeted clarifying questions based on the user's initial description
- Iteratively gathering relevant facts and details
- Synthesizing information into professional case summaries
- Maintaining conversation context across multiple interactions

This tool is designed to assist legal professionals in streamlining their intake workflow while ensuring comprehensive information collection.

## ✨ Features

- **Intelligent Question Generation**: AI-driven clarifying questions tailored to each case
- **Iterative Information Gathering**: Multi-turn conversation flow with context retention
- **Professional Case Summaries**: Automated generation of structured legal case descriptions
- **Stateful Workflow**: Built on LangGraph with checkpoint management for reliable state handling
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Flexible LLM Backend**: Configurable AI model support (currently using Grok via OpenRouter)

## 🏗️ Architecture

The system uses a LangGraph-based workflow with three main nodes:

![Workflow Diagram](assets/workflow.png)

### Workflow Components

1. **Generate Questions Node**: Analyzes the current state and generates 1-3 relevant clarifying questions
2. **Get Answers Node**: Interrupts workflow to collect user responses
3. **Generate Final Description Node**: Synthesizes all gathered information into a professional case summary

### State Management

The agent maintains state across interactions including:
- Initial case description
- Questions asked and answers received
- Iteration count and completion status
- Final synthesized description

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- OpenRouter API key (or compatible LLM provider)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Dr.-Lawyer-legal-intake-assistant
```

2. Install dependencies using uv (recommended):
```bash
cd src
uv sync
```

Or using pip:
```bash
cd src
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp src/.env.example src/.env
```

Edit `src/.env` and add your configuration:
```env
OPENROUTER_API_KEY=your_api_key_here
APP_NAME=Legal Intake Assistant
APP_VERSION=0.1.0
```

### Running the API

Start the FastAPI server:
```bash
cd src
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/
```

Returns application name and version.

**Response:**
```json
{
  "app_name": "Legal Intake Assistant",
  "app_version": "0.1.0"
}
```

### Ask Questions
```http
POST /api/v1/ask-questions
```

Generates clarifying questions based on the initial description and previous answers.

**Request Body:**
```json
{
  "initial_description": "Someone assaulted me and I want to raise a case",
  "previous_answers": ""
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "reasoning": "Need to gather key facts about the incident",
    "questions": [
      "When did the assault occur?",
      "Where did the incident take place?",
      "Were there any witnesses present?"
    ],
    "is_complete": false
  }
}
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs
- **LangChain**: LLM application framework
- **OpenAI/OpenRouter**: LLM provider integration
- **Pydantic**: Data validation and settings management
- **Python 3.11+**: Core programming language

## 📁 Project Structure

```
Dr.-Lawyer-legal-intake-assistant/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/
│   │   └── base.py            # API route definitions
│   ├── workflow/
│   │   ├── graph.py           # LangGraph workflow definition
│   │   ├── nodes.py           # Workflow node implementations
│   │   ├── prompts.py         # LLM prompt templates
│   │   └── state.py           # State schema definitions
│   ├── studio/                # LangGraph Studio configuration
│   ├── .env                   # Environment variables
│   └── pyproject.toml         # Project dependencies
├── assets/
│   └── workflow.png           # Workflow visualization
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for OpenRouter/LLM provider | Yes |
| `APP_NAME` | Application name | No |
| `APP_VERSION` | Application version | No |

### LLM Configuration

The default configuration uses Grok via OpenRouter. To change the model, edit `src/workflow/nodes.py`:

```python
llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="x-ai/grok-4.1-fast",  # Change model here
)
```

## 🧪 Development

### Running Tests

```bash
cd src
python test_graph.py
```

### LangGraph Studio

For visual workflow debugging, use LangGraph Studio:

```bash
cd src/studio
langgraph dev
```

## 🚧 Current Status

**Status**: In Development

This project is currently under active development. Planned enhancements include:
- Complete API endpoint implementation
- Enhanced error handling and validation
- Integration with legal knowledge bases
- Multi-language support
- Authentication and authorization
- Case history and persistence
- Advanced analytics and reporting

## ⚠️ Disclaimer

This tool is designed to assist with information gathering and does NOT provide legal advice. All outputs should be reviewed by qualified legal professionals. Users should consult with licensed attorneys for legal guidance specific to their situations.

## 📄 License

[Add your license information here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

[Add your contact information here]

---

**Note**: This is an AI-assisted legal intake tool and should be used as a supplement to, not a replacement for, professional legal consultation.
