import React from 'react';
import { Img, staticFile, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { 
  GradientBackground, 
  ParticleField, 
  LowerThird, 
  KineticHeadline, 
  StatHighlight,
  ComparisonLayout,
  TimelineBar,
  IconGrid,
  QuoteCard,
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
    value?: string;
    label?: string;
    emphasis?: string;
    leftLabel?: string;
    rightLabel?: string;
    leftItems?: string[];
    rightItems?: string[];
    events?: Array<{label: string; year?: string}>;
    title?: string;
    items?: string[];
    text?: string;
    attribution?: string;
    severity?: string;
  }>;
}

interface SectionSceneProps {
  scene: Scene;
}

export const SectionScene: React.FC<SectionSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  
  // Ken Burns zoom and pan effect
  const scale = interpolate(frame, [0, scene.durationFrames], [1.0, 1.06], {
    extrapolateRight: 'clamp'
  });
  const translateY = interpolate(frame, [0, scene.durationFrames], [0, -30], {
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
            transform: `scale(${scale}) translateY(${translateY}px)`,
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
          opacity: 0.6,
        }}
      />
      
      <ParticleField 
        count={50}
        color={scene.colorAccent}
        speed={1.8}
        opacity={0.35}
        maxSize={3.5}
        direction="up"
      />
      
      {/* Lower third with section title */}
      <LowerThird 
        title={scene.title}
        startFrame={0}
        durationFrames={450}
        position="left"
        accentColor={scene.colorAccent}
      />
      
      {/* Render all segments */}
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
              fontSize="56px"
            />
          )}
          
          {segment.visualType === 'stat_highlight' && segment.value && segment.label && (
            <StatHighlight 
              value={segment.value}
              label={segment.label}
              emphasis={segment.emphasis as any}
              color={scene.colorAccent}
              durationFrames={segment.durationFrames}
            />
          )}
          
          {segment.visualType === 'comparison' && segment.leftLabel && segment.rightLabel && (
            <ComparisonLayout 
              leftLabel={segment.leftLabel}
              rightLabel={segment.rightLabel}
              leftItems={segment.leftItems || []}
              rightItems={segment.rightItems || []}
              style="versus"
              leftColor={segment.emphasis === 'danger' ? '#ff4444' : scene.colorAccent}
              rightColor={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'timeline' && segment.events && (
            <TimelineBar 
              events={segment.events}
              orientation="horizontal"
              color={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'icon_list' && segment.items && (
            <IconGrid 
              title={segment.title}
              items={segment.items}
              columns={segment.items.length > 3 ? 2 : 1}
              iconStyle="card"
              color={scene.colorAccent}
            />
          )}
          
          {segment.visualType === 'quote' && segment.text && (
            <QuoteCard 
              text={segment.text}
              attribution={segment.attribution}
              style={segment.attribution ? 'elegant' : 'bold'}
              color={scene.colorAccent}
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
          
          {segment.visualType === 'reveal' && segment.value && segment.label && (
            <StatHighlight 
              value={segment.value}
              label={segment.label}
              emphasis="danger"
              color={scene.colorAccent}
              durationFrames={segment.durationFrames}
            />
          )}
        </Sequence>
      ))}
    </div>
  );
};