---
name: bytedance-seedance-2-fast
description: 使用字节豆包即梦 AI 视频生成 3.0 720P 模型生成视频。支持文生视频、图生视频（首帧/首尾帧）。使用火山引擎视觉服务 API（AccessKeyId/SecretAccessKey 签名认证）。当用户需要 AI 视频生成且指定使用字节豆包/即梦 AI 时使用。包含智能提示词优化工作流。
---

# 字节豆包即梦 AI 视频生成 3.0 720P

## 前置要求

- 火山引擎 AccessKeyId 和 SecretAccessKey
- 设置环境变量：
  ```bash
  export VOLC_ACCESSKEY="your-access-key-id"
  export VOLC_SECRETKEY="your-secret-access-key"
  ```

## 智能提示词优化工作流 (Intelligent Prompt Optimization)

为保证视频生成的专业审美与历史叙事的严谨性，所有视频生成任务应优先通过 LLM 润色提示词。

### 优化原则
1. **Cinematic Storytelling**：视觉语言优先，描述动作、光影、镜头而非抽象概念。
2. **Formula-Based**：必须严格遵循：`[Camera] + [Subject] + [Action] + [Atmosphere] + [Lighting] + [Quality Tags]`。
3. **Historical Aesthetic**：针对《鲸鱼老师讲历史》等系列，注入“史诗感”、“沉浸式”、“考古遗址真实纹理”等关键词。

### 优化步骤
1. **Context Analysis**：提取用户输入主题的核心视觉意图。
2. **Structure Injection**：根据公式强制填充提示词结构。
3. **Aesthetic Calibration**：添加高质量 tag（如 Cinematic texture, Masterful composition）。
4. **API Translation**：将润色后的中文 Prompt 传入 `generate_video.py`。

### 自动化调用指南 (给其他智能体)
其他 Agent 若需调用，请按照以下逻辑：
1. 接收用户指令 → 2. 润色提示词 (LLM) → 3. 调用 `python3 scripts/generate_video.py -p "<润色后的Prompt>" ...`

---

## API 配置

**模型名称：** `seedance-3-0-720p`（即梦视频 3.0 720P）

**API Endpoint：**
```
POST https://visual.volcengineapi.com
```

**认证方式：** AWS Signature V4 兼容签名（火山引擎标准）

**公共参数（Query）：**
- `Action`: `CVSync2AsyncSubmitTask`（提交任务）, `CVSync2AsyncGetResult`（查询结果）
- `Version`: `2022-08-31`

**请求体（JSON 格式）：**
```json
{
  "req_key": "jimeng_t2v_v30",
  "model": "seedance-3-0-720p",
  "prompt": "视频描述提示词",
  "frames": 121,
  "aspect_ratio": "16:9"
}
```

**参数说明：**
- `req_key`: `jimeng_t2v_v30`（即梦文生视频 3.0）
- `model`: `seedance-3-0-720p`
- `prompt`: 视频描述提示词，建议 400 字以内
- `frames`: 帧数（121=5 秒，241=10 秒）
- `aspect_ratio`: 长宽比（如 `16:9`）
- `image`: 首帧图片 Base64（可选，图生视频模式）
- `end_image`: 尾帧图片 Base64（可选，首尾帧模式）

**响应格式：**
```json
{
  "code": 10000,
  "data": {
    "task_id": "xxx",
    "status": "done"
  }
}
```

**查询结果：**
```json
{
  "code": 10000,
  "data": {
    "status": "done",
    "video_url": "https://..."
  }
}
```

## 使用方法

### 基础调用

```bash
# 文生视频（5 秒）
python scripts/generate_video.py -p "一只猫咪在草地上奔跑" -o output.mp4

# 文生视频（10 秒）
python scripts/generate_video.py -p "一只猫咪在草地上奔跑" -o output.mp4 -d 10

# 图生视频（首帧）
python scripts/generate_video.py -p "让图片中的女孩微笑" -i input.jpg -o output.mp4

# 图生视频（首尾帧）
python scripts/generate_video.py -p "从春天变到秋天" -i spring.jpg -e autumn.jpg -o output.mp4
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 视频描述提示词 | 必填 |
| `--output` | 输出文件路径 | output.mp4 |
| `--resolution` | 视频分辨率 | 720p |
| `--duration` | 视频时长 (秒) | 5 |
| `--image` | 首帧图片路径 (可选) | 无 |
| `--end-image` | 尾帧图片路径 (可选) | 无 |

### 支持时长

- 5 秒（121 帧）
- 10 秒（241 帧）

### 支持分辨率

- 720p (1280x720)
- 1080p (1920x1080)

## 任务状态

- `in_queue` - 排队中
- `processing` - 处理中
- `done` - 完成
- `failed` - 失败

## 错误处理

常见错误：

1. **401 SignatureDoesNotMatch** - 签名不匹配
2. **400 Invalid Input Parameters** - 参数错误
3. **401 Access Denied** - 权限问题
4. **429 Too Many Requests** - 触发限流

## 相关资源

- API 文档：https://www.volcengine.com/docs/85621/1792704
- 签名文档：https://www.volcengine.com/docs/6369/67268
- 签名示例：https://github.com/volcengine/volc-openapi-demos/blob/main/signature/python/sign.py
- 示例提示词：见 `references/prompts.md`
