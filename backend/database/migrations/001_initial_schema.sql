-- FreshKeep Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    family_id UUID,
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_family ON users(family_id);

-- ============================================
-- FAMILIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS families (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    admin_id UUID NOT NULL REFERENCES users(id),
    invite_code VARCHAR(10) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add foreign key constraint to users
ALTER TABLE users ADD CONSTRAINT fk_users_family 
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET NULL;

-- ============================================
-- FAMILY MEMBERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS family_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'editor' CHECK (role IN ('admin', 'editor', 'viewer')),
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);

CREATE INDEX idx_family_members_family ON family_members(family_id);
CREATE INDEX idx_family_members_user ON family_members(user_id);

-- ============================================
-- ITEMS TABLE (Inventory)
-- ============================================
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 1,
    unit VARCHAR(20) DEFAULT 'piece',
    category VARCHAR(50) DEFAULT 'other',
    storage VARCHAR(20) DEFAULT 'fridge' CHECK (storage IN ('fridge', 'freezer', 'pantry')),
    purchase_date DATE DEFAULT CURRENT_DATE,
    expiration_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'consumed', 'wasted', 'expired', 'deleted')),
    notes TEXT,
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_items_user ON items(user_id);
CREATE INDEX idx_items_family ON items(family_id);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_expiration ON items(expiration_date);
CREATE INDEX idx_items_category ON items(category);

-- ============================================
-- CONSUMPTION LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS consumption_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    quantity_consumed DECIMAL(10,2),
    consumed_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_consumption_item ON consumption_logs(item_id);
CREATE INDEX idx_consumption_user ON consumption_logs(user_id);

-- ============================================
-- WASTE LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS waste_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    wasted_at TIMESTAMP DEFAULT NOW(),
    reason VARCHAR(50) DEFAULT 'forgot',
    feedback_text TEXT,
    photo_url TEXT,
    estimated_value DECIMAL(10,2),
    co2_impact_kg DECIMAL(10,2),
    water_impact_liters DECIMAL(10,2)
);

CREATE INDEX idx_waste_item ON waste_logs(item_id);
CREATE INDEX idx_waste_user ON waste_logs(user_id);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    read BOOLEAN DEFAULT FALSE,
    voice_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, read);

-- ============================================
-- SHOPPING LISTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS shopping_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT 'Shopping List',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shopping_lists_user ON shopping_lists(user_id);
CREATE INDEX idx_shopping_lists_family ON shopping_lists(family_id);

-- ============================================
-- SHOPPING ITEMS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS shopping_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_id UUID NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 1,
    unit VARCHAR(20) DEFAULT 'piece',
    category VARCHAR(50),
    checked BOOLEAN DEFAULT FALSE,
    added_by UUID REFERENCES users(id),
    added_by_name VARCHAR(100),
    notes VARCHAR(200),
    auto_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shopping_items_list ON shopping_items(list_id);

-- ============================================
-- ANALYTICS DAILY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    items_saved INTEGER DEFAULT 0,
    money_saved DECIMAL(10,2) DEFAULT 0,
    co2_prevented_kg DECIMAL(10,2) DEFAULT 0,
    water_saved_liters DECIMAL(10,2) DEFAULT 0,
    waste_count INTEGER DEFAULT 0,
    waste_cost DECIMAL(10,2) DEFAULT 0,
    waste_co2 DECIMAL(10,2) DEFAULT 0,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_analytics_user_date ON analytics_daily(user_id, date);

-- ============================================
-- ACHIEVEMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(10) DEFAULT '🏅',
    target INTEGER DEFAULT 1
);

-- Insert default achievements
INSERT INTO achievements (id, name, description, icon, target) VALUES
    ('first_save', 'First Save', 'Saved your first item from waste', '🌱', 1),
    ('week_streak_7', 'Week Warrior', '7-day streak without waste', '🔥', 7),
    ('month_streak_30', 'Monthly Master', '30-day streak without waste', '🏆', 30),
    ('saved_10', 'Food Saver', 'Saved 10 items from waste', '⭐', 10),
    ('saved_50', 'Waste Fighter', 'Saved 50 items from waste', '🌟', 50),
    ('saved_100', 'Eco Champion', 'Saved 100 items from waste', '💫', 100),
    ('money_saved_50', 'Budget Conscious', 'Saved $50 worth of food', '💰', 50),
    ('money_saved_100', 'Smart Saver', 'Saved $100 worth of food', '💎', 100)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- USER ACHIEVEMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id VARCHAR(50) NOT NULL REFERENCES achievements(id),
    unlocked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements ON user_achievements(user_id);

-- ============================================
-- USER SETTINGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    notifications JSONB DEFAULT '{"enabled": true, "morning_alert_time": "07:00", "evening_reminder": true}',
    food JSONB DEFAULT '{"dietary_restrictions": [], "allergies": []}',
    expiration JSONB DEFAULT '{"mode": "standard", "auto_extend_freezer": true}'
);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_items ENABLE ROW LEVEL SECURITY;

-- Note: Configure RLS policies based on your auth setup
-- For service role access, RLS is bypassed
