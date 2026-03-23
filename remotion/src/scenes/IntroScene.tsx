import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  GradientBackground, 
  ParticleField, 
  LowerThird, 
  KineticHeadline, 
  WarningBanner, 
  IconGrid 
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
    title?: string;
    items?: string[];
  }>;
}

interface IntroSceneProps {
  scene: Scene;
}

export const IntroScene: React.FC<IntroSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  
  // Ken Burns pan effect
  const translateX = interpolate(frame, [0, scene.durationFrames], [0, -50], {
    extrapolateRight: 'clamp'
  });
  
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Background layers */}
      {scene.imagePath && (
        <Img 
          src={staticFile(scene.imagePath)} 
          style={{
            width: '110%',
            height: '100%',
            objectFit: 'cover',
            transform: `translateX(${translateX}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
          }} 
        />
      )}
      
      <GradientBackground 
        mood={scene.mood as any}
        colorAccent={scene.colorAccent}
        animationIntensity="medium"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          opacity: 0.5,
        }}
      />
      
      <ParticleField 
        count={40}
        color={scene.colorAccent}
        speed={1.5}
        opacity={0.3}
        maxSize={3}
        direction="random"
      />
      
      {/* Lower third with scene title */}
      <LowerThird 
        title={scene.title}
        startFrame={0}
        durationFrames={scene.durationFrames}
        position="left"
        accentColor={scene.colorAccent}
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
              style="impact"
              color={scene.colorAccent}
              fontSize="64px"
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
          
          {segment.visualType === 'icon_list' && segment.items && (
            <IconGrid 
              title={segment.title}
              items={segment.items}
              columns={2}
              iconStyle="card"
              color={scene.colorAccent}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
};