import { useCurrentFrame, interpolate } from 'remotion';

interface AnimatedTextProps {
  text: string;
  startFrame: number;
  style?: 'word-by-word' | 'line-by-line' | 'fade-in';
  className?: string;
  stagger?: number;
}

export const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  startFrame,
  style = 'line-by-line',
  className = '',
  stagger
}) => {
  const frame = useCurrentFrame();

  if (style === 'fade-in') {
    const opacity = interpolate(
      frame,
      [startFrame, startFrame + 30],
      [0, 1],
      { extrapolateRight: 'clamp' }
    );
    
    return (
      <div className={className} style={{ opacity }}>
        {text}
      </div>
    );
  }

  let units: string[];
  let defaultStagger: number;

  if (style === 'word-by-word') {
    units = text.split(' ');
    defaultStagger = stagger || 3;
  } else {
    // line-by-line: split on periods and newlines
    units = text.split(/[.\n]+/).filter(unit => unit.trim());
    defaultStagger = stagger || 20;
  }

  return (
    <div className={className}>
      {units.map((unit, i) => {
        const unitStartFrame = startFrame + i * defaultStagger;
        const opacity = interpolate(
          frame,
          [unitStartFrame, unitStartFrame + 15],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return (
          <span key={i} style={{ opacity }}>
            {unit}
            {style === 'word-by-word' && i < units.length - 1 ? ' ' : ''}
            {style === 'line-by-line' && i < units.length - 1 ? '. ' : ''}
          </span>
        );
      })}
    </div>
  );
};