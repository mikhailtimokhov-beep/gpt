### Phase 0af: Ping-pong Loop（短动作正放倒放循环）

手势、产品旋转或生成视频动作的首尾不闭合，又需要往返循环时，用 `ping_pong_loop.py`。先把动作范围限制在几秒内；FFmpeg `reverse` 会缓存全部选中帧，planner 会记录保守内存估算并在超过 `--max-working-set-mib` 时提前停止。

```bash
python3 scripts/ping_pong_loop.py plan origin/gesture.mp4 \
  --start 1.2 --end 2.05 --cycles 4 \
  --delivery work/gesture-ping-pong.mp4 \
  --turnaround-proof verify/gesture-turnaround.mp4 \
  --loop-seam-proof verify/gesture-loop-seam.mp4 \
  --project-dir . \
  --output work/ping_pong_loop_plan.json \
  --markdown work/ping_pong_loop_plan.md
python3 scripts/ping_pong_loop.py apply work/ping_pong_loop_plan.json
```

周期使用 `0…N-1,N-2…1`，主动排除折返点和周期末尾的重复端帧。源音频固定丢弃，视觉批准后再接 BGM/SFX。正常速度看完 turnaround proof、loop-seam proof 和完整 delivery，对折返运动、循环运动、重复停帧、构图与创意意图全部 `pass` 后运行 `confirm`，再用 `verify --strict` 或 `pipeline_manifest.py --require ping_pong_loop_plan --strict` 放行。详见 [Ping-pong Loop](./docs/prompts/128-ping-pong-loop.md)。
