#!/usr/bin/env python3

"""
=============================================================================
Smart Locker System - Database Migration Script
=============================================================================
Version: 2.0.0
Author: Alp Alpdogan
License: MIT - This program can only be used while keeping the names
         of Mehmet Ugurlu & Yusuf Alpdogan in their honor

In Memory of:
  Mehmet Ugurlu & Yusuf Alpdogan
  May their legacy inspire innovation and excellence
=============================================================================

Database migration script to update Log table for enhanced logging capabilities.
"""

import os
import sys
from sqlalchemy import text
from app import app, db

def migrate_log_table():
    """Migrate the Log table to support enhanced logging"""
    with app.app_context():
        try:
            # Check if we need to update the action_type column length
            result = db.session.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'log' AND column_name = 'action_type'
            """))
            
            column_info = result.fetchone()
            if column_info:
                current_length = column_info[2]
                print(f"Current action_type column length: {current_length}")
                
                if current_length and current_length < 64:
                    print("Updating action_type column to VARCHAR(64)...")
                    db.session.execute(text("""
                        ALTER TABLE log 
                        ALTER COLUMN action_type TYPE VARCHAR(64)
                    """))
                    db.session.commit()
                    print("SUCCESS: action_type column updated successfully")
                else:
                    print("SUCCESS: action_type column already has sufficient length")
            else:
                print("ERROR: Could not find action_type column")
                
            # Check if ip_address and user_agent columns exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'log' AND column_name IN ('ip_address', 'user_agent')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'ip_address' not in existing_columns:
                print("Adding ip_address column...")
                db.session.execute(text("""
                    ALTER TABLE log 
                    ADD COLUMN ip_address VARCHAR(45)
                """))
                print("SUCCESS: ip_address column added")
                
            if 'user_agent' not in existing_columns:
                print("Adding user_agent column...")
                db.session.execute(text("""
                    ALTER TABLE log 
                    ADD COLUMN user_agent TEXT
                """))
                print("SUCCESS: user_agent column added")
                
            db.session.commit()
            print("SUCCESS: Database migration completed successfully")
            
        except Exception as e:
            print(f"ERROR: Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

def create_indexes():
    """Create indexes for better query performance on logs"""
    with app.app_context():
        try:
            # Create indexes for common log queries
            indexes = [
                ("CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log(timestamp)", "timestamp"),
                ("CREATE INDEX IF NOT EXISTS idx_log_action_type ON log(action_type)", "action_type"),
                ("CREATE INDEX IF NOT EXISTS idx_log_user_id ON log(user_id)", "user_id"),
                ("CREATE INDEX IF NOT EXISTS idx_log_ip_address ON log(ip_address)", "ip_address"),
            ]
            
            for index_sql, index_name in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"SUCCESS: Created index: {index_name}")
                except Exception as e:
                    print(f"WARNING: Index {index_name} already exists or failed: {e}")
                    
            db.session.commit()
            print("SUCCESS: Indexes created successfully")
            
        except Exception as e:
            print(f"ERROR: Index creation failed: {e}")
            db.session.rollback()
            return False
            
    return True

def main():
    """Main migration function"""
    print("Smart Locker System - Database Migration")
    print("========================================")
    print("Author: Alp Alpdogan")
    print()
    
    print("Starting database migration...")
    
    # Run migrations
    if migrate_log_table():
        print("SUCCESS: Log table migration successful")
    else:
        print("ERROR: Log table migration failed")
        sys.exit(1)
        
    if create_indexes():
        print("SUCCESS: Index creation successful")
    else:
        print("ERROR: Index creation failed")
        sys.exit(1)
        
    print()
    print("SUCCESS: Database migration completed successfully!")
    print("The logging system is now ready for enhanced tracking.")
    print()
    print("New logging capabilities:")
    print("- Authentication events (login, logout, failed attempts)")
    print("- User registration events")
    print("- Admin actions (locker management, user management)")
    print("- Security events (JWT errors, access attempts)")
    print("- IP address and user agent tracking")
    print("- Comprehensive audit trail")

if __name__ == "__main__":
    main() 