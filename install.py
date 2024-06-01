import launch
from pathlib import Path

aria2path = Path(__file__).resolve().parents[0] / "aria2"

for item in aria2path.iterdir():
    if item.is_file():
        item.unlink()

def install_req(check_name, install_name=None):
    if not install_name: install_name = check_name
    if not launch.is_installed(f"{check_name}"):
        print("")
        launch.run_pip(f"install {install_name}", f"Installing missing requirement \"{check_name}\" for CivitAI Browser")

install_req("send2trash", "send2trash==1.8.2")
install_req("zip_unicode", "ZipUnicode==1.1.1")
install_req("bs4", "beautifulsoup4==4.12.3")
install_req("packaging","packaging==23.2")
install_req("pysocks","pysocks==1.7.1")