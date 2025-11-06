-- Migration: Add agent_id column to client table
-- Date: 2025-11-06

-- Add the agent_id column to the client table
ALTER TABLE client 
ADD COLUMN agent_id INT NULL AFTER user_id;

-- Optional: Add index for better performance
CREATE INDEX idx_client_agent_id ON client(agent_id);
