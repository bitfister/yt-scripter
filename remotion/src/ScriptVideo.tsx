import React from 'react';
import { Composition, Sequence, Audio, staticFile } from 'remotion';
import { ProgressBar } from './components';
import scriptData from './data/script.json';

// Scene components
import { HookScene } from './scenes/HookScene';
import { IntroScene } from './scenes/IntroScene';
import { SectionScene } from './scenes/SectionScene';
import { OutroScene } from './scenes/OutroScene';

export const ScriptVideo: React.FC = () => {
  return (
    <>
      {/* Progress bar across full video */}
      <ProgressBar color="#ff2200" position="top" height={3} />
      
      {/* Render each scene */}
      {scriptData.scenes.map((scene) => (
        <Sequence 
          key={scene.id} 
          from={scene.startFrame} 
          durationInFrames={scene.durationFrames}
        >
          {/* Voice-over audio for each scene */}
          {scene.audioPath && (
            <Audio src={staticFile(scene.audioPath)} />
          )}
          
          {/* Route to appropriate scene component */}
          {scene.type === 'hook' && <HookScene scene={scene} />}
          {scene.type === 'intro' && <IntroScene scene={scene} />}
          {scene.type === 'section' && <SectionScene scene={scene} />}
          {scene.type === 'outro' && <OutroScene scene={scene} />}
        </Sequence>
      ))}
    </>
  );
};

export { ScriptVideo as default };