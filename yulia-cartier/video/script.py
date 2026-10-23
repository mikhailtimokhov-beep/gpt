# Screenplay + voice-over builder for film III.
# Synthesizes the male narrator (French salutation + Russian text), fits scene lengths to the voice,
# and writes script.js (scene timeline for film3.html), voice_track.wav and duck.json (for music3.py).
import json, os, subprocess, hashlib, numpy as np, soundfile as sf, pyworld as pw

HERE = os.path.dirname(os.path.abspath(__file__))
TTS = '/root/tts'
SR = 22050
FINAL_VOICE = os.path.join(HERE, 'voice.wav')   # Misha's own recording

# Each scene: t (type), d (minimum length), visual fields, and optional voice parts.
# Part: ('fr', text) French salutation; ('hand', say) handwritten line read aloud; ('precept', say) closing line.
S = [
  dict(t='title', d=7.2),
  dict(t='text', d=9.3, bg='sepia', kicker='Погреб · сундук · письма',
       hand='Однажды дедушка попросил Франческу Картье принести из погреба бутылку вина. Там, в старом сундуке, лежали письма — сто лет переписки семьи.',
       voice=[('hand', None)]),
  dict(t='text', d=7.5, hand='Юля прочла эту книгу.', precept='А эти письма — для неё.',
       voice=[('hand', None), ('precept', None)]),

  dict(t='letter', d=13, img='lf', mono='LF', name='Луи-Франсуа Картье', meta='Париж · Монторгёй, 29 · 1847',
       hand='Я начинал с мастерской своего учителя и одного верстака. Вы — с одного браслета для мамы.',
       precept='Не стесняйтесь маленького. Так рождаются реликвии.',
       voice=[('fr', 'Ma chère Julie.'), ('hand', None), ('precept', None)]),
  dict(t='letter', d=13, img='alfred', mono='A', name='Альфред Картье', meta='Париж в осаде · 1870',
       hand='Когда Париж был в осаде, я увёз всё, что у нас было, в Лондон — и сохранил дом. У вас был свой трудный год. Вы выстояли.',
       precept='Дом проверяют не праздники, а осады.',
       voice=[('fr', 'Ma chère Julie.'), ('hand', None), ('precept', None)]),
  dict(t='letter', d=13, img='louis', mono='L', name='Луи Картье', meta='Рю де ла Пэ, 13 · 1904',
       hand='Я сделал часы для друга-авиатора: в полёте ему было неудобно доставать карманные. Лучшие вещи рождаются из заботы об одном человеке — как ваши гравировки.',
       precept='Делайте для одного — и вас узнает весь мир.',
       voice=[('fr', 'Chère Madame.'), ('hand', None), ('precept', None)]),
  dict(t='letter', d=13, img='pierre', mono='P', name='Пьер Картье', meta='Нью-Йорк · Пятая авеню · 1917',
       hand='Я продал «Надежду», рассказав историю алмаза. А дом на Пятой авеню получил за нитку жемчуга. Вещь стоит столько, сколько в ней смысла.',
       precept='Не бойтесь цены своих историй — и не бойтесь расти.',
       voice=[('fr', 'Chère Julie.'), ('hand', None), ('precept', None)]),
  dict(t='letter', d=13, img='jacques', mono='J', name='Жак Картье', meta='Лондон · Индия · 1911',
       hand='Я объездил Индию и Персидский залив в поисках камней и слушал людей больше, чем торговался. Ваши клиентки пишут: «Красота в деталях — это Juliette’s».',
       say_hand='Я объездил Индию и Персидский залив в поисках камней и слушал людей больше, чем торговался. Ваши клиентки пишут: красота в деталях — это Джульеттс.',
       precept='Храните их истории. Однажды они станут вашей книгой.',
       voice=[('fr', 'Ma chère Julie.'), ('hand', None), ('precept', None)]),
  dict(t='letter', d=13, img='jeanne', mono='JT', name='Жанна Туссен', meta='«Пантера» · 1933',
       hand='Я не умела рисовать — я умела знать, чего хочет женщина. Луи доверил мне вкус всего дома.',
       precept='Никому не отдавайте свой вкус. И не забывайте украшать себя.',
       voice=[('fr', 'Ma chère Julie.'), ('hand', None), ('precept', None)]),

  dict(t='photo', d=6.5, img='y2017', year='2017', hand='mamy-bracelets. Один браслет. Одна мама. Одна идея.',
       say_hand='Две тысячи семнадцатый. Один браслет. Одна мама. Одна идея.', voice=[('hand', None)]),
  dict(t='photo', d=5.2, img='yblossom', pos='42% 40%', year='Juliette’s', hand='Имя, данное в её честь.',
       say_hand='Джульеттс. Имя, данное в её честь.', voice=[('hand', None)]),
  dict(t='dark', d=7.4, hand='Самый трудный год. Многие закрывались. Вы — нет.',
       say_hand='Две тысячи двадцать второй. Самый трудный год. Многие закрывались. Вы — нет.', voice=[('hand', None)]),
  dict(t='photo', d=7, img='tatyana', year='Татьяна', hand='Оправа, без которой камень не держится.',
       say_hand='Татьяна. Оправа, без которой камень не держится.', voice=[('hand', None)]),
  dict(t='photo', d=7, img='ytoday', year='Сегодня', hand='2 000 моделей · 29 000 историй.',
       say_hand='Сегодня. Две тысячи моделей. Двадцать девять тысяч историй.', voice=[('hand', None)]),
  dict(t='photo', d=8, img='sveta', year='Света, 10', hand='Картье были домом четырёх поколений. У Juliette’s уже есть следующая глава.',
       say_hand='Света, десять лет. Картье были домом четырёх поколений. У Джульеттс уже есть следующая глава.', voice=[('hand', None)]),

  dict(t='text', d=6.5, hand='В 1969-м в нашем доме появился браслет, который закрывают маленькой отвёрткой.',
       say_hand='В тысяча девятьсот шестьдесят девятом в нашем доме появился браслет, который закрывают маленькой отвёрткой.',
       precept='Love. Любовь, закреплённая навсегда.', say_precept='Лав. Любовь, закреплённая навсегда.', sig='Жанна Туссен',
       voice=[('hand', None), ('precept', None)]),
  dict(t='gift', d=5.2, img='../photos/earrings-1.jpg', k='Première · Lumière', title='Свет — вам как женщине',
       voice=[('fr', 'Lumière.'), ('say', 'Свет — вам как женщине.')]),
  dict(t='gift', d=5.5, img='../photos/earrings-2.jpg', contain=True, k='Seconde · Union', title='Союз — вам как основательнице',
       hand='Внутри нет ничьих имён. Это место — для вашего.',
       voice=[('fr', 'Union.'), ('say', 'Союз — вам как основательнице.'), ('hand', None)]),

  dict(t='photo', d=7.8, img='yfinal', year='', hand='Ma chère Julie…', final_voice=True),
  dict(t='final', d=10.6),
]

def piper(model, text, out, scale=1.0):
    subprocess.run([f'{TTS}/piper/piper', '-m', f'{TTS}/{model}.onnx', '--length_scale', str(scale),
                    '--sentence_silence', '0.3', '-f', out], input=text.encode(), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    x, sr = sf.read(out)
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    return x.astype(np.float64)

def male(x):
    f0, t = pw.harvest(x, SR); sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    n = sp.shape[1]; idx = np.clip(np.arange(n) / 0.86, 0, n - 1)
    warp = lambda m: np.ascontiguousarray([np.interp(idx, np.arange(n), r) for r in m])
    y = pw.synthesize(f0 * 0.60, warp(sp), warp(ap), SR)
    return y / (np.max(np.abs(y)) + 1e-9) * .9

def trim(x, th=.01):
    nz = np.where(np.abs(x) > th)[0]
    return x[max(0, nz[0] - 200): nz[-1] + 400] if len(nz) else x

cache = os.path.join(HERE, 'vo_cache'); os.makedirs(cache, exist_ok=True)
VO = os.path.join(HERE, 'vo')
def load_clip(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return trim(np.frombuffer(raw, dtype=np.float32).astype(np.float64), .005)

def synth(kind, text, cid=None):
    if cid and os.path.exists(os.path.join(VO, cid + '.mp3')):   # natural neural clip generated by gen_vo.py
        y = load_clip(os.path.join(VO, cid + '.mp3')); return y / (np.max(np.abs(y)) + 1e-9) * .9
    key = os.path.join(cache, hashlib.md5((kind + text).encode()).hexdigest() + '.wav')
    if os.path.exists(key):
        return sf.read(key)[0]
    if kind == 'fr':
        y = trim(piper('fr-gilles-low', text, '/tmp/p.wav', 1.05)); y = y / np.max(np.abs(y)) * .85
    else:
        y = trim(male(piper('ru-irinia-medium', text, '/tmp/p.wav', 1.06)))
    sf.write(key, y, SR); return y

t = 0.0; clips = []; scenes = []; duck = []
for si, s in enumerate(S):
    s = dict(s); cues = {}
    lead = 1.0 if s['t'] == 'letter' else (0.9 if s['t'] == 'photo' else 0.5)
    cur = lead
    for k, (kind, txt) in enumerate(s.get('voice', [])):
        if kind == 'hand':   txt = s.get('say_hand', s['hand'])
        if kind == 'precept': txt = s.get('say_precept', s['precept'])
        y = synth('fr' if kind == 'fr' else 'ru', txt, f's{si:02d}_{k}')
        dur = len(y) / SR
        clips.append((t + cur, y)); duck.append((t + cur, t + cur + dur))
        if kind == 'hand':    cues['write'] = round(cur, 2); cues['cps'] = round(len(s['hand']) / max(dur * .92, .5), 2)
        if kind == 'precept': cues['precept'] = round(cur, 2)
        if kind == 'fr' and s['t'] == 'gift': cues['title'] = round(cur, 2)
        cur += dur + 0.45
    if s.get('final_voice'):
        y, sr = sf.read(FINAL_VOICE)
        if y.ndim > 1: y = y.mean(axis=1)
        y = np.interp(np.arange(int(len(y) * SR / sr)) * sr / SR, np.arange(len(y)), y)
        clips.append((t + 1.0, y)); duck.append((t + 1.0, t + 1.0 + len(y) / SR))
    d = max(s['d'], cur + 1.2) if s.get('voice') else s['d']
    s.update(a=round(t, 2), b=round(t + d, 2), cues=cues); s.pop('voice', None)
    scenes.append(s); t += d
total = max(t, max(a + len(y) / SR for a, y in clips) + 1.5)
scenes[-1]['b'] = round(total, 2)

track = np.zeros(int(SR * (total + 1)))
for a, y in clips:
    i = int(a * SR); track[i:i + len(y)] += y[:len(track) - i]
track = track / np.max(np.abs(track)) * .9
sf.write(os.path.join(HERE, 'voice_track.wav'), track, SR)
dark = next(s for s in scenes if s['t'] == 'dark')
json.dump(dict(total=total, duck=duck, quiet=[dark['a'], dark['b']]), open(os.path.join(HERE, 'duck.json'), 'w'))
open(os.path.join(HERE, 'script.js'), 'w').write('window.S = ' + json.dumps(scenes, ensure_ascii=False, indent=1) + ';\nwindow.DURATION = ' + str(round(total, 2)) + ';\n')
print('total', round(total, 1), 's,', len(clips), 'voice clips')
for s in scenes: print(f"{s['a']:7.2f}-{s['b']:7.2f} {s['t']:7s} {s.get('name') or s.get('year') or ''}")
