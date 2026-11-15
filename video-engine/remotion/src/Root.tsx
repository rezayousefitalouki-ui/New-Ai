import { Composition } from "remotion";
import { SocialMindIntro } from "./compositions/SocialMindIntro";

export const RemotionRoot: React.FC = () => <Composition id="SocialMindIntro" component={SocialMindIntro} durationInFrames={150} fps={30} width={1080} height={1920} />;
