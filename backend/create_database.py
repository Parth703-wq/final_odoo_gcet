"""
Create MySQL database for Rental Management System
"""

import pymysql

try:
    # Connect to MySQL server (not to a specific database)
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password=''
    )
    
    cursor = connection.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS rental_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("✓ Database 'rental_management_db' created successfully!")
    
    cursor.close()
    connection.close()
    
except pymysql.Error as e:
    print(f"✗ Error creating database: {e}")
    exit(1)
