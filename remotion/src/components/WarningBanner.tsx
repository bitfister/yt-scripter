import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface WarningBannerProps {
  text: string;
  startFrame?: number;
  durationFrames?: number;
  severity?: 'caution' | 'danger' | 'critical';
  color?: string;
}

export const WarningBanner: React.FC<WarningBannerProps> = ({
  text,
  startFrame = 0,
  durationFrames = 120,
  severity = 'danger',
  color,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  const severityColor = color || (
    severity === 'critical' ? '#ff0000' :
    severity === 'danger' ? '#ff4400' :
    '#ffaa00'
  );

  // Banner slides in from top
  const bannerY = spring({
    frame: relFrame,
    fps,
    config: { damping: 14, mass: 0.6 },
    from: -120,
    to: 0,
  });

  // Screen shake for critical
  const shakeX = severity === 'critical' && relFrame < 30
    ? Math.sin(relFrame * 2.5) * interpolate(relFrame, [0, 30], [8, 0], { extrapolateRight: 'clamp' })
    : 0;
  const shakeY = severity === 'critical' && relFrame < 30
    ? Math.cos(relFrame * 3.1) * interpolate(relFrame, [0, 30], [5, 0], { extrapolateRight: 'clamp' })
    : 0;

  // Pulse for danger/critical
  const pulse = severity !== 'caution'
    ? 0.7 + 0.3 * Math.sin(relFrame * 0.12)
    : 1;

  // Flash overlay for critical entrance
  const flashOpacity = severity === 'critical'
    ? interpolate(relFrame, [0, 8, 20], [0.4, 0.2, 0], { extrapolateRight: 'clamp' })
    : 0;

  // Exit
  const exitOpacity = interpolate(relFrame, [durationFrames - 20, durationFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Hazard stripe pattern
  const stripeOffset = relFrame * 0.5;

  return (
    <AbsoluteFill
      style={{
        transform: `translate(${shakeX}px, ${shakeY}px)`,
        opacity: exitOpacity,
      }}
    >
      {/* Flash overlay */}
      {flashOpacity > 0 && (
        <AbsoluteFill
          style={{
            backgroundColor: severityColor,
            opacity: flashOpacity,
          }}
        />
      )}

      {/* Banner */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, calc(-50% + ${bannerY}px))`,
          width: '80%',
          maxWidth: 900,
        }}
      >
        {/* Hazard stripe border */}
        <div
          style={{
            height: 6,
            background: `repeating-linear-gradient(
              ${45 + stripeOffset}deg,
              ${severityColor},
              ${severityColor} 10px,
              transparent 10px,
              transparent 20px
            )`,
            borderRadius: '4px 4px 0 0',
            opacity: pulse,
          }}
        />

        {/* Main banner body */}
        <div
          style={{
            backgroundColor: '#0a0a0a',
            border: `2px solid ${severityColor}50`,
            borderTop: 'none',
            padding: '32px 48px',
            display: 'flex',
            alignItems: 'center',
            gap: 24,
          }}
        >
          {/* Warning icon */}
          <svg width="48" height="48" viewBox="0 0 48 48" style={{ flexShrink: 0, opacity: pulse }}>
            <polygon
              points="24,4 44,40 4,40"
              fill="none"
              stroke={severityColor}
              strokeWidth="3"
            />
            <text x="24" y="34" textAnchor="middle" fill={severityColor} fontSize="22" fontWeight="bold">!</text>
          </svg>

          {/* Text */}
          <div
            style={{
              fontFamily: 'system-ui, sans-serif',
              fontWeight: 800,
              fontSize: 32,
              color: severityColor,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              textShadow: `0 0 20px ${severityColor}40`,
            }}
          >
            {text}
          </div>
        </div>

        {/* Bottom hazard stripe */}
        <div
          style={{
            height: 6,
            background: `repeating-linear-gradient(
              ${-45 + stripeOffset}deg,
              ${severityColor},
              ${severityColor} 10px,
              transparent 10px,
              transparent 20px
            )`,
            borderRadius: '0 0 4px 4px',
            opacity: pulse,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
