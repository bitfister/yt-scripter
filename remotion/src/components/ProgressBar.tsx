import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

interface ProgressBarProps {
  color?: string;
  position?: 'top' | 'bottom';
  height?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  color = '#ff4400',
  position = 'bottom',
  height = 3,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = (frame / durationInFrames) * 100;

  return (
    <div
      style={{
        position: 'absolute',
        [position]: 0,
        left: 0,
        right: 0,
        height,
        backgroundColor: '#ffffff10',
        zIndex: 100,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          backgroundColor: color,
          boxShadow: `0 0 8px ${color}80`,
          transition: 'none',
        }}
      />
    </div>
  );
};
