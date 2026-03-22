import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface IconGridProps {
  title?: string;
  items: string[];
  startFrame?: number;
  columns?: 2 | 3 | 4;
  iconStyle?: 'circle' | 'pill' | 'card';
  color?: string;
}

export const IconGrid: React.FC<IconGridProps> = ({
  title,
  items,
  startFrame = 0,
  columns = 2,
  iconStyle = 'card',
  color = '#ff8800',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  // Title entrance
  const titleOpacity = interpolate(relFrame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 120px',
      }}
    >
      {/* Title */}
      {title && (
        <div
          style={{
            fontFamily: 'system-ui, sans-serif',
            fontWeight: 700,
            fontSize: 36,
            color: '#ffffff',
            marginBottom: 48,
            opacity: titleOpacity,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
          }}
        >
          {title}
        </div>
      )}

      {/* Grid */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 20,
          maxWidth: columns * 300,
        }}
      >
        {items.map((item, i) => {
          const itemDelay = 15 + i * 18;
          const itemScale = spring({
            frame: Math.max(0, relFrame - itemDelay),
            fps,
            config: { damping: 12, mass: 0.5 },
          });

          // Generate a monogram from first letter
          const letter = item.charAt(0).toUpperCase();

          // Subtle glow when item appears
          const glowOpacity = interpolate(
            relFrame,
            [itemDelay, itemDelay + 10, itemDelay + 30],
            [0, 0.8, 0.2],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );

          const baseStyle: React.CSSProperties = {
            transform: `scale(${itemScale})`,
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            width: columns === 2 ? 340 : columns === 3 ? 260 : 200,
          };

          if (iconStyle === 'card') {
            return (
              <div
                key={i}
                style={{
                  ...baseStyle,
                  backgroundColor: '#ffffff08',
                  border: '1px solid #ffffff15',
                  borderRadius: 12,
                  padding: '16px 20px',
                  boxShadow: `0 0 ${20 * glowOpacity}px ${color}30`,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    backgroundColor: `${color}20`,
                    border: `1px solid ${color}40`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'system-ui, sans-serif',
                    fontWeight: 800,
                    fontSize: 20,
                    color,
                    flexShrink: 0,
                  }}
                >
                  {letter}
                </div>
                <span
                  style={{
                    fontFamily: 'system-ui, sans-serif',
                    fontSize: 18,
                    color: '#dddddd',
                    lineHeight: 1.3,
                  }}
                >
                  {item}
                </span>
              </div>
            );
          }

          if (iconStyle === 'pill') {
            return (
              <div
                key={i}
                style={{
                  ...baseStyle,
                  backgroundColor: `${color}15`,
                  border: `1px solid ${color}30`,
                  borderRadius: 40,
                  padding: '12px 24px',
                  justifyContent: 'center',
                }}
              >
                <span style={{ fontFamily: 'system-ui, sans-serif', fontSize: 18, color: '#dddddd' }}>
                  {item}
                </span>
              </div>
            );
          }

          // circle style
          return (
            <div
              key={i}
              style={{
                ...baseStyle,
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: '50%',
                  backgroundColor: `${color}20`,
                  border: `2px solid ${color}50`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: 'system-ui, sans-serif',
                  fontWeight: 800,
                  fontSize: 28,
                  color,
                  boxShadow: `0 0 ${15 * glowOpacity}px ${color}40`,
                }}
              >
                {letter}
              </div>
              <span style={{ fontFamily: 'system-ui, sans-serif', fontSize: 16, color: '#cccccc' }}>
                {item}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
