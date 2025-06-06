# SnookXporter

**SnookXporter** is a Python application that syncs snooker league match schedules (from the open SnookApp API) to your Google Calendar. It helps you keep your calendar up-to-date without manual input.

## 🔧 Requirements

- Python 3.11
- [Poetry](https://python-poetry.org/)
- Google Calendar API (OAuth credentials required)
- `make` (optional, for convenient commands)

## 🚀 Installation

Install the main dependencies:

```bash
make install
```

To install development dependencies (for testing, linting, etc.):

```bash
make install-dev
```

## ▶️ Running the App

To run the application:

```bash
make run
```

This executes the main entry point (`poetry run snookxporter`), which fetches upcoming matches from 
the SnookApp API and syncs them to your Google Calendar.

## 📁 Project Structure

```
snookxporter/
├── logs/                     # Logging output
├── secrets/                  # Secrets to Google Calendar API
├── snookxporter/settings/    # Configuration, including Google API setup
├── snookxporter/__main__.py  # Entry point
Makefile
pyproject.toml
README.md
```

## 🔐 Google Calendar API Setup

To access your Google Calendar, you’ll need to set up two files:

### 1. `credentials.json`

This file contains your OAuth 2.0 client credentials. To generate it:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Navigate to `API & Services` → `Credentials`.
4. Click `Create Credentials` → `OAuth client ID`.
5. Choose "Desktop App" as the application type.
6. After creation, click "Download JSON" — save it as `credentials.json` in the root directory of the project.

### 2. `token.json`

This file is generated automatically when you first run the app and authorize it through a browser. It stores your access and refresh tokens so that the app can access your calendar without asking every time.

📌 **Note:** Both `credentials.json` and `token.json` should be listed in your `.gitignore` file — they contain sensitive information.

## 🧪 Testing and Quality Checks

To run all tests and checks:

```bash
make tests
```

This includes:
- Unit tests using `pytest` (100% coverage required)
- Static typing checks with `mypy`
- Linting with `pylint`
- Import formatting checks with `isort`

## 📄 License

Private project for personal use. Feel free to use or modify as needed.
