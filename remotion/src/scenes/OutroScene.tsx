import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  GradientBackground, 
  ParticleField, 
  KineticHeadline, 
  IconGrid,
  TimelineBar,
  QuoteCard
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
    title?: string;
    items?: string[];
    events?: Array<{label: string; year?: string}>;
    text?: string;
    attribution?: string;
  }>;
}

interface OutroSceneProps {
  scene: Scene;
}

export const OutroScene: React.FC<OutroSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  
  // Ken Burns zoom out effect
  const scale = interpolate(frame, [0, scene.durationFrames - 60, scene.durationFrames], [1.05, 1.0, 0.95], {
    extrapolateRight: 'clamp'
  });
  
  // Fade to black in final 60 frames
  const fadeOpacity = interpolate(frame, [scene.durationFrames - 60, scene.durationFrames], [0, 1], {
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
        animationIntensity="low"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          opacity: 0.7,
        }}
      />
      
      <ParticleField 
        count={30}
        color={scene.colorAccent}
        speed={1}
        opacity={0.25}
        maxSize={2.5}
        direction="down"
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
              style="elegant"
              color={scene.colorAccent}
              fontSize="48px"
            />
          )}
          
          {segment.visualType === 'icon_list' && segment.items && (
            <IconGrid 
              title={segment.title}
              items={segment.items}
              columns={1}
              iconStyle="pill"
              color={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'timeline' && segment.events && (
            <TimelineBar 
              events={segment.events}
              orientation="horizontal"
              color={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'quote' && segment.text && (
            <QuoteCard 
              text={segment.text}
              attribution={segment.attribution}
              style="warning"
              color={scene.colorAccent}
            />
          )}
        </Sequence>
      ))}
      
      {/* Fade to black overlay */}
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'black',
          opacity: fadeOpacity,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};