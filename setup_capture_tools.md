# 📱 NYC Nightlife Capture Tools Setup

## 🖥️ Mac Desktop Tool

### Installation
```bash
# Install required packages
pip install tkinter requests

# Run the Mac capture tool
python mac_capture_tool.py
```

### Features
- **Native macOS screenshots** (Cmd+Shift+3/4 equivalent)
- **Screen recording** using built-in macOS tools
- **Drag & drop file selection**
- **Direct upload** to NYC Nightlife API
- **Native Mac UI** with SF Pro Display font

### Usage
1. **Launch the app**: `python mac_capture_tool.py`
2. **Capture content**:
   - Click "Screenshot (Selection)" for area selection
   - Click "Screenshot (Full Screen)" for full screen
   - Click "Screen Recording" for video capture
3. **Fill in details**: Select venue, content type, add caption
4. **Upload**: Click "Upload to NYC Nightlife"

---

## 📱 iPhone iOS PWA (Progressive Web App)

### Setup
1. **Add route to your API server** (add to `secure_api_server.py`):

```python
@app.get("/ios", response_class=HTMLResponse)
async def ios_webapp():
    with open("ios_webapp.html", "r") as f:
        return f.read()

@app.get("/manifest.json")
async def manifest():
    with open("manifest.json", "r") as f:
        return Response(content=f.read(), media_type="application/json")

@app.get("/sw.js")
async def service_worker():
    with open("sw.js", "r") as f:
        return Response(content=f.read(), media_type="application/javascript")
```

2. **Update the HTML head section** in `ios_webapp.html`:

```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#667eea">
```

### Installation on iPhone
1. **Open Safari** on iPhone
2. **Navigate to**: `http://your-server:8001/ios`
3. **Tap Share button** (box with arrow)
4. **Tap "Add to Home Screen"**
5. **App appears on home screen** like native app

### Features
- **Native camera access** for photos/videos
- **Touch-optimized interface**
- **Offline capable** (PWA)
- **Full-screen app experience**
- **iOS-style design** with blur effects

---

## 🚀 Quick Start Commands

### Mac Tool
```bash
cd /Users/cecilcoleman/nyc-nightlife-api/nyc-nightlife-api/nightlife_project
python mac_capture_tool.py
```

### Add iOS routes to server
Add these lines to your `secure_api_server.py`:

```python
@app.get("/ios", response_class=HTMLResponse)
async def ios_webapp():
    with open("ios_webapp.html", "r") as f:
        return f.read()

@app.get("/manifest.json")
async def manifest():
    with open("manifest.json", "r") as f:
        return Response(content=f.read(), media_type="application/json")

@app.get("/sw.js") 
async def service_worker():
    with open("sw.js", "r") as f:
        return Response(content=f.read(), media_type="application/javascript")
```

Then visit `http://localhost:8001/ios` on your iPhone!

---

## 📋 Features Comparison

| Feature | Mac Tool | iOS PWA |
|---------|----------|---------|
| Screenshots | ✅ Native macOS | ✅ Camera API |
| Screen Recording | ✅ Built-in tools | ✅ Video recording |
| File Upload | ✅ Drag & drop | ✅ Camera capture |
| Offline Mode | ❌ | ✅ PWA cache |
| Native Feel | ✅ Tkinter | ✅ iOS design |
| Install Required | ✅ Python | ❌ Web-based |

Both tools upload directly to your NYC Nightlife API and integrate seamlessly with the existing venue system!