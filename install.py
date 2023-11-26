import launch
from pathlib import Path

aria2path = Path(__file__).resolve().parents[0] / "aria2"

for item in aria2path.iterdir():
    if item.is_file():
        item.unlink()

if not launch.is_installed("send2trash"):
    launch.run_pip("install send2trash", "requirements for CivitAI Browser")
if not launch.is_installed("zip_unicode"):
    launch.run_pip("install ZipUnicode", "requirements for CivitAI Browser")
if not launch.is_installed("bs4"):
    launch.run_pip("install beautifulsoup4", "requirements for CivitAI Browser")
if not launch.is_installed("fake_useragent"):
    launch.run_pip("install fake_useragent", "requirements for CivitAI Browser")