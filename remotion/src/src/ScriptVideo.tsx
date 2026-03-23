import { Composition, Sequence, Audio, staticFile } from 'remotion';
import HookScene from './scenes/HookScene';
import IntroScene from './scenes/IntroScene';
import SectionScene from './scenes/SectionScene';
import OutroScene from './scenes/OutroScene';
import { ProgressBar } from './components';
import scriptData from './data/script.json';

export default function ScriptVideo() {
  return (
    <>
      <ProgressBar color="#ff2200" position="top" />
      
      {scriptData.scenes.map((scene, index) => (
        <Sequence 
          key={scene.id} 
          from={scene.startFrame} 
          durationInFrames={scene.durationFrames}
        >
          {scene.type === 'hook' && <HookScene scene={scene} />}
          {scene.type === 'intro' && <IntroScene scene={scene} />}
          {scene.type === 'section' && <SectionScene scene={scene} />}
          {scene.type === 'outro' && <OutroScene scene={scene} />}
          
          {scene.audioPath && (
            <Audio src={staticFile(scene.audioPath)} />
          )}
        </Sequence>
      ))}
    </>
  );
}