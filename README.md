# 🔥 AI Roast Master

An AI-powered comedy app that analyzes photos and generates personalized roasts, witty comebacks, and stand-up routines.

## Features

- 📸 **Photo Analysis**: Detects faces, objects, colors, and composition
- 🎭 **Multiple Humor Styles**: Savage, Playful, Sarcastic, Absurd
- 💬 **Real-time Comebacks**: Generate witty responses instantly
- 🎪 **Stand-up Routines**: Create mini comedy sets from photos
- 🌐 **Web Interface**: Easy-to-use browser-based UI

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up OpenAI API**
   - Get API key from https://platform.openai.com/
   - Create `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. **Run the App**
   ```bash
   python run.py
   ```

4. **Open Browser**
   - Go to http://localhost:8000
   - Upload a photo and get roasted!

## Project Structure

```
ai-roast-master/
├── backend/
│   ├── api.py              # FastAPI web server
│   ├── image_analyzer.py   # Photo analysis
│   └── roast_generator.py  # AI comedy generation
├── models/
│   └── roast_templates.json # Fallback jokes
├── requirements.txt        # Dependencies
├── .env                   # API keys (create this)
└── run.py                 # Launch script
```

## API Endpoints

- `GET /` - Web interface
- `POST /roast` - Upload photo and get roasted
- `POST /comeback` - Generate comeback to message
- `POST /standup` - Create stand-up routine
- `GET /health` - Health check

## Humor Styles

- **🔥 Savage**: Brutal and merciless roasts
- **😄 Playful**: Light and friendly teasing
- **😏 Sarcastic**: Dry and clever wit
- **🤪 Absurd**: Weird and unexpected humor

## Requirements

- Python 3.8+
- OpenAI API key
- Webcam or image files for testing

## Safety Features

- Content filtering for inappropriate language
- Fallback jokes when API is unavailable
- Humor boundaries to keep roasts fun, not cruel

## Contributing

Feel free to add new humor styles, improve image analysis, or enhance the UI!

## License

MIT License - Roast responsibly! 🔥