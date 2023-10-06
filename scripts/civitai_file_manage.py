import json
import gradio as gr
import urllib.request
import urllib.parse
import urllib.error
import os
import io
import re
import time
import shutil
import requests
import hashlib
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file
import scripts.civitai_download as _download
try:
    from send2trash import send2trash
except:
    print("Civit AI: Python module 'send2trash' has not been imported correctly, please try to restart or install it manually.")

gl.init()

no_update = False
from_ver = False
from_tag = False
from_installed = False

def delete_model(delete_finish, model_filename, model_name, list_versions, sha256=None):
    deleted = False
    gr_components = _api.update_model_versions(model_name)
    model_name_search = model_name
    
    (model_name, ver_value, ver_choices) = _file.card_update(gr_components, model_name, list_versions, False)
    if model_name_search is not None:
        selected_content_type = None
        for item in gl.json_data['items']:
            if item['name'] == model_name_search:
                selected_content_type = item['type']
                desc = item['description']
                break
        
        if selected_content_type is None:
            print("Model name not found in json_data. (delete_model)")
            return
    
    model_folder = os.path.join(_api.contenttype_folder(selected_content_type, desc))

    # Delete based on provided SHA-256 hash
    if sha256:
        sha256_upper = sha256.upper()  # Convert to upper case for case-insensitive matching
        for root, _, files in os.walk(model_folder):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as json_file:
                            data = json.load(json_file)
                            file_sha256 = data.get('sha256', '').upper()
                    except Exception as e:
                        print(f"Failed to open: {file_path}: {e}")
                        file_sha256 = "0"
                        
                    if file_sha256 == sha256_upper:
                        unpack_list = data.get('unpackList', [])
                        for unpacked_file in unpack_list:
                            unpacked_file_path = os.path.join(root, unpacked_file)
                            if os.path.isfile(unpacked_file_path):
                                try:
                                    send2trash(unpacked_file_path)
                                    print(f"File moved to trash based on unpackList: {unpacked_file_path}")
                                except:
                                    os.remove(unpacked_file_path)
                                    print(f"File deleted based on unpackList: {unpacked_file_path}")
                        
                        base_name, _ = os.path.splitext(file)
                        if os.path.isfile(file_path):
                            try:
                                send2trash(file_path)
                                print(f"Model moved to trash based on SHA-256: {file_path}")
                            except:
                                os.remove(file_path)
                                print(f"Model deleted based on SHA-256: {file_path}")
                            # Delete associated files
                            delete_associated_files(root, base_name)
                            deleted = True

    # Fallback to delete based on filename if not deleted based on SHA-256
    file_to_delete = os.path.splitext(model_filename)[0]
    if not deleted:
        for root, dirs, files in os.walk(model_folder):
            for file in files:
                current_file = os.path.splitext(file)[0]
                if file_to_delete == current_file:
                    path_file = os.path.join(root, file)
                    if os.path.isfile(path_file):
                        try:
                            send2trash(path_file)
                            print(f"Model moved to trash based on filename: {path_file}")
                        except:
                            os.remove(path_file)
                            print(f"Model deleted based on filename: {path_file}")
                        # Delete associated files
                        delete_associated_files(root, current_file)

    number = _download.random_number(delete_finish)
    
    return (
            gr.Button.update(interactive=False, visible=True),  # Download Button
            gr.Button.update(interactive=False, visible=False),  # Cancel Button
            gr.Button.update(interactive=False, visible=False),  # Delete Button
            gr.Textbox.update(value=number),  # Delete Finish Trigger
            gr.Textbox.update(value=model_name),  # Current Model 
            gr.Dropdown.update(value=ver_value, choices=ver_choices)  # Version List
    )

def delete_associated_files(directory, base_name):
    """Delete all files in the given directory with the same base name or base name followed by .preview"""
    for file in os.listdir(directory):
        current_base_name, ext = os.path.splitext(file)
        if current_base_name == base_name or current_base_name == f"{base_name}.preview":
            path_to_delete = os.path.join(directory, file)
            try:
                send2trash(path_to_delete)
                print(f"Associated file moved to trash: {path_to_delete}")
            except:
                os.remove(path_to_delete)
                print(f"Associated file deleted: {path_to_delete}")

def save_preview(preview_html, file_name, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'data-preview-img=[\'"]?([^\'" >]+)', preview_html)

    if not img_urls:
        return

    name = os.path.splitext(file_name)[0]
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    img_url = urllib.parse.quote(img_urls[0], safe=':/=')
    filename = f'{name}.preview.png'
    try:
        with urllib.request.urlopen(img_url) as url:
            preview_path = os.path.join(install_path, filename)
            with open(preview_path, 'wb') as f:
                f.write(url.read())
                
                print(f"Preview image saved to: {preview_path}")
    except Exception as e:
        print(f'Error downloading preview image: {e}')

def save_images(preview_html, model_filename, model_name, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'data-sampleimg="true" src=[\'"]?([^\'" >]+)', preview_html)
    
    name = os.path.splitext(model_filename)[0]

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    HTML = preview_html
    for i, img_url in enumerate(img_urls):
        filename = f'{name}_{i}.png'
        filenamethumb = f'{name}.png'
        if model_name is not None:
            for item in gl.json_data['items']:
                if item['name'] == model_name:
                    if item['type'] == "TextualInversion":
                        filename = f'{name}_{i}.preview.png'
                        filenamethumb = f'{name}.preview.png'
        HTML = HTML.replace(img_url,f'"{filename}"')
        img_url = urllib.parse.quote(img_url,  safe=':/=')
        print(img_url, install_path, filename)
        try:
            with urllib.request.urlopen(img_url) as url:
                with open(os.path.join(install_path, filename), 'wb') as f:
                    f.write(url.read())
                    if i == 0 and not os.path.exists(os.path.join(install_path, filenamethumb)):
                        shutil.copy2(os.path.join(install_path, filename),os.path.join(install_path, filenamethumb))
                    print("Downloaded images.")
                    
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    path_to_new_file = os.path.join(install_path, f'{name}.html')
    with open(path_to_new_file, 'wb') as f:
        f.write(HTML.encode('utf8'))
    path_to_new_file = os.path.join(install_path, f'{name}.civitai.info')
    with open(path_to_new_file, mode="w", encoding="utf-8") as f:
        json.dump(gl.json_info, f, indent=4, ensure_ascii=False)

def save_json(file_name, install_path, trained_tags):
    if not trained_tags:
        return trained_tags

    trained_tags = trained_tags.split(',')
    trained_tags = [tag.strip() for tag in trained_tags if not (tag.strip().startswith('<') and ':' in tag.strip() and tag.strip().endswith('>'))]
    trained_tags = ', '.join(trained_tags).strip()
    if trained_tags.endswith(','):
        trained_tags = trained_tags[:-1]

    if not os.path.exists(install_path):
        os.makedirs(install_path)

    parts = file_name.split('.')
    if len(parts) > 1:
        file_name = '.'.join(parts[:-1]) + ".json"
    else:
        file_name += ".json"
    
    path_to_new_file = os.path.join(install_path, file_name)

    if os.path.exists(path_to_new_file):
        try:
            with open(path_to_new_file, 'r') as f:
                content = json.load(f)
            content["activation text"] = trained_tags
        except Exception as e:
            print(f"Failed to open {path_to_new_file}: {e}")
    else:
        content = {"activation text": trained_tags}

    with open(path_to_new_file, 'w') as f:
        json.dump(content, f)

    print(f"Tags saved to: {path_to_new_file}")

    return trained_tags

def card_update(gr_components, model_name, list_versions, is_install):
    version_choices = gr_components[0]['choices']
    
    if is_install and not gl.download_fail and not gl.cancel_status:
        version_value_clean = list_versions + " [Installed]"
        version_choices_clean = [version if version + " [Installed]" != version_value_clean else version_value_clean for version in version_choices]
        
    else:
        version_value_clean = list_versions.replace(" [Installed]", "")
        version_choices_clean = [version if version.replace(" [Installed]", "") != version_value_clean else version_value_clean for version in version_choices]
    
    first_version_installed = "[Installed]" in version_choices_clean[0]
    any_later_version_installed = any("[Installed]" in version for version in version_choices_clean[1:])

    if first_version_installed:
        model_name += ".New"
    elif any_later_version_installed:
        model_name += ".Old"
    else:
        model_name += ".None"
    
    return model_name, version_value_clean, version_choices_clean

def list_files(folders):
    model_files = []
    
    extensions = ['.pt', '.ckpt', '.pth', '.safetensors', '.th', '.zip', '.vae']
    
    for folder in folders:
        if folder and os.path.exists(folder):
            for root, _, files in os.walk(folder):
                for file in files:
                    _, file_extension = os.path.splitext(file)
                    if file_extension.lower() in extensions:
                        model_files.append(os.path.join(root, file))

    model_files = sorted(list(set(model_files)))
    return model_files

def gen_sha256(file_path):
    json_file = os.path.splitext(file_path)[0] + ".json"
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        
            if 'sha256' in data:
                hash_value = data['sha256']
                return hash_value
        except Exception as e:
            print(f"Failed to open {json_file}: {e}")
        
    def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
        while True:
            chunk = file.read(size)
            if not chunk:
                break
            yield chunk
    
    blocksize = 1 << 20
    h = hashlib.sha256()
    length = 0
    with open(os.path.realpath(file_path), 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)

    hash_value = h.hexdigest()
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
    
            if 'sha256' not in data:
                data['sha256'] = hash_value
                
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to open {json_file}: {e}")
    else:
        data = {'sha256': hash_value}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    return hash_value
        
def tags_save(api_response, file_paths):
    for item in api_response.get('items', []):
        for model_version in item.get('modelVersions', []):
            for file in model_version.get('files', []):
                file_name = file.get('name', '')
                
                for file_path in file_paths:
                    base_name = os.path.basename(file_path)
                    
                    if file_name == base_name:
                        trained_words = model_version.get('trainedWords', [])
                        
                        if not trained_words:
                            break
                        
                        if isinstance(trained_words, list):
                            trained_tags = ",".join(trained_words)
                            trained_tags = re.sub(r'<[^>]*:[^>]*>', '', trained_tags)
                            trained_tags = re.sub(r', ?', ', ', trained_tags)
                            trained_tags = trained_tags.strip(', ')
                        else:
                            trained_tags = trained_words
                        
                        json_file = os.path.splitext(file_path)[0] + '.json'
                        if os.path.exists(json_file):
                            with open(json_file, 'r') as f:
                                try:
                                    content = json.load(f)
                                except:
                                    content = {}

                            content["activation text"] = trained_tags
                            with open(json_file, 'w') as f:
                                json.dump(content, f, indent=4)
                        else:
                            content = {"activation text": trained_tags}
                            with open(json_file, 'w') as f:
                                json.dump(content, f, indent=4)
                        
                        print(f"Tags saved in {json_file}")

def get_models(file_path):
    modelId = None
    json_file = os.path.splitext(file_path)[0] + ".json"
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                if 'modelId' in data:
                    modelId = data['modelId']
        except Exception as e:
            print(f"Failed to open {json_file}: {e}")
    
    if not modelId:
        model_hash = gen_sha256(file_path)
        by_hash = f"https://civitai.com/api/v1/model-versions/by-hash/{model_hash}"
    
    try:
        if not modelId:
            response = requests.get(by_hash, timeout=(10,30))
            if response.status_code == 200:
                data = response.json()
                modelId = data.get("modelId", "")
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)

                        if 'modelId' not in data:
                            data['modelId'] = modelId
                            
                        with open(json_file, 'w') as f:
                            json.dump(data, f, indent=4)
                    except Exception as e:
                        print(f"Failed to open {json_file}: {e}")
                else:
                    data = {'modelId': modelId}
                    with open(json_file, 'w') as f:
                        json.dump(data, f, indent=4)
        
        return modelId
    except requests.exceptions.Timeout:
        print(f"Request timed out for {file_path}. Skipping...")
    except Exception as e:
        print(f"An error occurred for {file_path}: {str(e)}")
        
def version_match(file_paths, api_response):
    updated_models = []
    outdated_models = []
    sha256_hashes = {}
    for file_path in file_paths:
        json_path = f"{os.path.splitext(file_path)[0]}.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                try:
                    json_data = json.load(f)
                    sha256 = json_data.get('sha256')
                    if sha256:
                        sha256_hashes[os.path.basename(file_path)] = sha256.upper()
                except Exception as e:
                    print(f"Failed to open {json_path}: {e}")
    
    for item in api_response.get('items', []):
        model_versions = item.get('modelVersions', [])
        
        if not model_versions:
            continue  
            
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            file_sha256 = sha256_hashes.get(file_name, "").upper()
            
            for idx, model_version in enumerate(model_versions):
                files = model_version.get('files', [])
                
                for file_entry in files:
                    entry_name = os.path.splitext(file_entry.get('name', ''))[0]
                    entry_sha256 = file_entry.get('hashes', {}).get('SHA256', "").upper()
                    
                    if entry_name == file_name_without_ext or entry_sha256 == file_sha256:
                        if idx == 0:
                            print(f"{file_name} is currently the latest version")
                            updated_models.append(f"&ids={item['id']}")
                        else:
                            print(f"{file_name} has an available update!")
                            outdated_models.append(f"&ids={item['id']}")
                        break 
                else:
                    continue
                break
                
    return updated_models, outdated_models

def file_scan(folders, ver_finish, tag_finish, installed_finish, progress=gr.Progress()):
    global from_ver, from_installed, no_update
    gl.scan_files = True
    no_update = False
    if from_ver:
        number = _download.random_number(ver_finish)
    if from_tag:
        number = _download.random_number(tag_finish)
    if from_installed:
        number = _download.random_number(installed_finish)
    
    if not folders:
        progress(0, desc=f"No folder selected.")
        no_update = True
        gl.scan_files = False
        from_ver, from_installed = False, False
        time.sleep(2)
        return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number))
    
    folders_to_check = []
    for item in folders:
        if item == "LORA & LoCon":
            folder = _api.contenttype_folder("LORA")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder("LoCon", None, True)
            if folder:
                folders_to_check.append(folder)
        if item == "Upscaler":
            folder = _api.contenttype_folder(item, "ESRGAN")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "RealESRGAN")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "SwinIR")
            if folder:
                folders_to_check.append(folder)
        else:
            folder = _api.contenttype_folder(item)
            if folder:
                folders_to_check.append(folder)
        
    total_files = 0
    files_done = 0

    files = list_files(folders_to_check)
    total_files += len(files)
    
    if total_files == 0:
        progress(1, desc=f"No files in selected folder.")
        no_update = True
        gl.scan_files = False
        from_ver, from_installed = False, False
        time.sleep(2)
        return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                        gr.Textbox.update(value=number))
    
    updated_models = []
    outdated_models = []
    all_model_ids = []
    file_paths = []
    
    for file_path in files:
        if gl.cancel_status:
            progress(files_done / total_files, desc=f"Saving tags cancelled.")
            no_update = True
            gl.scan_files = False
            from_ver, from_installed = False, False
            time.sleep(2)
            return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                    gr.Textbox.update(value=number))
        file_name = os.path.basename(file_path)
        progress(files_done / total_files, desc=f"Processing file: {file_name}")
        model_id = get_models(file_path)
        if model_id != None:
            all_model_ids.append(f"&ids={model_id}")
            file_paths.append(file_path)
        files_done += 1
        
    all_items = []

    all_model_ids = list(set(all_model_ids))

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
            
    if not from_installed:
        model_chunks = list(chunks(all_model_ids, 500))

        base_url = "https://civitai.com/api/v1/models?limit=100"
        url_list = [f"{base_url}{''.join(chunk)}" for chunk in model_chunks]
        
        for url in url_list:
            while url:
                progress(1, desc=f"Sending API request...")
                response = requests.get(url, timeout=(10,30))
                if response.status_code == 200:
                    api_response = response.json()

                    all_items.extend(api_response['items'])

                    metadata = api_response.get('metadata', {})
                    url = metadata.get('nextPage', None)
                else:
                    print(f"Error: Received status code {response.status_code} with URL:")
                    print(url)
                    break

        api_response['items'] = all_items
    
    if from_ver:
        # return a list of outdated and updated models by ID
        updated_models, outdated_models = version_match(file_paths, api_response)
        
        # Convert the lists to sets
        updated_set = set(updated_models)
        outdated_set = set(outdated_models)

        # Remove IDs from outdated_models that are in updated_models
        outdated_set = outdated_set - updated_set
        all_model_ids = list(outdated_set)
        
        if len(all_model_ids) == 0:
            no_update = True
            gl.scan_files = False
            from_ver = False
            return  (
                    gr.HTML.update(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">No updates found for selected models.</div>'),
                    gr.Textbox.update(value=number)
                )
    
    model_chunks = list(chunks(all_model_ids, gl.tile_count))

    base_url = "https://civitai.com/api/v1/models?limit=100"
    gl.url_list_with_numbers = {i+1: f"{base_url}{''.join(chunk)}" for i, chunk in enumerate(model_chunks)}

    api_url = gl.url_list_with_numbers.get(1)
    response = requests.get(api_url, timeout=(10,30))
    if response.status_code == 200:
        response.encoding = "utf-8"
        gl.ver_json = json.loads(response.text)
        
        # Modify the metadata
        highest_number = max(gl.url_list_with_numbers.keys())
        gl.ver_json["metadata"]["totalPages"] = highest_number
        
        if highest_number > 1:
            gl.ver_json["metadata"]["nextPage"] = gl.url_list_with_numbers.get(2)
    
    if from_ver:
        gl.scan_files = False
        return  (
                gr.HTML.update(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Outdated models have been found.<br>Please press the button above to load the models into the browser tab</div>'),
                gr.Textbox.update(value=number)
            )

    if from_installed:
        gl.scan_files = False
        return  (
                gr.HTML.update(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Installed models have been loaded.<br>Please press the button above to load the models into the browser tab</div>'),
                gr.Textbox.update(value=number)
            )

    if from_tag:
        tags_save(api_response, file_paths)
        progress(1, desc=f"All tags succesfully saved!")
        time.sleep(2)
        return  (
                gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number)
            )

def save_tag_start(tag_start):
    global from_tag, from_ver, from_installed
    from_tag, from_ver, from_installed = True, False, False
    number = _download.random_number(tag_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )

def save_tag_finish():
    global from_tag
    from_tag = False
    return (
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False)
    )
    
def start_ver_search(ver_start):
    global from_ver, from_tag, from_installed
    from_ver, from_tag, from_installed = True, False, False
    number = _download.random_number(ver_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )

def finish_ver_search():
    return (
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False if no_update else True, visible=False if no_update else True),
        
    )

def load_to_browser():
    global from_ver, from_installed
    _ = None
    if from_ver:
        (lm,lv,lh,pp,np,p,st,si,dm,ip,sf,fl,bt) = _api.update_model_list(_,_,_,_,_,_,_,_,True)
    if from_installed:
        (lm,lv,lh,pp,np,p,st,si,dm,ip,sf,fl,bt) = _api.update_model_list(_,_,_,_,_,_,_,_,False,True)
    
    gl.file_scan = True
    from_ver, from_installed = False, False
    return (
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False, visible=False),
        lm,lv,lh,pp,np,p,st,si,dm,ip,sf,fl,bt,
        gr.HTML.update(value='<div style="min-height: 0px;"></div>')
    )
    
def start_installed_models(installed_start):
    global from_installed, from_ver, from_tag
    from_installed, from_ver, from_tag = True, False, False
    number = _download.random_number(installed_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )
    
def finish_installed_models():
    return (
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False if no_update else True, visible=False if no_update else True),
    )

def cancel_scan():
    gl.cancel_status = True
    
    while True:
        if not gl.scan_files:
            gl.cancel_status = False
            return
        else:
            time.sleep(0.5)
            continue