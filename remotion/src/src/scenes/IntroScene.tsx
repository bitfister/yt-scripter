import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  ParticleField, 
  GradientBackground, 
  KineticHeadline, 
  WarningBanner,
  IconGrid,
  LowerThird
} from '../components';

interface IntroSceneProps {
  scene: {
    title: string;
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
      title?: string;
      items?: string[];
    }>;
  };
}

export default function IntroScene({ scene }: IntroSceneProps) {
  const frame = useCurrentFrame();
  
  // Ken Burns effect - slow pan and slight zoom
  const translateX = interpolate(frame, [0, 1350], [0, -50], {
    extrapolateRight: 'clamp'
  });
  const scale = interpolate(frame, [0, 1350], [1.0, 1.05], {
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
            transform: `translateX(${translateX}px) scale(${scale})`,
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
          animationIntensity="medium"
        />
      </div>
      
      {/* Particles */}
      <ParticleField 
        count={120}
        color={scene.colorAccent}
        speed={0.5}
        opacity={0.3}
        maxSize={2}
        direction="random"
      />
      
      {/* Lower Third with Topic */}
      <LowerThird 
        title={scene.title}
        subtitle="The AI Warning You Need to Hear"
        position="left"
        accentColor={scene.colorAccent}
        durationFrames={400}
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
              style="impact"
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
          {segment.visualType === 'icon_list' && (
            <IconGrid 
              title={segment.title}
              items={segment.items!}
              columns={2}
              iconStyle="card"
              color={scene.colorAccent}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
}