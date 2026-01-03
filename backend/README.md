# FreshKeep Backend

A scalable, real-time backend system for FreshKeep - a grocery management app that reduces food waste using OCR receipt scanning, barcode lookup, smart expiration tracking, recipe suggestions, family sharing, and analytics.

## Tech Stack

- **Backend:** Python 3.11+ with FastAPI
- **Database:** Supabase (PostgreSQL)
- **OCR:** OCR.space API
- **Text-to-Speech:** ElevenLabs API
- **Recipes:** Spoonacular API
- **Authentication:** JWT tokens

## Quick Start

### 1. Create Virtual Environment

```bash
cd freshkeep
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required API keys:
- **Supabase**: Create project at [supabase.com](https://supabase.com)
- **OCR.space**: Get free key at [ocr.space](https://ocr.space/ocrapi)
- **ElevenLabs**: Get key at [elevenlabs.io](https://elevenlabs.io)
- **Spoonacular**: Get key at [spoonacular.com](https://spoonacular.com/food-api)

### 4. Set Up Database

Run the SQL migrations in your Supabase SQL editor (see `database/migrations/`).

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
freshkeep/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration settings
│   ├── database.py          # Supabase client
│   ├── models/              # Pydantic models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── middleware/          # Auth & error handling
│   └── utils/               # Helper functions
├── database/
│   └── migrations/          # SQL schema files
├── tests/                   # Test suite
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Inventory
- `GET /api/inventory` - List all items
- `GET /api/inventory/expiring` - Items expiring soon
- `POST /api/inventory` - Add item manually
- `POST /api/inventory/receipt` - Add via receipt OCR
- `POST /api/inventory/barcode/{upc}` - Add via barcode
- `PUT /api/inventory/{id}` - Update item
- `DELETE /api/inventory/{id}` - Delete item
- `POST /api/inventory/{id}/consume` - Mark consumed
- `POST /api/inventory/{id}/waste` - Mark wasted

### Recipes
- `GET /api/recipes` - Get recommendations
- `GET /api/recipes/{id}` - Recipe details

### Notifications
- `GET /api/notifications` - List notifications
- `POST /api/notifications/{id}/dismiss` - Mark as read

### Analytics
- `GET /api/analytics/summary` - Quick stats
- `GET /api/analytics/insights` - AI tips

### Shopping List
- `GET /api/shopping-list` - Get list
- `POST /api/shopping-list` - Add item
- `PUT /api/shopping-list/{id}` - Toggle checked

### Family
- `POST /api/family` - Create family
- `POST /api/family/join` - Join via code
- `GET /api/family/members` - List members

### Settings
- `GET /api/settings` - Get preferences
- `PUT /api/settings` - Update preferences

## License

MIT
