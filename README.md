# 🍃 Freshen

**A smart grocery tracking app for Indians to reduce food waste and save money.**

Freshen helps you manage your kitchen inventory, track expiration dates, get recipe suggestions based on what you have, and share your pantry with family members—all designed specifically for Indian households.

---

## ✨ Features

### 📦 Smart Inventory Management
- **Quick Entry**: Add items manually or via barcode scanning
- **Expiration Tracking**: Never let food go bad with smart notifications
- **Organized Storage**: Categorize by Fridge, Freezer, or Pantry
- **Smart Categories**: Auto-categorize by product type

### 📷 Intelligent Scanning
- **🔍 Barcode Scanner**: Instant product lookup with auto-filled details
- **📄 Receipt OCR**: Bulk-add items by scanning grocery receipts
- **🇮🇳 Indian Products**: Built-in database of 80+ popular brands
  - Amul, Britannia, Tata, Parle, DMart, Patanjali, Haldiram's, ITC, and more!

### 🍳 Recipe Recommendations
- **Smart Suggestions**: Recipes based on your current inventory
- **Priority Cooking**: Highlights items expiring soon
- **Indian Cuisine**: Masala Chai, Dal Tadka, Paneer Butter Masala, Biryani, and more

### 👨‍👩‍👧‍👦 Family Sharing
- **Collaborative Pantry**: Share inventory with household members
- **Easy Invites**: Join family groups via unique codes
- **Real-time Sync**: Updates instantly across all devices

### 📊 Waste Analytics & Insights
- **Money Saved**: Track how much you've saved by reducing waste
- **Environmental Impact**: Monitor CO₂ and water conservation
- **Achievement System**: Earn badges for sustainable habits
- **Visual Reports**: Monthly and yearly waste trends

### 🔔 Smart Notifications
- **Expiring Soon Alerts**: Get reminded before items go bad
- **Shopping Reminders**: Never run out of essentials
- **Customizable Settings**: Control notification frequency and timing

---

## 🛠️ Tech Stack

### Mobile App
| Technology | Purpose |
|------------|---------|
| **React Native + Expo** | Cross-platform mobile framework |
| **React Navigation** | Navigation and routing |
| **Expo Camera** | Barcode and receipt scanning |
| **Expo SecureStore** | Secure token storage |
| **AsyncStorage** | Local data persistence |

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **Supabase** | PostgreSQL database with real-time capabilities |
| **JWT** | Secure authentication |
| **OCR.space API** | Receipt text extraction |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18 or higher
- **Python** 3.10 or higher
- **Expo CLI**: `npm install -g expo-cli`
- **Supabase Account** (free tier available)

---

### 📱 Mobile App Setup

#### 1. Navigate to Mobile Directory
```bash
cd mobile
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure API URL
Edit `src/api/client.js` and update your local network IP:

```javascript
const LOCAL_NETWORK_IP = '192.168.1.100';  // Replace with your IP
```

**Find Your IP Address:**
- **macOS/Linux**: `ipconfig getifaddr en0` or `hostname -I`
- **Windows**: `ipconfig` (look for IPv4 Address)

#### 4. Start Development Server
```bash
npx expo start
```

#### 5. Run on Device
- **Physical Device**: Scan QR code with Expo Go app
- **iOS Simulator**: Press `i`
- **Android Emulator**: Press `a`

---

### 🖥️ Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OCR Service
OCR_SPACE_API_KEY=your_ocr_space_key

# Authentication
JWT_SECRET=your_random_secret_string_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Get Your API Keys:**
- **Supabase**: Sign up at [supabase.com](https://supabase.com) → Create Project → Copy keys from Settings
- **OCR.space**: Get free key at [ocr.space/ocrapi](https://ocr.space/ocrapi)

#### 5. Initialize Database
Open your Supabase SQL Editor and run the migration:

```bash
# Run this SQL file in Supabase SQL Editor
database/migrations/001_initial_schema.sql
```

#### 6. Start the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. Verify Installation
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: `curl http://localhost:8000/health`

---

## 📱 App Screens

| Screen | Description |
|--------|-------------|
| **🏠 Home** | Dashboard with quick stats and expiring items widget |
| **📦 Inventory** | Complete item list with search and filters |
| **➕ Add Item** | Manual item entry with smart defaults |
| **📷 Scan Barcode** | Camera-based barcode scanner with instant lookup |
| **🧾 Scan Receipt** | OCR-powered receipt scanning for bulk entry |
| **🍳 Recipes** | AI-powered recipe suggestions from your inventory |
| **🛒 Shopping List** | Smart shopping list that learns your habits |
| **👨‍👩‍👧‍👦 Family** | Create and manage family groups |
| **📊 Analytics** | Waste tracking, savings, and achievements |
| **⚙️ Settings** | Profile management and app preferences |

---

## 🇮🇳 Indian Product Database

Built-in support for 80+ popular Indian brands:

### 🥛 Dairy & Beverages
- **Amul** - Butter, Milk, Cheese, Paneer
- **Mother Dairy** - Milk, Curd, Butter
- **Nandini** - Milk, Ghee

### 🍪 Snacks & Biscuits
- **Britannia** - Good Day, Marie Gold, Bread
- **Parle** - Parle-G, Monaco, Hide & Seek
- **Sunfeast** - Dark Fantasy, Marie Light

### 🍜 Packaged Foods
- **Nestle** - Maggi Noodles, KitKat
- **ITC** - Aashirvaad Atta, Bingo Chips
- **MTR** - Ready-to-Eat, Spice Mixes

### 🌾 Staples & Groceries
- **Tata** - Tea, Salt, Sampann Dal
- **DMart** - Rice, Dal, Atta, Oil
- **Fortune** - Rice Bran Oil, Soya Chunks

### 🌿 Health & Wellness
- **Patanjali** - Ghee, Atta, Honey, Chyawanprash
- **Dabur** - Honey, Chyawanprash

### 🥘 Snacks & Namkeen
- **Haldiram's** - Bhujia, Namkeen, Sweets
- **Bikaji** - Namkeen, Bhujia

*And 50+ more brands across all categories!*

---

## 🔌 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register new user account |
| `POST` | `/api/auth/login` | Login and receive access token |
| `POST` | `/api/auth/refresh` | Refresh expired access token |
| `GET` | `/api/auth/me` | Get current user profile |

### Inventory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/inventory` | List all inventory items |
| `POST` | `/api/inventory` | Add new item manually |
| `GET` | `/api/inventory/barcode/{upc}` | Lookup product by barcode |
| `POST` | `/api/inventory/receipt` | Scan receipt with OCR |
| `PUT` | `/api/inventory/{id}` | Update item details |
| `DELETE` | `/api/inventory/{id}` | Remove item |
| `POST` | `/api/inventory/{id}/consume` | Mark item as consumed |
| `POST` | `/api/inventory/{id}/waste` | Mark item as wasted |

### Recipe Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recipes` | Get recipe recommendations |
| `GET` | `/api/recipes/{id}` | Get detailed recipe information |

### Family Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/family` | Create new family group |
| `POST` | `/api/family/join` | Join existing family via code |
| `GET` | `/api/family/members` | List all family members |
| `DELETE` | `/api/family/members/{id}` | Remove family member |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/summary` | Get quick statistics |
| `GET` | `/api/analytics/insights` | Get AI-powered insights |

---

## 📁 Project Structure

```
freshen/
├── mobile/                     # React Native mobile app
│   ├── src/
│   │   ├── screens/           # App screens
│   │   ├── components/        # Reusable components
│   │   ├── api/               # API client
│   │   ├── navigation/        # Navigation setup
│   │   └── utils/             # Helper functions
│   ├── app.json
│   └── package.json
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry
│   │   ├── models/            # Data models
│   │   ├── routes/            # API routes
│   │   ├── services/          # Business logic
│   │   └── database.py        # Database connection
│   ├── database/
│   │   └── migrations/        # SQL migrations
│   ├── requirements.txt
│   └── .env.example
│
└── README.md                   # This file
```

---

## 🐛 Troubleshooting

### Mobile App Issues

**Cannot Connect to Backend:**
```bash
# Ensure both devices are on same WiFi network
# Check firewall isn't blocking port 8000
# Verify IP address in src/api/client.js is correct
```

**Expo Start Fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npx expo start --clear
```

**Camera Not Working:**
- Ensure app has camera permissions
- On iOS: Settings → Freshen → Camera → Allow
- On Android: Settings → Apps → Freshen → Permissions → Camera

### Backend Issues

**Database Connection Failed:**
```bash
# Verify Supabase credentials in .env
python -c "from app.database import supabase; print(supabase)"
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

**OCR Not Working:**
- Check OCR.space API key is valid
- Ensure image size is under 1MB
- Supported formats: JPG, PNG, PDF

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest

# With coverage
pytest --cov=app tests/
```

### Mobile Tests
```bash
cd mobile
npm test

# E2E tests (requires Detox setup)
npm run test:e2e
```

---

## 🚀 Deployment

### Backend Deployment (Heroku)
```bash
cd backend
heroku create freshen-api
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_ANON_KEY=your_key
git push heroku main
```

### Mobile App Deployment
```bash
cd mobile

# Build for Android
eas build --platform android

# Build for iOS (requires Apple Developer account)
eas build --platform ios
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Write clear commit messages
- Add tests for new features
- Update documentation as needed

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **React Native Community** for the excellent mobile framework
- **FastAPI** for the blazing-fast backend framework
- **Supabase** for database and authentication services
- **OCR.space** for receipt scanning capabilities
- **Indian households** for inspiration and feedback

---

## 📞 Support

Having issues? We're here to help!

- **📧 Email**: support@freshen.app
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/yourusername/freshen/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/freshen/discussions)

---

**Built with ❤️ for India — reducing food waste, one kitchen at a time.**

*Star ⭐ this repo if Freshen helps you save food and money!*
