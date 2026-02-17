import { useRef, useState, useCallback } from "react";
import { Camera, X } from "lucide-react";

interface Props {
  onCapture: (file: File) => void;
}

export default function CameraCapture({ onCapture }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setStream(mediaStream);
      setError(null);
    } catch {
      setError("No se pudo acceder a la camara");
    }
  }, []);

  function stopCamera() {
    stream?.getTracks().forEach((t) => t.stop());
    setStream(null);
  }

  function capture() {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d")?.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `captura-${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        onCapture(file);
        stopCamera();
      }
    }, "image/jpeg");
  }

  if (error) {
    return (
      <p className="text-center text-sm text-slate-400">{error}</p>
    );
  }

  if (!stream) {
    return (
      <button className="btn-secondary w-full" onClick={startCamera}>
        <Camera className="h-4 w-4" />
        Tomar Foto
      </button>
    );
  }

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">Camara</span>
        <button
          className="rounded-lg p-1 text-slate-400 hover:bg-slate-100"
          onClick={stopCamera}
        >
          <X className="h-5 w-5" />
        </button>
      </div>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full rounded-lg"
      />
      <button className="btn-primary w-full" onClick={capture}>
        Capturar
      </button>
    </div>
  );
}
