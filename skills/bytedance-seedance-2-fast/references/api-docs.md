# API Reference: ByteDance Seedance 2.0 (Jimeng)

## Endpoint & Authentication
- **Endpoint**: `POST https://visual.volcengineapi.com`
- **Auth**: AWS Signature V4 compatible (Volcengine standard)

## Request Specification
- **req_key**: `jimeng_t2v_v30`
- **model**: `seedance-3-0-720p`
- **frames**: 121 (5s), 241 (10s)
- **aspect_ratio**: `16:9`

## Status Codes
- `in_queue`: Queued
- `processing`: Running
- `done`: Success
- `failed`: Failed

## Error Codes
- `401 SignatureDoesNotMatch`: Check signing logic in `generate_video.py`
- `429 Too Many Requests`: Triggered rate limit
