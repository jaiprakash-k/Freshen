# Freshen Backend 🥬

A scalable, real-time backend system for **Freshen** — a smart grocery management app that reduces food waste through OCR receipt scanning, barcode lookup, expiration tracking, recipe suggestions, family sharing, and analytics.

---

## 🚀 Features

- **📸 Smart Receipt Scanning**: OCR-powered receipt processing to automatically add items
- **🔍 Barcode Lookup**: Instant product identification via UPC codes
- **⏰ Expiration Tracking**: Smart notifications for items nearing expiry
- **🍳 Recipe Suggestions**: AI-powered recommendations based on available ingredients
- **👨‍👩‍👧‍👦 Family Sharing**: Collaborative inventory management across households
- **📊 Waste Analytics**: Track consumption patterns and reduce waste
- **🎙️ Voice Feedback**: Text-to-speech notifications via ElevenLabs
- **🛒 Smart Shopping Lists**: Auto-generated lists based on consumption habits

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database** | Supabase (PostgreSQL) |
| **OCR Engine** | OCR.space API |
| **Text-to-Speech** | ElevenLabs API |
| **Recipe Data** | Spoonacular API |
| **Authentication** | JWT tokens |
| **Real-time** | WebSockets |

---

## ⚡ Quick Start

### 1. Clone and Setup Environment

```bash
cd freshen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OCR
OCR_SPACE_API_KEY=your_ocr_space_key

# Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_key

# Recipes
SPOONACULAR_API_KEY=your_spoonacular_key

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

**Get Your API Keys:**
- **Supabase**: [Create project at supabase.com](https://supabase.com)
- **OCR.space**: [Get free key at ocr.space](https://ocr.space/ocrapi)
- **ElevenLabs**: [Get key at elevenlabs.io](https://elevenlabs.io)
- **Spoonacular**: [Get key at spoonacular.com](https://spoonacular.com/food-api)

### 4. Initialize Database

Run the SQL migrations in your Supabase SQL editor:

```bash
# Apply migrations in order
database/migrations/001_init_schema.sql
database/migrations/002_add_indexes.sql
database/migrations/003_add_functions.sql
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Installation

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: `curl http://localhost:8000/health`

---

## 📁 Project Structure

```
freshen/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Supabase client initialization
│   ├── models/                 # Pydantic request/response models
│   │   ├── user.py
│   │   ├── inventory.py
│   │   ├── recipe.py
│   │   └── analytics.py
│   ├── routes/                 # API endpoint definitions
│   │   ├── auth.py
│   │   ├── inventory.py
│   │   ├── recipes.py
│   │   ├── notifications.py
│   │   ├── analytics.py
│   │   ├── shopping_list.py
│   │   ├── family.py
│   │   └── settings.py
│   ├── services/               # Business logic layer
│   │   ├── ocr_service.py
│   │   ├── barcode_service.py
│   │   ├── recipe_service.py
│   │   ├── notification_service.py
│   │   └── tts_service.py
│   ├── middleware/             # Authentication & error handling
│   │   ├── auth_middleware.py
│   │   └── error_handler.py
│   └── utils/                  # Helper functions
│       ├── jwt_utils.py
│       ├── validators.py
│       └── formatters.py
├── database/
│   └── migrations/             # SQL schema migrations
│       ├── 001_init_schema.sql
│       ├── 002_add_indexes.sql
│       └── 003_add_functions.sql
├── tests/                      # Test suite
│   ├── test_auth.py
│   ├── test_inventory.py
│   └── test_recipes.py
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register new user |
| `POST` | `/api/auth/login` | Login and receive JWT |
| `POST` | `/api/auth/refresh` | Refresh access token |
| `GET` | `/api/auth/me` | Get current user profile |

### Inventory Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/inventory` | List all inventory items |
| `GET` | `/api/inventory/expiring` | Get items expiring soon |
| `POST` | `/api/inventory` | Add item manually |
| `POST` | `/api/inventory/receipt` | Add items via receipt OCR |
| `POST` | `/api/inventory/barcode/{upc}` | Add item via barcode scan |
| `PUT` | `/api/inventory/{id}` | Update inventory item |
| `DELETE` | `/api/inventory/{id}` | Remove item |
| `POST` | `/api/inventory/{id}/consume` | Mark item as consumed |
| `POST` | `/api/inventory/{id}/waste` | Mark item as wasted |

### Recipes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recipes` | Get recipe recommendations |
| `GET` | `/api/recipes/{id}` | Get detailed recipe info |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notifications` | List all notifications |
| `POST` | `/api/notifications/{id}/dismiss` | Mark notification as read |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/summary` | Get quick statistics |
| `GET` | `/api/analytics/insights` | Get AI-powered insights |

### Shopping List

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/shopping-list` | Get shopping list |
| `POST` | `/api/shopping-list` | Add item to list |
| `PUT` | `/api/shopping-list/{id}` | Toggle item checked status |
| `DELETE` | `/api/shopping-list/{id}` | Remove item from list |

### Family Sharing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/family` | Create family group |
| `POST` | `/api/family/join` | Join family via invite code |
| `GET` | `/api/family/members` | List family members |
| `DELETE` | `/api/family/members/{id}` | Remove family member |

### Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/settings` | Get user preferences |
| `PUT` | `/api/settings` | Update preferences |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_inventory.py

# Run with verbose output
pytest -v
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Verify Supabase credentials
python -c "from app.database import supabase; print(supabase)"
```

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use alternative port
uvicorn app.main:app --reload --port 8001
```

### OCR Not Working

- Verify OCR.space API key is valid
- Check image file size (max 1MB for free tier)
- Ensure image format is supported (JPG, PNG, PDF)

### Missing Dependencies

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Database Schema

### Core Tables

- **users**: User accounts and authentication
- **inventory_items**: Food items and expiration dates
- **families**: Shared household groups
- **family_members**: User-family relationships
- **recipes**: Cached recipe data
- **notifications**: User alerts and reminders
- **shopping_list**: Shopping list items
- **analytics_events**: Usage tracking and insights

---

## 🔐 Security

- JWT-based authentication with token refresh
- Password hashing with bcrypt
- Rate limiting on sensitive endpoints
- Input validation with Pydantic
- SQL injection prevention via parameterized queries
- CORS configuration for frontend integration

---

## 🚀 Deployment

### Using Docker

```bash
# Build image
docker build -t freshen-backend .

# Run container
docker run -p 8000:8000 --env-file .env freshen-backend
```

### Using Heroku

```bash
heroku create freshen-api
heroku config:set SUPABASE_URL=your_url
# ... set other environment variables
git push heroku main
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Supabase** for backend infrastructure
- **OCR.space** for receipt processing
- **Spoonacular** for recipe data
- **ElevenLabs** for voice synthesis

---

**Built with ❤️ to reduce food waste and save money**

*Star ⭐ this repo if Freshen helps you keep your groceries fresh!*
