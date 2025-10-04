# Legacy Streamlit App

This directory contains the original Streamlit prototype for the AI 个性化学习助手.

The app is retained during the transition period and should eventually consume the new FastAPI endpoints exposed under `services/api`. For now, the code remains largely unchanged but paths were adjusted to work from this subdirectory.

Run via:

```bash
cd apps/streamlit
streamlit run streamlit_app.py
```

Provide a `.env` with API base URLs when integrating with the new backend.
