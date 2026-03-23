import React from 'react';
import { useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface AnimatedCounterProps {
  from?: number;
  to: number;
  startFrame?: number;
  durationFrames?: number;
  format?: 'number' | 'percent' | 'currency' | 'multiplier';
  suffix?: string;
  prefix?: string;
  color?: string;
  fontSize?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  from = 0,
  to,
  startFrame = 0,
  durationFrames = 60,
  format = 'number',
  suffix = '',
  prefix = '',
  color = '#ffffff',
  fontSize = 96,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  // Eased progress with overshoot
  const progress = spring({
    frame: relFrame,
    fps,
    config: { damping: 20, mass: 0.8, stiffness: 100 },
    durationInFrames: durationFrames,
  });

  const value = from + (to - from) * progress;

  // Format the number
  let display: string;
  switch (format) {
    case 'percent':
      display = `${Math.round(value)}%`;
      break;
    case 'currency':
      display = `$${Math.round(value).toLocaleString()}`;
      break;
    case 'multiplier':
      display = `${value >= 1000 ? `${(value / 1000).toFixed(1)}K` : Math.round(value).toLocaleString()}x`;
      break;
    default:
      display = value >= 1000000
        ? `${(value / 1000000).toFixed(1)}M`
        : value >= 1000
        ? `${(value / 1000).toFixed(1)}K`
        : Math.round(value).toLocaleString();
  }

  // Scale entrance
  const scale = spring({
    frame: relFrame,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  // Glow intensity peaks mid-animation
  const glowIntensity = interpolate(relFrame, [0, durationFrames * 0.5, durationFrames], [0, 1, 0.3], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `scale(${scale})`,
      }}
    >
      <span
        style={{
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontWeight: 900,
          fontSize,
          color,
          textShadow: `0 0 ${30 * glowIntensity}px ${color}40, 0 0 ${60 * glowIntensity}px ${color}20`,
          letterSpacing: '-0.02em',
        }}
      >
        {prefix}{display}{suffix}
      </span>
    </div>
  );
};
