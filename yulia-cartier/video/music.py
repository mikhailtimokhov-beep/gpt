# Original musette-style waltz in A minor, music-box timbre. Royalty-free (generated).
import numpy as np, wave
SR = 44100
BPM = 126
BEAT = 60 / BPM
TOTAL = 62.1

A, B = 'A', 'B'
# (chord, [(midi, beats), ...]) — 3 beats per bar
PHRASE = [
 ('Am', [(69,1),(72,1),(76,1)]), ('Dm', [(77,2),(76,.5),(74,.5)]),
 ('G',  [(74,1),(71,1),(67,1)]), ('C',  [(76,2),(72,1)]),
 ('F',  [(81,1.5),(79,.5),(77,1)]), ('Dm', [(77,1),(76,1),(74,1)]),
 ('E7', [(76,1.5),(74,.5),(71,1)]), ('Am', [(69,3)]),
 ('Am', [(72,1),(76,1),(81,1)]), ('Dm', [(81,1.5),(79,.5),(77,1)]),
 ('G',  [(79,1),(77,1),(74,1)]), ('C',  [(76,3)]),
 ('F',  [(72,1),(77,1),(81,1)]), ('Dm', [(79,1),(77,1),(74,1)]),
 ('E7', [(71,1),(74,1),(68,1)]), ('Am', [(69,3)]),
]
BASS = {'Am':45,'Dm':50,'G':43,'C':48,'F':41,'E7':40}
CHORD = {'Am':[57,60,64],'Dm':[57,62,65],'G':[55,59,62],'C':[55,60,64],'F':[57,60,65],'E7':[56,59,62]}
bars = PHRASE + PHRASE + PHRASE[8:] + [('Am', [(69,3)])]

def f(m): return 440 * 2 ** ((m - 69) / 12)
out = np.zeros(int(SR * (TOTAL + 3)))

def add(t, m, dur, amp, kind):
    n = int(SR * min(dur + 1.6, 4.0)); i = int(SR * t)
    x = np.arange(n) / SR; fr = f(m)
    if kind == 'box':      # music box: bright, fast decay, inharmonic sparkle
        s = (np.sin(2*np.pi*fr*x) + .45*np.sin(2*np.pi*fr*2*x)*np.exp(-x*6) + .18*np.sin(2*np.pi*fr*5.4*x)*np.exp(-x*14))
        env = np.exp(-x * 2.6) * np.minimum(1, x / .004)
    elif kind == 'acc':    # accordion-ish reed for chords: sustained, soft
        s = sum(np.sin(2*np.pi*fr*k*x*(1 + .0015*np.sin(2*np.pi*5.5*x))) / k**1.3 for k in range(1, 6))
        env = np.minimum(1, x / .03) * np.where(x < dur, 1, np.exp(-(x - dur) * 12))
    else:                  # bass: round
        s = np.sin(2*np.pi*fr*x) + .3*np.sin(2*np.pi*fr*2*x)
        env = np.exp(-x * 3) * np.minimum(1, x / .01)
    seg = amp * s * env
    out[i:i+n] += seg[:max(0, len(out) - i)]

t = 0.0
for chord, notes in bars:
    add(t, BASS[chord], BEAT, .32, 'bass')
    for k in (1, 2):
        for m in CHORD[chord]:
            add(t + k*BEAT, m, BEAT*.55, .045, 'acc')
    tt = t
    for m, b in notes:
        add(tt, m, b*BEAT, .30, 'box'); add(tt, m + 12, b*BEAT, .06, 'box')
        tt += b * BEAT
    t += 3 * BEAT

# simple room reverb
for d, g in ((.031,.35),(.047,.28),(.071,.22),(.113,.16),(.173,.11)):
    k = int(SR*d); out[k:] += g * out[:-k].copy() * .6

out = out[:int(SR*TOTAL)]
tl = np.arange(len(out)) / SR
gain = np.ones_like(tl)
gain *= np.clip(tl / 1.5, 0, 1)                                  # fade in
gain *= np.interp(tl, [0, 48.3, 49.4, 99], [1, 1, .28, .28])       # duck for voice-over
gain *= np.clip((TOTAL - tl) / 2.5, 0, 1)                         # fade out
out *= gain
out = out / np.max(np.abs(out)) * .85
pcm = (out * 32767).astype(np.int16)
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('bars', len(bars), 'music length', len(bars)*3*BEAT)
