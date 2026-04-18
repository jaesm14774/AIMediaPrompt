#!/usr/bin/env python3
"""
使用 ffmpeg 合併多段影片為一部連續影片，或擷取影片末幀。

用途：
  - 合併 story/ 目錄下所有 clip_*.mp4 → final_story.mp4
  - 擷取單段影片最後一幀 → PNG（供下一幕 reference image 使用）

需要：ffmpeg 已安裝並在 PATH 中
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 接力幀需與「上一張 reference」有足夠像素差異（避免短片段仍卡在起始構圖）
_RELAY_DIVERGENCE_MAE_MIN = 5.5
_MIN_TRIMMED_DURATION_SECONDS = 2.0


def _get_duration_seconds(video_path: Path) -> float | None:
    """取得影片時長（秒），失敗回傳 None"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return None


def _raw_rgb_scaled(image_path: Path, size: int = 96) -> bytes | None:
    """將圖片縮放為 size×size 的 RGB raw bytes（供與 reference 比對差異）。"""
    try:
        r = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "quiet",
                "-i",
                str(image_path),
                "-vf",
                f"scale={size}:{size}",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "pipe:1",
            ],
            capture_output=True,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        return r.stdout
    except Exception:
        return None


def _mean_abs_diff_rgb(a: bytes, b: bytes) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(abs(a[i] - b[i]) for i in range(len(a))) / float(len(a))


def _relay_fraction_candidates(duration: float) -> list[float]:
    """依片長挑選多個候選比例（短片段若取太前面，畫面仍貼近 reference 起始幀）。"""
    if duration <= 4.5:
        return [0.62, 0.72, 0.52, 0.82, 0.45, 0.35]
    if duration <= 6.5:
        return [0.55, 0.48, 0.65, 0.42, 0.72, 0.38]
    return [0.45, 0.55, 0.40, 0.65, 0.35, 0.72]


def extract_relay_frame_divergent(
    video_path: Path,
    output_path: Path,
    diverge_from: Path,
    mae_min: float = _RELAY_DIVERGENCE_MAE_MIN,
) -> bool:
    """擷取接力幀：優先選與 diverge_from（本段使用的 reference）足夠不同的時間點。

    解決：短片段 + 固定 30% 時，時間點仍接近片頭，與上一張 reference 視覺幾乎相同，
    導致下一幕再度從「同一張圖」生成。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not diverge_from.exists():
        print(f"⚠️  找不到 --diverge-from：{diverge_from}，改用一般擷取")
        return extract_frame_at(video_path, output_path, at="55%")

    ref_rgb = _raw_rgb_scaled(diverge_from)
    if not ref_rgb:
        print(f"⚠️  無法解碼 reference 供比對：{diverge_from.name}，改用一般擷取")
        return extract_frame_at(video_path, output_path, at="55%")

    duration = _get_duration_seconds(video_path)
    if duration is None or duration <= 0.05:
        print(f"⚠️  無法取得片長，改用 55% 擷取")
        return extract_frame_at(video_path, output_path, at="55%")

    fractions = _relay_fraction_candidates(duration)
    fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="relay_try_")
    os.close(fd)
    tmp = Path(tmp_path)

    try:
        for frac in fractions:
            t = max(0.0, min(duration * frac, duration - 0.04))
            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                f"{t:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(tmp),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
                continue
            cand_rgb = _raw_rgb_scaled(tmp)
            if not cand_rgb:
                continue
            mae = _mean_abs_diff_rgb(cand_rgb, ref_rgb)
            if mae >= mae_min:
                tmp.replace(output_path)
                print(
                    f"✅ 接力幀已擷取（與 reference 平均差異 MAE={mae:.2f}，t={t:.2f}s / {frac*100:.0f}%）："
                    f"{output_path.name}"
                )
                return True

        # 候選皆偏像 reference：改取較晚時間點（片尾前）
        late_t = max(0.0, duration - 0.12)
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            f"{late_t:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(tmp),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            cand_rgb = _raw_rgb_scaled(tmp)
            mae = _mean_abs_diff_rgb(cand_rgb, ref_rgb) if cand_rgb else 0.0
            tmp.replace(output_path)
            print(
                f"⚠️  與 reference 差異仍偏小（MAE={mae:.2f} < {mae_min}），已改用接近片尾 t={late_t:.2f}s："
                f"{output_path.name}"
            )
            return True

        print(f"❌ 無法擷取接力幀：{video_path.name}")
        return False
    finally:
        tmp.unlink(missing_ok=True)


def extract_frame_at(video_path: Path, output_path: Path, at: str = "50%") -> bool:
    """擷取影片指定時間點的幀。

    at 參數：
      "50%"  → 影片中段（預設，角色姿態最穩定）
      "3.0"  → 第 3.0 秒
      "last" → 倒退 1 秒（舊行為，角色可能變形）
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if at == "last":
        # 舊行為：從結尾倒退 1 秒
        cmd = [
            "ffmpeg", "-y", "-sseof", "-1",
            "-i", str(video_path),
            "-frames:v", "1", "-q:v", "2",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"✅ 末幀已擷取：{output_path.name}")
            return True
        print(f"❌ 無法擷取末幀：{video_path.name}")
        return False

    # 計算絕對時間戳
    if at.endswith("%"):
        pct = float(at[:-1]) / 100.0
        duration = _get_duration_seconds(video_path)
        if duration is None:
            print(f"⚠️  無法取得影片時長，改用 50% 估算（假設 8s）")
            duration = 8.0
        timestamp = duration * pct
    else:
        timestamp = float(at)

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{timestamp:.3f}",
        "-i", str(video_path),
        "-frames:v", "1", "-q:v", "2",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
        print(f"✅ 接力幀已擷取（{timestamp:.1f}s）：{output_path.name}")
        return True

    # 備用：直接用末幀
    print(f"⚠️  指定時間點擷取失敗，改用末幀")
    return extract_frame_at(video_path, output_path, at="last")


def concat_clips(clips: list[Path], output_path: Path) -> bool:
    """使用 ffmpeg concat demuxer 合併多段影片"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 寫入 concat 清單（絕對路徑，避免 Windows 路徑問題）
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        for clip in clips:
            # ffmpeg concat 清單路徑需用正斜線，特殊字元需跳脫
            safe_path = str(clip.resolve()).replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
        concat_list = Path(f.name)

    try:
        print(f"🎬 合併 {len(clips)} 段影片...")
        for i, clip in enumerate(clips, 1):
            duration_info = _get_duration(clip)
            print(f"   Clip {i}：{clip.name}{duration_info}")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

        if result.returncode != 0:
            print(f"❌ ffmpeg 合併失敗")
            print(f"   stderr：{result.stderr[-500:] if result.stderr else '(無輸出)'}")
            return False

        if not output_path.exists() or output_path.stat().st_size == 0:
            print("❌ 輸出檔案不存在或為空")
            return False

        total_duration = _get_duration(output_path)
        print(f"✅ 合併完成：{output_path.name}{total_duration}")
        return True

    finally:
        concat_list.unlink(missing_ok=True)


def _get_duration(video_path: Path) -> str:
    """取得影片時長，失敗時回傳空字串"""
    secs = _get_duration_seconds(video_path)
    return f"（{secs:.1f}s）" if secs is not None else ""


def _run_ffmpeg(cmd: list[str]) -> tuple[bool, str]:
    """Run ffmpeg with UTF-8 decoding so Windows console encoding does not corrupt stderr."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return False, result.stderr[-500:] if result.stderr else ""
    return True, result.stderr[-500:] if result.stderr else ""


def trim_clip_precise(
    video_path: Path,
    output_path: Path,
    trim_start: float = 0.0,
    trim_end: float = 0.0,
    min_duration: float = _MIN_TRIMMED_DURATION_SECONDS,
) -> bool:
    """Trim head/tail with precise re-encode to remove repeated motion around joins."""
    duration = _get_duration_seconds(video_path)
    if duration is None or duration <= 0:
        print(f"?? ?⊥???敶梁??嚗{video_path.name}")
        return False

    trim_start = max(0.0, trim_start)
    trim_end = max(0.0, trim_end)
    max_total_trim = max(0.0, duration - min_duration)

    if trim_start + trim_end > max_total_trim:
        requested = trim_start + trim_end
        if requested > 0:
            scale = max_total_trim / requested
            trim_start *= scale
            trim_end *= scale

    kept_duration = duration - trim_start - trim_end
    if kept_duration < min_duration:
        print(
            f"??  靽桀?????閮?嚗{video_path.name} "
            f"嚗?? {duration:.2f}s嚗?start={trim_start:.2f}s嚗?end={trim_end:.2f}s"
        )
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{trim_start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{kept_duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(output_path),
    ]
    success, stderr_tail = _run_ffmpeg(cmd)
    if not success or not output_path.exists() or output_path.stat().st_size == 0:
        print(f"?? 靽桀憭望?嚗{video_path.name}")
        if stderr_tail:
            print(f"   stderr嚗{stderr_tail}")
        return False

    print(
        f"?? 靽桀摰?嚗{output_path.name} "
        f"嚗?start={trim_start:.2f}s嚗?end={trim_end:.2f}s嚗?keep={kept_duration:.2f}s"
    )
    return True


def auto_trim_clips(
    clips: list[Path],
    trim_prev_end: float,
    trim_next_start: float,
    min_duration: float = _MIN_TRIMMED_DURATION_SECONDS,
) -> list[Path] | None:
    """Create _trim clips so each join skips repeated motion from the previous beat."""
    trimmed_clips: list[Path] = []

    for idx, clip in enumerate(clips):
        trim_start = trim_next_start if idx > 0 else 0.0
        trim_end = trim_prev_end if idx < len(clips) - 1 else 0.0

        if trim_start <= 0 and trim_end <= 0:
            trimmed_clips.append(clip)
            continue

        output_path = clip.with_name(f"{clip.stem}_trim{clip.suffix}")
        success = trim_clip_precise(
            clip,
            output_path,
            trim_start=trim_start,
            trim_end=trim_end,
            min_duration=min_duration,
        )
        if not success:
            return None
        trimmed_clips.append(output_path)

    return trimmed_clips


def main():
    parser = argparse.ArgumentParser(
        description="合併多段影片 / 擷取影片末幀（ffmpeg）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 合併指定影片（依序）
  python scripts/concat_video_clips.py \\
    --clips Local_Media/MyStory/story/clip_01.mp4 clip_02.mp4 clip_03.mp4 \\
    --output Local_Media/MyStory/story/final_story.mp4

  # 自動探索 story/ 資料夾內所有 clip_*.mp4
  python scripts/concat_video_clips.py \\
    --template "MyStory" \\
    --output Local_Media/MyStory/story/final_story.mp4

  # 擷取影片最後一幀
  python scripts/concat_video_clips.py \\
    --extract-last-frame Local_Media/MyStory/story/clip_01.mp4 \\
    --output Local_Media/MyStory/story/frame_01_end.png

  # Comedy 接力幀：與本段起始 reference 足夠區隔（避免短片段固定比例仍像同一張）
  python scripts/concat_video_clips.py \\
    --extract-last-frame Local_Media/Tpl/comedy/clip_03.mp4 \\
    --diverge-from Local_Media/Tpl/comedy/frame_02_relay.png \\
    --output Local_Media/Tpl/comedy/frame_03_relay.png
""",
    )
    parser.add_argument(
        "--clips", nargs="+", metavar="CLIP",
        help="要合併的影片路徑清單（依序）",
    )
    parser.add_argument(
        "--template", "-t",
        help="Template 名稱，自動探索 Local_Media/<name>/story/clip_*.mp4",
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="輸出路徑（合併影片或末幀圖片）",
    )
    parser.add_argument(
        "--extract-last-frame", metavar="VIDEO",
        help="擷取指定影片的幀（不執行合併）",
    )
    parser.add_argument(
        "--extract-at", metavar="TIME", default="50%%",
        help="擷取幀的時間點：'50%%'=中段（預設），'3.0'=第3秒，'last'=末尾",
    )
    parser.add_argument(
        "--diverge-from",
        metavar="IMAGE",
        help=(
            "接力幀專用：上一支影片使用的 reference 圖路徑。"
            "若設定，會在片內多個時間點試擷，直到與此圖像素差異足夠大（避免短片段固定 30%% 仍像同一張）。"
        ),
    )
    parser.add_argument(
        "--relay-mae-min",
        type=float,
        default=_RELAY_DIVERGENCE_MAE_MIN,
        help=f"與 --diverge-from 的最小平均像素差異門檻（0-255 尺度，預設 {_RELAY_DIVERGENCE_MAE_MIN}）",
    )

    parser.add_argument(
        "--trim-overlap",
        action="store_true",
        help="?蔥??敶梁?嚗?銝??亙?瘚??靽桀??嚗nable automatic join trimming",
    )
    parser.add_argument(
        "--trim-prev-end",
        type=float,
        default=0.4,
        help="??頝喲?閬??敶梁?怠偏靽桀??嚗?閮?0.4s",
    )
    parser.add_argument(
        "--trim-next-start",
        type=float,
        default=0.3,
        help="??頝喲?閬??敶梁?靽桀??嚗?閮?0.3s",
    )
    parser.add_argument(
        "--min-trimmed-duration",
        type=float,
        default=_MIN_TRIMMED_DURATION_SECONDS,
        help=f"靽桀??敶梁???蝮?閮?{_MIN_TRIMMED_DURATION_SECONDS}s",
    )

    args = parser.parse_args()

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else PROJECT_ROOT / path

    output_path = resolve(args.output)

    # ── 擷取幀模式 ────────────────────────────────────────────────
    if args.extract_last_frame:
        video_path = resolve(args.extract_last_frame)
        if not video_path.exists():
            print(f"❌ 找不到影片：{video_path}")
            sys.exit(1)
        print("=" * 50)
        if args.diverge_from:
            div = resolve(args.diverge_from)
            print("🖼️  接力幀擷取（diverge-from 模式，避免與 reference 重複）")
            print(f"   reference 比對圖：{div.name}")
            print("=" * 50)
            success = extract_relay_frame_divergent(
                video_path,
                output_path,
                div,
                mae_min=args.relay_mae_min,
            )
        else:
            at = args.extract_at
            print(f"🖼️  接力幀擷取（at={at}）")
            print("=" * 50)
            success = extract_frame_at(video_path, output_path, at=at)
        sys.exit(0 if success else 1)

    # ── 合併模式 ──────────────────────────────────────────────────
    clips: list[Path] = []

    if args.clips:
        clips = [resolve(c) for c in args.clips]
    elif args.template:
        story_dir = PROJECT_ROOT / "Local_Media" / args.template / "story"
        clips = sorted(story_dir.glob("clip_*.mp4"))
        if not clips:
            print(f"❌ 在 {story_dir} 找不到 clip_*.mp4")
            sys.exit(1)
    else:
        print("❌ 請指定 --clips 清單或 --template 名稱")
        parser.print_help()
        sys.exit(1)

    missing = [c for c in clips if not c.exists()]
    if missing:
        for m in missing:
            print(f"❌ 找不到：{m}")
        sys.exit(1)

    if len(clips) < 2:
        print(f"❌ 至少需要 2 段影片才能合併（目前只有 {len(clips)} 段）")
        sys.exit(1)

    clips_to_concat = clips
    if args.trim_overlap:
        print("=" * 50)
        print("?貉? ?蔥?靽桀???亙?瘚")
        print("=" * 50)
        print(
            f"   ?恍?怠偏靽桀嚗{args.trim_prev_end:.2f}s  |  "
            f"???靽桀嚗{args.trim_next_start:.2f}s"
        )
        trimmed = auto_trim_clips(
            clips,
            trim_prev_end=args.trim_prev_end,
            trim_next_start=args.trim_next_start,
            min_duration=args.min_trimmed_duration,
        )
        if trimmed is None:
            print("?? ?蔥?靽桀憭望?嚗???頝喲?銝剝??蔥")
            sys.exit(1)
        clips_to_concat = trimmed

    print("=" * 50)
    print("🎬 Story Video 合併")
    print("=" * 50)
    success = concat_clips(clips_to_concat, output_path)

    if success:
        print()
        print(f"📁 輸出位置：{output_path.relative_to(PROJECT_ROOT)}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
