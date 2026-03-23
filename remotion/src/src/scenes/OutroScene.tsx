import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  ParticleField, 
  GradientBackground, 
  KineticHeadline, 
  IconGrid,
  TimelineBar,
  QuoteCard,
  LowerThird
} from '../components';

interface OutroSceneProps {
  scene: {
    title: string;
    imagePath: string | null;
    mood: string;
    colorAccent: string;
    durationFrames: number;
    segments: Array<{
      startOffset: number;
      durationFrames: number;
      visualType: string;
      headline?: string;
      title?: string;
      items?: string[];
      events?: Array<{ label: string; year?: string }>;
      text?: string;
      attribution?: string;
    }>;
  };
}

export default function OutroScene({ scene }: OutroSceneProps) {
  const frame = useCurrentFrame();
  
  // Ken Burns effect - slow zoom out
  const scale = interpolate(frame, [0, scene.durationFrames], [1.05, 1.0], {
    extrapolateRight: 'clamp'
  });
  
  // Fade to black in last 60 frames
  const fadeOpacity = interpolate(
    frame, 
    [scene.durationFrames - 60, scene.durationFrames], 
    [1, 0], 
    { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' }
  );
  
  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      backgroundColor: '#000'
    }}>
      <div style={{ opacity: fadeOpacity }}>
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
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.7 }}>
          <GradientBackground 
            mood={scene.mood as any}
            colorAccent={scene.colorAccent}
            animationIntensity="low"
          />
        </div>
        
        {/* Particles */}
        <ParticleField 
          count={80}
          color={scene.colorAccent}
          speed={0.3}
          opacity={0.25}
          maxSize={2}
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
                style="elegant"
                color={scene.colorAccent}
              />
            )}
            
            {segment.visualType === 'icon_list' && (
              <IconGrid 
                title={segment.title}
                items={segment.items!}
                columns={2}
                iconStyle="pill"
                color={scene.colorAccent}
              />
            )}
            
            {segment.visualType === 'timeline' && (
              <TimelineBar 
                events={segment.events!}
                color={scene.colorAccent}
                orientation="horizontal"
              />
            )}
            
            {segment.visualType === 'quote' && (
              <QuoteCard 
                text={segment.text!}
                attribution={segment.attribution}
                style="elegant"
                color={scene.colorAccent}
              />
            )}
          </Sequence>
        ))}
      </div>
      
      {/* Final CTA after segments */}
      <Sequence from={1200} durationInFrames={420}>
        <KineticHeadline 
          text="The Future is Being Written Now"
          style="impact"
          color={scene.colorAccent}
        />
      </Sequence>
    </div>
  );
}