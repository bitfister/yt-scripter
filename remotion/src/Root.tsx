import { Composition } from 'remotion';
import { ScriptVideo } from './ScriptVideo';
import scriptData from './data/script.json';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AIScaryWarning"
        component={ScriptVideo}
        durationInFrames={scriptData.totalDurationFrames}
        fps={scriptData.fps}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};