# backend/app.py
import os, json
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from pymongo import MongoClient
from models import OverlayDoc
from ffmpeg_manager import FFmpegManager

load_dotenv()

PORT = int(os.getenv("PORT", "5001"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "rtsp_overlay")
HLS_ROOT = os.getenv("HLS_ROOT", "./streams")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": "*"}})

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
overlays = db["overlays"]

ff = FFmpegManager(HLS_ROOT)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --------- Streams (RTSP -> HLS) ----------
@app.post("/api/streams/start")
def start_stream():
    data = request.get_json(force=True)
    rtsp_url = data.get("rtspUrl")
    if not rtsp_url:
        return jsonify({"error": "rtspUrl required"}), 400
    stream_id = ff.start(rtsp_url)
    return jsonify({
        "streamId": stream_id,
        "hlsUrl": f"/streams/{stream_id}/index.m3u8"
    }), 201

@app.get("/api/streams/status/<stream_id>")
def stream_status(stream_id):
    return jsonify(ff.status(stream_id))

@app.delete("/api/streams/stop/<stream_id>")
def stop_stream(stream_id):
    ok = ff.stop(stream_id)
    return jsonify({"stopped": ok})

# serve HLS files
@app.get("/streams/<path:path>")
def serve_hls(path: str):
    full_path = os.path.join(HLS_ROOT)
    # security: ensure path stays within HLS_ROOT
    # `send_from_directory` guards traversal by default
    return send_from_directory(full_path, path, conditional=True)

# --------- Uploads (logos) ----------
@app.post("/api/uploads")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400
    f = request.files["file"]
    name = f.filename
    if not name:
        return jsonify({"error": "invalid filename"}), 400
    # very simple allowlist; extend as needed
    ext = os.path.splitext(name.lower())[1]
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
        return jsonify({"error": "unsupported file type"}), 400
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_as = os.path.join(UPLOAD_DIR, name)
    f.save(save_as)
    return jsonify({"url": f"/uploads/{name}"}), 201

@app.get("/uploads/<path:filename>")
def serve_upload(filename: str):
    return send_from_directory(UPLOAD_DIR, filename, conditional=True)

# --------- Overlay CRUD ----------
def oid(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        abort(400, "Invalid id")

@app.post("/api/overlays")
def create_overlay():
    data = request.get_json(force=True)
    doc = OverlayDoc(**data).model_dump()
    res = overlays.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return jsonify(doc), 201

@app.get("/api/overlays")
def list_overlays():
    user_id = request.args.get("userId")
    stream_id = request.args.get("streamId")
    q = {}
    if user_id: q["userId"] = user_id
    if stream_id: q["streamId"] = stream_id
    out = []
    for d in overlays.find(q).sort("updatedAt", -1):
        d["_id"] = str(d["_id"])
        out.append(d)
    return jsonify(out)

@app.get("/api/overlays/<id>")
def get_overlay(id):
    d = overlays.find_one({"_id": oid(id)})
    if not d: return jsonify({"error": "not found"}), 404
    d["_id"] = str(d["_id"])
    return jsonify(d)

@app.put("/api/overlays/<id>")
def update_overlay(id):
    data = request.get_json(force=True)
    data["updatedAt"] = datetime.utcnow()
    overlays.update_one({"_id": oid(id)}, {"$set": data})
    d = overlays.find_one({"_id": oid(id)})
    if not d: return jsonify({"error": "not found"}), 404
    d["_id"] = str(d["_id"])
    return jsonify(d)

@app.delete("/api/overlays/<id>")
def delete_overlay(id):
    res = overlays.delete_one({"_id": oid(id)})
    return jsonify({"deleted": res.deleted_count == 1})

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
