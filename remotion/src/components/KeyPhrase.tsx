import { useCurrentFrame, spring, useVideoConfig } from 'remotion';

interface KeyPhraseProps {
  text: string;
  delay: number;
  color?: string;
  className?: string;
}

export const KeyPhrase: React.FC<KeyPhraseProps> = ({
  text,
  delay,
  color = '#ff4400',
  className = ''
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - delay,
    fps,
    config: {
      damping: 12,
      mass: 0.5,
    },
    from: 0.8,
    to: 1,
  });

  const overshootScale = spring({
    frame: frame - delay,
    fps,
    config: {
      damping: 10,
      mass: 0.3,
    },
    from: 1,
    to: 1.1,
    durationInFrames: 20,
  });

  const finalScale = frame > delay + 20 ? scale : overshootScale * scale;

  return (
    <span
      className={`inline-block font-bold px-3 py-1 rounded-full ${className}`}
      style={{
        transform: `scale(${finalScale})`,
        backgroundColor: color,
        color: 'white',
        opacity: frame >= delay ? 1 : 0,
      }}
    >
      {text}
    </span>
  );
};