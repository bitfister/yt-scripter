import React from 'react';
import { useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface LowerThirdProps {
  title: string;
  subtitle?: string;
  startFrame?: number;
  durationFrames?: number;
  position?: 'left' | 'center';
  accentColor?: string;
}

export const LowerThird: React.FC<LowerThirdProps> = ({
  title,
  subtitle,
  startFrame = 0,
  durationFrames = 150,
  position = 'left',
  accentColor = '#ff4400',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  // Slide in
  const slideProgress = spring({
    frame: relFrame,
    fps,
    config: { damping: 16, mass: 0.6 },
  });

  // Slide out
  const slideOut = relFrame > durationFrames - 25
    ? spring({
        frame: relFrame - (durationFrames - 25),
        fps,
        config: { damping: 20, mass: 0.5 },
      })
    : 0;

  const translateX = position === 'left'
    ? interpolate(slideProgress, [0, 1], [-400, 0]) + interpolate(slideOut, [0, 1], [0, -400])
    : 0;

  const opacity = position === 'center'
    ? interpolate(slideProgress, [0, 1], [0, 1]) * interpolate(slideOut, [0, 1], [1, 0])
    : 1;

  // Accent bar width animation
  const barWidth = interpolate(slideProgress, [0, 1], [0, 4]);

  // Title text reveal
  const titleOpacity = interpolate(relFrame, [5, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Subtitle delayed
  const subtitleOpacity = subtitle ? interpolate(relFrame, [15, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }) : 0;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 80,
        left: position === 'left' ? 60 : '50%',
        transform: position === 'center'
          ? `translateX(-50%)`
          : `translateX(${translateX}px)`,
        opacity,
        display: 'flex',
        alignItems: 'stretch',
        gap: 0,
      }}
    >
      {/* Accent bar */}
      <div
        style={{
          width: barWidth,
          backgroundColor: accentColor,
          borderRadius: 2,
          boxShadow: `0 0 10px ${accentColor}60`,
        }}
      />

      {/* Content */}
      <div
        style={{
          backgroundColor: '#0a0a0aDD',
          backdropFilter: 'blur(10px)',
          padding: '14px 28px',
          marginLeft: 2,
          borderRadius: '0 6px 6px 0',
          border: '1px solid #ffffff10',
          borderLeft: 'none',
        }}
      >
        <div
          style={{
            fontFamily: 'system-ui, sans-serif',
            fontWeight: 700,
            fontSize: 24,
            color: '#ffffff',
            opacity: titleOpacity,
            letterSpacing: '0.02em',
          }}
        >
          {title}
        </div>
        {subtitle && (
          <div
            style={{
              fontFamily: 'system-ui, sans-serif',
              fontSize: 16,
              color: '#999999',
              opacity: subtitleOpacity,
              marginTop: 4,
              letterSpacing: '0.03em',
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
