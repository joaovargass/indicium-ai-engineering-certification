"""File operations for SRAG reports."""

import zipfile
from datetime import datetime
from pathlib import Path


def save_report_to_file(
    report_content: str,
    location: str,
    output_dir: Path | None = None,
) -> Path:
    """
    Save report to file for download.

    Args:
        report_content: Markdown report content
        location: Location name (for filename)
        output_dir: Directory to save reports (default: reports/ in project root)

    Returns:
        Path to saved file

    """
    if output_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        output_dir = project_root / "reports"

    output_dir.mkdir(parents=True, exist_ok=True)

    location_clean = location
    if "Brasil" in location and "nacional" in location.lower():
        location_clean = "Brasil"

    location_safe = (
        location_clean.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Relatorio_SRAG_{location_safe}_{date_str}.md"
    file_path = output_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path


def save_report_zip(
    report_content: str,
    location: str,
    image_files: dict[str, Path],
    output_dir: Path | None = None,
) -> Path:
    """
    Save report and images to a zip file for download.

    Args:
        report_content: Markdown report content
        location: Location name (for filename)
        image_files: Dictionary mapping image names to file paths (e.g., {"grafico_1.png": Path(...)})
        output_dir: Directory to save zip file (default: reports/ in project root)

    Returns:
        Path to saved zip file

    """
    if output_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        output_dir = project_root / "reports"

    output_dir.mkdir(parents=True, exist_ok=True)

    location_clean = location
    if "Brasil" in location and "nacional" in location.lower():
        location_clean = "Brasil"

    location_safe = (
        location_clean.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )
    date_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"Relatorio_SRAG_{location_safe}_{date_str}.zip"
    zip_path = output_dir / zip_filename

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        md_filename = f"Relatorio_SRAG_{location_safe}_{date_str}.md"
        zipf.writestr(md_filename, report_content, compress_type=zipfile.ZIP_DEFLATED)

        for image_name, image_path in image_files.items():
            if image_path.exists():
                zipf.write(image_path, image_name)

    return zip_path
