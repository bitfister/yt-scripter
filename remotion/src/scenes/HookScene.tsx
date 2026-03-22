import { useCurrentFrame, spring, useVideoConfig, interpolate, AbsoluteFill } from 'remotion';
import { AnimatedText } from '../components/AnimatedText';
import { KeyPhrase } from '../components/KeyPhrase';

interface HookSceneProps {
  scene: {
    narration: string;
    keyPhrases: string[];
    durationFrames: number;
  };
}

export const HookScene: React.FC<HookSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Continuous subtle zoom on background
  const bgScale = interpolate(
    frame,
    [0, scene.durationFrames],
    [1, 1.05],
    { extrapolateRight: 'clamp' }
  );

  // Dramatic entrance animation for main text
  const textScale = spring({
    frame,
    fps,
    config: {
      damping: 12,
      mass: 0.5,
    },
    from: 0,
    to: 1,
  });

  // Split narration for better visual impact
  const parts = scene.narration.split('A research paper just proved');
  const firstPart = parts[0];
  const secondPart = 'A research paper just proved' + (parts[1] || '');

  return (
    <AbsoluteFill>
      {/* Dark gradient background with subtle zoom */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%)',
          transform: `scale(${bgScale})`,
        }}
      />

      {/* Warning overlay pattern */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `repeating-linear-gradient(
            45deg,
            #ff4400 0px,
            #ff4400 2px,
            transparent 2px,
            transparent 20px
          )`,
        }}
      />

      <div className="flex flex-col items-center justify-center h-full px-16 text-center">
        {/* First part of narration */}
        <div
          className="mb-8"
          style={{
            transform: `scale(${textScale})`,
            opacity: textScale,
          }}
        >
          <AnimatedText
            text={firstPart}
            startFrame={30}
            style="word-by-word"
            className="text-6xl font-bold text-white leading-tight"
            stagger={4}
          />
        </div>

        {/* Key phrase highlight */}
        <div className="mb-8">
          <KeyPhrase
            text="2026"
            delay={200}
            className="text-5xl mx-2"
          />
        </div>

        {/* Second part with dramatic reveal */}
        <div className="space-y-6">
          <AnimatedText
            text={secondPart.split('.')[0] + '.'}
            startFrame={400}
            style="word-by-word"
            className="text-5xl font-bold text-white leading-tight"
            stagger={3}
          />
          
          {/* Final devastating line */}
          <div className="mt-8">
            <AnimatedText
              text="And they don't think you're worth very much."
              startFrame={700}
              style="word-by-word"
              className="text-6xl font-bold leading-tight"
              stagger={5}
            />
          </div>
        </div>

        {/* Additional key phrases scattered through */}
        <div className="absolute bottom-32 left-1/2 transform -translate-x-1/2">
          <KeyPhrase
            text="ADVANCED AI SYSTEMS"
            delay={500}
            className="text-3xl"
          />
        </div>

        <div className="absolute top-32 right-32">
          <KeyPhrase
            text="RANKED HUMAN LIVES"
            delay={600}
            className="text-2xl"
            color="#ff8800"
          />
        </div>
      </div>

      {/* Subtle vignette effect */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.6) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};