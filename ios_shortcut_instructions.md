# 📱 iOS Shortcut for NYC Nightlife Content Capture

## Quick Setup Instructions

### Method 1: iOS Shortcuts App (Recommended)

1. **Open Shortcuts app** on your iPhone
2. **Tap the "+" to create new shortcut**
3. **Add these actions in order:**

#### Action 1: Take Photo/Video
- Add Action → Camera → "Take Photo" or "Take Video"
- Set to "Ask Each Time" for photo/video choice

#### Action 2: Get Text Input
- Add Action → Scripting → "Ask for Input" 
- Input Type: Text
- Prompt: "Enter caption (optional)"
- Allow Multiple Lines: ON

#### Action 3: Choose from Menu
- Add Action → Scripting → "Choose from Menu"
- Prompt: "Select Content Type"
- Menu Items: "Story (24h)", "Post (Permanent)"

#### Action 4: Choose Venue
- Add Action → Scripting → "Choose from Menu"
- Prompt: "Select Venue"
- Menu Items: Add your venues like:
  - "House of Yes - Bushwick"
  - "Elsewhere - Bushwick" 
  - "Output - Williamsburg"
  - etc.

#### Action 5: Upload to API
- Add Action → Web → "Get Contents of URL"
- URL: `http://localhost:8001/api/content`
- Method: POST
- Headers:
  - Content-Type: multipart/form-data
- Request Body: 
  - venue_id: [from venue choice]
  - content_type: [from type choice] 
  - caption: [from text input]
  - file: [from photo/video]

#### Action 6: Show Result
- Add Action → Scripting → "Show Notification"
- Title: "NYC Nightlife Upload"
- Body: "Content uploaded successfully!"

### Method 2: Simple Mobile Web App

Create a mobile-optimized web app that works like an iOS app: