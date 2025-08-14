// frontend/src/api.ts
import axios from "axios";
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5001";

export const api = axios.create({
  baseURL: API_BASE,
});

// Overlays
export async function createOverlay(payload: any) {
  const { data } = await api.post("/api/overlays", payload);
  return data;
}
export async function listOverlays(params?: any) {
  const { data } = await api.get("/api/overlays", { params });
  return data;
}
export async function getOverlay(id: string) {
  const { data } = await api.get(`/api/overlays/${id}`);
  return data;
}
export async function updateOverlay(id: string, payload: any) {
  const { data } = await api.put(`/api/overlays/${id}`, payload);
  return data;
}
export async function deleteOverlay(id: string) {
  const { data } = await api.delete(`/api/overlays/${id}`);
  return data;
}

// Streams
export async function startStream(rtspUrl: string) {
  const { data } = await api.post("/api/streams/start", { rtspUrl });
  return data as { streamId: string; hlsUrl: string };
}
export async function stopStream(streamId: string) {
  const { data } = await api.delete(`/api/streams/stop/${streamId}`);
  return data;
}

// Uploads
export async function uploadLogo(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/api/uploads", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data as { url: string };
}
