import React, { useMemo } from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface ParticleFieldProps {
  count?: number;
  color?: string;
  speed?: number;
  opacity?: number;
  maxSize?: number;
  direction?: 'up' | 'down' | 'random';
}

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  delay: number;
  opacity: number;
}

export const ParticleField: React.FC<ParticleFieldProps> = ({
  count = 40,
  color = '#ff4400',
  speed = 1,
  opacity = 0.6,
  maxSize = 4,
  direction = 'up',
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const particles = useMemo<Particle[]>(() => {
    const seeded = (i: number) => {
      let s = i * 2654435761;
      s = ((s >>> 16) ^ s) * 45679;
      s = ((s >>> 16) ^ s) * 45679;
      return ((s >>> 16) ^ s) / 4294967296 + 0.5;
    };

    return Array.from({ length: count }, (_, i) => ({
      x: seeded(i * 3) * width,
      y: seeded(i * 3 + 1) * height,
      size: 1 + seeded(i * 3 + 2) * (maxSize - 1),
      speedX: direction === 'random' ? (seeded(i * 7) - 0.5) * 2 * speed : (seeded(i * 7) - 0.5) * 0.3 * speed,
      speedY: direction === 'up' ? -(0.5 + seeded(i * 5) * 1.5) * speed :
              direction === 'down' ? (0.5 + seeded(i * 5) * 1.5) * speed :
              (seeded(i * 5) - 0.5) * 2 * speed,
      delay: seeded(i * 11) * 60,
      opacity: 0.3 + seeded(i * 13) * 0.7,
    }));
  }, [count, width, height, speed, maxSize, direction]);

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      {particles.map((p, i) => {
        const t = Math.max(0, frame - p.delay);
        const x = ((p.x + p.speedX * t) % (width + 20)) - 10;
        const rawY = p.y + p.speedY * t;
        const y = direction === 'up'
          ? ((rawY % height) + height) % height
          : direction === 'down'
          ? rawY % height
          : ((rawY % (height + 20)) + height + 20) % (height + 20) - 10;

        const pulse = 0.7 + 0.3 * Math.sin(t * 0.05 + i);

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: color,
              opacity: opacity * p.opacity * pulse,
              boxShadow: `0 0 ${p.size * 2}px ${color}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
