# Run on a machine with internet: pip install edge-tts ; python gen_vo.py
# Generates natural neural voice-over clips listed in vo_manifest.json into ./vo/
# Behind an HTTPS proxy (cloud sessions) it uses HTTPS_PROXY and the proxy's CA bundle.
import asyncio, json, os, ssl, edge_tts, edge_tts.communicate
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo'); os.makedirs(OUT, exist_ok=True)
items = json.load(open(os.path.join(HERE, 'vo_manifest.json'), encoding='utf-8'))
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
CA = '/root/.ccr/ca-bundle.crt'
if PROXY and os.path.exists(CA):
    edge_tts.communicate._SSL_CTX = ssl.create_default_context(cafile=CA)
async def main():
    for it in items:
        path = os.path.join(OUT, it['id'] + '.mp3')
        if os.path.exists(path) and os.path.getsize(path) > 0: continue
        for attempt in range(4):
            try:
                await edge_tts.Communicate(it['text'], it['voice'], rate=it['rate'], pitch=it.get('pitch', '+0Hz'), proxy=PROXY).save(path)
                break
            except Exception as e:
                print('retry', it['id'], e); await asyncio.sleep(2)
        print('ok', it['id'], it['voice'])
asyncio.run(main())
