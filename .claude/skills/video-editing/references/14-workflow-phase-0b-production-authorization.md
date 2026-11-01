### Phase 0b: Production Authorization（按确切范围授权）

当流程涉及把素材交给外部服务、改变原始叙事顺序/删减范围、消耗生成额度、克隆真人声音、使用真人/未成年人/公众人物/品牌/IP，或直接发布时，在动作发生前先写 `production_authorization_scope.v1`。scope 必须命名项目内素材、具体动作、用途、exact provider/surface、可能的 cost/quota，以及适用的 rights subject；完整 schema 见 [Production Authorization](./docs/prompts/97-production-authorization.md)。

```bash
python3 scripts/production_authorization.py prepare \
  --project-dir . \
  --scope work/production_authorization_scope.json \
  --output work/production_authorization_request.json \
  --markdown work/production_authorization_request.md \
  --response-template work/production_authorization_response.json \
  --strict

# 逐项填写 approve/reject、note、rights basis 与 evidence_note 后：
python3 scripts/production_authorization.py audit \
  --project-dir . \
  --request work/production_authorization_request.json \
  --response work/production_authorization_response.json \
  --output work/production_authorization.json \
  --markdown work/production_authorization.md \
  --strict

python3 scripts/production_authorization.py verify \
  --project-dir . \
  --report work/production_authorization.json \
  --strict
```

`prepare` 绑定 scope 与每个 source asset 的相对路径、大小和 SHA-256；`audit` 要求动作与权利项完整逐项决定；`verify` 现场重读 scope、素材、request、response 并重算 report。任一 provider、用途、成本说明、权利对象、素材字节或决定变化都会让旧报告失效。该 artifact 只记录本地、自报的复核范围，不执行上传/剪辑/生成/发布，也不替代身份认证、数字签名、真实授权文件或法律意见。
