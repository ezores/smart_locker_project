"""
Smart Locker System - Export Test Script

@author Alp
@date 2024-12-XX
@description Test script to verify Excel and PDF export functionality
"""

import requests
import os
from datetime import datetime, timedelta

def test_exports():
    """Test Excel and PDF export functionality"""
    
    base_url = "http://localhost:5050"
    
    # Test data
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print("🧪 Testing Smart Locker System Export Functionality")
    print("=" * 50)
    
    # Test Excel export
    print("\nTesting Excel Export...")
    try:
        excel_url = f"{base_url}/api/admin/export?format=xlsx&start_date={start_date}&end_date={end_date}"
        response = requests.get(excel_url)
        
        if response.status_code == 200:
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Excel export successful: {filename}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"Excel export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"Excel export error: {e}")
    
    # Test PDF export
    print("\n📄 Testing PDF Export...")
    try:
        pdf_url = f"{base_url}/api/admin/export?format=pdf&start_date={start_date}&end_date={end_date}"
        response = requests.get(pdf_url)
        
        if response.status_code == 200:
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"PDF export successful: {filename}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"PDF export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"PDF export error: {e}")
    
    # Test CSV fallback
    print("\n📋 Testing CSV Fallback...")
    try:
        csv_url = f"{base_url}/api/admin/export?format=csv&start_date={start_date}&end_date={end_date}"
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"CSV export successful: {filename}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"CSV export failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"CSV export error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Export testing completed!")
    print("📁 Check the generated files in the current directory")

if __name__ == "__main__":
    test_exports() 