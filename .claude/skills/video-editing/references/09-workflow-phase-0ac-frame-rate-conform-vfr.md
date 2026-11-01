### Phase 0ac: Frame-rate Conform（手机 / 录屏 VFR 可选）

当源素材已知是 VFR、`r_frame_rate` 与 `avg_frame_rate` 可疑，或多段裁切后出现累积音画漂移时，先创建项目内 CFR 工作副本：

```bash
python3 scripts/frame_rate_conform.py plan origin/phone.mp4 \
  --fps 30 \
  --delivery work/phone-cfr.mp4 \
  --project-dir . \
  --output work/frame_rate_conform_plan.json \
  --markdown work/frame_rate_conform_plan.md
python3 scripts/frame_rate_conform.py apply work/frame_rate_conform_plan.json
python3 scripts/frame_rate_conform.py verify work/frame_rate_conform_plan.json --strict
```

脚本读取全部解码视频帧的 PTS 间隔，记录 variable/non-monotonic interval、精确目标有理帧率、源/输出 SHA-256、媒体合同和完整解码 receipt。apply 只有在输出帧间隔恒定、`frame_count ≈ duration × fps`、音画起止在容差内、显示尺寸/方向正确时才原子提升；之后所有转写、裁切、字幕、同步和渲染改用 `work/phone-cfr.mp4`。30/60 fps 需按真实运动和平台选择；升帧只复制画面，降帧会丢运动采样。HDR/BT.2020/>8-bit、明显既有音画 offset 或独立设备 clock drift 不在此工具的自动修复范围。详见 [Frame-rate Conform](./docs/prompts/112-frame-rate-conform.md)。
