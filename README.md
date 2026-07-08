# DeepDive AI

DeepDive AI is a multi-agent research assistant built with Streamlit, LangChain, Mistral AI, and Tavily. It searches the web, scrapes relevant sources, writes a report, and critiques the result.

## Features

- Web search with Tavily
- URL scraping for deeper reading
- Report generation with Mistral AI
- Critic feedback and scoring
- Streamlit UI with a custom dark theme

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your API keys in a `.env` file:

```env
MISTRAL_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
```

4. Run the app:

```bash
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this project to GitHub.
2. Go to Streamlit Cloud and create a new app.
3. Select the repository.
4. Set the main file path to `app.py`.
5. Add secrets in the Streamlit app settings:

```toml
MISTRAL_API_KEY = "your_mistral_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

6. Click Deploy.

## Important

- Do not commit `.env` to GitHub.
- Keep API keys only in local environment variables or Streamlit secrets.
- If you change dependencies, update `requirements.txt` before redeploying.
