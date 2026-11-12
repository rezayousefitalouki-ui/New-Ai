import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

export const SocialMindIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ alignItems: "center", background: "linear-gradient(150deg,#171327,#30255c 52%,#7255db)", color: "white", direction: "rtl", display: "flex", flexDirection: "column", fontFamily: "Arial,sans-serif", justifyContent: "center", opacity, textAlign: "center" }}>
    <div style={{ color: "#c6b8ff", fontSize: 34, letterSpacing: 2 }}>SOCIALMIND AI</div>
    <div style={{ fontSize: 78, fontWeight: 700, marginTop: 36 }}>ایدهٔ بعدی، همین‌جاست</div>
    <div style={{ color: "#e2ddf5", fontSize: 34, marginTop: 22 }}>استودیوی ویدیوی فارسی</div>
  </AbsoluteFill>;
};
