/*
  # Initial database schema for Scout Teams Management System

  1. Tables
    - teams: Stores scout team information
    - inventory: Stores available items and their costs
    - action_logs: Stores system activity logs
  
  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated access
*/

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    leader TEXT NOT NULL,
    assistants TEXT,
    resources TEXT,
    balance INTEGER DEFAULT 0,
    expiration_date DATE,
    points INTEGER DEFAULT 0,
    penalties TEXT,
    last_charge_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_loan TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_name TEXT NOT NULL,
    point_cost INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Action logs table
CREATE TABLE IF NOT EXISTS action_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    action TEXT NOT NULL,
    team_name TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_logs ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for authenticated users" ON teams
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable read access for authenticated users" ON inventory
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable read access for authenticated users" ON action_logs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable insert for authenticated users" ON teams
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable insert for authenticated users" ON inventory
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable insert for authenticated users" ON action_logs
    FOR INSERT TO authenticated WITH CHECK (true);