import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface QuoteCardProps {
  text: string;
  attribution?: string | null;
  startFrame?: number;
  style?: 'elegant' | 'bold' | 'warning';
  color?: string;
}

export const QuoteCard: React.FC<QuoteCardProps> = ({
  text,
  attribution,
  startFrame = 0,
  style = 'elegant',
  color = '#ff8800',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  // Card entrance from bottom
  const cardY = spring({
    frame: relFrame,
    fps,
    config: { damping: 14, mass: 0.7 },
    from: 80,
    to: 0,
  });

  const cardOpacity = interpolate(relFrame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Typewriter effect for text
  const charsToShow = Math.floor(interpolate(
    relFrame,
    [15, 15 + text.length * 1.2],
    [0, text.length],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  ));

  const displayText = text.slice(0, charsToShow);
  const showCursor = charsToShow < text.length && relFrame > 15;

  // Attribution fades in after text completes
  const attrDelay = 15 + text.length * 1.2 + 10;
  const attrOpacity = attribution ? interpolate(
    relFrame,
    [attrDelay, attrDelay + 20],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  ) : 0;

  const isWarning = style === 'warning';
  const isBold = style === 'bold';

  const cardBg = isWarning ? '#1a080820' : '#ffffff06';
  const cardBorder = isWarning ? `${color}40` : '#ffffff15';
  const fontSize = isBold ? 42 : 36;

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 140px',
      }}
    >
      <div
        style={{
          opacity: cardOpacity,
          transform: `translateY(${cardY}px)`,
          backgroundColor: cardBg,
          border: `1px solid ${cardBorder}`,
          borderRadius: 16,
          padding: '48px 56px',
          maxWidth: 900,
          position: 'relative',
        }}
      >
        {/* Quote mark */}
        <svg
          width="48"
          height="40"
          viewBox="0 0 48 40"
          style={{
            position: 'absolute',
            top: -20,
            left: 32,
            opacity: 0.4,
          }}
        >
          <text
            x="0"
            y="40"
            fontFamily="Georgia, serif"
            fontSize="80"
            fill={color}
          >
            &#8220;
          </text>
        </svg>

        {/* Text */}
        <div
          style={{
            fontFamily: isBold ? 'system-ui, sans-serif' : 'Georgia, serif',
            fontSize,
            fontWeight: isBold ? 700 : 400,
            fontStyle: isBold ? 'normal' : 'italic',
            color: isWarning ? color : '#eeeeee',
            lineHeight: 1.5,
            letterSpacing: isBold ? '-0.01em' : '0.01em',
          }}
        >
          {displayText}
          {showCursor && (
            <span
              style={{
                opacity: Math.sin(relFrame * 0.15) > 0 ? 1 : 0,
                color,
              }}
            >
              |
            </span>
          )}
        </div>

        {/* Attribution */}
        {attribution && (
          <div
            style={{
              marginTop: 24,
              fontFamily: 'system-ui, sans-serif',
              fontSize: 18,
              color: '#888888',
              opacity: attrOpacity,
              letterSpacing: '0.03em',
            }}
          >
            — {attribution}
          </div>
        )}

        {/* Accent line at bottom */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 24,
            right: 24,
            height: 2,
            backgroundColor: color,
            opacity: 0.3,
            borderRadius: 1,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
