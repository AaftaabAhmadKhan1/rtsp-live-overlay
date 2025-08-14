Setup
Install prerequisites and clone repo.


Start MongoDB (local or Atlas).


Backend:


Create .env from example.


pip install -r backend/requirements.txt


python backend/app.py (listens on http://localhost:5001).


Frontend:


cd frontend && npm i && npm run dev (opens on http://localhost:5173 by default).


Create frontend/.env with VITE_API_BASE=http://localhost:5001.


Use the app
Landing page: paste an RTSP URL (from rtsp.me, rtsp.stream, or an IP camera), click Start.


Click Play/Pause, adjust Volume.


Overlays:


Click + Text to add text overlay; type to edit content.


Click + Logo to upload an image; drag/resize to position it.


Toggle Edit overlays / Lock overlays.


Click Save overlay to persist (CRUD API in MongoDB).


Stop to kill the ffmpeg process and cleanup HLS files.
