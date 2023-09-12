import requests
import gradio as gr
import time
import subprocess
import threading
import os
import random
import platform
import stat
import json
from pathlib import Path
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file

gl.init()

def rpc_running():
    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "aria2.getVersion",
            "params": []
        })
        response = requests.post("http://localhost:6800/jsonrpc", data=payload, timeout=2)
        if response.status_code == 200:
            return True
    except Exception as e:
        pass
    return False

def start_aria2_rpc(aria2c):
    if not rpc_running():
        try:
            cmd_options = '--enable-rpc --rpc-listen-all --check-certificate=false --ca-certificate=" "'
            os_cmd_mapping = {
                'Windows': f'"{aria2c}" {cmd_options} --async-dns=false',
                'Linux': f'"{aria2c}" {cmd_options}'
            }
            cmd = os_cmd_mapping.get(os_type, 'Unsupported OS')
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Aria2 RPC server started")
        except Exception as e:
            print(f"Failed to start Aria2 RPC server: {e}")

aria2path = Path(__file__).resolve().parents[1] / "aria2"
os_type = platform.system()

if os_type == 'Windows':
    aria2 = os.path.join(aria2path, 'aria2c.exe')
elif os_type == 'Linux':
    aria2 = os.path.join(aria2path, 'aria2c')
    st = os.stat(aria2)
    os.chmod(aria2, st.st_mode | stat.S_IEXEC)

start_aria2_rpc(aria2)

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
        
    if gl.cancel_status:
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
    max_retries = 5
    gl.download_fail = False
    aria2_rpc_url = "http://localhost:6800/jsonrpc"

    if os.path.exists(file_path):
        os.remove(file_path)

    file_name_display = os.path.basename(file_path)
    
    options = {
        "dir": install_path,
        "max-connection-per-server": "64",
        "split": "64",
        "min-split-size": "1M"
    }
    
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "1",
        "method": "aria2.addUri",
        "params": [[url], options]
    })
    
    try:
        response = requests.post(aria2_rpc_url, data=payload)
        gid = json.loads(response.text)['result']
    except Exception as e:
        print(f"Failed to start download: {e}")
        gl.download_fail = True
        return
    
    while True:
        if gl.cancel_status:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": "1",
                "method": "aria2.remove",
                "params": [gid]
            })
            requests.post(aria2_rpc_url, data=payload)
            progress(0, desc=f"Download cancelled.")
            time.sleep(2)
            return

        try:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": "1",
                "method": "aria2.tellStatus",
                "params": [gid]
            })
            
            response = requests.post(aria2_rpc_url, data=payload)
            status_info = json.loads(response.text)['result']
            
            total_length = int(status_info['totalLength'])
            completed_length = int(status_info['completedLength'])
            download_speed = int(status_info['downloadSpeed'])
            
            progress_percent = (completed_length / total_length) * 100 if total_length else 0
            progress(progress_percent / 100, desc=f"Downloading: {file_name_display} - {convert_size(completed_length)}/{convert_size(total_length)} - Speed: {convert_size(download_speed)}/s")
            
            if status_info['status'] == 'complete':
                progress(1, desc=f"Model saved to: {file_path}")
                time.sleep(2)
                gl.download_fail = False
                return
            
            time.sleep(0.25)

        except Exception as e:
            print(f"An error occurred: {e}")
            max_retries -= 1
            if max_retries == 0:
                progress(0, desc="An error occurred while downloading the file, please try again.")
                time.sleep(2)
                gl.download_fail = True
                return
            time.sleep(5)

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

    thread = threading.Thread(target=download_file, args=(url, path_to_new_file, install_path, progress))
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
