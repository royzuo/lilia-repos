#!/usr/bin/env python3
"""
字节豆包即梦 AI 视频生成 3.0 720P 脚本
使用火山引擎视觉服务 API（AccessKeyId/SecretAccessKey 签名认证）
文档：https://www.volcengine.com/docs/85621/1792704
签名参考：https://github.com/volcengine/volc-openapi-demos/blob/main/signature/python/sign.py
"""

import os
import sys
import json
import base64
import hashlib
import hmac
import argparse
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode, quote
from typing import Optional, Tuple, Dict, Any

import requests
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 从环境变量获取密钥
VOLC_ACCESSKEY = os.environ.get("VOLC_ACCESSKEY")
VOLC_SECRETKEY = os.environ.get("VOLC_SECRETKEY")

# API 配置
SERVICE = "cv"
REGION = "cn-north-1"
HOST = "visual.volcengineapi.com"
CONTENT_TYPE = "application/json; charset=utf-8"

# 任务配置
MAX_WAIT_TIME = 600  # 最大等待时间（秒）
POLL_INTERVAL = 5    # 轮询间隔（秒）


def sha256_hex(content: str) -> str:
    """sha256 hash 算法"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def hmac_sha256(key: bytes, content: str) -> bytes:
    """sha256 非对称加密"""
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def norm_query(params: Dict[str, Any]) -> str:
    """规范化查询字符串"""
    query = ""
    for key in sorted(params.keys()):
        if isinstance(params[key], list):
            for k in params[key]:
                query += quote(key, safe="-_.~") + "=" + quote(k, safe="-_.~") + "&"
        else:
            query += quote(key, safe="-_.~") + "=" + quote(params[key], safe="-_.~") + "&"
    return query[:-1].replace("+", "%20")


def sign_request(method: str, path: str, query_params: Dict[str, Any], 
                 body: str, now: datetime) -> Dict[str, str]:
    """
    火山引擎 Signature V4 签名
    
    Args:
        method: HTTP 方法
        path: 请求路径
        query_params: 查询参数
        body: 请求体
        now: 当前时间
    
    Returns:
        签名后的 headers
    """
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    x_content_sha256 = sha256_hex(body)
    
    # 准备签名 headers
    sign_result = {
        "Host": HOST,
        "X-Content-Sha256": x_content_sha256,
        "X-Date": x_date,
        "Content-Type": CONTENT_TYPE,
    }
    
    # 计算签名
    signed_headers_str = ";".join(["content-type", "host", "x-content-sha256", "x-date"])
    
    canonical_request_str = "\n".join([
        method.upper(),
        path,
        norm_query(query_params),
        "\n".join([
            f"content-type:{sign_result['Content-Type']}",
            f"host:{sign_result['Host']}",
            f"x-content-sha256:{x_content_sha256}",
            f"x-date:{x_date}",
        ]),
        "",
        signed_headers_str,
        x_content_sha256,
    ])
    
    hashed_canonical_request = sha256_hex(canonical_request_str)
    credential_scope = "/".join([short_x_date, REGION, SERVICE, "request"])
    string_to_sign = "\n".join([
        "HMAC-SHA256",
        x_date,
        credential_scope,
        hashed_canonical_request
    ])
    
    # 计算签名
    k_date = hmac_sha256(VOLC_SECRETKEY.encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, REGION)
    k_service = hmac_sha256(k_region, SERVICE)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()
    
    sign_result["Authorization"] = (
        f"HMAC-SHA256 Credential={VOLC_ACCESSKEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers_str}, Signature={signature}"
    )
    
    return sign_result


def submit_task(prompt: str, resolution: str = "720p", duration: int = 5,
                image_path: Optional[str] = None, 
                end_image_path: Optional[str] = None) -> Optional[str]:
    """
    提交视频生成任务
    
    Returns:
        task_id 或 None
    """
    now = datetime.now(timezone.utc)
    
    # 计算帧数
    frames = 121 if duration <= 5 else 241
    
    # 构建请求体
    request_body = {
        "req_key": "jimeng_t2v_v30",
        "model": "seedance-3-0-720p",
        "prompt": prompt,
        "frames": frames,
    }
    
    if resolution in ["720p", "1080p"]:
        request_body["aspect_ratio"] = "16:9"
    
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            request_body["image"] = base64.b64encode(f.read()).decode('utf-8')
        logger.info(f"使用首帧图片：{image_path}")
    
    if end_image_path and os.path.exists(end_image_path):
        with open(end_image_path, "rb") as f:
            request_body["end_image"] = base64.b64encode(f.read()).decode('utf-8')
        logger.info(f"使用尾帧图片：{end_image_path}")
    
    body = json.dumps(request_body)
    
    # Query 参数
    query_params = {
        "Action": "CVSync2AsyncSubmitTask",
        "Version": "2022-08-31",
    }
    
    # 签名
    headers = sign_request("POST", "/", query_params, body, now)
    
    logger.info("提交视频生成任务...")
    
    try:
        response = requests.post(
            url=f"https://{HOST}/",
            headers=headers,
            params=query_params,
            data=body,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求失败：{e}")
        return None
    
    if response.status_code != 200:
        logger.error(f"API 请求失败：{response.status_code}")
        logger.error(response.text)
        return None
    
    result = response.json()
    
    # 检查错误
    error = result.get("ResponseMetadata", {}).get("Error", {})
    if error:
        error_msg = error.get("Message", "Unknown error")
        logger.error(f"任务提交失败：{error_msg}")
        return None
    
    task_id = result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
    
    if not task_id:
        logger.error("未获取到任务 ID")
        logger.debug(json.dumps(result, indent=2))
        return None
    
    logger.info(f"任务已提交：{task_id}")
    return task_id


def get_result(task_id: str) -> Tuple[Optional[str], str]:
    """
    查询任务结果
    
    Returns:
        (video_url, status)
    """
    now = datetime.now(timezone.utc)
    
    body = json.dumps({
        "req_key": "jimeng_t2v_v30",
        "task_id": task_id
    })
    
    query_params = {
        "Action": "CVSync2AsyncGetResult",
        "Version": "2022-08-31",
    }
    
    # 签名
    headers = sign_request("POST", "/", query_params, body, now)
    
    try:
        response = requests.post(
            url=f"https://{HOST}/",
            headers=headers,
            params=query_params,
            data=body,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"查询任务失败：{e}")
        return None, "PENDING"
    
    if response.status_code != 200:
        logger.error(f"查询请求失败：{response.status_code}")
        return None, "PENDING"
    
    result = response.json()
    
    # 检查错误
    if result.get("code") not in [0, 10000] and result.get("status") not in [0, 10000]:
        error = result.get("ResponseMetadata", {}).get("Error", {})
        if error:
            logger.error(f"查询错误：{error.get('Message', 'Unknown')}")
        return None, "ERROR"
    
    data = result.get("data", {})
    status = data.get("status", "PENDING")
    
    # 提取视频 URL
    video_url = None
    if status in ["success", "completed", "SUCCESS", "done"]:
        video_url = (data.get("video_url") or 
                    data.get("output", {}).get("video_url") or
                    data.get("result", {}).get("video_url"))
        if video_url:
            logger.info(f"视频生成完成")
    
    return video_url, status


def download_video(url: str, output_path: str) -> bool:
    """下载视频到本地"""
    logger.info(f"下载视频：{output_path}")
    
    try:
        response = requests.get(url, stream=True, timeout=300)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"视频已保存：{output_path}")
            return True
        else:
            logger.error(f"下载失败：{response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败：{e}")
        return False


def generate_video(prompt: str, resolution: str = "720p", duration: int = 5,
                   image_path: Optional[str] = None,
                   end_image_path: Optional[str] = None) -> Optional[str]:
    """
    主流程：提交任务并轮询结果
    
    Returns:
        视频 URL 或 None
    """
    # 提交任务
    task_id = submit_task(
        prompt=prompt,
        resolution=resolution,
        duration=duration,
        image_path=image_path,
        end_image_path=end_image_path
    )
    
    if not task_id:
        return None
    
    # 轮询结果
    logger.info("等待视频生成完成...")
    start_time = time.time()
    
    while True:
        elapsed = int(time.time() - start_time)
        
        if elapsed >= MAX_WAIT_TIME:
            logger.error("等待超时")
            return None
        
        time.sleep(POLL_INTERVAL)
        
        video_url, status = get_result(task_id)
        logger.info(f"任务状态：{status} (已等待 {elapsed}s)")
        
        if video_url:
            return video_url
        elif status == "ERROR":
            logger.error("任务失败")
            return None
        elif status == "failed":
            logger.error("任务失败")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="字节豆包即梦 AI 视频生成 3.0 720P",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文生视频（5 秒）
  %(prog)s -p "一只猫咪在草地上奔跑" -o output.mp4
  
  # 文生视频（10 秒）
  %(prog)s -p "一只猫咪在草地上奔跑" -o output.mp4 -d 10
  
  # 图生视频（首帧）
  %(prog)s -p "让图片中的女孩微笑" -i input.jpg -o output.mp4
  
  # 图生视频（首尾帧）
  %(prog)s -p "从春天变到秋天" -i spring.jpg -e autumn.jpg -o output.mp4
        """
    )
    parser.add_argument("--prompt", "-p", required=True, help="视频描述提示词")
    parser.add_argument("--output", "-o", default="output.mp4", help="输出文件路径")
    parser.add_argument("--resolution", "-r", default="720p", choices=["720p", "1080p"], 
                       help="视频分辨率")
    parser.add_argument("--duration", "-d", type=int, default=5, choices=[5, 10], 
                       help="视频时长 (秒)")
    parser.add_argument("--image", "-i", help="首帧图片路径 (可选)")
    parser.add_argument("--end-image", "-e", help="尾帧图片路径 (可选)")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示调试信息")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 检查环境变量
    if not VOLC_ACCESSKEY or not VOLC_SECRETKEY:
        logger.error("未设置环境变量 VOLC_ACCESSKEY 或 VOLC_SECRETKEY")
        sys.exit(1)
    
    logger.info(f"正在生成视频：{args.prompt}")
    logger.info(f"分辨率：{args.resolution}, 时长：{args.duration}秒")
    
    video_url = generate_video(
        prompt=args.prompt,
        resolution=args.resolution,
        duration=args.duration,
        image_path=args.image,
        end_image_path=args.end_image
    )
    
    if video_url:
        logger.info(f"生成成功！")
        logger.info(f"视频 URL: {video_url}")
        if download_video(video_url, args.output):
            logger.info("完成！")
        else:
            sys.exit(1)
    else:
        logger.error("未生成视频")
        sys.exit(1)


if __name__ == "__main__":
    main()
