import requests
import gradio as gr
import time
import subprocess
import threading
import os
import re
import random
import platform
import socket
import stat
import json
from pathlib import Path
from modules.shared import opts
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file

gl.init()
current_sha256 = None

def rpc_running():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("localhost", 6800))

        return True
    except Exception as e:
        pass
    finally:
        sock.close()

    return False

def start_aria2_rpc(aria2c):
    if not rpc_running():
        try:
            show_log = getattr(opts, "show_log", False)
            cmd = f'"{aria2c}" --enable-rpc --rpc-listen-all --check-certificate=false --ca-certificate=" " --file-allocation=none'
            subprocess_args = {'shell': True}
            if not show_log:
                subprocess_args.update({'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
                
            subprocess.Popen(cmd, **subprocess_args)
            print("Aria2 RPC started")
        except Exception as e:
            print(f"Failed to start Aria2 RPC server: {e}")

aria2path = Path(__file__).resolve().parents[1] / "aria2"
os_type = platform.system()

if os_type == 'Windows':
    aria2 = os.path.join(aria2path, 'win', 'aria2c.exe')
elif os_type == 'Linux':
    aria2 = os.path.join(aria2path, 'lin', 'aria2c')
    st = os.stat(aria2)
    os.chmod(aria2, st.st_mode | stat.S_IEXEC)
elif os_type == 'Darwin':
    aria2 = os.path.join(aria2path, 'mac', 'aria2c')

start_aria2_rpc(aria2)

class TimeOutFunction(Exception):
    pass

def random_number(prev):
    number = str(random.randint(10000, 99999))

    while number == prev:
        number = str(random.randint(10000, 99999))
    
    return number

def download_start(download_start, model_name, model_filename, version, sha256, modelId):
    global current_sha256, current_id
    gl.last_version = version
    gl.current_download = model_filename
    gl.cancel_status = False
    gl.recent_model = model_name
    current_sha256 = sha256
    current_id = modelId
    number = random_number(download_start)
    return  (
            gr.Button.update(interactive=False, visible=False), # Download Button
            gr.Button.update(interactive=True, visible=True), # Cancel Button
            gr.Textbox.update(value=number), # Download Start Trigger
            gr.HTML.update(value='<div style="min-height: 100px;"></div>') # Download Progress
    )

def download_finish(model_filename, version, model_name):
    gr_components = _api.update_model_versions(model_name)
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
    
    return  (
            gr.Button.update(interactive=model_filename, visible=Down), # Download Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.Button.update(interactive=Del, visible=Del), # Delete Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>'), # Download Progress
            gr.Dropdown.update(value=version, choices=version_choices)
            
    )

def download_cancel(delete_finish, model_name, list_versions, model_filename, sha256):
    gl.cancel_status = True
    gl.download_fail = True
    while True:        
        if not gl.isDownloading:
            _file.delete_model(delete_finish, gl.current_download, model_name, list_versions, sha256)
            break
        else:
            time.sleep(0.5)
            
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
    disable_dns = getattr(opts, "disable_dns", False)
    split_aria2 = getattr(opts, "split_aria2", 64)
    
    max_retries = 5
    gl.download_fail = False
    aria2_rpc_url = "http://localhost:6800/jsonrpc"

    if os.path.exists(file_path):
        os.remove(file_path)

    file_name = os.path.basename(file_path)
    
    if disable_dns:
        dns = "false"
    else:
        dns = "true"
    
    options = {
        "dir": install_path,
        "max-connection-per-server": str(f"{split_aria2}"),
        "split": str(f"{split_aria2}"),
        "async-dns": dns,
        "out": file_name
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
            
            remaining_size = total_length - completed_length
            if download_speed > 0:
                eta_seconds = remaining_size / download_speed
                eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
            else:
                eta_formatted = "XX:XX:XX"
            
            progress(progress_percent / 100, desc=f"Downloading: {file_name} - {convert_size(completed_length)}/{convert_size(total_length)} - Speed: {convert_size(download_speed)}/s - ETA: {eta_formatted}")
            
            if status_info['status'] == 'complete':
                print(f"Model saved to: {file_path}")
                progress(1, desc=f"Model saved to: {file_path}")
                sha256_to_json(file_path)
                time.sleep(2)
                gl.download_fail = False
                return
            
            if status_info['status'] == 'error':
                progress(0, desc=f"Encountered an error during download of: \"{file_name}\" Please try again.")
                gl.download_fail = True
                time.sleep(2)
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

def sha256_to_json(install_path):
    
    json_file = os.path.splitext(install_path)[0] + ".json"
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)

            data['modelId'] = current_id
            data['sha256'] = current_sha256
            
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        data = {'sha256': current_sha256, 'modelId': current_id}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)

def download_file_old(url, file_path,progress=gr.Progress()):
    gl.download_fail = False
    max_retries = 5
    if os.path.exists(file_path):
        os.remove(file_path)
    downloaded_size = 0
    tokens = re.split(re.escape('\\'), file_path)
    file_name_display = tokens[-1]
    start_time = time.time()
    while True:
        if gl.cancel_status:
            progress(0, desc=f"Download cancelled.")
            time.sleep(2)
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
                        progress(0, desc=f"Download cancelled.")
                        time.sleep(2)
                        return
                    try:
                        if gl.cancel_status:
                            progress(0, desc=f"Download cancelled.")
                            time.sleep(2)
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
                                progress(0, desc=f"Download cancelled.")
                                time.sleep(2)
                                return
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            elapsed_time = time.time() - start_time
                            download_speed = downloaded_size / elapsed_time
                            remaining_size = total_size - downloaded_size
                            if download_speed > 0:
                                eta_seconds = remaining_size / download_speed
                                eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                            else:
                                eta_formatted = "XX:XX:XX"
                            progress(
                                downloaded_size / total_size,
                                desc=f"Downloading: {file_name_display} {convert_size(downloaded_size)} / {convert_size(total_size)} - Speed: {convert_size(int(download_speed))}/s - ETA: {eta_formatted}"
                            )
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
                sha256_to_json(file_path)
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

def download_create_thread(download_finish, url, file_name, preview_html, create_json, trained_tags, install_path, model_name, list_versions, progress=gr.Progress()):
    gr_components = _api.update_model_versions(model_name)
    gl.cancel_status = False
    try:
        use_aria2 = getattr(opts, "use_aria2", True)
    except:
        use_aria2 = True
    name = model_name
    
    number = random_number(download_finish)
    
    if gl.isDownloading:
        gl.isDownloading = False
        return
    
    gl.isDownloading = True
    if not os.path.exists(install_path):
        os.makedirs(install_path)
        
    path_to_new_file = os.path.join(install_path, file_name)
    
    if use_aria2:
        thread = threading.Thread(target=download_file, args=(url, path_to_new_file, install_path, progress))
        thread.start()
        thread.join()
    else:
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
        if not gl.cancel_status:
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
