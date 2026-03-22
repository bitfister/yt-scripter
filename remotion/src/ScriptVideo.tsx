import { Sequence, AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import scriptData from './data/script.json';
import { HookScene } from './scenes/HookScene';
import { IntroScene } from './scenes/IntroScene';
import { SectionScene } from './scenes/SectionScene';
import { OutroScene } from './scenes/OutroScene';

export const ScriptVideo: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0a0a' }}>
      {scriptData.scenes.map((scene, index) => {
        const nextScene = scriptData.scenes[index + 1];
        
        // Handle transition overlaps
        let sequenceDuration = scene.durationFrames;
        let nextSequenceFrom = scene.startFrame + scene.durationFrames;
        
        if (scene.transition === 'fade' && nextScene) {
          // 30-frame overlap for fade transitions
          sequenceDuration += 30;
          nextSequenceFrom -= 30;
        } else if (scene.transition === 'cut') {
          // No overlap for cut transitions
        }

        return (
          <Sequence
            key={scene.id}
            from={scene.startFrame}
            durationInFrames={sequenceDuration}
          >
            {/* Fade transition handling */}
            <AbsoluteFill
              style={{
                opacity: scene.transition === 'fade' && nextScene && frame >= scene.startFrame + scene.durationFrames - 30
                  ? interpolate(
                      frame,
                      [scene.startFrame + scene.durationFrames - 30, scene.startFrame + scene.durationFrames],
                      [1, 0]
                    )
                  : 1,
              }}
            >
              {scene.type === 'hook' && (
                <HookScene scene={scene} />
              )}
              
              {scene.type === 'intro' && (
                <IntroScene scene={scene} allScenes={scriptData.scenes} />
              )}
              
              {scene.type === 'section' && (
                <SectionScene scene={scene} />
              )}
              
              {scene.type === 'outro' && (
                <OutroScene scene={scene} />
              )}
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};