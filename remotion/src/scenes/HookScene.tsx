import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  GradientBackground, 
  ParticleField, 
  KineticHeadline, 
  WarningBanner 
} from '../components';

interface Scene {
  id: string;
  type: string;
  title: string;
  durationFrames: number;
  mood: string;
  colorAccent: string;
  imagePath: string | null;
  segments: Array<{
    startOffset: number;
    durationFrames: number;
    visualType: string;
    headline?: string;
    text?: string;
    severity?: string;
  }>;
}

interface HookSceneProps {
  scene: Scene;
}

export const HookScene: React.FC<HookSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  
  // Ken Burns zoom effect
  const scale = interpolate(frame, [0, scene.durationFrames], [1.0, 1.08], {
    extrapolateRight: 'clamp'
  });
  
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Background layers */}
      {scene.imagePath && (
        <Img 
          src={staticFile(scene.imagePath)} 
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${scale})`,
            position: 'absolute',
            top: 0,
            left: 0,
          }} 
        />
      )}
      
      <GradientBackground 
        mood={scene.mood as any}
        colorAccent={scene.colorAccent}
        animationIntensity="high"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          opacity: 0.6,
        }}
      />
      
      <ParticleField 
        count={60}
        color={scene.colorAccent}
        speed={2}
        opacity={0.4}
        maxSize={4}
        direction="up"
      />
      
      {/* Render segments */}
      {scene.segments.map((segment, index) => (
        <Sequence 
          key={index} 
          from={segment.startOffset} 
          durationInFrames={segment.durationFrames}
        >
          {segment.visualType === 'headline' && segment.headline && (
            <KineticHeadline 
              text={segment.headline}
              style="glitch"
              color={scene.colorAccent}
              fontSize="72px"
            />
          )}
          
          {segment.visualType === 'warning' && segment.text && (
            <WarningBanner 
              text={segment.text}
              severity={segment.severity as any}
              color={scene.colorAccent}
              durationFrames={segment.durationFrames}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
};