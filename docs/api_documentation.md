# SportRadar Tennis API – Data Collection

This document covers only the API integration and raw JSON collection module.

## API configuration

Create a project-root `.env` file using `.env.example` as a template:

```env
SPORTRADAR_API_KEY=your_api_key
SPORTRADAR_ACCESS_LEVEL=trial
SPORTRADAR_LANGUAGE=en
```

The client sends the API key in the `x-api-key` HTTP request header. The API key must not be committed to Git.

## API base URL

`https://api.sportradar.com/tennis/{access_level}/v3/{language}`

## Feeds collected

| Data | Endpoint | Raw output |
|---|---|---|
| Competitions and categories | `competitions.json` | `data/raw/competitions.json` |
| Complexes and venues | `complexes.json` | `data/raw/complexes.json` |
| Doubles competitor rankings | `double_competitors_rankings.json` | `data/raw/doubles_rankings.json` |

Official endpoint references:

- [Competitions](https://developer.sportradar.com/tennis/reference/competitions)
- [Complexes](https://developer.sportradar.com/tennis/reference/complexes)
- [Doubles competitor rankings](https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings)
- [API authentication and URL structure](https://developer.sportradar.com/tennis/docs/tennis-ig-api-basics)

## Setup and run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and provide a valid key and the access level assigned to that key. Then run:

```bash
python main.py
```

The three raw API response objects are saved as UTF-8 JSON files under `data/raw/`. The response structure is preserved; this module does not flatten or transform the data.

## Error handling

The shared client handles network errors, HTTP errors, authentication/access failures, rate limiting (HTTP 429), server errors, invalid JSON, and file-writing errors. It retries transient network, rate-limit, and server failures a limited number of times. Authentication failures are not retried.