# PPE Compliance Monitoring System - Frontend

A clean, professional React frontend for monitoring Personal Protective Equipment (PPE) compliance violations in industrial settings.

## Features

- **Video Upload & Processing**: Upload videos and process them through the backend YOLO detection system
- **Real-time Statistics**: View violation counts by type (No Helmet, No Vest, Both)
- **Alerts Dashboard**: Browse all detected violations with timestamps and screenshots
- **Screenshot Viewer**: Click to view full-size violation screenshots in modal
- **Backend Status**: Monitor backend connection status in real-time

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **React Icons** - Icon library

## Project Structure

```
src/
├── components/
│   ├── Header.jsx           # Header with backend status
│   ├── UploadCard.jsx       # Video upload and processing
│   ├── StatsCards.jsx       # Statistics cards display
│   ├── AlertsTable.jsx      # Alerts table with screenshots
│   ├── ScreenshotModal.jsx  # Full-size screenshot viewer
│   └── Loader.jsx           # Loading spinner
├── pages/
│   └── Dashboard.jsx        # Main dashboard page
├── services/
│   └── api.js               # API service layer
├── App.jsx                  # Root component
├── App.css                  # Custom styles
├── index.css                # Global styles with Tailwind
└── main.jsx                 # Entry point
```

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Backend Integration

The frontend expects the backend API to be running on `http://localhost:8000` with the following endpoints:

- `GET /` - Health check
- `POST /upload` - Upload video file
- `POST /process?file_name={filename}` - Process uploaded video
- `GET /alerts` - Get all alerts
- `GET /screenshots/{filename}` - Get screenshot image

To change the backend URL, edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Usage Workflow

1. **Upload Video**: Click "Choose video file" and select a .mp4 file
2. **Upload**: Click "Upload Video" to send the file to backend
3. **Process**: Click "Process Video" to run PPE detection
4. **View Results**: See statistics cards update with violation counts
5. **Review Alerts**: Scroll down to view detailed alerts table
6. **View Screenshots**: Click "View" on any alert to see the violation screenshot

## Design Philosophy

- **Minimal & Professional**: Clean design suitable for industrial/corporate environments
- **Resume-Ready**: Easy for recruiters to understand the workflow within seconds
- **Responsive**: Works on desktop and tablet screens
- **Consistent Spacing**: Uses rounded cards with soft shadows
- **Clear Workflow**: Upload → Process → View pattern is immediately obvious

## Component Details

### Header
- Displays project title and subtitle
- Shows backend connection status with color indicator
- Auto-checks backend every 30 seconds

### UploadCard
- File input with visual feedback
- Upload and Process buttons with loading states
- Success/error message display

### StatsCards
- 4 cards showing violation statistics
- Color-coded by severity (blue, orange, yellow, red)
- Icons for visual identification

### AlertsTable
- Sortable table of all violations
- Timestamp, violation type, and screenshot preview
- Click screenshot to view in modal

### ScreenshotModal
- Full-screen image viewer
- Click outside to close
- ESC key support (browser default)

## Customization

### Colors
Primary color is blue. To change, update Tailwind classes in components:
- `bg-blue-600` → `bg-[your-color]-600`
- `text-blue-600` → `text-[your-color]-600`

### Layout
Adjust max-width in Dashboard.jsx:
```javascript
<div className="max-w-7xl mx-auto">
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development Notes

- Uses React Hooks (useState, useEffect)
- All components are functional components
- No class components
- API calls centralized in services/api.js
- Reusable, single-responsibility components

## License

This project is part of a portfolio/resume project.
