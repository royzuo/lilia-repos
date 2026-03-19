#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class ConversionError(RuntimeError):
    pass


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise ConversionError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def detect_backend():
    if shutil.which("pdftoppm"):
        return "pdftoppm"
    if shutil.which("magick"):
        return "magick"
    if shutil.which("convert"):
        return "convert"
    if shutil.which("gs"):
        return "gs"
    return None


def pdf_to_jpg_pdftoppm(pdf_path: Path, output_dir: Path, prefix: str, dpi: int):
    stem = output_dir / prefix
    cmd = [
        "pdftoppm",
        "-jpeg",
        "-r",
        str(dpi),
        str(pdf_path),
        str(stem),
    ]
    run(cmd)
    return sorted(output_dir.glob(f"{prefix}-*.jpg"))


def pdf_to_jpg_magick(binary: str, pdf_path: Path, output_dir: Path, prefix: str, dpi: int, quality: int):
    target_pattern = output_dir / f"{prefix}-%03d.jpg"
    cmd = [
        binary,
        "-density",
        str(dpi),
        str(pdf_path),
        "-background",
        "white",
        "-alpha",
        "remove",
        "-alpha",
        "off",
        "-quality",
        str(quality),
        str(target_pattern),
    ]
    run(cmd)
    return sorted(output_dir.glob(f"{prefix}-*.jpg"))


def pdf_to_jpg_gs(pdf_path: Path, output_dir: Path, prefix: str, dpi: int, quality: int):
    quality_map = {
        95: "4",
        85: "3",
        75: "2",
        50: "1",
    }
    gs_quality = "4"
    for threshold, bucket in sorted(quality_map.items(), reverse=True):
        if quality >= threshold:
            gs_quality = bucket
            break

    target_pattern = output_dir / f"{prefix}-%03d.jpg"
    cmd = [
        "gs",
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=jpeg",
        f"-dJPEGQ={gs_quality}",
        f"-r{dpi}",
        f"-sOutputFile={target_pattern}",
        str(pdf_path),
    ]
    run(cmd)
    return sorted(output_dir.glob(f"{prefix}-*.jpg"))


def convert_pdf_to_jpg(pdf_path: Path, output_dir: Path, prefix: str, dpi: int, quality: int, backend: str | None = None):
    backend = backend or detect_backend()
    if not backend:
        raise ConversionError(
            "No supported PDF-to-image backend found. Install one of: pdftoppm (Poppler), "
            "ImageMagick (magick/convert), or Ghostscript (gs)."
        )

    if backend == "pdftoppm":
        files = pdf_to_jpg_pdftoppm(pdf_path, output_dir, prefix, dpi)
    elif backend in {"magick", "convert"}:
        files = pdf_to_jpg_magick(backend, pdf_path, output_dir, prefix, dpi, quality)
    elif backend == "gs":
        files = pdf_to_jpg_gs(pdf_path, output_dir, prefix, dpi, quality)
    else:
        raise ConversionError(f"Unsupported backend: {backend}")

    if not files:
        raise ConversionError("Conversion completed but no JPG files were produced.")
    return files, backend


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split a PDF into one JPG per page. Useful for Gamma PDF exports."
    )
    parser.add_argument("pdf", help="Path to the source PDF")
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to write JPG pages into (default: <pdf_stem>_jpg)",
    )
    parser.add_argument(
        "--prefix",
        help="Output filename prefix (default: <pdf_stem>)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Rasterization DPI (default: 200)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=92,
        help="JPG quality 1-100 (default: 92)",
    )
    parser.add_argument(
        "--backend",
        choices=["pdftoppm", "magick", "convert", "gs"],
        help="Force a specific conversion backend",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Warning: input does not end with .pdf: {pdf_path}", file=sys.stderr)

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else pdf_path.with_suffix("")
    if not args.output_dir:
        output_dir = output_dir.parent / f"{output_dir.name}_jpg"
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = args.prefix or pdf_path.stem
    quality = max(1, min(100, args.quality))
    dpi = max(36, args.dpi)

    try:
        files, backend = convert_pdf_to_jpg(
            pdf_path=pdf_path,
            output_dir=output_dir,
            prefix=prefix,
            dpi=dpi,
            quality=quality,
            backend=args.backend,
        )
    except ConversionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"Backend: {backend}")
    print(f"Output directory: {output_dir}")
    print(f"Pages exported: {len(files)}")
    for file in files:
        print(file)


if __name__ == "__main__":
    main()
