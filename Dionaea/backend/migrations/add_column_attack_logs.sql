-- Add new columns to attack_logs table

ALTER TABLE attack_logs ADD COLUMN IF NOT EXISTS raw_log TEXT;
ALTER TABLE attack_logs ADD COLUMN IF NOT EXISTS attack_type VARCHAR(50);
