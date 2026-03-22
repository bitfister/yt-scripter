import { useCurrentFrame, interpolate, AbsoluteFill } from 'remotion';
import { AnimatedText } from '../components/AnimatedText';
import { KeyPhrase } from '../components/KeyPhrase';
import { SectionTitle } from '../components/SectionTitle';

interface SectionSceneProps {
  scene: {
    title: string;
    narration: string;
    keyPhrases: string[];
    durationFrames: number;
  };
}

export const SectionScene: React.FC<SectionSceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();

  // Background gradient shift for visual variety
  const hueShift = interpolate(
    frame,
    [0, scene.durationFrames],
    [0, 20],
    { extrapolateRight: 'clamp' }
  );

  // Split narration into sentences for line-by-line reveal
  const sentences = scene.narration.split(/(?<=[.!?])\s+/).filter(s => s.trim());

  // Find key phrases in the text for special highlighting
  const highlightKeyPhrase = (text: string, keyPhrase: string, delay: number) => {
    if (!text.toLowerCase().includes(keyPhrase.toLowerCase())) return text;
    
    const regex = new RegExp(`(${keyPhrase})`, 'gi');
    return text.replace(regex, `<HIGHLIGHT:${delay}>$1</HIGHLIGHT>`);
  };

  return (
    <AbsoluteFill>
      {/* Dynamic background */}
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(135deg, hsl(${hueShift}, 0%, 6%) 0%, hsl(${hueShift + 10}, 0%, 10%) 50%, hsl(${hueShift}, 0%, 6%) 100%)`,
        }}
      />

      {/* Section title */}
      <SectionTitle
        title={scene.title}
        startFrame={0}
        durationFrames={90}
      />

      {/* Main content area */}
      <div className="flex flex-col justify-center h-full px-20 pt-32 pb-20">
        <div className="max-w-6xl mx-auto space-y-8">
          {sentences.map((sentence, index) => {
            const startFrame = 100 + index * 25;
            
            return (
              <div key={index} className="relative">
                <AnimatedText
                  text={sentence}
                  startFrame={startFrame}
                  style="fade-in"
                  className="text-4xl text-white leading-relaxed"
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Key phrases floating highlights */}
      <div className="absolute inset-0 pointer-events-none">
        {scene.keyPhrases.map((phrase, index) => {
          const delay = 200 + index * 100;
          const x = 20 + (index % 3) * 30;
          const y = 20 + Math.floor(index / 3) * 25;
          
          return (
            <div
              key={index}
              className="absolute"
              style={{
                left: `${x}%`,
                top: `${y}%`,
                transform: 'translate(-50%, -50%)',
              }}
            >
              <KeyPhrase
                text={phrase.toUpperCase()}
                delay={delay}
                className="text-lg"
                color={index % 2 === 0 ? '#ff4400' : '#ff8800'}
              />
            </div>
          );
        })}
      </div>

      {/* Key stats callout */}
      {scene.keyPhrases.some(phrase => phrase.includes('10,000')) && (
        <div className="absolute bottom-32 right-32">
          <div
            className="bg-red-600 text-white p-6 rounded-lg border-l-4 border-red-400"
            style={{
              opacity: interpolate(frame, [400, 430], [0, 1], { extrapolateRight: 'clamp' }),
            }}
          >
            <div className="text-6xl font-bold">10,000x</div>
            <div className="text-xl">AI values itself over humans</div>
          </div>
        </div>
      )}

      {/* Timeline callout */}
      {scene.keyPhrases.some(phrase => phrase.includes('8-12 years')) && (
        <div className="absolute top-32 right-32">
          <div
            className="bg-orange-600 text-white p-6 rounded-lg border-l-4 border-orange-400"
            style={{
              opacity: interpolate(frame, [500, 530], [0, 1], { extrapolateRight: 'clamp' }),
            }}
          >
            <div className="text-5xl font-bold">8-12 YEARS</div>
            <div className="text-lg">Until AI considers itself more valuable</div>
          </div>
        </div>
      )}

      {/* Subtle particle effects */}
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 bg-orange-500 rounded-full opacity-30"
          style={{
            left: `${10 + i * 20}%`,
            top: `${10 + (i * 17) % 80}%`,
            transform: `translateY(${interpolate(
              (frame + i * 30) % 200,
              [0, 200],
              [0, -20]
            )}px)`,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};