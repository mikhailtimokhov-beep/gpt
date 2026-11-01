### Phase 2c: Video Understanding（抽样帧 + 可选 YOLO）

当素材里的人、手机、电脑屏幕、产品、车辆或其他动态对象会影响裁切、隐私遮挡或 B-roll 选择时，使用 [video_understanding.py](./scripts/video_understanding.py) 生成结构化视觉理解 artifact。默认不需要安装 detector；如果要运行 YOLO，先安装可选依赖 `ultralytics`。

需要在无检测模型时查看运动位置，可运行 `python3 scripts/motion_center.py analyze video.mp4 --output work/motion_center.json`，再用 `verify work/motion_center.json` 现场复测。报告按默认 2 fps 比较缩小后的相邻灰度帧；`local_motion` 给出 0–1 归一化中心，`static` 和 `global_change` 不给中心。像素运动可能来自背景或镜头移动，不能当作人物检测结果直接交给 `smart_reframe.py --detections`；先回看对应时间点，再决定构图。

```bash
# 无 detector：只抽样帧并生成 review shell
python3 scripts/video_understanding.py video.mp4 \
  --output work/video_understanding.json \
  --markdown work/video_understanding.md

# 可选 YOLO：检测对象并生成 detections/tracks/scene_tags
pip install ultralytics
python3 scripts/video_understanding.py video.mp4 \
  --scene-boundaries work/scene_boundaries.json \
  --detector yolo \
  --model yolo11n.pt \
  --output work/video_understanding.json \
  --markdown work/video_understanding.md \
  --strict
```

输出：
- `video_understanding.json` — `video_understanding.v1`，包含 `frames[]`、`detections[]`、`tracks[]`、`scene_tags[]`、`warnings[]`
- `video_understanding.md` — 人工 review 表，列出抽样帧、检测数量、轨迹、标签和 warning

典型下游：
```bash
python3 scripts/smart_reframe.py video.mp4 \
  --detections work/video_understanding.json \
  --platform douyin \
  --output work/reframe_douyin.json \
  --markdown work/reframe_douyin.md

python3 scripts/privacy_redact.py \
  --video video.mp4 \
  --detections work/video_understanding.json \
  --output work/privacy_redaction.json \
  --markdown work/privacy_redaction.md
```

注意：内置 tracklets 是为口播剪辑做的轻量关联，不等同于逐帧多目标跟踪。对体育、车流、多人遮挡等高动态素材，可以用 Ultralytics `model.track(..., tracker="bytetrack.yaml")`、BoT-SORT 或 Norfair 生成更密集的检测/track 结果，再转换成同一份 `detections[]` / `tracks[]` JSON。
