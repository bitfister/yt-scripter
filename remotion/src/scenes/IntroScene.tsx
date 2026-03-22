import { useCurrentFrame, spring, useVideoConfig, interpolate, AbsoluteFill } from 'remotion';
import { AnimatedText } from '../components/AnimatedText';

interface IntroSceneProps {
  scene: {
    narration: string;
    keyPhrases: string[];
    durationFrames: number;
  };
  allScenes: Array<{ title: string; type: string; }>;
}

export const IntroScene: React.FC<IntroSceneProps> = ({ scene, allScenes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Topic title animation
  const titleScale = spring({
    frame,
    fps,
    config: {
      damping: 10,
      mass: 0.8,
    },
    from: 0.8,
    to: 1,
  });

  const titleOpacity = interpolate(frame, [0, 30], [0, 1]);

  // Get section titles for bullet points (excluding hook, intro, outro)
  const sectionTitles = allScenes
    .filter(s => s.type === 'section')
    .map(s => s.title);

  return (
    <AbsoluteFill>
      {/* Background gradient */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #0f0f0f 0%, #1f1f1f 100%)',
        }}
      />

      <div className="flex flex-col items-center justify-center h-full px-16">
        {/* Main topic title */}
        <div
          className="mb-16 text-center"
          style={{
            transform: `scale(${titleScale})`,
            opacity: titleOpacity,
          }}
        >
          <h1 className="text-8xl font-bold text-white mb-4">AI SCARY WARNING</h1>
          <div className="w-32 h-1 bg-gradient-to-r from-transparent via-orange-500 to-transparent mx-auto" />
        </div>

        {/* Preview text */}
        <div className="mb-12 max-w-4xl text-center">
          <AnimatedText
            text="In the next few minutes, you'll discover uncomfortable truths about AI that institutions don't want you to know:"
            startFrame={60}
            style="fade-in"
            className="text-3xl text-gray-300 leading-relaxed"
          />
        </div>

        {/* Bullet points of what's covered */}
        <div className="space-y-6 max-w-5xl">
          {sectionTitles.map((title, index) => {
            const slideProgress = spring({
              frame: frame - (120 + index * 30),
              fps,
              config: {
                damping: 15,
                mass: 0.5,
              },
              from: 200,
              to: 0,
            });

            const opacity = interpolate(
              frame,
              [120 + index * 30, 120 + index * 30 + 20],
              [0, 1],
              { extrapolateRight: 'clamp' }
            );

            return (
              <div
                key={index}
                className="flex items-center"
                style={{
                  transform: `translateX(${slideProgress}px)`,
                  opacity,
                }}
              >
                <div className="w-3 h-3 bg-orange-500 rounded-full mr-6 flex-shrink-0" />
                <p className="text-2xl text-white font-medium">{title}</p>
              </div>
            );
          })}
        </div>

        {/* Final CTA */}
        <div className="mt-16">
          <AnimatedText
            text="The evidence is documented. The timeline is real. Let me show you."
            startFrame={300}
            style="fade-in"
            className="text-3xl text-orange-500 font-bold text-center"
          />
        </div>
      </div>

      {/* Subtle animated background elements */}
      <div className="absolute top-20 right-20 opacity-20">
        <div
          className="w-2 h-2 bg-orange-500 rounded-full"
          style={{
            transform: `scale(${interpolate(frame % 120, [0, 60, 120], [1, 1.5, 1])})`,
          }}
        />
      </div>
      <div className="absolute bottom-20 left-20 opacity-20">
        <div
          className="w-2 h-2 bg-red-500 rounded-full"
          style={{
            transform: `scale(${interpolate((frame + 60) % 120, [0, 60, 120], [1, 1.5, 1])})`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};