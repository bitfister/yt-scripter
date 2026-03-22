import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';

interface TimelineEvent {
  label: string;
  year?: string;
}

interface TimelineBarProps {
  events: TimelineEvent[];
  startFrame?: number;
  orientation?: 'horizontal' | 'vertical';
  color?: string;
}

export const TimelineBar: React.FC<TimelineBarProps> = ({
  events,
  startFrame = 0,
  orientation = 'horizontal',
  color = '#ff8800',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relFrame = frame - startFrame;
  if (relFrame < 0) return null;

  const isHorizontal = orientation === 'horizontal';
  const framesPerEvent = 40;

  // Line progress
  const lineProgress = interpolate(
    relFrame,
    [0, events.length * framesPerEvent],
    [0, 100],
    { extrapolateRight: 'clamp' }
  );

  if (isHorizontal) {
    return (
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 120px',
        }}
      >
        {/* Timeline line */}
        <div style={{ position: 'relative', width: '100%', height: 4, marginBottom: 60 }}>
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${lineProgress}%`,
              height: '100%',
              backgroundColor: color,
              boxShadow: `0 0 15px ${color}60`,
              borderRadius: 2,
            }}
          />
          {/* Track background */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: '100%',
              height: '100%',
              backgroundColor: '#ffffff10',
              borderRadius: 2,
            }}
          />
          {/* Animated line on top */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${lineProgress}%`,
              height: '100%',
              backgroundColor: color,
              boxShadow: `0 0 15px ${color}60`,
              borderRadius: 2,
              zIndex: 1,
            }}
          />

          {/* Event dots */}
          {events.map((event, i) => {
            const pos = (i / (events.length - 1)) * 100;
            const eventFrame = i * framesPerEvent + 10;
            const dotScale = spring({
              frame: Math.max(0, relFrame - eventFrame),
              fps,
              config: { damping: 10, mass: 0.5 },
            });
            const labelOpacity = interpolate(
              relFrame,
              [eventFrame + 5, eventFrame + 20],
              [0, 1],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            );

            return (
              <div key={i} style={{ position: 'absolute', left: `${pos}%`, top: '50%', transform: 'translate(-50%, -50%)', zIndex: 2 }}>
                {/* Dot */}
                <div
                  style={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    backgroundColor: color,
                    transform: `scale(${dotScale})`,
                    boxShadow: `0 0 12px ${color}80`,
                  }}
                />
                {/* Year above */}
                {event.year && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: 24,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontFamily: 'system-ui, sans-serif',
                      fontWeight: 700,
                      fontSize: 20,
                      color,
                      opacity: labelOpacity,
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {event.year}
                  </div>
                )}
                {/* Label below */}
                <div
                  style={{
                    position: 'absolute',
                    top: 28,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontFamily: 'system-ui, sans-serif',
                    fontSize: 18,
                    color: '#cccccc',
                    opacity: labelOpacity,
                    whiteSpace: 'nowrap',
                    maxWidth: 180,
                    textAlign: 'center',
                  }}
                >
                  {event.label}
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    );
  }

  // Vertical orientation
  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 200px',
      }}
    >
      <div style={{ position: 'relative', height: '100%', width: 4 }}>
        {/* Track */}
        <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', backgroundColor: '#ffffff10', borderRadius: 2 }} />
        {/* Progress */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: '100%',
            height: `${lineProgress}%`,
            backgroundColor: color,
            boxShadow: `0 0 15px ${color}60`,
            borderRadius: 2,
            zIndex: 1,
          }}
        />

        {events.map((event, i) => {
          const pos = (i / (events.length - 1)) * 100;
          const eventFrame = i * framesPerEvent + 10;
          const dotScale = spring({
            frame: Math.max(0, relFrame - eventFrame),
            fps,
            config: { damping: 10, mass: 0.5 },
          });
          const labelOpacity = interpolate(relFrame, [eventFrame + 5, eventFrame + 20], [0, 1], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          });

          return (
            <div key={i} style={{ position: 'absolute', top: `${pos}%`, left: '50%', transform: 'translate(-50%, -50%)', zIndex: 2, display: 'flex', alignItems: 'center' }}>
              <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: color, transform: `scale(${dotScale})`, boxShadow: `0 0 12px ${color}80` }} />
              <div style={{ marginLeft: 24, opacity: labelOpacity, whiteSpace: 'nowrap' }}>
                {event.year && <span style={{ fontFamily: 'system-ui, sans-serif', fontWeight: 700, fontSize: 20, color, marginRight: 12 }}>{event.year}</span>}
                <span style={{ fontFamily: 'system-ui, sans-serif', fontSize: 20, color: '#cccccc' }}>{event.label}</span>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
