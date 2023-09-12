import requests
import gradio as gr
import time
import subprocess
import threading
import os
import random
import re
import shutil
import platform
from pathlib import Path
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file

gl.init()

aria2path = Path(__file__).resolve().parents[1] / "aria2"
os_type = platform.system()

if os_type == 'Windows':
    aria2 = os.path.join(aria2path, 'aria2c.exe')
    old_download = False
elif os_type == 'Linux':
    aria2 = os.path.join('/usr/bin', 'aria2c')
    if os.path.exists(aria2):
        print("Aria2 installation found")
        old_download = False
    else:
        print("Aria2 installation not found")
        old_download = True

class TimeOutFunction(Exception):
    pass

def download_start(model_name, model_filename, version):
    gl.last_version = version
    gl.current_download = model_filename
    gl.cancel_status = False
    gl.recent_model = model_name
    number = str(random.randint(10000, 99999))

    while number == gl.last_start:
        number = str(random.randint(10000, 99999))
    
    gl.last_start = number 
    return  (
            gr.Button.update(interactive=False, visible=False), # Download Button
            gr.Button.update(interactive=True, visible=True), # Cancel Button
            gr.Textbox.update(value=number), # Download Start Trigger
            gr.HTML.update(value='<div style="min-height: 100px;"></div>') # Download Progress
    )

def download_finish(model_filename, version, model_name, content_type):
    gr_components = _api.update_model_versions(model_name, content_type)
    version_choices = gr_components[0]['choices']
    
    prev_version = gl.last_version + " [Installed]"
    
    if prev_version in version_choices:
        version = prev_version
        Del = True
        Down = False
        
    else:
        Del = False
        Down = True
    
    gl.cancel_status = False
    return  (
            gr.Button.update(interactive=model_filename, visible=Down), # Download Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.Button.update(interactive=Del, visible=Del), # Delete Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>'), # Download Progress
            gr.Dropdown.update(value=version, choices=version_choices)
            
    )

def download_cancel(content_type, model_name, list_versions, model_filename):
    gl.cancel_status = True
    
    while True:        
        if not gl.isDownloading:
            _file.delete_model(content_type, gl.current_download, model_name, list_versions)
            break
        else:
            time.sleep(0.5)
            
    gl.cancel_status = False
    return  (
            gr.Button.update(interactive=model_filename, visible=True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>') # Download Progress
    )

def convert_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

def download_file(url, file_path, install_path, progress=gr.Progress()):
    process = None
    download_start = False
    gl.download_fail = False
    max_retries = 5
    if os.path.exists(file_path):
        os.remove(file_path)

    tokens = re.split(re.escape('\\'), file_path)
    file_name_display = tokens[-1]

    progress(0, desc="Download is starting...")
    
    while True:
        if gl.cancel_status:
            if process:
                process.terminate()
            progress(0, desc=f"Download cancelled.")
            time.sleep(2)
            return

        try:
            if os_type == 'Windows':
                cmd = f'"{aria2}" "{url}" -d "{install_path}" --async-dns=false --show-console-readout=true -x 16 -s 16'
            elif os_type == 'Linux':
                stdbuf_available = shutil.which("stdbuf") is not None
                cmd = f'stdbuf -o0 "{aria2}" "{url}" -d "{install_path}" --async-dns=false --show-console-readout=true -x 16 -s 16' if stdbuf_available else f'"{aria2}" "{url}" -d "{install_path}" --async-dns=false --show-console-readout=true -x 16 -s 16'
            
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
            for line in iter(process.stdout.readline, ''):
                if gl.cancel_status:
                    progress(0, desc=f"Download cancelled.")
                    time.sleep(2)
                    process.terminate()
                    return
                if 'DL:0B' in line:
                    if download_start:
                        progress(0, desc="Download has stalled. Please wait or cancel.")
                        continue
                    progress(0, desc="Download is starting...")
                    continue

                match = re.search(r'([\d.]+[KMGT]?iB)/([\d.]+[KMGT]?iB)\((\d+)%\) CN:\d+ DL:([\d.]+[KMGT]?iB) ETA:([\dm]+[s]?[\dm]*[s]?)', line)
                if match:
                    download_start = True
                    downloaded_size_str = match.group(1)
                    total_size_str = match.group(2)
                    progress_percent = int(match.group(3))
                    download_speed = match.group(4)
                    eta = match.group(5)
                    
                    progress(progress_percent / 100, desc=f"Downloading: {file_name_display} - {downloaded_size_str}/{total_size_str} - Speed: {download_speed}/s - ETA: {eta}")

            stdout, stderr = process.communicate()
            
            if gl.cancel_status:
                    progress(0, desc="Download cancelled.")
                    time.sleep(2)
                    process.terminate()
                    return

            if process.returncode != 0:
                progress(0, desc="Aria2 failed, switching to old download method")
                print(f"aria2c failed with error: {stderr}")
                print("switching to old download method")
                old_download = True
                return
            
            else:
                print(f"Model saved to: {file_path}")
                progress(1, desc=f"Model saved to: {file_path}")
                time.sleep(2)
                gl.download_fail = False
                return

        except Exception as e:
            print(f"An error occurred: {e}")
            max_retries -= 1
            if max_retries == 0:
                progress(0, desc="An error occured while downloading the file, please try again.")
                time.sleep(2)
                gl.download_fail = True
                return
            time.sleep(5)

def download_file_old(url, file_path, progress=gr.Progress()):
    gl.download_fail = False
    max_retries = 5
    if os.path.exists(file_path):
        os.remove(file_path)
    downloaded_size = 0
    tokens = re.split(re.escape('\\'), file_path)
    file_name_display = tokens[-1]
    
    while True:
        if gl.cancel_status:
            return
        if os.path.exists(file_path):
            downloaded_size = os.path.getsize(file_path)
            headers = {"Range": f"bytes={downloaded_size}-"}
        else:
            headers = {}
        with open(file_path, "ab") as f:
            while gl.isDownloading:
                try:
                    if gl.cancel_status:
                        return
                    try:
                        if gl.cancel_status:
                            return
                        response = requests.get(url, headers=headers, stream=True, timeout=4)
                        if response.status_code == 404:
                            progress(0, desc="File returned a 404, file is not found.")
                            time.sleep(3)
                            gl.download_fail = True
                            return
                        total_size = int(response.headers.get("Content-Length", 0))
                    except:
                        raise TimeOutFunction("Timed Out")
                    
                    if total_size == 0:
                        total_size = downloaded_size

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            if gl.cancel_status:
                                return
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            progress(downloaded_size / total_size, desc=f"Downloading: {file_name_display} {convert_size(downloaded_size)} / {convert_size(total_size)}")
                            if gl.isDownloading == False:
                                response.close
                                break
                    downloaded_size = os.path.getsize(file_path)
                    break
                
                except TimeOutFunction:
                    progress(0, desc="CivitAI API did not respond, retrying...")
                    max_retries -= 1
                    if max_retries == 0:
                        progress(0, desc="Unable to download file due to time-out, please try to download again.")
                        time.sleep(2)
                        gl.download_fail = True
                        return
                    time.sleep(5)

        if (gl.isDownloading == False):
            break
        
        gl.isDownloading = False
        downloaded_size = os.path.getsize(file_path)
        if downloaded_size >= total_size:
            if not gl.cancel_status:
                print(f"Model saved to: {file_path}")
                progress(1, desc=f"Model saved to: {file_path}")
                time.sleep(2)
                gl.download_fail = False
                return
                
        else:
            progress(0, desc="Download failed, please try again.")
            print(f"Error: File download failed: {file_name_display}")
            gl.download_fail = True
            time.sleep(2)
            if os.path.exists(file_path):
                os.remove(file_path)

def download_create_thread(url, file_name, preview_html, create_json, trained_tags, install_path, model_name, content_type, list_versions, progress=gr.Progress()):
    gr_components = _api.update_model_versions(model_name, content_type)
    
    name = model_name
    
    number = str(random.randint(10000, 99999))
    while number == gl.last_dwn:
        number = str(random.randint(10000, 99999))

    gl.last_dwn = number
    
    if gl.isDownloading:
        gl.isDownloading = False
        return
    
    gl.isDownloading = True
    if not os.path.exists(install_path):
        os.makedirs(install_path)
        
    path_to_new_file = os.path.join(install_path, file_name)
    if not old_download:
        thread = threading.Thread(target=download_file, args=(url, path_to_new_file, install_path, progress))
        thread.start()
        thread.join()
    
    if old_download:
        thread = threading.Thread(target=download_file_old, args=(url, path_to_new_file, progress))
        thread.start()
        thread.join()
    
    if not gl.cancel_status:
        if create_json:
            _file.save_json(file_name, install_path, trained_tags)
        _file.save_preview(preview_html, path_to_new_file, install_path)
    
    base_name = os.path.splitext(file_name)[0]
    base_name_preview = base_name + '.preview'

    if gl.download_fail:
        print(f'Error occured during download of "{path_to_new_file}".')
        gl.download_fail = True
        for root, dirs, files in os.walk(install_path):
            for file in files:
                file_base_name = os.path.splitext(file)[0]
                if file_base_name == base_name or file_base_name == base_name_preview:
                    path_file = os.path.join(root, file)
                    os.remove(path_file)
                    print(f"Removed: {path_file}")
                        
    if gl.isDownloading:
        gl.isDownloading = False

    (model, _, _) = _file.card_update(gr_components, name, list_versions, True)
    
    if not gl.cancel_status:
        modelName = model
    else:
        modelName = None
    
    return  (
            gr.HTML.update(), # Download Progress HTML
            gr.Textbox.update(value=modelName), # Current Model
            gr.Textbox.update(value=number) # Download Finish Trigger
    )
