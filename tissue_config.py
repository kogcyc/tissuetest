from pathlib import Path

# Directory paths
ROOT_DIR = Path(__file__).resolve().parent
MARKDOWN_DIR = ROOT_DIR / "markdown"
BUILD_DIR = ROOT_DIR / "public"
TEMPLATE_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"

# sitemap.xml config
sitemap_path = BUILD_DIR / "sitemap.xml"
sitemap_base_url = "https://domain.io"  # CHANGE THIS!
