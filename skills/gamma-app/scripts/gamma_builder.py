import argparse
import json
import os
import subprocess
import sys
import time


def build_payload(input_text, format="presentation", theme_name=None, theme_id=None, export_as=None):
    payload = {
        "inputText": input_text,
        "textMode": "preserve",
        "format": format,
        "cardSplit": "inputTextBreaks",
        "cardOptions": {
            "dimensions": "9x16" if format == "social" else "fluid"
        }
    }
    if theme_name:
        payload["themeName"] = theme_name
    if theme_id:
        payload["themeId"] = theme_id
    if export_as:
        payload["exportAs"] = export_as
    return payload


def curl_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    try:
        return json.loads(result.stdout)
    except Exception:
        print(f"Error parsing response: {result.stdout}", file=sys.stderr)
        sys.exit(1)


def generate_gamma(api_key, input_text, format="presentation", theme_name=None, theme_id=None, export_as=None):
    payload = build_payload(
        input_text=input_text,
        format=format,
        theme_name=theme_name,
        theme_id=theme_id,
        export_as=export_as,
    )

    cmd = [
        "curl", "-s", "-X", "POST", "https://public-api.gamma.app/v1.0/generations",
        "-H", "Content-Type: application/json",
        "-H", f"X-API-KEY: {api_key}",
        "-H", "User-Agent: curl/8.5.0",
        "-d", json.dumps(payload)
    ]

    res_body = curl_json(cmd)
    generation_id = res_body.get("generationId")
    if not generation_id:
        print("Error: No generationId returned.", file=sys.stderr)
        print(res_body, file=sys.stderr)
        sys.exit(1)

    print(f"Generation started... ID: {generation_id}")
    return poll_status(api_key, generation_id)


def poll_status(api_key, generation_id):
    print("Polling for completion (this may take a minute)...")
    while True:
        cmd = [
            "curl", "-s", "-X", "GET", f"https://public-api.gamma.app/v1.0/generations/{generation_id}",
            "-H", "accept: application/json",
            "-H", f"X-API-KEY: {api_key}",
            "-H", "User-Agent: curl/8.5.0"
        ]
        res_body = curl_json(cmd)
        status = res_body.get("status")

        if status == "completed":
            gamma_url = res_body.get("gammaUrl")
            download_url = res_body.get("downloadUrl") or res_body.get("exportUrl")
            print("\nSuccess! Gamma presentation generated:")
            if gamma_url:
                print(f"URL: {gamma_url}")
            if download_url:
                print(f"DOWNLOAD_URL: {download_url}")
            print(json.dumps(res_body, ensure_ascii=False, indent=2))
            return res_body
        elif status == "failed":
            print("\nGeneration failed.", file=sys.stderr)
            print(json.dumps(res_body, ensure_ascii=False, indent=2), file=sys.stderr)
            sys.exit(1)
        else:
            print(".", end="", flush=True)
            time.sleep(3)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("format", nargs="?", default="presentation")
    parser.add_argument("--theme-name")
    parser.add_argument("--theme-id")
    parser.add_argument("--export-as", choices=["pdf", "pptx"])
    return parser.parse_args()


if __name__ == "__main__":
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        print("Error: GAMMA_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    args = parse_args()
    if not os.path.exists(args.input_file):
        print("Error: Provide a valid markdown file path as the first argument.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        input_text = f.read()

    generate_gamma(
        api_key,
        input_text,
        format=args.format,
        theme_name=args.theme_name,
        theme_id=args.theme_id,
        export_as=args.export_as,
    )
