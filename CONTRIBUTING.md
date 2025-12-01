# Contributing to RAG Chatbot

Thank you for considering contributing to RAG Chatbot! 🎉

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details**: OS, Python version, Node version, browser

**Example:**
```
Title: Upload fails for PDF files larger than 10MB

Steps to reproduce:
1. Create a new chat
2. Upload a 15MB PDF file
3. Observe error message

Expected: File uploads successfully
Actual: Error "File too large" despite MAX_FILE_SIZE_MB=30

Environment: Windows 11, Python 3.11, Chrome 120
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear use case** - Why is this enhancement needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - What other approaches did you think about?
- **Additional context** - Screenshots, mockups, examples

### Pull Requests

We actively welcome pull requests:

1. Fork the repo and create your branch from `main`
2. Make your changes following our [coding standards](#coding-standards)
3. Add tests if applicable
4. Ensure the test suite passes
5. Update documentation as needed
6. Submit the pull request!

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git
- Azure OpenAI and Azure AI Search accounts

### Local Setup

1. **Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/rag-chatbot.git
cd rag-chatbot
```

2. **Set up Backend:**
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Azure credentials
```

3. **Set up Frontend:**
```bash
cd ../Frontend
npm install
```

4. **Run tests:**
```bash
# Backend tests
cd Backend
pytest

# Frontend tests (if available)
cd Frontend
npm test
```

5. **Start development servers:**
```bash
# Terminal 1 - Backend
cd Backend/app
uvicorn Main:app --reload --port 8000

# Terminal 2 - Frontend
cd Frontend
npm run dev
```

## 🔀 Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clean, readable code
   - Add comments for complex logic
   - Follow existing code style

3. **Test your changes:**
   - Run all tests
   - Test manually in the browser
   - Check for console errors

4. **Commit your changes:**
```bash
git add .
git commit -m "feat: add amazing feature"
```

5. **Push to your fork:**
```bash
git push origin feature/your-feature-name
```

6. **Open a Pull Request:**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link any related issues

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] Screenshots included (for UI changes)

## 💻 Coding Standards

### Python (Backend)

```python
# Use type hints
def process_document(file_path: str, filename: str) -> dict:
    """
    Process a document and return status.
    
    Args:
        file_path: Path to the document file
        filename: Original filename
        
    Returns:
        Dictionary with processing status
    """
    pass

# Follow PEP 8
# Use descriptive variable names
# Keep functions focused and small
# Add docstrings to all public functions
```

**Style Guide:**
- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black --line-length 100 .`
- Use `flake8` for linting: `flake8 .`
- Maximum line length: 100 characters

### JavaScript/React (Frontend)

```javascript
/**
 * ChatWindow component for the chat interface
 * @param {string} chatId - Unique chat identifier
 * @param {Array} messages - Chat message history
 */
const ChatWindow = ({ chatId, messages }) => {
  // Use descriptive variable names
  const [isLoading, setIsLoading] = useState(false);
  
  // Group related logic
  const handleSend = async () => {
    // Implementation
  };
  
  return (
    // JSX
  );
};
```

**Style Guide:**
- Use functional components with hooks
- Follow [Airbnb React Style Guide](https://airbnb.io/javascript/react/)
- Use PropTypes or TypeScript for type checking
- Use `prettier` for formatting
- Use `eslint` for linting

### General Guidelines

- **Write self-documenting code**: Clear variable and function names
- **DRY principle**: Don't Repeat Yourself
- **KISS principle**: Keep It Simple, Stupid
- **SOLID principles**: For object-oriented code
- **Add comments**: For complex logic only
- **Error handling**: Always handle errors gracefully
- **Security**: Never commit secrets or API keys

## 📝 Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:

```bash
# Feature
git commit -m "feat(chat): add message persistence to localStorage"

# Bug fix
git commit -m "fix(upload): handle large PDF files correctly"

# Documentation
git commit -m "docs: update deployment instructions for Azure"

# With body
git commit -m "feat(backend): add separate indexes per chat

- Create dynamic index based on chat name
- Implement index name sanitization
- Add search client caching

Closes #123"
```

## 🧪 Testing Guidelines

### Backend Tests

```python
def test_document_upload():
    """Test document upload functionality"""
    # Arrange
    file_path = "test_doc.pdf"
    
    # Act
    result = indexer.process_document(file_path, "test.pdf", "chat-123")
    
    # Assert
    assert result["success"] == True
    assert result["chunks"] > 0
```

### Frontend Tests

```javascript
describe('ChatWindow', () => {
  it('should send message when button clicked', () => {
    // Test implementation
  });
});
```

## 📚 Documentation

When adding new features:

1. **Update README.md** - Add feature to features list
2. **Update API docs** - Document new endpoints
3. **Add code comments** - Explain complex logic
4. **Update CHANGELOG.md** - Note version changes

## 🐛 Found a Security Issue?

Please **DO NOT** open a public issue. Instead, email [your.email@example.com](mailto:your.email@example.com) with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 🎉 Recognition

Contributors will be added to our [Contributors](https://github.com/yourusername/rag-chatbot/graphs/contributors) page and may be featured in release notes!

## 💬 Questions?

Feel free to:
- Open a [Discussion](https://github.com/yourusername/rag-chatbot/discussions)
- Comment on an existing issue
- Reach out via [email](mailto:your.email@example.com)

Thank you for contributing to RAG Chatbot! 🚀
