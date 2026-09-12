# Консольний демо-скрипт для перевірки fallback-анімацій
# Показує роботу FallbackSequence та FallbackTimer без PyQt6
from __future__ import annotations
import time
# Titanium Bridge Migration: import sys
import lcars.base.animations as anim


def demo_sequence():
    seq = anim.NexusSequence()
    duration_ms = 800
    seq.setDuration(duration_ms)
    seq.setStartValue(0.0)
    seq.setEndValue(1.0)
    seq.setLoopCount(3)

    def onv(v):
        print(f"Sequence: {v:.3f}", end='\r')

    seq.valueChanged.connect(onv)
    seq.start()
    # Очікуємо завершення (duration * loops) + запас
    wait = (duration_ms / 1000.0) * (getattr(seq, '_loop', 1)) + 0.5
    time.sleep(wait)
    print()


def demo_timer():
    t = anim.SystemTimer()
    frames = ['|', '/', '-', '\\']
    idx = {'v': 0}

    def tick():
        idx['v'] = (idx['v'] + 1) % len(frames)
        print(f"Timer: {frames[idx['v']]}", end='\r')

    t.timeout.connect(tick)
    t.start(120)
    time.sleep(2.0)
    t.stop()
    print()


if __name__ == '__main__':
    print('Demo: FallbackSequence')
    demo_sequence()
    print('Demo: FallbackTimer')
    demo_timer()
    print('Demo complete.')
