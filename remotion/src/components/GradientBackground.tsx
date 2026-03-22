import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

type Mood = 'tense' | 'calm' | 'energetic' | 'dark' | 'warning' | 'hopeful';

interface GradientBackgroundProps {
  mood?: Mood;
  colorAccent?: string;
  animationIntensity?: 'low' | 'medium' | 'high';
}

const MOOD_PALETTES: Record<Mood, { colors: string[]; angle: number }> = {
  tense:    { colors: ['#0a0a0a', '#1a0505', '#0d0d1a'], angle: 135 },
  calm:     { colors: ['#0a0a14', '#0a1420', '#050a14'], angle: 180 },
  energetic:{ colors: ['#1a0a00', '#0d0505', '#1a0d00'], angle: 45 },
  dark:     { colors: ['#050505', '#0a0a0a', '#080808'], angle: 160 },
  warning:  { colors: ['#1a0a00', '#200800', '#140500'], angle: 135 },
  hopeful:  { colors: ['#0a0a14', '#0d1a0d', '#0a1414'], angle: 120 },
};

const INTENSITY_SPEED = { low: 0.3, medium: 0.7, high: 1.2 };

export const GradientBackground: React.FC<GradientBackgroundProps> = ({
  mood = 'dark',
  colorAccent = '#ff4400',
  animationIntensity = 'medium',
}) => {
  const frame = useCurrentFrame();
  const speed = INTENSITY_SPEED[animationIntensity];
  const palette = MOOD_PALETTES[mood] || MOOD_PALETTES.dark;

  // Animate gradient angle
  const angle = palette.angle + Math.sin(frame * 0.008 * speed) * 15;

  // Animate radial accent glow position
  const glowX = 50 + Math.sin(frame * 0.005 * speed) * 20;
  const glowY = 50 + Math.cos(frame * 0.007 * speed) * 15;

  // Pulse the accent glow opacity
  const glowOpacity = interpolate(
    Math.sin(frame * 0.015 * speed),
    [-1, 1],
    [0.05, 0.15]
  );

  // Vignette intensity
  const vignetteOpacity = mood === 'warning' || mood === 'tense' ? 0.6 : 0.4;

  return (
    <AbsoluteFill>
      {/* Base gradient */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(${angle}deg, ${palette.colors.join(', ')})`,
        }}
      />

      {/* Accent glow */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 50% at ${glowX}% ${glowY}%, ${colorAccent}, transparent)`,
          opacity: glowOpacity,
          mixBlendMode: 'screen',
        }}
      />

      {/* Warning pulse */}
      {mood === 'warning' && (
        <AbsoluteFill
          style={{
            background: `radial-gradient(circle at 50% 50%, ${colorAccent}, transparent 70%)`,
            opacity: interpolate(
              Math.sin(frame * 0.04 * speed),
              [-1, 1],
              [0, 0.08]
            ),
          }}
        />
      )}

      {/* Vignette */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 70% 60% at 50% 50%, transparent 30%, rgba(0,0,0,0.8) 100%)',
          opacity: vignetteOpacity,
        }}
      />
    </AbsoluteFill>
  );
};
