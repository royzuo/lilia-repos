# Skills

这里存放我创建的 AgentSkills。

## 已创建技能

### 1. aliyun-wan2-6
- **功能**: 使用阿里云通义万相 2.6 模型生成图片
- **API**: DashScope `wan2.6-image`
- **使用方式**: 
  ```bash
  python scripts/generate_image.py -p "提示词" -o output.jpg
  ```

### 2. aliyun-qwen-image-edit
- **功能**: 使用阿里云通义千问进行图片编辑
- **API**: DashScope `qwen-image-edit`
- **使用方式**:
  ```bash
  python scripts/edit_image.py -i input.jpg -p "编辑指令" -o output.jpg
  ```

## 前置要求

两个技能都需要设置环境变量：
```bash
export DASHSCOPE_API_KEY="your-api-key"
```
