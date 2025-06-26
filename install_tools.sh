#!/bin/bash

echo "Installing NYC Nightlife Content Tools..."

# Install Python dependencies
pip install requests pillow pyautogui opencv-python

echo "✅ Installation complete!"
echo ""
echo "Available tools:"
echo "1. Content Submission Tool: python content_submission_tool.py"
echo "2. Screen Capture Tool: python screen_capture_tool.py"
echo "3. Instagram Guide: open instagram_guide.html in browser"
echo ""
echo "⚠️  Legal Notice:"
echo "These tools are for submitting your own content or content you have permission to share."
echo "Always respect copyright and platform terms of service."