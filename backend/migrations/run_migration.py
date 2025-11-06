"""
Migration script to add agent_id column to client table
Run this script to update the database schema
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

# Convert to async URL if needed
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


async def run_migration():
    """Run the migration to add agent_id column"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'client'
                AND COLUMN_NAME = 'agent_id'
            """)
            
            result = await conn.execute(check_query)
            row = result.fetchone()
            
            if row and row[0] > 0:
                print("✓ Column 'agent_id' already exists in 'client' table")
                return
            
            print("Adding 'agent_id' column to 'client' table...")
            
            # Add the column
            alter_query = text("""
                ALTER TABLE client 
                ADD COLUMN agent_id INT NULL AFTER user_id
            """)
            await conn.execute(alter_query)
            
            # Add index for better performance
            index_query = text("""
                CREATE INDEX idx_client_agent_id ON client(agent_id)
            """)
            await conn.execute(index_query)
            
            print("✓ Migration completed successfully!")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("Starting migration: Add agent_id to client table")
    asyncio.run(run_migration())
