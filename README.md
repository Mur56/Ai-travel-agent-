# AI Travel Planner

A professional AI-powered travel planning application that generates personalized travel itineraries using advanced language models and specialized tools.

## Features

- 🤖 **AI-Powered Planning**: Uses advanced LLMs to generate detailed travel itineraries
- 🌍 **Multi-Tool Integration**: Weather information, place search, expense calculation, and currency conversion
- 🎨 **Modern UI**: Clean, responsive React frontend with professional design
- ⚡ **Fast API**: High-performance FastAPI backend with proper error handling
- 🔧 **Modular Architecture**: Well-structured codebase with clear separation of concerns

## Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- **Axios** for API communication
- **CSS3** with modern design patterns

### Backend
- **FastAPI** with Python 3.8+
- **LangGraph** for agentic workflows
- **LangChain** for LLM integration
- **Pydantic** for data validation
- **Uvicorn** for ASGI server

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- API keys for LLM providers (Groq, OpenAI, etc.)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Run the backend server:**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /travel/query` - Generate travel plans
- `GET /health` - Health check endpoint

## Project Structure

```
AI_Trip_Planner/
├── backend/
│   ├── agent/                 # AI agent workflow
│   ├── config/               # Configuration files
│   ├── exception/            # Exception handling
│   ├── logger/               # Logging utilities
│   ├── Routes/               # API routes
│   ├── tools/                # Specialized tools
│   ├── utils/                # Utility functions
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.tsx          # Main application
│   │   └── main.tsx         # Application entry point
│   └── package.json         # Frontend dependencies
└── README.md                # This file
```

## Development

### Code Quality

- **Python**: Follow PEP 8 style guidelines
- **TypeScript**: Use strict mode and proper typing
- **React**: Use functional components with hooks
- **CSS**: Use modern CSS with proper accessibility

### Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Backend
cd backend
python setup.py build

# Frontend
cd frontend
npm run build
```

## Configuration

### Environment Variables

#### Backend
- `GROQ_API_KEY`: API key for Groq LLM provider
- `OPENAI_API_KEY`: API key for OpenAI LLM provider
- `TAVILY_API_KEY`: API key for Tavily search
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: false)

#### Frontend
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_APP_TITLE`: Application title
- `VITE_APP_VERSION`: Application version

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: support@aitravelplanner.com

## Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://langchain.com/langgraph)
- UI components inspired by modern design systems
- Powered by advanced language models 