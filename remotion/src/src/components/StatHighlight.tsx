import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface StatHighlightProps {
  value: string;
  label: string;
  emphasis?: 'normal' | 'danger' | 'success';
  startFrame?: number;
  durationFrames?: number;
  color?: string;
}

const EMPHASIS_COLORS = {
  normal: '#ffffff',
  danger: '#ff4444',
  success: '#44ff88',
};

export const StatHighlight: React.FC<StatHighlightProps> = ({
  value,
  label,
  emphasis = 'normal',
  startFrame = 0,
  durationFrames = 120,
  color,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  const accentColor = color || EMPHASIS_COLORS[emphasis];

  // Value entrance: scale up with spring
  const valueScale = spring({
    frame: relFrame,
    fps,
    config: { damping: 10, mass: 0.6, stiffness: 120 },
  });

  // Label fades in 15 frames after value
  const labelOpacity = interpolate(relFrame, [15, 35], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const labelY = interpolate(relFrame, [15, 35], [20, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Exit animation
  const exitOpacity = interpolate(
    relFrame,
    [durationFrames - 20, durationFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Danger pulse
  const dangerPulse = emphasis === 'danger'
    ? 0.8 + 0.2 * Math.sin(relFrame * 0.1)
    : 1;

  // Glow intensity
  const glowSize = emphasis === 'danger' ? 40 : emphasis === 'success' ? 30 : 20;

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: exitOpacity,
      }}
    >
      {/* Value */}
      <div
        style={{
          transform: `scale(${valueScale * dangerPulse})`,
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontWeight: 900,
          fontSize: 120,
          color: accentColor,
          textShadow: `0 0 ${glowSize}px ${accentColor}60, 0 0 ${glowSize * 2}px ${accentColor}30`,
          letterSpacing: '-0.03em',
          lineHeight: 1,
        }}
      >
        {value}
      </div>

      {/* Label */}
      <div
        style={{
          opacity: labelOpacity,
          transform: `translateY(${labelY}px)`,
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontWeight: 400,
          fontSize: 36,
          color: '#cccccc',
          marginTop: 24,
          maxWidth: '70%',
          textAlign: 'center',
          letterSpacing: '0.02em',
        }}
      >
        {label}
      </div>

      {/* Accent line */}
      <div
        style={{
          width: interpolate(relFrame, [5, 30], [0, 200], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
          height: 3,
          backgroundColor: accentColor,
          marginTop: 32,
          opacity: labelOpacity * 0.6,
          boxShadow: `0 0 10px ${accentColor}80`,
        }}
      />
    </AbsoluteFill>
  );
};
