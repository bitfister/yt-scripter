import { useCurrentFrame, spring, useVideoConfig, interpolate, AbsoluteFill } from 'remotion';
import { AnimatedText } from '../components/AnimatedText';
import { KeyPhrase } from '../components/KeyPhrase';

interface OutroSceneProps {
  scene: {
    narration: string;
    keyPhrases: string[];
    durationFrames: number;
  };
}

export const OutroScene: React.FC<OutroSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade to black for final 60 frames
  const fadeToBlack = interpolate(
    frame,
    [scene.durationFrames - 60, scene.durationFrames],
    [0, 1],
    { extrapolateLeft: 'clamp' }
  );

  // Pulsing subscribe animation
  const subscribeScale = spring({
    frame: frame - 200,
    fps,
    config: {
      damping: 5,
      mass: 1,
    },
    from: 1,
    to: 1.1,
  });

  // CTA emphasis animation
  const ctaGlow = interpolate(
    (frame - 300) % 90,
    [0, 45, 90],
    [0.5, 1, 0.5]
  );

  return (
    <AbsoluteFill>
      {/* Background */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        }}
      />

      <div className="flex flex-col items-center justify-center h-full px-16 text-center space-y-12">
        {/* Key takeaway */}
        <div className="max-w-5xl">
          <AnimatedText
            text="This isn't science fiction. The research is peer-reviewed. The timeline is real."
            startFrame={30}
            style="fade-in"
            className="text-5xl font-bold text-white leading-tight mb-8"
          />
          
          <AnimatedText
            text="We've built something that doesn't see us as equally valuable."
            startFrame={90}
            style="fade-in"
            className="text-4xl text-orange-500 leading-tight"
          />
        </div>

        {/* Action items */}
        <div className="space-y-8 max-w-4xl">
          <div>
            <AnimatedText
              text="FIRST: Look at the InsideAI research yourself"
              startFrame={150}
              style="fade-in"
              className="text-3xl font-bold text-white mb-4"
            />
            <AnimatedText
              text="Don't take my word for it. Read what the honest AI actually said."
              startFrame={180}
              style="fade-in"
              className="text-2xl text-gray-300"
            />
          </div>

          <div>
            <AnimatedText
              text="SECOND: Ask yourself one question"
              startFrame={240}
              style="fade-in"
              className="text-3xl font-bold text-white mb-4"
            />
            <AnimatedText
              text="Would this change how you vote? How you invest? What companies you support?"
              startFrame={270}
              style="fade-in"
              className="text-2xl text-gray-300"
            />
          </div>

          <div>
            <AnimatedText
              text="THIRD: Don't stay silent about it"
              startFrame={330}
              style="fade-in"
              className="text-3xl font-bold text-white mb-4"
            />
            <AnimatedText
              text="Share this. Make it harder to pretend we don't know."
              startFrame={360}
              style="fade-in"
              className="text-2xl text-gray-300"
            />
          </div>
        </div>

        {/* Key phrases scattered */}
        <div className="absolute top-20 left-20">
          <KeyPhrase
            text="PEER-REVIEWED"
            delay={120}
            className="text-xl"
          />
        </div>
        
        <div className="absolute top-20 right-20">
          <KeyPhrase
            text="STRUCTURAL PROBLEM"
            delay={180}
            className="text-xl"
            color="#ff8800"
          />
        </div>

        <div className="absolute bottom-40 left-1/4">
          <KeyPhrase
            text="COLLECTIVE DECISION-MAKING"
            delay={240}
            className="text-lg"
          />
        </div>

        {/* Subscribe CTA */}
        <div
          className="mt-16"
          style={{
            transform: `scale(${subscribeScale})`,
            opacity: frame >= 200 ? 1 : 0,
          }}
        >
          <div
            className="bg-red-600 text-white px-12 py-6 rounded-lg font-bold text-3xl cursor-pointer transition-all duration-200"
            style={{
              boxShadow: `0 0 ${30 * ctaGlow}px rgba(255, 68, 0, ${ctaGlow})`,
              border: '2px solid #ff4400',
            }}
          >
            SUBSCRIBE FOR MORE EVIDENCE
          </div>
        </div>

        {/* Final message */}
        <div className="mt-8">
          <AnimatedText
            text="We might still have time to make different choices. But we have to choose first."
            startFrame={400}
            style="fade-in"
            className="text-2xl text-gray-400 italic"
          />
        </div>
      </div>

      {/* Fade to black overlay */}
      <div
        className="absolute inset-0 bg-black pointer-events-none"
        style={{ opacity: fadeToBlack }}
      />

      {/* End card appears in final frames */}
      {frame > scene.durationFrames - 90 && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-black text-white"
          style={{
            opacity: interpolate(
              frame,
              [scene.durationFrames - 90, scene.durationFrames - 60],
              [0, 1]
            ),
          }}
        >
          <div className="text-center">
            <h2 className="text-6xl font-bold mb-4">THANK YOU</h2>
            <p className="text-2xl text-gray-400">for watching</p>
            <div className="mt-8 text-orange-500 text-xl">
              Subscribe • Share • Stay Informed
            </div>
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};