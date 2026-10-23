from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


class InlineScriptParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._capture = False
        self._parts = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        attributes = dict(attrs)
        script_type = (attributes.get("type") or "").lower()
        if attributes.get("src"):
            self._capture = False
            return
        if script_type in {"application/json", "application/ld+json", "importmap"}:
            self._capture = False
            return
        self._capture = True
        self._parts = []

    def handle_data(self, data):
        if self._capture:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._capture:
            source = "".join(self._parts).strip()
            if source:
                self.scripts.append(source)
            self._capture = False
            self._parts = []


def main():
    checked = 0
    for html_file in sorted(FRONTEND.rglob("*.html")):
        parser = InlineScriptParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for index, source in enumerate(parser.scripts, start=1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
                temp.write(source)
                temp.flush()
                subprocess.run(["node", "--check", temp.name], check=True)
            checked += 1
            print(f"Syntax OK: {html_file.relative_to(ROOT)} inline script #{index}")
    print(f"Checked {checked} inline JavaScript block(s).")


if __name__ == "__main__":
    main()
