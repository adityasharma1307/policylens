import os
import re
import shutil
import subprocess
from pathlib import Path

import markdown

from policylens.config import ROOT_DIR
from policylens.report.brief_figures import plot_state_extremes
from policylens.report.figures import save_figure

BRIEF_MD = ROOT_DIR / "brief" / "policy_brief.md"
BRIEF_HTML = ROOT_DIR / "brief" / "policy_brief.html"
BRIEF_PDF = ROOT_DIR / "brief" / "policy_brief.pdf"

_FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)

_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  @page {{ size: A4; margin: 12mm 18mm; }}
  body {{
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #0b0b0b;
    font-size: 9.5pt;
    line-height: 1.28;
    max-width: 720px;
    margin: 0 auto;
  }}
  h1 {{ font-size: 15.5pt; margin: 0 0 1pt 0; }}
  .subtitle {{ color: #52514e; font-size: 9pt; margin: 0 0 8pt 0; }}
  h2 {{
    font-size: 11pt; margin: 8pt 0 3pt 0;
    border-bottom: 1px solid #e1e0d9; padding-bottom: 1pt;
  }}
  p {{ margin: 3pt 0; text-align: justify; }}
  ul {{ margin: 3pt 0; padding-left: 15pt; }}
  li {{ margin: 1pt 0; text-align: justify; }}
  strong {{ color: #0b0b0b; }}
  em {{ color: #52514e; }}
  img {{ max-width: 100%; margin: 3pt 0; }}
  .footnote {{ color: #898781; font-size: 8pt; margin-top: 6pt; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    front, body = match.groups()
    meta = dict(
        line.split(":", 1) for line in front.splitlines() if ":" in line
    )
    meta = {k.strip(): v.strip().strip('"') for k, v in meta.items()}
    return meta, body


def render_html() -> Path:
    save_figure(plot_state_extremes(), "brief_state_extremes")
    text = BRIEF_MD.read_text(encoding="utf-8")
    meta, body_md = _split_front_matter(text)

    figure_path = ROOT_DIR / "reports" / "figures" / "brief_state_extremes.png"
    header = f"<h1>{meta.get('title', 'Policy Brief')}</h1>"
    if "subtitle" in meta:
        header += f'<p class="subtitle">{meta["subtitle"]}</p>'
    header += f'<img src="file:///{figure_path.as_posix()}" alt="State extremes chart">'

    body_html = markdown.markdown(body_md, extensions=["extra"])
    html = _TEMPLATE.format(title=meta.get("title", "Policy Brief"), body=header + body_html)
    BRIEF_HTML.write_text(html, encoding="utf-8")
    return BRIEF_HTML


_WINDOWS_FALLBACKS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
]


def _find_chrome_binary() -> str:
    env_override = os.environ.get("POLICYLENS_CHROME_BIN")
    if env_override and Path(env_override).exists():
        return env_override

    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found

    for candidate in _WINDOWS_FALLBACKS:
        if Path(candidate).exists():
            return candidate

    raise FileNotFoundError(
        "No Chrome/Chromium binary found. Set POLICYLENS_CHROME_BIN to its path."
    )


def render_pdf() -> Path:
    html_path = render_html()
    chrome = _find_chrome_binary()
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={BRIEF_PDF}",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            html_path.as_uri(),
        ],
        check=True,
        timeout=60,
    )
    return BRIEF_PDF


def main() -> None:
    pdf_path = render_pdf()
    print(f"Policy brief -> {pdf_path}")


if __name__ == "__main__":
    main()
