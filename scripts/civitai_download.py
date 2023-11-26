import requests
import gradio as gr
import time
import subprocess
import threading
import os
import re
import random
import platform
import stat
import json
import time
from pathlib import Path
from modules.shared import opts, cmd_opts
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file
try:
    from zip_unicode import ZipHandler
except:
    print(f"{gl.print} Python module 'ZipUnicode' has not been imported correctly, please try to restart or install it manually.")
try:
    from fake_useragent import UserAgent
except:
    print(f"{gl.print} Python module 'fake_useragent' has not been imported correctly, please try to restart or install it manually.")


def random_number(prev):
    number = str(random.randint(10000, 99999))
    
    while number == prev:
        number = str(random.randint(10000, 99999))
    
    return number

gl.init()
current_sha256 = None
rpc_secret = "R7T5P2Q9K6"
try:
    queue = not cmd_opts.no_gradio_queue
except AttributeError:
    queue = not cmd_opts.disable_queue
except:
    queue = True

def start_aria2_rpc():
    start_file = os.path.join(aria2path, '_')
    running_file = os.path.join(aria2path, 'running')
    null = open(os.devnull, 'w')
    
    if os.path.exists(running_file):
        try:
            if os_type == 'Linux':
                env = os.environ.copy()
                env['PATH'] = '/usr/bin:' + env['PATH']
                subprocess.Popen("pkill aria2", shell=True, env=env)
            else:
                subprocess.Popen(stop_rpc, stdout=null, stderr=null)
            time.sleep(1)
        except Exception as e:
            print(f"{gl.print} Failed to stop Aria2 RPC : {e}")
    else:
        if os.path.exists(start_file):
            os.rename(start_file, running_file)
            return
        else:
            with open(start_file, 'w'):
                pass

    try:
        show_log = getattr(opts, "show_log", False)
        aria2_flags = getattr(opts, "aria2_flags", "")
        cmd = f'"{aria2}" --enable-rpc --rpc-listen-all --rpc-listen-port=24000 --rpc-secret {rpc_secret} --check-certificate=false --ca-certificate=" " --file-allocation=none {aria2_flags}'
        subprocess_args = {'shell': True}
        if not show_log:
            subprocess_args.update({'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
            
        subprocess.Popen(cmd, **subprocess_args)
        if os.path.exists(running_file):
            print(f"{gl.print} Aria2 RPC restarted")
        else:
            print(f"{gl.print} Aria2 RPC started")
    except Exception as e:
        print(f"{gl.print} Failed to start Aria2 RPC server: {e}")
        
aria2path = Path(__file__).resolve().parents[1] / "aria2"
os_type = platform.system()

if os_type == 'Windows':
    aria2 = os.path.join(aria2path, 'win', 'aria2.exe')
    stop_rpc = "taskkill /im aria2.exe /f"
    start_aria2_rpc()
elif os_type == 'Linux':
    aria2 = os.path.join(aria2path, 'lin', 'aria2')
    st = os.stat(aria2)
    os.chmod(aria2, st.st_mode | stat.S_IEXEC)
    stop_rpc = "pkill aria2"
    start_aria2_rpc()

class TimeOutFunction(Exception):
    pass

def download_start(download_start, model_name, model_filename, version, sha256):
    global current_sha256, current_id
    gl.last_version = version
    gl.current_download = model_filename
    gl.cancel_status = False
    gl.recent_model = model_name
    if sha256:
        current_sha256 = sha256.upper()
    for item in gl.json_data['items']:
        if item['name'] == model_name:
            current_id = item['id']
    number = random_number(download_start)
    return  (
            gr.Button.update(interactive=False, visible=False), # Download Button
            gr.Button.update(interactive=True, visible=True), # Cancel Button
            gr.Textbox.update(value=number), # Download Start Trigger
            gr.HTML.update(value='<div style="min-height: 100px;"></div>') # Download Progress
    )

def download_finish(model_filename, version, model_name):
    gr_components = _api.update_model_versions(model_name)
    if gr_components:
        version_choices = gr_components['choices']
    else:
        version_choices = []
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
            gr.Button.update(interactive=model_filename, visible=True), # Down Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>') # Download Progress
    )

def convert_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

def get_download_link(url):
    api_key = getattr(opts, "custom_api_key", "")
    if not api_key:
        api_key = "eaee11648ef4c72efb2333d5ebc68b98"
    headers = {
        'User-Agent': UserAgent().chrome,
        'Sec-Ch-Ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Gpc': '1',
        'Upgrade-Insecure-Requests': '1',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.get(url, headers=headers, allow_redirects=False)
    if 300 <= response.status_code <= 308:
        download_link = response.headers["Location"]
        return download_link
    else:
        return None

def download_file(url, file_path, install_path, progress=gr.Progress() if queue else None):
    disable_dns = getattr(opts, "disable_dns", False)
    split_aria2 = getattr(opts, "split_aria2", 64)
    
    max_retries = 5
    gl.download_fail = False
    aria2_rpc_url = "http://localhost:24000/jsonrpc"

    download_link = get_download_link(url)
    if not download_link:
        print(f"{gl.print} Couldn't retrieve download link")
        gl.download_fail = True
        return
    
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
        "params": ["token:" + rpc_secret, [download_link], options]
    })
    
    try:
        response = requests.post(aria2_rpc_url, data=payload)
        data = json.loads(response.text)
        if 'result' not in data:
                raise ValueError(f'Failed to start download: {data}')
        gid = data['result']
    except Exception as e:
        print(f"{gl.print} Failed to start download: {e}")
        gl.download_fail = True
        return
        
    while True:
        if gl.cancel_status:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": "1",
                "method": "aria2.remove",
                "params": ["token:" + rpc_secret, gid]
            })
            requests.post(aria2_rpc_url, data=payload)
            if progress != None:
                progress(0, desc=f"Download cancelled.")
            time.sleep(2)
            return

        try:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": "1",
                "method": "aria2.tellStatus",
                "params": ["token:" + rpc_secret, gid]
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
            if progress != None:
                progress(progress_percent / 100, desc=f"Downloading: {file_name} - {convert_size(completed_length)}/{convert_size(total_length)} - Speed: {convert_size(download_speed)}/s - ETA: {eta_formatted}")
            
            if status_info['status'] == 'complete':
                print(f"{gl.print} Model saved to: {file_path}")
                if progress != None:
                    progress(1, desc=f"Model saved to: {file_path}")
                time.sleep(2)
                gl.download_fail = False
                return
            
            if status_info['status'] == 'error':
                if progress != None:
                    progress(0, desc=f"Encountered an error during download of: \"{file_name}\" Please try again.")
                gl.download_fail = True
                time.sleep(2)
                return
                
            time.sleep(0.25)

        except Exception as e:
            print(f"{gl.print} Error occurred during Aria2 status update: {e}")
            max_retries -= 1
            if max_retries == 0:
                if progress != None:
                    progress(0, desc="An error occurred while downloading the file, please try again.")
                time.sleep(2)
                gl.download_fail = True
                return
            time.sleep(5)

def info_to_json(install_path, unpackList=None):
    json_file = os.path.splitext(install_path)[0] + ".json"
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"{gl.print} Failed to open {json_file}: {e}")
    else:
        data = {}

    data['modelId'] = current_id
    data['sha256'] = current_sha256
    if unpackList:
        data['unpackList'] = unpackList

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

def download_file_old(url, file_path, progress=gr.Progress() if queue else None):
    gl.download_fail = False
    max_retries = 5
    if os.path.exists(file_path):
        os.remove(file_path)
        
    downloaded_size = 0
    tokens = re.split(re.escape('\\'), file_path)
    file_name_display = tokens[-1]
    start_time = time.time()
    last_update_time = 0
    update_interval = 0.25
    
    download_link = get_download_link(url)
    if not download_link:
        print(f"{gl.print} Couldn't retrieve download link")
        gl.download_fail = True
        return
    
    while True:
        if gl.cancel_status:
            if progress != None:
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
                        if progress != None:
                            progress(0, desc=f"Download cancelled.")
                        time.sleep(2)
                        return
                    try:
                        if gl.cancel_status:
                            if progress != None:
                                progress(0, desc=f"Download cancelled.")
                            time.sleep(2)
                            return
                        response = requests.get(download_link, headers=headers, stream=True, timeout=4)
                        if response.status_code == 404:
                            if progress != None:
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
                                if progress != None:
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
                            current_time = time.time()
                            if current_time - last_update_time >= update_interval:
                                progress(downloaded_size / total_size, desc=f"Downloading: {file_name_display} {convert_size(downloaded_size)} / {convert_size(total_size)} - Speed: {convert_size(int(download_speed))}/s - ETA: {eta_formatted}")
                                last_update_time = current_time
                            if gl.isDownloading == False:
                                response.close
                                break
                    downloaded_size = os.path.getsize(file_path)
                    break

                except TimeOutFunction:
                    if progress != None:
                        progress(0, desc="CivitAI API did not respond, retrying...")
                    max_retries -= 1
                    if max_retries == 0:
                        if progress != None:
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
                print(f"{gl.print} Model saved to: {file_path}")
                if progress != None:
                    progress(1, desc=f"Model saved to: {file_path}")
                time.sleep(2)
                gl.download_fail = False
                return

        else:
            if progress != None:
                progress(0, desc="Download failed, please try again.")
            print(f"{gl.print} File download failed: {file_name_display}")
            gl.download_fail = True
            time.sleep(2)
            if os.path.exists(file_path):
                os.remove(file_path)

def download_create_thread(download_finish, url, file_name, preview_html, create_json, install_path, model_name, list_versions, progress=gr.Progress() if queue else None):
    gr_components = _api.update_model_versions(model_name)
    gl.cancel_status = False
    use_aria2 = getattr(opts, "use_aria2", True)
    unpack_zip = getattr(opts, "unpack_zip", False)
    name = model_name
    
    number = random_number(download_finish)
    
    if gl.isDownloading:
        gl.isDownloading = False
        return
    
    gl.isDownloading = True
    if not os.path.exists(install_path):
        os.makedirs(install_path)
        
    path_to_new_file = os.path.join(install_path, file_name)
    
    if use_aria2 and os_type != 'Darwin':
        thread = threading.Thread(target=download_file, args=(url, path_to_new_file, install_path, progress))
    else:
        thread = threading.Thread(target=download_file_old, args=(url, path_to_new_file, progress))
    thread.start()
    thread.join()
    
    if not gl.cancel_status or gl.download_fail:
        if os.path.exists(path_to_new_file):
            unpackList = []
            if unpack_zip:
                try:
                    if path_to_new_file.endswith('.zip'):
                        directory = Path(os.path.dirname(path_to_new_file))
                        zip_handler = ZipHandler(path_to_new_file)
                        
                        for original_name, decoded_name in zip_handler.name_map.items():
                            unpackList.append(decoded_name)
                        
                        zip_handler.extract_all(directory)
                        zip_handler.zip_ref.close()
                        
                        print(f"{gl.print} Successfully extracted {file_name} to {directory}")
                        os.remove(path_to_new_file)
                except Exception as e:
                    print(f"{gl.print} Failed to extract {file_name} with error: {e}")
            if create_json:
                _file.save_model_info(install_path, file_name, current_sha256, gl.json_data)
            if not gl.cancel_status:
                info_to_json(path_to_new_file, unpackList)
                _file.save_preview(file_name, install_path, preview_html)
                
    base_name = os.path.splitext(file_name)[0]
    base_name_preview = base_name + '.preview'

    if gl.download_fail:
        for root, dirs, files in os.walk(install_path):
            for file in files:
                file_base_name = os.path.splitext(file)[0]
                if file_base_name == base_name or file_base_name == base_name_preview:
                    path_file = os.path.join(root, file)
                    os.remove(path_file)
        if gl.cancel_status:
            print(f'{gl.print} Cancelled download of "{file_name}"')
        else:
            print(f'{gl.print} Error occured during download of "{file_name}"')
                    
    if gl.isDownloading:
        gl.isDownloading = False
    
    (model, _, _) = _file.card_update(gr_components, name, list_versions, True)
    
    if not gl.cancel_status:
        modelName = model
    else:
        modelName = None
    
    gl.cancel_status = False
    
    return  (
            gr.HTML.update(), # Download Progress HTML
            gr.Textbox.update(value=modelName), # Current Model
            gr.Textbox.update(value=number) # Download Finish Trigger
    )
