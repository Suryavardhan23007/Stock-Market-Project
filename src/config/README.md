# Config Management Module

This directory manages application settings, loading credential strings from environmental variables, and checking configurations.

## Components

- `config.py`: Loads environment configurations from `.env` or system variables using python-dotenv.

## Configuration Variables

* **Database Connection Details**: Hosts, users, and credentials.
* **Vector Store**: Qdrant endpoints.
* **Broker API**: 5paisa OAuth keys and TOTP tokens.
* **Large Language Model API**: Gemini credentials.
