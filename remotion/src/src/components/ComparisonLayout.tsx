import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface ComparisonLayoutProps {
  leftLabel: string;
  rightLabel: string;
  leftItems: string[];
  rightItems: string[];
  startFrame?: number;
  style?: 'side-by-side' | 'versus';
  leftColor?: string;
  rightColor?: string;
}

export const ComparisonLayout: React.FC<ComparisonLayoutProps> = ({
  leftLabel,
  rightLabel,
  leftItems,
  rightItems,
  startFrame = 0,
  style = 'side-by-side',
  leftColor = '#ff4444',
  rightColor = '#44aaff',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  // Labels entrance
  const labelProgress = spring({
    frame: relFrame,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  // Divider line grows
  const dividerHeight = interpolate(relFrame, [10, 40], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // VS badge
  const vsScale = style === 'versus' ? spring({
    frame: Math.max(0, relFrame - 20),
    fps,
    config: { damping: 8, mass: 0.4 },
  }) : 0;

  const maxItems = Math.max(leftItems.length, rightItems.length);

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 80px',
      }}
    >
      {/* Left column */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', paddingRight: 60 }}>
        <div
          style={{
            fontFamily: 'system-ui, sans-serif',
            fontWeight: 800,
            fontSize: 36,
            color: leftColor,
            marginBottom: 32,
            opacity: labelProgress,
            transform: `translateX(${(1 - labelProgress) * -50}px)`,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          {leftLabel}
        </div>
        {leftItems.map((item, i) => {
          const itemDelay = 30 + i * 20;
          const itemOpacity = interpolate(relFrame, [itemDelay, itemDelay + 15], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const itemX = interpolate(relFrame, [itemDelay, itemDelay + 15], [-30, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <div
              key={i}
              style={{
                fontFamily: 'system-ui, sans-serif',
                fontSize: 24,
                color: '#cccccc',
                opacity: itemOpacity,
                transform: `translateX(${itemX}px)`,
                marginBottom: 16,
                padding: '10px 20px',
                borderRight: `3px solid ${leftColor}60`,
                textAlign: 'right',
              }}
            >
              {item}
            </div>
          );
        })}
      </div>

      {/* Center divider */}
      <div style={{ position: 'relative', width: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            width: 2,
            height: `${dividerHeight}%`,
            backgroundColor: '#ffffff20',
            boxShadow: '0 0 10px rgba(255,255,255,0.1)',
          }}
        />
        {style === 'versus' && (
          <div
            style={{
              position: 'absolute',
              transform: `scale(${vsScale})`,
              fontFamily: 'system-ui, sans-serif',
              fontWeight: 900,
              fontSize: 28,
              color: '#ff8800',
              backgroundColor: '#1a1a1a',
              border: '2px solid #ff880060',
              borderRadius: '50%',
              width: 56,
              height: 56,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px #ff880030',
            }}
          >
            VS
          </div>
        )}
      </div>

      {/* Right column */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', paddingLeft: 60 }}>
        <div
          style={{
            fontFamily: 'system-ui, sans-serif',
            fontWeight: 800,
            fontSize: 36,
            color: rightColor,
            marginBottom: 32,
            opacity: labelProgress,
            transform: `translateX(${(1 - labelProgress) * 50}px)`,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          {rightLabel}
        </div>
        {rightItems.map((item, i) => {
          const itemDelay = 30 + i * 20;
          const itemOpacity = interpolate(relFrame, [itemDelay, itemDelay + 15], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const itemX = interpolate(relFrame, [itemDelay, itemDelay + 15], [30, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <div
              key={i}
              style={{
                fontFamily: 'system-ui, sans-serif',
                fontSize: 24,
                color: '#cccccc',
                opacity: itemOpacity,
                transform: `translateX(${itemX}px)`,
                marginBottom: 16,
                padding: '10px 20px',
                borderLeft: `3px solid ${rightColor}60`,
              }}
            >
              {item}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
