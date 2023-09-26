import launch

if not launch.is_installed("send2trash"):
    launch.run_pip("install send2trash", "requirements for CivitAI Browser")
if not launch.is_installed("ZipUnicode"):
    launch.run_pip("install ZipUnicode", "requirements for CivitAI Browser")