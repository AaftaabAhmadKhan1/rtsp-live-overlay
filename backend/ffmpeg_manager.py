# backend/ffmpeg_manager.py
import os, shutil, uuid, subprocess, signal, threading
from typing import Dict

class FFmpegManager:
    def __init__(self, hls_root: str):
        self.hls_root = hls_root
        os.makedirs(self.hls_root, exist_ok=True)
        self.procs: Dict[str, subprocess.Popen] = {}
        self.locks: Dict[str, threading.Lock] = {}

    def start(self, rtsp_url: str) -> str:
        stream_id = str(uuid.uuid4())
        out_dir = os.path.join(self.hls_root, stream_id)
        os.makedirs(out_dir, exist_ok=True)

        # low-latency-ish HLS settings
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-tune", "zerolatency",
            "-preset", "veryfast",
            "-g", "48",
            "-sc_threshold", "0",
            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "6",
            "-hls_flags", "delete_segments+append_list+program_date_time",
            "-hls_segment_filename", os.path.join(out_dir, "segment_%03d.ts"),
            os.path.join(out_dir, "index.m3u8")
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.procs[stream_id] = proc
        self.locks[stream_id] = threading.Lock()
        return stream_id

    def status(self, stream_id: str) -> dict:
        proc = self.procs.get(stream_id)
        if not proc:
            return {"exists": False, "running": False}
        running = proc.poll() is None
        return {"exists": True, "running": running}

    def stop(self, stream_id: str) -> bool:
        proc = self.procs.get(stream_id)
        if not proc:
            return False
        try:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        self.procs.pop(stream_id, None)
        self.locks.pop(stream_id, None)
        out_dir = os.path.join(self.hls_root, stream_id)
        shutil.rmtree(out_dir, ignore_errors=True)
        return True
