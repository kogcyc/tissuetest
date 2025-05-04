#!/usr/bin/env python3
"""
Tissue - Functional static site generator with `groups` support only.
"""

import shutil
import frontmatter
import markdown
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from tissue_config import MARKDOWN_DIR, BUILD_DIR, TEMPLATE_DIR, STATIC_DIR, sitemap_path, sitemap_base_url

VERBOSE = True

REQUIRED_KEYS = {"title", "desc", "image", "template"}
OPTIONAL_KEYS = {"permalink", "pages_exclude", "groups"}
KNOWN_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS

def validate_frontmatter(metadata, filepath):
    missing = REQUIRED_KEYS - metadata.keys()
    unknown = set(metadata.keys()) - KNOWN_KEYS

    if missing:
        print(f"❌ {filepath} is missing required keys: {', '.join(missing)}")
    if unknown:
        print(f"⚠️ {filepath} has unknown keys: {', '.join(unknown)}")

    return not missing

def generate_permalink(md_path):
    rel = md_path.relative_to(MARKDOWN_DIR)
    return "/" + rel.with_suffix("").as_posix() + "/"
    
def prerender_partials_to_templates():
    """Render Markdown partials to HTML files inside TEMPLATE_DIR for Jinja includes"""
    partial_source = TEMPLATE_DIR / "partialsource"
    if not partial_source.exists():
        return

    for md_path in partial_source.glob("*.md"):
        name = md_path.stem
        html = markdown.markdown(md_path.read_text(encoding="utf-8"))
        out_path = TEMPLATE_DIR / f"partial_{name}.html"
        out_path.write_text(html, encoding="utf-8")
        if VERBOSE:
            print(f"🧩 Pre-rendered: {out_path.relative_to(TEMPLATE_DIR)}")

def prepare_build_dir():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)

def copy_static():
    static_target = BUILD_DIR / "static"
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, static_target)
        if VERBOSE:
            print(f"📁 Freshly copied static assets from {STATIC_DIR} → {static_target}")
    else:
        if VERBOSE:
            print("⚠️  No static directory found to copy.")

def build_index():
    index = []

    for md_path in MARKDOWN_DIR.rglob("*.md"):
        page = frontmatter.load(md_path)
        if not validate_frontmatter(page.metadata, md_path):
            continue

        html = markdown.markdown(page.content)

        section = md_path.relative_to(MARKDOWN_DIR).parent.name or "root"

        raw_groups = page.get("groups", [])
        if isinstance(raw_groups, str):
            raw_groups = [raw_groups]
        elif not isinstance(raw_groups, list):
            raw_groups = []

        groups = [section] + raw_groups

        index.append({
            "content": html,
            "title": page.get("title", ""),
            "desc": page.get("desc", ""),
            "image": page.get("image", ""),
            "permalink": page.get("permalink") or generate_permalink(md_path),
            "template": page.get("template", "template_default.html"),
            "groups": groups,
            "pages_exclude": page.get("pages_exclude", False)
        })

    return index

def check_for_duplicate_permalinks(index):
    seen = {}
    for page in index:
        permalink = page["permalink"]
        if permalink in seen:
            print(f"🚨 Duplicate permalink found:\n  {seen[permalink]} and\n  {page['title']}\n  → {permalink}")
        else:
            seen[permalink] = page["title"]


def render_pages(index, env):
    for page in index:
        template = env.get_template(page["template"])
        rendered = template.render(
            **page,
            all_pages=index
        )

        out_path = BUILD_DIR / page["permalink"].strip("/")
        if out_path.suffix == "":
            out_path /= "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        if VERBOSE:
            print(f"📝 Rendered page: {out_path.relative_to(BUILD_DIR)}")

def render_partials(env):
    partial_dir = TEMPLATE_DIR / "partialsource"
    if partial_dir.exists():
        for md_path in partial_dir.glob("*.md"):
            name = md_path.stem
            html = markdown.markdown(md_path.read_text(encoding="utf-8"))
            out_path = BUILD_DIR / f"partial_{name}.html"
            out_path.write_text(html, encoding="utf-8")
            if VERBOSE:
                print(f"🧹 Partial rendered: {out_path.relative_to(BUILD_DIR)}")

def generate_search_index(index):
    searchable_pages = [p for p in index if not p.get("pages_exclude")]
    path = BUILD_DIR / "search_index.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(searchable_pages, f, indent=2)
    if VERBOSE:
        print(f"🔍 search_index.json written with {len(searchable_pages)} pages.")
    return searchable_pages

def generate_sitemap(pages):
    entries = []
    for page in pages:
        url = sitemap_base_url.rstrip("/") + page["permalink"]
        entries.append(f"<url><loc>{url}</loc></url>")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(entries)}
</urlset>
"""
    sitemap_path.write_text(sitemap_content, encoding="utf-8")
    if VERBOSE:
        print(f"🗺️ sitemap.xml written with {len(entries)} URLs.")

def main():
    prepare_build_dir()
    prerender_partials_to_templates()
    copy_static()
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    index = build_index()
    check_for_duplicate_permalinks(index)
    render_pages(index, env)
    # render_partials(env)
    searchable_pages = generate_search_index(index)
    generate_sitemap(searchable_pages)

if __name__ == "__main__":
    main()
