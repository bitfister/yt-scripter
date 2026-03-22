import { useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface SectionTitleProps {
  title: string;
  startFrame?: number;
  durationFrames?: number;
  color?: string;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({
  title,
  startFrame = 0,
  durationFrames = 90,
  color = '#ff8800'
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideProgress = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: 15,
      mass: 0.8,
    },
    from: -400,
    to: 0,
  });

  const opacity = interpolate(
    frame,
    [startFrame + durationFrames - 30, startFrame + durationFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const isVisible = frame >= startFrame && frame < startFrame + durationFrames;

  if (!isVisible) return null;

  return (
    <div
      className="absolute bottom-20 left-0 bg-gradient-to-r from-transparent via-black/80 to-transparent px-8 py-3"
      style={{
        transform: `translateX(${slideProgress}px)`,
        opacity,
        backgroundColor: `${color}20`,
        borderLeft: `4px solid ${color}`,
      }}
    >
      <h2 className="text-2xl font-bold text-white">{title}</h2>
    </div>
  );
};