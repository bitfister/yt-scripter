import React, { useMemo } from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface KineticHeadlineProps {
  text: string;
  startFrame?: number;
  durationFrames?: number;
  style?: 'impact' | 'elegant' | 'glitch';
  color?: string;
  fontSize?: number;
}

export const KineticHeadline: React.FC<KineticHeadlineProps> = ({
  text,
  startFrame = 0,
  durationFrames = 90,
  style = 'impact',
  color = '#ffffff',
  fontSize: customFontSize,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  const words = useMemo(() => text.split(/\s+/), [text]);

  // Auto-size: shrink font if text is long
  const fontSize = customFontSize || Math.min(80, Math.max(48, Math.floor(width * 0.8 / (text.length * 0.5))));

  // Exit
  const exitOpacity = interpolate(relFrame, [durationFrames - 15, durationFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  if (style === 'impact') {
    return (
      <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: exitOpacity }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '8px 16px', padding: '0 80px', maxWidth: '85%' }}>
          {words.map((word, i) => {
            const wordScale = spring({
              frame: Math.max(0, relFrame - i * 4),
              fps,
              config: { damping: 10, mass: 0.4, stiffness: 200 },
            });

            const wordOpacity = interpolate(relFrame, [i * 4, i * 4 + 8], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });

            return (
              <span
                key={i}
                style={{
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  fontWeight: 900,
                  fontSize,
                  color,
                  transform: `scale(${wordScale})`,
                  opacity: wordOpacity,
                  display: 'inline-block',
                  textShadow: `0 0 30px ${color}40, 0 4px 8px rgba(0,0,0,0.5)`,
                  letterSpacing: '-0.03em',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    );
  }

  if (style === 'elegant') {
    const fadeIn = interpolate(relFrame, [0, 30], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

    const tracking = interpolate(relFrame, [0, 40], [0.3, 0.08], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

    return (
      <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: exitOpacity }}>
        <div
          style={{
            fontFamily: 'Georgia, serif',
            fontSize: fontSize * 0.9,
            fontWeight: 400,
            fontStyle: 'italic',
            color,
            opacity: fadeIn,
            letterSpacing: `${tracking}em`,
            textAlign: 'center',
            padding: '0 100px',
            maxWidth: '80%',
            lineHeight: 1.3,
          }}
        >
          {text}
        </div>
      </AbsoluteFill>
    );
  }

  // Glitch style
  const glitchOffset = relFrame < 20
    ? Math.sin(relFrame * 5) * interpolate(relFrame, [0, 20], [12, 0], { extrapolateRight: 'clamp' })
    : 0;

  const rgbSplit = relFrame < 25
    ? interpolate(relFrame, [0, 25], [6, 0], { extrapolateRight: 'clamp' })
    : Math.sin(relFrame * 0.3) > 0.8
    ? 3
    : 0;

  const scanlineOpacity = 0.03 + 0.02 * Math.sin(relFrame * 0.2);

  const mainOpacity = interpolate(relFrame, [0, 5], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: exitOpacity }}>
      {/* Scanlines */}
      <AbsoluteFill
        style={{
          background: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,${scanlineOpacity}) 2px, rgba(0,0,0,${scanlineOpacity}) 4px)`,
          pointerEvents: 'none',
        }}
      />

      <div style={{ position: 'relative', padding: '0 80px', maxWidth: '85%' }}>
        {/* Red channel offset */}
        {rgbSplit > 0 && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              fontFamily: 'system-ui, sans-serif',
              fontWeight: 900,
              fontSize,
              color: '#ff000080',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `translate(${rgbSplit}px, ${-rgbSplit * 0.5}px)`,
              mixBlendMode: 'screen',
              textAlign: 'center',
            }}
          >
            {text}
          </div>
        )}

        {/* Blue channel offset */}
        {rgbSplit > 0 && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              fontFamily: 'system-ui, sans-serif',
              fontWeight: 900,
              fontSize,
              color: '#0044ff80',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `translate(${-rgbSplit}px, ${rgbSplit * 0.5}px)`,
              mixBlendMode: 'screen',
              textAlign: 'center',
            }}
          >
            {text}
          </div>
        )}

        {/* Main text */}
        <div
          style={{
            fontFamily: 'system-ui, sans-serif',
            fontWeight: 900,
            fontSize,
            color,
            opacity: mainOpacity,
            transform: `translateX(${glitchOffset}px)`,
            textAlign: 'center',
            textShadow: '0 2px 4px rgba(0,0,0,0.5)',
            letterSpacing: '-0.02em',
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
