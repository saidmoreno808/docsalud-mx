import { Composition } from "remotion";
import { ClinicaIAVideo, VIDEO_FPS, VIDEO_DURATION_FRAMES } from "./ClinicaIAVideo";

export const RemotionRoot = () => (
  <Composition
    id="ClinicaIAVideo"
    component={ClinicaIAVideo}
    durationInFrames={VIDEO_DURATION_FRAMES}
    fps={VIDEO_FPS}
    width={1920}
    height={1080}
  />
);
