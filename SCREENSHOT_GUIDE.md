# 📸 Dashboard Screenshot Guide

## Screenshots Needed for README

Save all screenshots in the `dashboard/` folder with these exact names:

### 1. **dashboard-main.png**
**What to capture**: Main dashboard overview showing:
- Violation statistics cards (Total Alerts, No Helmet, No Vest, No Helmet + No Vest)
- Alerts history table with multiple entries
- All UI elements visible

**How to capture**:
1. Run `python app.py` in backend
2. Run `npm start` in frontend
3. Process 2-3 test videos (test3.mp4, test4.mp4, test5.mp4)
4. Wait for processing to complete
5. Scroll to show full dashboard
6. Take screenshot

---

### 2. **live-detection.png**
**What to capture**: Real-time detection window showing:
- Multiple workers with colored bounding boxes
- Green box (Safe worker)
- Orange/Yellow/Red boxes (Violations)
- Worker IDs and status labels
- Frame counter and stats overlay

**How to capture**:
1. Run detection on test11.mp4 (has 3 workers)
2. Pause when all 3 workers are visible
3. Take screenshot of the OpenCV window
4. Should show: "Worker 1 | No Vest" (yellow), "Worker 2 | Safe" (green), "Worker 3 | No Helmet" (orange)

---

### 3. **alert-details.png**
**What to capture**: Alert details showing:
- Alert history table with multiple rows
- Timestamps column
- Violation types column
- Screenshot column with "View" buttons
- At least 5-6 alert entries visible

**How to capture**:
1. After processing videos, scroll to Alerts History section
2. Ensure multiple alerts are visible
3. Capture the full table with variety of violation types

---

### 4. **analytics.png**
**What to capture**: Statistics breakdown showing:
- Large statistics cards at top
- Different colors for each violation type
- Numbers showing breakdown
- Professional dashboard layout

**How to capture**:
1. Same as dashboard-main.png but focus on the statistics cards
2. Crop to show just the top section with stats
3. Make sure all 4 cards are visible

---

## Optional Screenshots (Bonus)

### 5. **violation-screenshot.png**
A close-up of an actual violation screenshot from the database:
- Shows a worker with red bounding box
- Clear violation label
- Worker ID visible

### 6. **dashboard-mobile.png**
Dashboard on mobile/tablet view (if responsive)

---

## Screenshot Tips

### Quality
- **Resolution**: 1920x1080 or higher
- **Format**: PNG (better quality than JPG)
- **Clarity**: Ensure text is readable
- **Lighting**: Use good screen brightness

### Composition
- **Frame it well**: Include relevant UI elements
- **No clutter**: Close unnecessary browser tabs
- **Professional**: Clean browser UI, no personal bookmarks visible

### Tools
- **Windows**: `Windows + Shift + S` (Snipping Tool)
- **Browser**: F12 → Device toolbar for responsive screenshots
- **Full page**: Browser extensions like "Full Page Screen Capture"

---

## After Capturing Screenshots

1. Save all images in `dashboard/` folder
2. Use exact filenames as listed above
3. Verify images display correctly in README:
   ```bash
   # Preview README
   code README.md  # or open in VS Code
   ```
4. Push to GitHub:
   ```bash
   git add dashboard/
   git add README.md
   git commit -m "Add dashboard screenshots"
   git push
   ```

---

## Testing README Display

View your README on GitHub to ensure images display correctly:
- Images should load without broken links
- Proper aspect ratios maintained
- Professional appearance

---

**Current Status**: 
- ✅ Dashboard folder created
- ✅ README.md created with image placeholders
- ⏳ Screenshots pending (follow this guide)

**Next Steps**:
1. Run the application
2. Process test videos
3. Capture screenshots as described above
4. Save in `dashboard/` folder with correct names
5. Verify README displays correctly
