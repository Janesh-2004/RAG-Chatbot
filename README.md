# 🤖 RAG Chatbot - Production-Ready AI Document Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Azure](https://img.shields.io/badge/Azure-OpenAI%20%7C%20AI%20Search-0078D4.svg)](https://azure.microsoft.com/)

A modern, production-ready **Retrieval-Augmented Generation (RAG)** chatbot that allows users to upload documents and have intelligent conversations with them. Built with **FastAPI**, **React**, **Azure OpenAI**, and **Azure AI Search**.

---

## ✨ Features

### 🎯 Core Capabilities
- **📄 Multi-Format Support**: Upload PDF, DOCX, and TXT documents
- **💬 Intelligent Chat**: Ask questions and get AI-powered answers from your documents
- **🔍 Vector Search**: Powered by Azure AI Search with HNSW algorithm for fast, accurate retrieval
- **📚 Multi-Chat Management**: Create separate chats with unique names and isolated document indexes
- **💾 Persistent History**: Chat messages saved locally and restored on refresh
- **🎨 Modern UI**: Beautiful, responsive interface with ChatGPT-like design

### 🚀 Advanced Features
- **Separate Indexes**: Each chat gets its own Azure AI Search index for complete isolation
- **Chat History**: Full conversation persistence across sessions using localStorage
- **Real-time Streaming**: Architecture ready for streaming responses
- **Markdown Support**: Rich text rendering with code syntax highlighting
- **Source Citations**: See which document chunks were used to generate answers
- **Smart Chunking**: Intelligent document splitting with configurable overlap

### 🏗️ Technical Highlights
- **Production-Ready**: Comprehensive error handling, logging, and validation
- **Scalable Architecture**: Lazy initialization, connection pooling, efficient caching
- **Type-Safe**: Pydantic models for request/response validation
- **CORS Configured**: Ready for cross-origin requests
- **Environment-Based Config**: Easy deployment across environments

---

## 📸 Screenshots

### Main Chat Interface
![Chat Interface](./docs/screenshots/chat-interface.png)
*Modern ChatGPT-like interface with document upload and multi-chat support*

### Document Upload & Chat
![Document Upload](./docs/screenshots/document-upload.png)
*Upload documents and start asking questions immediately*

### Multi-Chat Management
![Multi-Chat](./docs/screenshots/multi-chat.png)
*Manage multiple conversations with separate document contexts*

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   React Frontend│─────▶│  FastAPI Backend │─────▶│  Azure OpenAI       │
│   (Vite + TW)   │◀─────│  (Python 3.10+)  │◀─────│  (GPT-4 + Embeddings)│
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                  │
                                  │
                         ┌────────▼─────────┐
                         │  Azure AI Search │
                         │  (Vector Store)  │
                         └──────────────────┘
```

### Technology Stack

**Frontend:**
- React 18.2 with Hooks
- Vite 5.0 (Lightning-fast HMR)
- TailwindCSS 3.4 (Utility-first styling)
- Axios (HTTP client)
- React Markdown (Rich text rendering)
- React Syntax Highlighter (Code blocks)

**Backend:**
- FastAPI (High-performance async API)
- LangChain (RAG orchestration)
- Azure OpenAI SDK
- Azure AI Search SDK
- Pydantic (Data validation)
- Python-dotenv (Environment management)

**AI Services:**
- Azure OpenAI (GPT-4, GPT-3.5-turbo)
- Azure OpenAI Embeddings (text-embedding-ada-002)
- Azure AI Search (Vector database with HNSW)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm
- **Azure OpenAI** resource with deployed models
- **Azure AI Search** service (Basic tier or higher)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

### 2️⃣ Backend Setup

```bash
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Azure credentials (see Configuration section)
```

### 3️⃣ Frontend Setup

```bash
cd ../Frontend

# Install dependencies
npm install

# The frontend uses environment variables from Backend/.env
```

### 4️⃣ Run the Application

**Terminal 1 - Backend:**
```bash
cd Backend/app
uvicorn Main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm run dev
```

**Access the app:** http://localhost:5173

---

## ⚙️ Configuration

### Backend Configuration (`.env`)

Create `Backend/.env` with your Azure credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key
AZURE_SEARCH_INDEX_NAME=rag-index

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=30
```

### Getting Azure Credentials

1. **Azure OpenAI:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to your Azure OpenAI resource
   - **Keys and Endpoint** → Copy Key 1 and Endpoint
   - **Model deployments** → Note your deployment names

2. **Azure AI Search:**
   - Navigate to your Azure AI Search service
   - **Overview** → Copy URL
   - **Keys** → Copy Primary admin key

---

## 📖 Usage Guide

### Creating a New Chat

1. Click **"+ New Chat"** button in the sidebar
2. Enter a **unique name** for your chat (e.g., "Sales Report", "Tech Docs")
3. Each chat creates its own Azure AI Search index for complete isolation

### Uploading Documents

1. Click the **📎 paperclip icon** in the chat input area
2. Select a PDF, DOCX, or TXT file (max 30MB)
3. Wait for processing (typically 5-15 seconds)
4. Status changes to **"✓ Ready"** when complete

### Asking Questions

1. Type your question in the chat input
2. Examples:
   - "Summarize the key points from this document"
   - "What does the document say about [topic]?"
   - "Extract all the dates mentioned"
3. Get AI-powered answers with source citations

### Managing Chats

- **Switch Chats:** Click on any chat in the sidebar
- **View History:** All messages are automatically saved
- **Delete Chat:** Hover over a chat and click the **×** button
- **Reset Chat:** Click the reset button to clear documents and messages

---

## 🏛️ Project Structure

```
RAG_chatbot/
├── Backend/
│   ├── app/
│   │   ├── Main.py              # FastAPI application & endpoints
│   │   ├── rag_indexer.py       # RAG logic, embeddings, vector search
│   │   ├── utils.py             # Text extraction utilities
│   │   └── uploads/             # Uploaded documents (auto-created)
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (DO NOT COMMIT)
│   └── .env.example             # Template for environment variables
│
├── Frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── Components/
│   │   │   ├── Chatwindow.jsx   # Chat interface
│   │   │   ├── MessageBubble.jsx # Message rendering
│   │   │   └── Fileuploader.jsx  # File upload component
│   │   ├── index.css            # Global styles + Tailwind
│   │   └── main.jsx             # App entry point
│   ├── package.json             # Frontend dependencies
│   ├── vite.config.js           # Vite configuration
│   └── tailwind.config.js       # TailwindCSS configuration
│
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
└── CONTRIBUTING.md              # Contribution guidelines
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "service": "RAG Chatbot API",
  "version": "1.0.0",
  "rag_indexer": "ready"
}
```

#### `POST /upload`
Upload a document for a specific chat

**Request (multipart/form-data):**
```
chat_id: string (required)
chat_name: string (optional)
file: binary (required)
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed document.pdf for chat chat-123",
  "filename": "document.pdf",
  "chunks": 25,
  "chat_id": "chat-123",
  "has_documents": true
}
```

#### `POST /query` or `POST /chat`
Ask a question about uploaded documents

**Request:**
```json
{
  "question": "What are the main topics?",
  "chat_id": "chat-123",
  "chat_name": "My Chat" 
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The main topics discussed are...",
  "sources": [
    {
      "content": "Excerpt from document...",
      "source": "document.pdf"
    }
  ]
}
```

#### `POST /reset`
Reset a chat (clear documents and history)

**Request:**
```json
{
  "chat_id": "chat-123"
}
```

---

## 🧪 Testing

### Backend Tests
```bash
cd Backend
pytest tests/
```

### Frontend Tests
```bash
cd Frontend
npm test
```

### End-to-End Testing
1. Start both backend and frontend
2. Create a new chat named "Test Chat"
3. Upload a sample PDF
4. Ask: "Summarize this document"
5. Verify answer contains relevant information
6. Switch to another chat
7. Return to "Test Chat" - verify messages persist

---

## 🚢 Deployment

### Backend Deployment (Azure App Service)

1. **Create Azure App Service**
```bash
az webapp create --resource-group myResourceGroup \
  --plan myAppServicePlan --name my-rag-backend \
  --runtime "PYTHON:3.10"
```

2. **Configure Environment Variables**
```bash
az webapp config appsettings set --resource-group myResourceGroup \
  --name my-rag-backend \
  --settings AZURE_OPENAI_API_KEY="your-key" \
             AZURE_OPENAI_ENDPOINT="your-endpoint" \
             # ... add all environment variables
```

3. **Deploy**
```bash
cd Backend
az webapp up --name my-rag-backend --resource-group myResourceGroup
```

### Frontend Deployment (Vercel/Netlify)

**Vercel:**
```bash
cd Frontend
vercel --prod
```

**Netlify:**
```bash
cd Frontend
npm run build
netlify deploy --prod --dir=dist
```

### Environment Variables for Production
Update `Frontend/src/App.jsx` and `Chatwindow.jsx`:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Add `.env` to Frontend:
```env
VITE_API_URL=https://your-backend-url.azurewebsites.net
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Azure OpenAI** for powerful LLM capabilities
- **Azure AI Search** for efficient vector storage
- **LangChain** for RAG orchestration
- **FastAPI** for high-performance backend
- **React** and **Vite** for modern frontend development
- **TailwindCSS** for beautiful, responsive design

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/rag-chatbot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/rag-chatbot/discussions)
- **Email:** your.email@example.com

---

## 🗺️ Roadmap

- [ ] Streaming responses for real-time chat
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Advanced document preprocessing (OCR, tables)
- [ ] User authentication and authorization
- [ ] Export chat history (PDF, JSON)
- [ ] Docker containerization
- [ ] Kubernetes deployment templates
- [ ] Prometheus metrics and Grafana dashboards

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/rag-chatbot&type=Date)](https://star-history.com/#yourusername/rag-chatbot&Date)

---

**Made with ❤️ by [Your Name](https://github.com/yourusername)**

If you find this project useful, please consider giving it a ⭐!
