import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  ParticleField, 
  GradientBackground, 
  KineticHeadline, 
  WarningBanner 
} from '../components';

interface HookSceneProps {
  scene: {
    imagePath: string | null;
    mood: string;
    colorAccent: string;
    segments: Array<{
      startOffset: number;
      durationFrames: number;
      visualType: string;
      headline?: string;
      text?: string;
      severity?: string;
    }>;
  };
}

export default function HookScene({ scene }: HookSceneProps) {
  const frame = useCurrentFrame();
  
  // Ken Burns effect - slow zoom
  const scale = interpolate(frame, [0, 540], [1.0, 1.08], {
    extrapolateRight: 'clamp'
  });
  
  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      backgroundColor: '#000'
    }}>
      {/* Background Image with Ken Burns */}
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
            left: 0
          }}
        />
      )}
      
      {/* Gradient Overlay */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.6 }}>
        <GradientBackground 
          mood={scene.mood as any}
          colorAccent={scene.colorAccent}
          animationIntensity="high"
        />
      </div>
      
      {/* Particles */}
      <ParticleField 
        count={150}
        color={scene.colorAccent}
        speed={0.8}
        opacity={0.4}
        maxSize={3}
        direction="up"
      />
      
      {/* Segments */}
      {scene.segments.map((segment, index) => (
        <Sequence 
          key={index}
          from={segment.startOffset} 
          durationInFrames={segment.durationFrames}
        >
          {segment.visualType === 'headline' && (
            <KineticHeadline 
              text={segment.headline!}
              style="glitch"
              color={scene.colorAccent}
            />
          )}
          {segment.visualType === 'warning' && (
            <WarningBanner 
              text={segment.text!}
              severity={segment.severity as any}
              color={scene.colorAccent}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
}