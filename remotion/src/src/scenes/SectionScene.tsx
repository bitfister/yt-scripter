import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  ParticleField, 
  GradientBackground, 
  KineticHeadline, 
  WarningBanner,
  IconGrid,
  StatHighlight,
  ComparisonLayout,
  TimelineBar,
  QuoteCard,
  LowerThird
} from '../components';

interface SectionSceneProps {
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
      text?: string;
      severity?: string;
      title?: string;
      items?: string[];
      value?: string;
      label?: string;
      emphasis?: string;
      leftLabel?: string;
      rightLabel?: string;
      leftItems?: string[];
      rightItems?: string[];
      events?: Array<{ label: string; year?: string }>;
      attribution?: string;
    }>;
  };
}

export default function SectionScene({ scene }: SectionSceneProps) {
  const frame = useCurrentFrame();
  
  // Ken Burns effect - alternating pan directions based on scene
  const direction = scene.title.includes('Nightmare') ? 1 : -1;
  const translateX = interpolate(frame, [0, scene.durationFrames], [0, 40 * direction], {
    extrapolateRight: 'clamp'
  });
  const translateY = interpolate(frame, [0, scene.durationFrames], [0, -20], {
    extrapolateRight: 'clamp'
  });
  const scale = interpolate(frame, [0, scene.durationFrames], [1.0, 1.06], {
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
            transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
            position: 'absolute',
            top: 0,
            left: 0
          }}
        />
      )}
      
      {/* Gradient Overlay */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.65 }}>
        <GradientBackground 
          mood={scene.mood as any}
          colorAccent={scene.colorAccent}
          animationIntensity="medium"
        />
      </div>
      
      {/* Particles */}
      <ParticleField 
        count={100}
        color={scene.colorAccent}
        speed={0.6}
        opacity={0.35}
        maxSize={2.5}
        direction={scene.mood === 'warning' ? 'down' : 'up'}
      />
      
      {/* Section Title Lower Third */}
      <LowerThird 
        title={scene.title}
        position="center"
        accentColor={scene.colorAccent}
        durationFrames={300}
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
          
          {segment.visualType === 'stat_highlight' && (
            <StatHighlight 
              value={segment.value!}
              label={segment.label!}
              emphasis={segment.emphasis as any}
              color={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'comparison' && (
            <ComparisonLayout 
              leftLabel={segment.leftLabel!}
              rightLabel={segment.rightLabel!}
              leftItems={segment.leftItems!}
              rightItems={segment.rightItems!}
              style="versus"
              leftColor="#666"
              rightColor={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'timeline' && (
            <TimelineBar 
              events={segment.events!}
              color={scene.colorAccent}
              orientation="horizontal"
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
          
          {segment.visualType === 'quote' && (
            <QuoteCard 
              text={segment.text!}
              attribution={segment.attribution}
              style="warning"
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
          
          {segment.visualType === 'reveal' && (
            <StatHighlight 
              value={segment.value!}
              label={segment.label!}
              emphasis="danger"
              color={scene.colorAccent}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
}