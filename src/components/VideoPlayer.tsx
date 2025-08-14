import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";

type Props = {
  hlsUrl: string;         // e.g. /streams/<id>/index.m3u8
  playing: boolean;
  volume: number;         // 0..1
  onReady?: () => void;
};

export default function VideoPlayer({ hlsUrl, playing, volume, onReady }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const hlsRef = useRef<Hls | null>(null);
  const [canPlay, setCanPlay] = useState(false);

  useEffect(() => {
    const video = videoRef.current!;
    if (!video) return;

    async function setup() {
      if (Hls.isSupported()) {
        const hls = new Hls({ lowLatencyMode: true });
        hlsRef.current = hls;
        hls.loadSource(hlsUrl);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setCanPlay(true);
          onReady?.();
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = hlsUrl;
        video.addEventListener("canplay", () => {
          setCanPlay(true);
          onReady?.();
        });
      } else {
        console.error("HLS not supported");
      }
    }
    setup();

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }
    };
  }, [hlsUrl, onReady]);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    v.volume = volume;
    if (playing && canPlay) v.play().catch(()=>{});
    if (!playing) v.pause();
  }, [playing, volume, canPlay]);

  return <video ref={videoRef} controls={false} playsInline muted={false} />;
}
