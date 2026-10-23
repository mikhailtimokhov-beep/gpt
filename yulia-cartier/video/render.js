// Renders index.html frame-by-frame and encodes film.mp4 with music.wav.
// Usage: node render.js [fps] [--stills t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const fps = +(process.argv[2] || 30);
  const stills = (process.argv.find(a => a.startsWith('--stills=')) || '').slice(9);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'index.html'), { waitUntil: 'load' }).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(800);
  if (stills) {
    for (const t of stills.split(',')) {
      await p.evaluate(t => render(t), +t);
      await p.screenshot({ path: `still-${t}.jpg`, type: 'jpeg', quality: 80 });
    }
    await b.close(); return;
  }
  const dur = await p.evaluate(() => DURATION);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', 'music.wav', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '20',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'film.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * fps);
  for (let i = 0; i <= n; i++) {
    await p.evaluate(t => render(t), i / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 90 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log('done');
})();
