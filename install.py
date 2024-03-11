import launch
from pathlib import Path

aria2path = Path(__file__).resolve().parents[0] / "aria2"

for item in aria2path.iterdir():
    if item.is_file():
        item.unlink()

def install_req(check_name, install_name=None):
    if not install_name: install_name = check_name
    if not launch.is_installed(f"{check_name}"):
        launch.run_pip(f"install {install_name}", "requirements for CivitAI Browser")

install_req("send2trash")
install_req("zip_unicode", "ZipUnicode")
install_req("bs4", "beautifulsoup4")
install_req("fake_useragent")
install_req("packaging")
install_req("pysocks")