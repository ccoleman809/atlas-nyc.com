# Google Analytics 4 Setup for Atlas-NYC

## ✅ What's Already Implemented

Google Analytics 4 tracking code has been added to your site and will track:
- **Page views** and session data
- **Search events** (successful searches, no results)
- **Neighborhood filtering** events
- **Venue interactions** (map markers, venue cards)
- **Performance metrics** (page load times)

## 🔧 Setup Required (FREE)

### Step 1: Create Google Analytics Account
1. Go to [Google Analytics](https://analytics.google.com/)
2. Sign in with your Google account
3. Click "Start measuring" or "Create Account"
4. Set up a new property for "Atlas-NYC"

### Step 2: Get Your Measurement ID
1. In Google Analytics, go to Admin (bottom left)
2. Select your property
3. Click "Data Streams"
4. Click "Add stream" → "Web"
5. Enter your domain (e.g., `atlas-nyc.onrender.com`)
6. Copy the **Measurement ID** (format: G-XXXXXXXXXX)

### Step 3: Update Your Site
Replace `G-XXXXXXXXXX` in two places in `atlas_public_interface.html`:
- Line 51: `<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>`
- Line 58: `gtag('config', 'G-XXXXXXXXXX', {`

### Step 4: Deploy and Verify
1. Commit and push your changes
2. Visit your live site
3. In Google Analytics, go to Reports → Realtime
4. You should see your visit in real-time!

## 📊 What You'll Track

Once set up, you'll see data for:
- **Visitors** and page views
- **Search behavior** (what people search for)
- **Popular neighborhoods** (which areas get filtered most)
- **User engagement** (time on site, bounce rate)
- **Performance** (page load speeds)

## 💰 Cost
**Completely FREE** - Google Analytics 4 is free for standard use (up to 10 million events per month).

## 🚀 Next Steps
After setup, you can create custom dashboards and reports to understand your users better!