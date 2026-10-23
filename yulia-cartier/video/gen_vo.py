# Run on a machine with internet: pip install edge-tts ; python gen_vo.py
# Generates natural neural voice-over clips listed in vo_manifest.json into ./vo/
import asyncio, json, os, edge_tts
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo'); os.makedirs(OUT, exist_ok=True)
items = json.load(open(os.path.join(HERE, 'vo_manifest.json'), encoding='utf-8'))
async def main():
    for it in items:
        path = os.path.join(OUT, it['id'] + '.mp3')
        if os.path.exists(path) and os.path.getsize(path) > 0: continue
        await edge_tts.Communicate(it['text'], it['voice'], rate=it['rate']).save(path)
        print('ok', it['id'], it['voice'])
asyncio.run(main())
