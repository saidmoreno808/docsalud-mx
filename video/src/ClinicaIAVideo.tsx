import { AbsoluteFill, Sequence } from "remotion";
import { TitleScene } from "./scenes/TitleScene";
import { ProblemScene } from "./scenes/ProblemScene";
import { SolutionFlowScene } from "./scenes/SolutionFlowScene";
import { DemoUploadScene } from "./scenes/DemoUploadScene";
import { DemoAnalysisScene } from "./scenes/DemoAnalysisScene";
import { DemoResultScene } from "./scenes/DemoResultScene";
import { TechStackScene } from "./scenes/TechStackScene";
import { CTAScene } from "./scenes/CTAScene";

export const VIDEO_FPS = 30;

// Scene durations in frames (30fps)
const D = {
  title:       15 * 30,  // 450f
  problem:     25 * 30,  // 750f
  solution:    20 * 30,  // 600f
  demoUpload:  25 * 30,  // 750f
  demoAnalysis:30 * 30,  // 900f
  demoResult:  35 * 30,  // 1050f
  techStack:   15 * 30,  // 450f
  cta:         15 * 30,  // 450f
};

// Cumulative start frames
const S = {
  title:        0,
  problem:      D.title,
  solution:     D.title + D.problem,
  demoUpload:   D.title + D.problem + D.solution,
  demoAnalysis: D.title + D.problem + D.solution + D.demoUpload,
  demoResult:   D.title + D.problem + D.solution + D.demoUpload + D.demoAnalysis,
  techStack:    D.title + D.problem + D.solution + D.demoUpload + D.demoAnalysis + D.demoResult,
  cta:          D.title + D.problem + D.solution + D.demoUpload + D.demoAnalysis + D.demoResult + D.techStack,
};

export const VIDEO_DURATION_FRAMES =
  D.title + D.problem + D.solution + D.demoUpload +
  D.demoAnalysis + D.demoResult + D.techStack + D.cta;

export const ClinicaIAVideo = () => (
  <AbsoluteFill style={{ background: "#0a0e1a" }}>
    <Sequence from={S.title} durationInFrames={D.title}>
      <TitleScene />
    </Sequence>
    <Sequence from={S.problem} durationInFrames={D.problem}>
      <ProblemScene />
    </Sequence>
    <Sequence from={S.solution} durationInFrames={D.solution}>
      <SolutionFlowScene />
    </Sequence>
    <Sequence from={S.demoUpload} durationInFrames={D.demoUpload}>
      <DemoUploadScene />
    </Sequence>
    <Sequence from={S.demoAnalysis} durationInFrames={D.demoAnalysis}>
      <DemoAnalysisScene />
    </Sequence>
    <Sequence from={S.demoResult} durationInFrames={D.demoResult}>
      <DemoResultScene />
    </Sequence>
    <Sequence from={S.techStack} durationInFrames={D.techStack}>
      <TechStackScene />
    </Sequence>
    <Sequence from={S.cta} durationInFrames={D.cta}>
      <CTAScene />
    </Sequence>
  </AbsoluteFill>
);
