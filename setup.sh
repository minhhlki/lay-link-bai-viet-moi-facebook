#!/bin/bash

echo "=========================================="
echo "  Facebook Group Scraper - Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Tạo virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Nâng cấp pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Cài đặt dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Cài đặt Playwright browsers..."
playwright install chromium

echo ""
echo "=========================================="
echo "✅ Setup hoàn tất!"
echo "=========================================="
echo ""
echo "Để sử dụng tool:"
echo "  1. Kích hoạt virtual environment: source venv/bin/activate"
echo "  2. Chạy tool: python facebook_group_scraper.py"
echo ""
