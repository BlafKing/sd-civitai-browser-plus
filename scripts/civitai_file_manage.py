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
from pathlib import Path
from urllib.parse import urlparse
from modules.shared import cmd_opts, opts
import scripts.civitai_global as gl
import scripts.civitai_api as _api
import scripts.civitai_file_manage as _file
import scripts.civitai_download as _download

try:
    from send2trash import send2trash
except:
    print(f"{gl.print} Python module 'send2trash' has not been imported correctly, please try to restart or install it manually.")
try:
    from bs4 import BeautifulSoup
except:
    print(f"{gl.print} Python module 'BeautifulSoup' has not been imported correctly, please try to restart or install it manually.")

gl.init()

css_path = Path(__file__).resolve().parents[1] / "style_html.css"
no_update = False
from_ver = False
from_tag = False
from_installed = False
try:
    queue = not cmd_opts.no_gradio_queue
except AttributeError:
    queue = not cmd_opts.disable_queue
except:
    queue = True

def delete_model(delete_finish=None, model_filename=None, model_name=None, list_versions=None, sha256=None, selected_list=None):
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
            print(f"{gl.print} Model name not found in json_data. (delete_model)")
            return
    
    model_folder = os.path.join(_api.contenttype_folder(selected_content_type, desc))

    # Delete based on provided SHA-256 hash
    if sha256:
        sha256_upper = sha256.upper()
        for root, _, files in os.walk(model_folder):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as json_file:
                            data = json.load(json_file)
                            file_sha256 = data.get('sha256', '').upper()
                    except Exception as e:
                        print(f"{gl.print} Failed to open: {file_path}: {e}")
                        file_sha256 = "0"
                        
                    if file_sha256 == sha256_upper:
                        unpack_list = data.get('unpackList', [])
                        for unpacked_file in unpack_list:
                            unpacked_file_path = os.path.join(root, unpacked_file)
                            if os.path.isfile(unpacked_file_path):
                                try:
                                    send2trash(unpacked_file_path)
                                    print(f"{gl.print} File moved to trash based on unpackList: {unpacked_file_path}")
                                except:
                                    os.remove(unpacked_file_path)
                                    print(f"{gl.print} File deleted based on unpackList: {unpacked_file_path}")
                        
                        base_name, _ = os.path.splitext(file)
                        if os.path.isfile(file_path):
                            try:
                                send2trash(file_path)
                                print(f"{gl.print} Model moved to trash based on SHA-256: {file_path}")
                            except:
                                os.remove(file_path)
                                print(f"{gl.print} Model deleted based on SHA-256: {file_path}")
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
                            print(f"{gl.print} Model moved to trash based on filename: {path_file}")
                        except:
                            os.remove(path_file)
                            print(f"{gl.print} Model deleted based on filename: {path_file}")
                        delete_associated_files(root, current_file)

    number = _download.random_number(delete_finish)


    btnDwn = not selected_list or selected_list == "[]"
    
    return (
            gr.Button.update(interactive=btnDwn, visible=btnDwn),  # Download Button
            gr.Button.update(interactive=False, visible=False),  # Cancel Button
            gr.Button.update(interactive=False, visible=False),  # Delete Button
            gr.Textbox.update(value=number),  # Delete Finish Trigger
            gr.Textbox.update(value=model_name),  # Current Model 
            gr.Dropdown.update(value=ver_value, choices=ver_choices)  # Version List
    )

def delete_associated_files(directory, base_name):
    for file in os.listdir(directory):
        current_base_name, ext = os.path.splitext(file)
        if current_base_name == base_name or current_base_name == f"{base_name}.preview":
            path_to_delete = os.path.join(directory, file)
            try:
                send2trash(path_to_delete)
                print(f"{gl.print} Associated file moved to trash: {path_to_delete}")
            except:
                os.remove(path_to_delete)
                print(f"{gl.print} Associated file deleted: {path_to_delete}")

def save_preview(file_path, api_response, overwrite_toggle=False, sha256=None):
    json_file = os.path.splitext(file_path)[0] + ".json"
    install_path, file_name = os.path.split(file_path)
    name = os.path.splitext(file_name)[0]
    filename = f'{name}.preview.png'
    image_path = os.path.join(install_path, filename)
    
    if overwrite_toggle:
        if os.path.exists(image_path):
            return
    
    if not sha256:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'sha256' in data:
                        sha256 = data['sha256'].upper()
            except Exception as e:
                print(f"{gl.print} Failed to open {json_file}: {e}")
    else:
        sha256 = sha256.upper()

    for item in api_response["items"]:
        for version in item["modelVersions"]:
            for file_entry in version["files"]:
                if file_entry["hashes"]["SHA256"] == sha256:
                    for image in version["images"]:
                        if image["type"] == "image":
                            url_with_width = re.sub(r'/width=\d+', f'/width={image["width"]}', image["url"])

                            response = requests.get(url_with_width)
                            if response.status_code == 200:
                                with open(image_path, 'wb') as img_file:
                                    img_file.write(response.content)
                                print(f"{gl.print} Preview saved at \"{image_path}\"")
                            else:
                                print(f"{gl.print} Failed to preview. Status code: {response.status_code}")

                            return
                    print(f"{gl.print} No preview images found for \"{name}\"")
                    return

def save_images(preview_html, model_filename, model_name, install_path):
    image_location = getattr(opts, "image_location", r"")
    if image_location:
        install_path = Path(image_location)
        
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'data-sampleimg="true" src=[\'"]?([^\'" >]+)', preview_html)
    
    name = os.path.splitext(model_filename)[0]

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    HTML = preview_html
    image_count = 0
    for i, img_url in enumerate(img_urls):
        image_count += 1
        filename = f'{name}_{i}.png'
        filenamethumb = f'{name}.png'
        if model_name is not None:
            for item in gl.json_data['items']:
                if item['name'] == model_name:
                    if item['type'] == "TextualInversion":
                        filename = f'{name}_{i}.preview.png'
                        filenamethumb = f'{name}.preview.png'
        HTML = HTML.replace(img_url,f'{filename}')
        img_url = urllib.parse.quote(img_url,  safe=':/=')
        try:
            with urllib.request.urlopen(img_url) as url:
                with open(os.path.join(install_path, filename), 'wb') as f:
                    f.write(url.read())
                    if i == 0 and not os.path.exists(os.path.join(install_path, filenamethumb)):
                        shutil.copy2(os.path.join(install_path, filename),os.path.join(install_path, filenamethumb))
                    print(f"{gl.print} Downloaded image {image_count}")
                    
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    match = re.search(r'(\s*)<div class="model-block">', preview_html)
    if match:
        indentation = match.group(1)
    else:
        indentation = ''
    css_link = f'<link rel="stylesheet" type="text/css" href="{css_path}">'
    head_section = f'{indentation}<head>{indentation}    {css_link}{indentation}</head>'
    
    HTML = head_section + HTML
    path_to_new_file = os.path.join(install_path, f'{name}.html')
    with open(path_to_new_file, 'wb') as f:
        f.write(HTML.encode('utf8'))
    path_to_new_file = os.path.join(install_path, f'{name}.civitai.info')
    with open(path_to_new_file, mode="w", encoding="utf-8") as f:
        json.dump(gl.json_info, f, indent=4, ensure_ascii=False)

def card_update(gr_components, model_name, list_versions, is_install):
    if gr_components:
        version_choices = gr_components['choices']
    else:
        print(f"{gl.print} Couldn't retrieve version, defaulting to installed")
        model_name += ".New"
        return model_name, None, None
    
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
            print(f"{gl.print} Failed to open {json_file}: {e}")
        
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
            print(f"{gl.print} Failed to open {json_file}: {e}")
    else:
        data = {'sha256': hash_value}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    return hash_value

def model_from_sent(model_name, content_type, click_first_item):
    model_name = re.sub(r'\.\d{3}$', '', model_name)
    content_type = re.sub(r'\.\d{3}$', '', content_type)
    content_mapping = {
        "txt2img_textual_inversion_cards_html": ['TextualInversion'],
        "txt2img_hypernetworks_cards_html": ['Hypernetwork'],
        "txt2img_checkpoints_cards_html": ['Checkpoint'],
        "txt2img_lora_cards_html": ['LORA', 'LoCon']
    }
    content_type = content_mapping.get(content_type, content_type)
    
    for content_type_item in content_type:
        folder = _api.contenttype_folder(content_type_item)
        for folder_path, _, files in os.walk(folder):
            for file in files:
                if file.startswith(model_name) and not file.endswith(".json"):
                    model_file = os.path.join(folder_path, file)
    
    
    modelID = get_models(model_file)
    gl.json_data = _api.api_to_data(content_type, "Newest", "AllTime", "Model name", None, None, None, f"civitai.com/models/{modelID}")
    if gl.json_data == "timeout":
        HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or the selected model could not be found.</div>'
        number = click_first_item
    if gl.json_data != None and gl.json_data != "timeout":
        model_dict = {}
        for item in gl.json_data['items']:
            model_dict[item['name']] = item['name']
        HTML = _api.model_list_html(gl.json_data, model_dict)
        (hasPrev, hasNext, current_page, total_pages) = _api.pagecontrol(gl.json_data)
        page_string = f"Page: {current_page}/{total_pages}"
        number = _download.random_number(click_first_item)
    else:
        hasPrev = False
        hasNext = False
        page_string = "Page: 0/0"
        current_page = 0
        total_pages = 0
        
    return (
        gr.HTML.update(HTML), # Card HTML
        gr.Button.update(interactive=hasPrev), # Prev Button
        gr.Button.update(interactive=hasNext), # Next Button 
        gr.Slider.update(value=current_page, maximum=total_pages, label=page_string), # Page Slider
        gr.Textbox.update(number) # Click first card trigger 
    )
    
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    parsed = urlparse(url)
    path = parsed.path
    return any(path.endswith(ext) for ext in image_extensions)

def clean_description(desc):
    soup = BeautifulSoup(desc, 'html.parser')
    for a in soup.find_all('a', href=True):
        link_text = a.text + ' ' + a['href']
        if not is_image_url(a['href']):
            a.replace_with(link_text)

    cleaned_text = soup.get_text()
    return cleaned_text

def save_model_info(install_path, file_name, sha256=None, overwrite_toggle=False, api_response=None):
    file_path = os.path.join(install_path, file_name)
    json_file = os.path.splitext(file_path)[0] + ".json"
    
    if not sha256:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'sha256' in data:
                        sha256 = data['sha256'].upper()
            except Exception as e:
                print(f"{gl.print} Failed to open {json_file}: {e}")
    
    if not api_response:
        api_response = gl.json_data

    result = find_and_save(api_response, sha256, file_name, json_file, False, overwrite_toggle)
    if result == "found":
        return
    else:
        result = find_and_save(api_response, sha256, file_name, json_file, True, overwrite_toggle)
    
def find_and_save(api_response, sha256, file_name, json_file, no_hash, overwrite_toggle):
    for item in api_response.get('items', []):
        for model_version in item.get('modelVersions', []):
            for file in model_version.get('files', []):
                file_name_api = file.get('name', '')
                sha256_api = file.get('hashes', {}).get('SHA256', '')
                
                if file_name == file_name_api if no_hash else sha256 == sha256_api:
                    trained_words = model_version.get('trainedWords', [])
                    model_id = model_version.get('modelId', '')
                    
                    if model_id:
                        model_url = f'Model URL: \"https://civitai.com/models/{model_id}\"\n'
                    
                    description = item.get('description', '')
                    if description != None:
                        description = clean_description(description)
                        description = model_url + description
                    
                    base_model = model_version.get('baseModel', '')
                    
                    if base_model.startswith("SD 1"):
                        base_model = "SD1"
                    elif base_model.startswith("SD 2"):
                        base_model = "SD2"
                    elif base_model.startswith("SDXL"):
                        base_model = "SDXL"
                    else:
                        base_model = "Other"
                    
                    if isinstance(trained_words, list):
                        trained_tags = ",".join(trained_words)
                        trained_tags = re.sub(r'<[^>]*:[^>]*>', '', trained_tags)
                        trained_tags = re.sub(r', ?', ', ', trained_tags)
                        trained_tags = trained_tags.strip(', ')
                    else:
                        trained_tags = trained_words
                    
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            try:
                                content = json.load(f)
                            except:
                                content = {}
                    else:
                        content = {}
                    changed = False
                    if not overwrite_toggle:
                        if "activation text" not in content or not content["activation text"]:
                            content["activation text"] = trained_tags
                            changed = True
                        if "description" not in content or not content["description"]:
                            content["description"] = description
                            changed = True
                        if "sd version" not in content or not content["sd version"]:
                            content["sd version"] = base_model
                            changed = True
                    else:
                        content["activation text"] = trained_tags
                        content["description"] = description
                        content["sd version"] = base_model
                        changed = True
                    
                    with open(json_file, 'w') as f:
                        json.dump(content, f, indent=4)
                        
                    if changed: print(f"{gl.print} Model info saved to \"{json_file}\"")
                    return "found"
    
    return "not found"

def get_models(file_path):
    modelId = None
    sha256 = None
    json_file = os.path.splitext(file_path)[0] + ".json"
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                if 'modelId' in data:
                    modelId = data['modelId']
                if 'sha256' in data:
                    sha256 = data['sha256']
        except Exception as e:
            print(f"{gl.print} Failed to open {json_file}: {e}")
    
    if not modelId or not sha256:
        sha256 = gen_sha256(file_path)
        by_hash = f"https://civitai.com/api/v1/model-versions/by-hash/{sha256}"
    
    try:
        if not modelId:
            response = requests.get(by_hash, timeout=(10,30))
            if response.status_code == 200:
                api_response = response.json()
                modelId = api_response.get("modelId", "")
        if not modelId or not sha256:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    if 'modelId' not in data:
                        data['modelId'] = modelId
                    if 'sha256' not in data:
                        data['sha256'] = sha256.upper()
                        
                    with open(json_file, 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    print(f"{gl.print} Failed to open {json_file}: {e}")
            else:
                data = {
                    'modelId': modelId,
                    'sha256': sha256.upper()
                    }
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=4)
        
        return modelId
    except requests.exceptions.Timeout:
        print(f"{gl.print} Request timed out for {file_path}. Skipping...")
    except Exception as e:
        print(f"{gl.print} An error occurred for {file_path}: {str(e)}")

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
                    print(f"{gl.print} Failed to open {json_path}: {e}")
        
    file_names_and_hashes = set()
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        file_sha256 = sha256_hashes.get(file_name, "").upper()
        file_names_and_hashes.add((file_name_without_ext, file_sha256))
    
    for item in api_response.get('items', []):
        model_versions = item.get('modelVersions', [])
        
        if not model_versions:
            continue
        
        for idx, model_version in enumerate(model_versions):
            files = model_version.get('files', [])
            match_found = False
            for file_entry in files:
                entry_name = os.path.splitext(file_entry.get('name', ''))[0]
                entry_sha256 = file_entry.get('hashes', {}).get('SHA256', "").upper()
                
                if (entry_name, entry_sha256) in file_names_and_hashes:
                    match_found = True
                    break
            
            if match_found:
                if idx == 0:
                    updated_models.append((f"&ids={item['id']}", item["name"]))
                else:
                    outdated_models.append((f"&ids={item['id']}", item["name"]))
                break
                
    return updated_models, outdated_models

def get_content_choices(scan_choices=False):
    use_LORA = getattr(opts, "use_LORA", False)
    if use_LORA:
        content_list = ["Checkpoint", "TextualInversion", "LORA & LoCon", "Poses", "Controlnet", "Hypernetwork", "AestheticGradient", "VAE", "Upscaler", "MotionModule", "Wildcards", "Workflows", "Other"]
    else:
        content_list = ["Checkpoint", "TextualInversion", "LORA", "LoCon", "Poses", "Controlnet", "Hypernetwork", "AestheticGradient", "VAE", "Upscaler", "MotionModule", "Wildcards", "Workflows", "Other"]
    if scan_choices:
        content_list.insert(0, 'All')
        return content_list
    return content_list
    
def file_scan(folders, ver_finish, tag_finish, installed_finish, preview_finish, overwrite_toggle, progress=gr.Progress() if queue else None):
    global from_ver, from_installed, no_update
    update_log = getattr(opts, "update_log", True)
    gl.scan_files = True
    no_update = False
    if from_ver:
        number = _download.random_number(ver_finish)
    elif from_tag:
        number = _download.random_number(tag_finish)
    elif from_installed:
        number = _download.random_number(installed_finish)
    elif from_preview:
        number = _download.random_number(preview_finish)
    
    if not folders:
        if progress != None:
            progress(0, desc=f"No folder selected.")
        no_update = True
        gl.scan_files = False
        from_ver, from_installed = False, False
        time.sleep(2)
        return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number))
    
    folders_to_check = []
    if 'All' in folders:
        folders = _file.get_content_choices()
        
    for item in folders:
        if item == "LORA & LoCon":
            folder = _api.contenttype_folder("LORA")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder("LoCon", fromCheck=True)
            if folder:
                folders_to_check.append(folder)
        elif item == "Upscaler":
            folder = _api.contenttype_folder(item, "SwinIR")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "RealESRGAN")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "GFPGAN")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "BSRGAN")
            if folder:
                folders_to_check.append(folder)
            folder = _api.contenttype_folder(item, "ESRGAN")
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
        if progress != None:
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
            if progress != None:
                progress(files_done / total_files, desc=f"Saving tags cancelled.")
            no_update = True
            gl.scan_files = False
            from_ver, from_installed = False, False
            time.sleep(2)
            return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                    gr.Textbox.update(value=number))
        file_name = os.path.basename(file_path)
        if progress != None:
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

        url_count = len(all_model_ids) // 100
        if len(all_model_ids) % 100 != 0:
            url_count += 1
        url_done = 0
        for url in url_list:
            while url:
                if progress != None:
                    progress(url_done / url_count, desc=f"Sending API request... {url_done}/{url_count}")
                response = requests.get(url, timeout=(10,30))
                if response.status_code == 200:
                    api_response = response.json()

                    all_items.extend(api_response['items'])
                    metadata = api_response.get('metadata', {})
                    url = metadata.get('nextPage', None)
                else:
                    print(f"{gl.print} Error: Received status code {response.status_code} with URL:")
                    print(url)
                url_done += 1
                
        api_response['items'] = all_items
        
    if progress != None:
        progress(1, desc="Processing final results...")
    
    if from_ver:
        updated_models, outdated_models = version_match(file_paths, api_response)
        
        updated_set = set(updated_models)
        outdated_set = set(outdated_models)
        outdated_set = {model for model in outdated_set if model[0] not in {updated_model[0] for updated_model in updated_set}}
        
        all_model_ids = [model[0] for model in outdated_set]
        all_model_names = [model[1] for model in outdated_set]
        
        if update_log:
            for model_name in all_model_names:
                print(f'{gl.print} "{model_name}" is currently outdated.')
        
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

    elif from_installed:
        gl.scan_files = False
        return  (
                gr.HTML.update(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Installed models have been loaded.<br>Please press the button above to load the models into the browser tab</div>'),
                gr.Textbox.update(value=number)
            )

    elif from_tag:
        for file in file_paths:
            install_path, file_name = os.path.split(file)
            save_model_info(install_path, file_name, api_response=api_response, overwrite_toggle=overwrite_toggle)
        if progress != None:
            progress(1, desc=f"All tags succesfully saved!")
        time.sleep(2)
        return  (
                gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number)
            )
    
    elif from_preview:
        completed_preview = 0
        preview_count = len(file_paths)
        for file in file_paths:
            _, file_name = os.path.split(file)
            name = os.path.splitext(file_name)[0]
            if progress != None:
                progress(completed_preview / preview_count, desc=f"Saving preview images... {completed_preview}/{preview_count} | {name}")
            save_preview(file, api_response, overwrite_toggle)
            completed_preview += 1
        return  (
                gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number)
            )
    
def save_tag_start(tag_start):
    global from_tag, from_ver, from_installed, from_preview
    from_tag, from_ver, from_installed, from_preview = True, False, False, False
    number = _download.random_number(tag_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
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
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False)
    )
    
def save_preview_start(preview_start):
    global from_tag, from_ver, from_installed, from_preview
    from_preview, from_tag, from_ver, from_installed = True, False, False, False
    number = _download.random_number(preview_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )

def save_preview_finish():
    global from_preview
    from_preview = False
    return (
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False)
    )
    
def start_ver_search(ver_start):
    global from_ver, from_tag, from_installed, from_preview
    from_ver, from_tag, from_installed, from_preview = True, False, False, False
    number = _download.random_number(ver_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )

def finish_ver_search():
    return (
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False if no_update else True, visible=False if no_update else True)
    )

def start_installed_models(installed_start):
    global from_installed, from_ver, from_tag, from_preview
    from_installed, from_ver, from_tag, from_preview = True, False, False, False
    number = _download.random_number(installed_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.Button.update(interactive=False, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )
    
def finish_installed_models():
    return (
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=True if no_update else False, visible=True if no_update else False),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False if no_update else True, visible=False if no_update else True)
    )

def load_to_browser():
    global from_ver, from_installed
    if from_ver:
        model_list_return = _api.update_model_list(from_ver=True)
    if from_installed:
        model_list_return = _api.update_model_list(from_installed=True)
    
    gl.file_scan = True
    from_ver, from_installed = False, False
    return (
        *model_list_return,
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=False, visible=False),
        gr.HTML.update(value='<div style="min-height: 0px;"></div>')
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