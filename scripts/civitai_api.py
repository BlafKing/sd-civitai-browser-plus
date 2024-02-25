import requests
import json
import gradio as gr
import urllib.request
import urllib.parse
import urllib.error
import os
import re
import datetime
import platform
import time
from PIL import Image
from io import BytesIO
from collections import defaultdict
from modules.images import read_info_from_image
try:
    from modules.generation_parameters_copypaste import parse_generation_parameters
except:
    from modules.infotext_utils import parse_generation_parameters

from modules.shared import cmd_opts, opts
from modules.paths import models_path, extensions_dir, data_path
from html import escape
from scripts.civitai_global import print
import scripts.civitai_global as gl
import scripts.civitai_download as _download
try:
    from fake_useragent import UserAgent
except ImportError:
    print("Python module 'fake_useragent' has not been imported correctly, please try to restart or install it manually.")

gl.init()

def contenttype_folder(content_type, desc=None, fromCheck=False, custom_folder=None):
    use_LORA = getattr(opts, "use_LORA", False)
    folder = None
    if desc:
        desc = desc.upper()
    else:
        desc = "PLACEHOLDER"
    if custom_folder:
        main_models = custom_folder
        main_data = custom_folder
    else:
        main_models = models_path
        main_data = data_path
        
    if content_type == "modelFolder":
        folder = os.path.join(main_models)
        
    if content_type == "Checkpoint":
        if cmd_opts.ckpt_dir and not custom_folder:
            folder = cmd_opts.ckpt_dir
        else:
            folder = os.path.join(main_models,"Stable-diffusion")
            
    elif content_type == "Hypernetwork":
        if cmd_opts.hypernetwork_dir and not custom_folder:
            folder = cmd_opts.hypernetwork_dir
        else:
            folder = os.path.join(main_models, "hypernetworks")
        
    elif content_type == "TextualInversion":
        if cmd_opts.embeddings_dir and not custom_folder:
            folder = cmd_opts.embeddings_dir
        else:
            folder = os.path.join(main_data, "embeddings")
        
    elif content_type == "AestheticGradient":
        if not custom_folder:
            folder = os.path.join(extensions_dir, "stable-diffusion-webui-aesthetic-gradients", "aesthetic_embeddings")
        else:
            folder = os.path.join(custom_folder, "aesthetic_embeddings")
    elif content_type == "LORA":
        if cmd_opts.lora_dir and not custom_folder:
            folder = cmd_opts.lora_dir
        else:
            folder = folder = os.path.join(main_models, "Lora")
        
    elif content_type == "LoCon":
        folder = os.path.join(main_models, "LyCORIS")
        if use_LORA and not fromCheck:
            if cmd_opts.lora_dir and not custom_folder:
                folder = cmd_opts.lora_dir
            else:
                folder = folder = os.path.join(main_models, "Lora")
            
    elif content_type == "VAE":
        if cmd_opts.vae_dir and not custom_folder:
            folder = cmd_opts.vae_dir
        else:
            folder = os.path.join(main_models, "VAE")
            
    elif content_type == "Controlnet":  
        folder = os.path.join(main_models, "ControlNet")
            
    elif content_type == "Poses":
        folder = os.path.join(main_models, "Poses")
    
    elif content_type == "Upscaler":
        if "SWINIR" in desc:
            if cmd_opts.swinir_models_path and not custom_folder:
                folder = cmd_opts.swinir_models_path
            else:
                folder = os.path.join(main_models, "SwinIR")
        elif "REALESRGAN" in desc:
            if cmd_opts.realesrgan_models_path and not custom_folder:
                folder = cmd_opts.realesrgan_models_path
            else:
                folder = os.path.join(main_models, "RealESRGAN")
        elif "GFPGAN" in desc:
            if cmd_opts.gfpgan_models_path and not custom_folder:
                folder = cmd_opts.gfpgan_models_path
            else:
                folder = os.path.join(main_models, "GFPGAN")
        elif "BSRGAN" in desc:
            if cmd_opts.bsrgan_models_path and not custom_folder:
                folder = cmd_opts.bsrgan_models_path
            else:
                folder = os.path.join(main_models, "BSRGAN")
        else:
            if cmd_opts.esrgan_models_path and not custom_folder:
                folder = cmd_opts.esrgan_models_path
            else:
                folder = os.path.join(main_models, "ESRGAN")
            
    elif content_type == "MotionModule":
        folder = os.path.join(extensions_dir, "sd-webui-animatediff", "model")
        
    elif content_type == "Workflows":
        folder = os.path.join(main_models, "Workflows")
        
    elif content_type == "Other":
        if "ADETAILER" in desc:
            folder = os.path.join(main_models, "adetailer")
        else:
            folder = os.path.join(main_models, "Other")
    
    elif content_type == "Wildcards":
        folder = os.path.join(extensions_dir, "UnivAICharGen", "wildcards")
        if not os.path.exists(folder):
            folder = os.path.join(extensions_dir, "sd-dynamic-prompts", "wildcards")
    
    return folder

def api_to_data(content_type, sort_type, period_type, use_search_term, current_page, base_filter, only_liked, tile_count, search_term=None, nsfw=None, timeOut=None, isNext=None, inputs_changed=None):
    if current_page in [0, None, ""]:
        current_page = 1
    if inputs_changed:
        gl.file_scan = False
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page=1"
    else:
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page={current_page}"
    
    if timeOut:
        if isNext:
            next_page = str(int(current_page) + 1)
        else:
            if current_page not in [1, 0, None, ""]:
                next_page = str(int(current_page) - 1)
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page={next_page}"
    
    if period_type:
        period_type = period_type.replace(" ", "")
    query = {'sort': sort_type, 'period': period_type}
    
    types_query_str = ""
    
    if content_type:
        types_query_str = "".join([f"&types={type}" for type in content_type])
    
    query_str = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
    
    if types_query_str:
        query_str += types_query_str

    if use_search_term != "None" and search_term:
        search_term = search_term.replace("\\","\\\\")
        if "civitai.com" in search_term:
            match = re.search(r'models/(\d+)', search_term)
            model_number = match.group(1)
            query_str = f"&ids={urllib.parse.quote(model_number)}"
        elif use_search_term == "User name":
            query_str += f"&username={urllib.parse.quote(search_term)}"
        elif use_search_term == "Tag":
            query_str += f"&tag={urllib.parse.quote(search_term)}"
        else:
            query_str += f"&query={urllib.parse.quote(search_term)}"
            
    if base_filter:
        for base in base_filter:
            query_str += f"&baseModels={urllib.parse.quote(base)}"
    
    if only_liked:
        query_str += f"&favorites=true"
    
    if nsfw == False:
        query_str += f"&nsfw=false"
    
    full_url = f"{api_url}&{query_str}"
    
    if gl.file_scan:
        highest_number = max(gl.url_list_with_numbers.keys())
        full_url = gl.url_list_with_numbers.get(int(current_page))
        nextPage = int(current_page) + 1
        prevPage = int(current_page) - 1
        data = request_civit_api(full_url)
        data["metadata"]["currentPage"] = current_page
        data["metadata"]["totalPages"] = highest_number
        if not nextPage > highest_number:
            data["metadata"]["nextPage"] = gl.url_list_with_numbers.get(nextPage)
        if not prevPage == 0:
            data["metadata"]["prevPage"] = gl.url_list_with_numbers.get(prevPage)
    else:
        data = request_civit_api(full_url)
        
    return data

def model_list_html(json_data):
    video_playback = getattr(opts, "video_playback", True)
    playback = ""
    if video_playback: playback = "autoplay loop"
    
    hide_early_access = getattr(opts, "hide_early_access", True)
    filtered_items = []
    current_time = datetime.datetime.utcnow()
    
    for item in json_data['items']:
        versions_to_keep = []

        for version in item['modelVersions']:
            if not version['files']:
                continue
            if hide_early_access:
                early_access_days = version['earlyAccessTimeFrame']
                if early_access_days != 0:
                    published_at_str = version.get('publishedAt')
                    if published_at_str is not None:
                        published_at = datetime.datetime.strptime(version['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        adjusted_date = published_at + datetime.timedelta(days=early_access_days)
                    if not current_time > adjusted_date or not published_at_str:
                        continue
            versions_to_keep.append(version)

        if versions_to_keep:
            item['modelVersions'] = versions_to_keep
            filtered_items.append(item)
            
        json_data['items'] = filtered_items
    
    HTML = '<div class="column civmodellist">'
    sorted_models = {}
    existing_files = set()
    existing_files_sha256 = set()
    model_folders = set()
    
    for item in json_data['items']:
        model_folder = os.path.join(contenttype_folder(item['type'], item['description']))
        model_folders.add(model_folder)
    
    for folder in model_folders:
        for root, dirs, files in os.walk(folder, followlinks=True):
            for file in files:
                existing_files.add(file)
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    with open(json_path, 'r', encoding="utf-8") as f:
                        try:
                            json_file = json.load(f)
                            if isinstance(json_file, dict):
                                sha256 = json_file.get('sha256')
                                if sha256:
                                    existing_files_sha256.add(sha256.upper())
                            else:
                                print(f"Invalid JSON data in {json_path}. Expected a dictionary.")
                        except Exception as e:
                            print(f"Error decoding JSON in {json_path}: {e}")
    
    for item in json_data['items']:
        model_id = item.get('id')
        model_name = item.get('name')
        nsfw = ""
        installstatus = ""
        baseModel = ""
        try:
            if 'baseModel' in item['modelVersions'][0]:
                baseModel = item['modelVersions'][0]['baseModel']
        except:
            baseModel = "Not Found"
        
        try:
            if 'updatedAt' in item['modelVersions'][0]:
                date = item['modelVersions'][0]['updatedAt'].split('T')[0]
        except:
            baseModel = "Not Found"
            
        if gl.sortNewest:
            if date not in sorted_models:
                sorted_models[date] = []
        
        if any(item['modelVersions']):
            if len(item['modelVersions'][0]['images']) > 0:
                if item["modelVersions"][0]["images"][0]['nsfw'] not in ["None", "Soft"]:
                    nsfw = "civcardnsfw"
                media_type = item["modelVersions"][0]["images"][0]["type"]
                image = item["modelVersions"][0]["images"][0]["url"]
                if media_type == "video":
                    image = image.replace("width=", "transcode=true,width=")
                    imgtag = f'<video class="video-bg" {playback} muted playsinline><source src="{image}" type="video/mp4"></video>'
                else:
                    imgtag = f'<img src="{image}"></img>'
            else:
                imgtag = f'<img src="./file=html/card-no-preview.png"></img>'
            
            installstatus = None
            
            for version in reversed(item['modelVersions']):
                for file in version.get('files', []):
                    file_name = file['name']
                    file_sha256 = file.get('hashes', {}).get('SHA256', "").upper()
                    
                    name_match = file_name in existing_files
                    sha256_match = file_sha256 in existing_files_sha256
                    if name_match or sha256_match:
                        if version == item['modelVersions'][0]:
                            installstatus = "civmodelcardinstalled"
                        else:
                            installstatus = "civmodelcardoutdated"
            model_name_js = model_name.replace("'", "\\'")
            model_string = escape(f"{model_name_js} ({model_id})")
            model_card = f'<figure class="civmodelcard {nsfw} {installstatus}" base-model="{baseModel}" date="{date}" onclick="select_model(\'{model_string}\', event)">'
            if installstatus != "civmodelcardinstalled":
                model_card += f'<input type="checkbox" class="model-checkbox" id="checkbox-{model_string}" onchange="multi_model_select(\'{model_string}\', \'{item["type"]}\', this.checked)" style="opacity: 0; position: absolute; top: 10px; right: 10px;">' \
                            + f'<label for="checkbox-{model_string}" class="custom-checkbox"></label>'
            if len(item["name"]) > 40:
                display_name = item["name"][:40] + '...'
            else:
                display_name = item["name"]
            
            display_name = escape(display_name)
            full_name = escape(item['name'])
            model_card += imgtag \
                        + f'<figcaption title="{full_name}">{display_name}</figcaption></figure>'
        
        if gl.sortNewest:
            sorted_models[date].append(model_card)
        else:
            HTML += model_card
    
    if gl.sortNewest:
        for date, cards in sorted(sorted_models.items(), reverse=True):
            HTML += f'<div class="date-section"><h4>{date}</h4><hr style="margin-bottom: 5px; margin-top: 5px;">'
            HTML += '<div class="card-row">'
            for card in cards:
                HTML += card
            HTML += '</div></div>'
            
    HTML += '</div>'
    return HTML

def update_prev_page(content_type, sort_type, period_type, use_search_term, search_term, current_page, base_filter, only_liked, nsfw, tile_count):
    return update_next_page(content_type, sort_type, period_type, use_search_term, search_term, current_page, base_filter, only_liked, nsfw, tile_count, isNext=False)

def update_next_page(content_type, sort_type, period_type, use_search_term, search_term, current_page, base_filter, only_liked, nsfw, tile_count, isNext=True):
    use_LORA = getattr(opts, "use_LORA", False)
    
    if content_type:
        if use_LORA and 'LORA & LoCon' in content_type:
            content_type.remove('LORA & LoCon')
            if 'LORA' not in content_type:
                content_type.append('LORA')
            if 'LoCon' not in content_type:
                content_type.append('LoCon')
            
    if gl.json_data is None or gl.json_data == "timeout":
        timeOut = True
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, current_page, base_filter, only_liked, nsfw, timeOut=timeOut, isNext=isNext)
        timeOut = False
        
        return return_values
    
    current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, tile_count, base_filter, nsfw)
    if current_inputs != gl.previous_inputs and gl.previous_inputs != None:
        inputs_changed = True
    else:
        inputs_changed = False

    if inputs_changed:
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, current_page, base_filter, only_liked, nsfw, tile_count)
        return return_values

    if not gl.file_scan:
        if isNext:
            if gl.json_data['metadata']['nextPage'] is not None:
                gl.json_data = request_civit_api(gl.json_data['metadata']['nextPage'])
            else:
                gl.json_data = None
        else:
            if gl.json_data['metadata']['prevPage'] is not None:
                gl.json_data = request_civit_api(gl.json_data['metadata']['prevPage'])
            else:
                gl.json_data = None
    else:
        highest_number = max(gl.url_list_with_numbers.keys())
        if isNext:
            if gl.json_data['metadata']['nextPage'] is not None:
                currentPage = int(gl.json_data['metadata']['currentPage'])
                nextPage = currentPage + 2
                prevPage = currentPage
                pageCount = currentPage + 1
                gl.json_data = request_civit_api(gl.json_data['metadata']['nextPage'])
                
                gl.json_data["metadata"]["totalPages"] = highest_number
                if not nextPage > highest_number:
                    gl.json_data["metadata"]["nextPage"] = gl.url_list_with_numbers.get(nextPage)
                if not prevPage == 0:
                    gl.json_data["metadata"]["prevPage"] = gl.url_list_with_numbers.get(prevPage)
                gl.json_data["metadata"]["currentPage"] = pageCount
            else:
                gl.json_data = None
        else:
            if gl.json_data['metadata']['prevPage'] is not None:
                currentPage = int(gl.json_data['metadata']['currentPage'])
                nextPage = currentPage
                prevPage = currentPage - 2
                pageCount = currentPage - 1
                gl.json_data = request_civit_api(gl.json_data['metadata']['prevPage'])
                
                gl.json_data["metadata"]["totalPages"] = highest_number
                if not nextPage > highest_number:
                    gl.json_data["metadata"]["nextPage"] = gl.url_list_with_numbers.get(nextPage)
                if not prevPage == 0:
                    gl.json_data["metadata"]["prevPage"] = gl.url_list_with_numbers.get(prevPage)
                gl.json_data["metadata"]["currentPage"] = pageCount
            else:
                gl.json_data = None
                
    if gl.json_data is None:
        return
    
    if gl.json_data == "timeout":
        HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
        hasPrev = current_page not in [0, 1]
        hasNext = current_page == 1 or hasPrev
        model_dict = {}
        
    if gl.json_data != None and gl.json_data != "timeout":
        (hasPrev, hasNext, current_page, total_pages) = pagecontrol(gl.json_data)
        model_dict = {}
        try:
            gl.json_data['items']
        except TypeError:
            return gr.Dropdown.update(choices=[], value=None)
        
        HTML = model_list_html(gl.json_data)

    page_string = f"Page: {current_page}/{total_pages}"
    
    return  (
            gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value="", interactive=True), # Model List
            gr.Dropdown.update(choices=[], value=""), # Version List
            gr.HTML.update(value=HTML), # HTML Tiles
            gr.Button.update(interactive=hasPrev), # Prev Page Button
            gr.Button.update(interactive=hasNext), # Next Page Button
            gr.Slider.update(value=current_page, maximum=total_pages, label=page_string), # Page Count
            gr.Button.update(interactive=False), # Save Tags
            gr.Button.update(interactive=False), # Save Images
            gr.Button.update(interactive=False, visible=False if gl.isDownloading else True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Delete Button
            gr.Textbox.update(interactive=False, value=None), # Install Path
            gr.Dropdown.update(choices=[], value="", interactive=False), # Sub Folder List
            gr.Dropdown.update(choices=[], value="", interactive=False), # File List
            gr.HTML.update(value='<div style="min-height: 0px;"></div>'), # Preview HTML
            gr.Textbox.update(value=None), # Trained Tags
            gr.Textbox.update(value=None), # Base Model
            gr.Textbox.update(value=None) # Model Filename
    )

def pagecontrol(json_data):
    current_page = f"{json_data['metadata']['currentPage']}"
    total_pages = f"{json_data['metadata']['totalPages']}"
    hasNext = False
    hasPrev = False
    if 'nextPage' in json_data['metadata']:
        hasNext = True
    if 'prevPage' in json_data['metadata']:
        hasPrev = True
    return hasPrev, hasNext, current_page, total_pages

def update_model_list(content_type=None, sort_type=None, period_type=None, use_search_term=None, search_term=None, current_page=None, base_filter=None, only_liked=None, nsfw=None, tile_count=None, timeOut=None, isNext=None, from_ver=False, from_installed=False):
    use_LORA = getattr(opts, "use_LORA", False)
    model_list = []
    id_list = []
    
    if content_type:
        if use_LORA and 'LORA & LoCon' in content_type:
            content_type.remove('LORA & LoCon')
            if 'LORA' not in content_type:
                content_type.append('LORA')
            if 'LoCon' not in content_type:
                content_type.append('LoCon')
            
    if not from_ver and not from_installed:
        gl.ver_json = None
        
        current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, tile_count, base_filter, nsfw)
        if current_inputs != gl.previous_inputs and gl.previous_inputs != None:
            inputs_changed = True
        else:
            inputs_changed = False
        
        gl.previous_inputs = current_inputs
        
        gl.json_data = api_to_data(content_type, sort_type, period_type, use_search_term, current_page, base_filter, only_liked, tile_count, search_term, nsfw, timeOut, isNext, inputs_changed)
        if gl.json_data == "timeout":
            HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
            hasPrev = current_page not in [0, 1]
            hasNext = current_page == 1 or hasPrev
        
        if gl.json_data is None:
            return
    
    if from_installed or from_ver:
        gl.json_data = gl.ver_json
    
    if gl.json_data != None and gl.json_data != "timeout":
        if not from_ver:
            (hasPrev, hasNext, current_page, total_pages) = pagecontrol(gl.json_data)
        else:
            current_page = 1
            total_pages = 1
            hasPrev = False
            hasNext = False
        for item in gl.json_data['items']:
            model_list.append(f"{item['name']} ({item['id']})")
        
        HTML = model_list_html(gl.json_data)
    else:
        current_page = 1
        total_pages = 1
    
    page_string = f"Page: {current_page}/{total_pages}"
    
    return  (
            gr.Dropdown.update(choices=model_list, value="", interactive=True), # Model List
            gr.Dropdown.update(choices=[], value=""), # Version List
            gr.HTML.update(value=HTML), # HTML Tiles
            gr.Button.update(interactive=hasPrev), # Prev Page Button
            gr.Button.update(interactive=hasNext), # Next Page Button
            gr.Slider.update(value=current_page, maximum=total_pages, label=page_string), # Page Count
            gr.Button.update(interactive=False), # Save Tags
            gr.Button.update(interactive=False), # Save Images
            gr.Button.update(interactive=False, visible=False if gl.isDownloading else True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Delete Button
            gr.Textbox.update(interactive=False, value=None, visible=True), # Install Path
            gr.Dropdown.update(choices=[], value="", interactive=False), # Sub Folder List
            gr.Dropdown.update(choices=[], value="", interactive=False), # File List
            gr.HTML.update(value='<div style="min-height: 0px;"></div>'), # Preview HTML
            gr.Textbox.update(value=None), # Trained Tags
            gr.Textbox.update(value=None), # Base Model
            gr.Textbox.update(value=None) # Model Filename
    )

def update_model_versions(model_id, json_input=None):
    if json_input:
        api_json = json_input
    else:
        api_json = gl.json_data
    for item in api_json['items']:
        if int(item['id']) == int(model_id):
            content_type = item['type']
            desc = item.get('description', "None")
            
            versions_dict = defaultdict(list)
            installed_versions = set()

            model_folder = os.path.join(contenttype_folder(content_type, desc))
            gl.main_folder = model_folder
            versions = item['modelVersions']
            
            version_files = set()
            for version in versions:
                versions_dict[version['name']].append(item["name"])
                for version_file in version['files']:
                    file_sha256 = version_file.get('hashes', {}).get('SHA256', "").upper()
                    version_filename = version_file['name']
                    version_files.add((version['name'], version_filename, file_sha256))

            for root, _, files in os.walk(model_folder, followlinks=True):
                for file in files:
                    if file.endswith('.json'):
                        try:
                            json_path = os.path.join(root, file)
                            with open(json_path, 'r', encoding="utf-8") as f:
                                json_data = json.load(f)
                                if isinstance(json_data, dict):
                                    if 'sha256' in json_data and json_data['sha256']:
                                        sha256 = json_data.get('sha256', "").upper()
                                        for version_name, _, file_sha256 in version_files:
                                            if sha256 == file_sha256:
                                                installed_versions.add(version_name)
                                                break
                        except Exception as e:
                            print(f"failed to read: \"{file}\": {e}")

                    for version_name, version_filename, _ in version_files:
                        if file == version_filename:
                            installed_versions.add(version_name)
                            break

            version_names = list(versions_dict.keys())
            display_version_names = [f"{v} [Installed]" if v in installed_versions else v for v in version_names]
            default_installed = next((f"{v} [Installed]" for v in installed_versions), None)
            default_value = default_installed or next(iter(version_names), None)
            
            return gr.Dropdown.update(choices=display_version_names, value=default_value, interactive=True) # Version List
    
    return gr.Dropdown.update(choices=[], value=None, interactive=False) # Version List

def cleaned_name(file_name):
    if platform.system() == "Windows":
        illegal_chars_pattern = r'[\\/:*?"<>|]'
    else:
        illegal_chars_pattern = r'/'

    name, extension = os.path.splitext(file_name)
    clean_name = re.sub(illegal_chars_pattern, '', name)

    return f"{clean_name}{extension}"

def fetch_and_process_image(image_url):
    try:
        parsed_url = urllib.parse.urlparse(image_url)
        if parsed_url.scheme and parsed_url.netloc:
            response = requests.get(image_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                geninfo, _ = read_info_from_image(image)
                return geninfo
        else:
            image = Image.open(image_url)
            geninfo, _ = read_info_from_image(image)
            return geninfo
    except:
        return None

def image_url_to_promptInfo(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        
        prompt, _ = read_info_from_image(image)
        if prompt:
            prompt_dict = parse_generation_parameters(prompt)
            
            invalid_values = [None, 0, "", "Use same sampler", "Use same checkpoint"]
            keys_to_remove = [key for key, value in prompt_dict.items() if key != "Clip skip" and value in invalid_values]
            for key in keys_to_remove:
                prompt_dict.pop(key, None)
            
            if "Size-1" in prompt_dict and "Size-2" in prompt_dict:
                prompt_dict["Size"] = f'{prompt_dict["Size-1"]}x{prompt_dict["Size-2"]}'
                prompt_dict.pop("Size-1", None)
                prompt_dict.pop("Size-2", None)
            if "Hires resize-1" in prompt_dict and "Hires resize-2" in prompt_dict:
                prompt_dict["Hires resize"] = f'{prompt_dict["Hires resize-1"]}x{prompt_dict["Hires resize-2"]}'
                prompt_dict.pop("Hires resize-1", None)
                prompt_dict.pop("Hires resize-2", None)
            
            return prompt_dict
        else:
            return []
    return []

def extract_model_info(input_string):
    last_open_parenthesis = input_string.rfind("(")
    last_close_parenthesis = input_string.rfind(")")

    name = input_string[:last_open_parenthesis].strip()
    id_number = input_string[last_open_parenthesis + 1:last_close_parenthesis]

    return name, int(id_number)

def update_model_info(model_string=None, model_version=None, only_html=False, input_id=None, json_input=None, from_preview=False):
    video_playback = getattr(opts, "video_playback", True)
    meta_btn = getattr(opts, "individual_meta_btn", True)
    playback = ""
    if video_playback: playback = "autoplay loop"
    
    if json_input:
        api_data = json_input
    else:
        api_data = gl.json_data
    
    BtnDownInt = True
    BtnDel = False
    BtnImage = False
    model_id = None
    
    if not input_id:
        _, model_id = extract_model_info(model_string)
    else:
        model_id = input_id
    
    if model_version and "[Installed]" in model_version:
        model_version = model_version.replace(" [Installed]", "")
    if model_id:
        output_html = ""
        output_training = ""
        output_basemodel = ""
        img_html = ""
        dl_dict = {}
        is_LORA = False
        file_list = []
        file_dict = []
        default_file = None
        model_filename = None
        sha256_value = None
        for item in api_data['items']:
            if int(item['id']) == int(model_id):
                content_type = item['type']
                if content_type == "LORA":
                    is_LORA = True
                desc = item['description']
                model_name = item['name']
                model_folder = os.path.join(contenttype_folder(content_type, desc))
                model_uploader = item['creator']['username']
                uploader_avatar = item['creator']['image']
                if uploader_avatar is None:
                     uploader_avatar = ''
                else:
                    uploader_avatar = f'<div class="avatar"><img src={uploader_avatar}></div>'
                tags = item.get('tags', "")
                model_desc = item.get('description', "")
                if model_desc:
                    model_desc = model_desc.replace('<img', '<img style="max-width: -webkit-fill-available;"')
                    model_desc = model_desc.replace('<code>', '<code style="text-wrap: wrap">')
                if model_version is None:
                    selected_version = item['modelVersions'][0]
                else:
                    for model in item['modelVersions']:
                        if model['name'] == model_version:
                            selected_version = model
                            break
                    
                if selected_version['trainedWords']:
                    output_training = ",".join(selected_version['trainedWords'])
                    output_training = re.sub(r'<[^>]*:[^>]*>', '', output_training)
                    output_training = re.sub(r', ?', ', ', output_training)
                    output_training = output_training.strip(', ')
                if selected_version['baseModel']:
                    output_basemodel = selected_version['baseModel']
                for file in selected_version['files']:
                    dl_dict[file['name']] = file['downloadUrl']
                    
                    if not model_filename:
                        model_filename = file['name']
                        dl_url = file['downloadUrl']
                        gl.json_info = item
                        sha256_value = file['hashes'].get('SHA256', 'Unknown')
                        
                    size = file['metadata'].get('size', 'Unknown')
                    format = file['metadata'].get('format', 'Unknown')
                    fp = file['metadata'].get('fp', 'Unknown')
                    sizeKB = file.get('sizeKB', 0) * 1024
                    filesize = _download.convert_size(sizeKB)
                    
                    unique_file_name = f"{size} {format} {fp} ({filesize})"
                    is_primary = file.get('primary', False)
                    file_list.append(unique_file_name)
                    file_dict.append({
                        "format": format,
                        "sizeKB": sizeKB
                    })
                    if is_primary:
                        default_file = unique_file_name
                        model_filename = file['name']
                        dl_url = file['downloadUrl']
                        gl.json_info = item
                        sha256_value = file['hashes'].get('SHA256', 'Unknown')
                
                safe_tensor_found = False
                pickle_tensor_found = False
                if is_LORA and file_dict:
                    for file_info in file_dict:
                        file_format = file_info.get("format", "")
                        if "SafeTensor" in file_format:
                            safe_tensor_found = True
                        if "PickleTensor" in file_format:
                            pickle_tensor_found = True
                            
                    if safe_tensor_found and pickle_tensor_found:
                        if "PickleTensor" in file_dict[0].get("format", ""):
                            if file_dict[0].get("sizeKB", 0) <= 100:
                                model_folder = os.path.join(contenttype_folder("TextualInversion"))
                
                model_url = selected_version.get('downloadUrl', '')
                model_main_url = f"https://civitai.com/models/{item['id']}"
                img_html = '<div class="sampleimgs"><input type="radio" name="zoomRadio" id="resetZoom" class="zoom-radio" checked>'
                for index, pic in enumerate(selected_version['images']):
                    # Change width value in URL to original image width
                    image_url = re.sub(r'/width=\d+', f'/width={pic["width"]}', pic["url"])
                    if pic['type'] == "video":
                        image_url = image_url.replace("width=", "transcode=true,width=")
                        prompt_dict = []
                    else:
                        prompt_dict = image_url_to_promptInfo(image_url)
                        
                    nsfw = 'class="model-block"'
                    
                    meta_button = False
                    if prompt_dict and prompt_dict.get('Prompt'):
                        meta_button = True
                    BtnImage = True
                    
                    if pic['nsfw'] not in ["None", "Soft"]:
                        nsfw = 'class="civnsfw model-block"'

                    img_html += f'''
                    <div {nsfw} style="display:flex;align-items:flex-start;">
                    <div class="civitai-image-container">
                    <input type="radio" name="zoomRadio" id="zoomRadio{index}" class="zoom-radio">
                    <label for="zoomRadio{index}" class="zoom-img-container">
                    '''
                    
                    # Check if the pic is an image or video
                    if pic['type'] == "video":
                        img_html += f'<video data-sampleimg="true" {playback} muted playsinline><source src="{image_url}" type="video/mp4"></video>'
                        meta_button = False
                    else:
                        img_html += f'<img data-sampleimg="true" src="{image_url}">'

                    img_html += '''
                        </label>
                        <label for="resetZoom" class="zoom-overlay"></label>
                    '''
                    
                    if meta_button:
                        img_html += f'''
                            <div class="civitai_txt2img" style="margin-top:30px;margin-bottom:30px;">
                            <label onclick='sendImgUrl("{escape(image_url)}")' class="civitai-txt2img-btn" style="max-width:fit-content;cursor:pointer;">Send to txt2img</label>
                            </div></div>
                        '''
                    else:
                        img_html += '</div>'
                        
                    if prompt_dict:
                        img_html += '<div style="margin:1em 0em 1em 1em;text-align:left;line-height:1.5em;" id="image_info"><dl style="gap:10px; display:grid;">'
                        # Define the preferred order of keys and convert them to lowercase
                        preferred_order = ["Prompt", "Negative prompt", "Seed", "Size", "Model", "Clip skip", "Sampler", "Steps", "CFG scale"]
                        # Loop through the keys in the preferred order and add them to the HTML
                        for key in preferred_order:
                            if key in prompt_dict:
                                value = prompt_dict[key]
                                if meta_btn:
                                    img_html += f'<div class="civitai-meta-btn" onclick="metaToTxt2Img(\'{escape(str(key))}\', this)"><dt>{escape(str(key).capitalize())}</dt><dd>{escape(str(value))}</dd></div>'
                                else:
                                    img_html += f'<div class="civitai-meta"><dt>{escape(str(key).capitalize())}</dt><dd>{escape(str(value))}</dd></div>'
                        # Check if there are remaining keys in meta
                        remaining_keys = [key for key in prompt_dict if key not in preferred_order]

                        # Add the rest
                        if remaining_keys:
                            img_html += f"""
                            <div class="tabs">
                                <div class="tab">
                                    <input type="checkbox" class="accordionCheckbox" id="chck{index}">
                                    <label class="tab-label" for="chck{index}">More details...</label>
                                    <div class="tab-content" style="gap:10px;display:grid;margin-left:1px;">
                            """
                            for key in remaining_keys:
                                value = prompt_dict[key]
                                img_html += f'<div class="civitai-meta"><dt>{escape(str(key).capitalize())}</dt><dd>{escape(str(value))}</dd></div>'
                            img_html = img_html + '</div></div></div>'

                        img_html += '</dl></div>'

                    img_html = img_html + '</div>'
                img_html = img_html + '</div>'
                tags_html = ''.join([f'<span class="civitai-tag">{escape(str(tag))}</span>' for tag in tags])
                def perms_svg(color):
                    return  f'<span style="display:inline-block;vertical-align:middle;">'\
                            f'<svg width="15" height="15" viewBox="0 1.5 24 24" stroke-width="4" stroke-linecap="round" stroke="{color}">'
                allow_svg = f'{perms_svg("lime")}<path d="M5 12l5 5l10 -10"></path></svg></span>'
                deny_svg = f'{perms_svg("red")}<path d="M18 6l-12 12"></path><path d="M6 6l12 12"></path></svg></span>'
                perms_html= '<p style="line-height: 2; font-weight: bold;">'\
                            f'{allow_svg if item.get("allowNoCredit") else deny_svg} Use the model without crediting the creator<br/>'\
                            f'{allow_svg if item.get("allowCommercialUse") in ["Image", "Rent", "RentCivit", "Sell"] else deny_svg} Sell images they generate<br/>'\
                            f'{allow_svg if item.get("allowCommercialUse") in ["Rent", "Sell"] else deny_svg} Run on services that generate images for money<br/>'\
                            f'{allow_svg if item.get("allowCommercialUse") in ["RentCivit", "Rent", "Sell"] else deny_svg} Run on Civitai<br/>'\
                            f'{allow_svg if item.get("allowDerivatives") else deny_svg} Share merges using this model<br/>'\
                            f'{allow_svg if item.get("allowCommercialUse") == "Sell" else deny_svg} Sell this model or merges using this model<br/>'\
                            f'{allow_svg if item.get("allowDifferentLicense") else deny_svg} Have different permissions when sharing merges'\
                            '</p>'
                output_html = f'''
                <div class="model-block">
                    <h2><a href={model_main_url} target="_blank" id="model_header">{escape(str(model_name))}</a></h2>
                    <h3 class="model-uploader">Uploaded by <a href="https://civitai.com/user/{escape(str(model_uploader))}" target="_blank">{escape(str(model_uploader))}</a>{uploader_avatar}</h3>
                    <div class="civitai-version-info" style="display:flex; flex-wrap:wrap; justify-content:space-between;">
                        <dl id="info_block">
                            <dt>Version</dt>
                            <dd>{escape(str(model_version))}</dd>
                            <dt>Base Model</dt>
                            <dd>{escape(str(output_basemodel))}</dd>
                            <dt>CivitAI Tags</dt>
                            <dd>
                                <div class="civitai-tags-container">
                                    {tags_html}
                                </div>
                            </dd>
                            {"<dt>Download Link</dt>" if model_url else ''}
                            {f'<dd><a href={model_url} target="_blank">{model_url}</a></dd>' if model_url else ''}
                        </dl>
                        <div style="align-self:center; min-width:320px;">
                            <div>
                                {perms_html}
                            </div>
                        </div>
                    </div>
                    <div class="model-description" style="overflow-wrap: break-word;">
                        <h2>Description</h2>
                        {model_desc}
                    </div>
                </div>
                <div align=center>{img_html}</div>
                '''
        
        if only_html:
            return output_html
                          
        folder_location = "None"
        default_subfolder = "None"
        sub_folders = ["None"]

        for root, dirs, files in os.walk(model_folder, followlinks=True):
            for filename in files:
                if filename.endswith('.json'):
                    json_file_path = os.path.join(root, filename)
                    with open(json_file_path, 'r', encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            sha256 = data.get('sha256')
                            if sha256:
                                sha256 = sha256.upper()
                            if sha256 == sha256_value:
                                folder_location = root
                                BtnDownInt = False
                                BtnDel = True
                                
                                break
                        except Exception as e:
                            print(f"Error decoding JSON: {str(e)}")
            else:
                for filename in files:
                    if filename == model_filename or filename == cleaned_name(model_filename):
                        folder_location = root
                        BtnDownInt = False
                        BtnDel = True
                        break

            if folder_location != "None":
                break

        insert_sub_1 = getattr(opts, "insert_sub_1", False)
        insert_sub_2 = getattr(opts, "insert_sub_2", False)
        insert_sub_3 = getattr(opts, "insert_sub_3", False)
        insert_sub_4 = getattr(opts, "insert_sub_4", False)
        insert_sub_5 = getattr(opts, "insert_sub_5", False)
        insert_sub_6 = getattr(opts, "insert_sub_6", False)
        insert_sub_7 = getattr(opts, "insert_sub_7", False)
        insert_sub_8 = getattr(opts, "insert_sub_8", False)
        insert_sub_9 = getattr(opts, "insert_sub_9", False)
        insert_sub_10 = getattr(opts, "insert_sub_10", False)
        insert_sub_11 = getattr(opts, "insert_sub_11", False)
        insert_sub_12 = getattr(opts, "insert_sub_12", False)
        insert_sub_13 = getattr(opts, "insert_sub_13", False)
        insert_sub_14 = getattr(opts, "insert_sub_14", False)
        dot_subfolders = getattr(opts, "dot_subfolders", True)
        
        try:
            sub_folders = ["None"]
            for root, dirs, _ in os.walk(model_folder, followlinks=True):
                if dot_subfolders:
                    dirs = [d for d in dirs if not d.startswith('.')]
                    dirs = [d for d in dirs if not any(part.startswith('.') for part in os.path.join(root, d).split(os.sep))]
                for d in dirs:
                    sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                    if sub_folder:
                        sub_folders.append(f'{os.sep}{sub_folder}')
            
            sub_folders.remove("None")
            sub_folders = sorted(sub_folders, key=lambda x: (x.lower(), x))
            sub_folders.insert(0, "None")
            base = cleaned_name(model_uploader)
            author = cleaned_name(model_uploader)
            name = cleaned_name(model_name)
            ver = cleaned_name(model_version)
            
            if insert_sub_1:
                sub_folders.insert(1, os.path.join(os.sep, base))
            if insert_sub_2:
                sub_folders.insert(2, os.path.join(os.sep, base, author))
            if insert_sub_3:
                sub_folders.insert(3, os.path.join(os.sep, base, author, name))
            if insert_sub_4:
                sub_folders.insert(4, os.path.join(os.sep, base, author, name, ver))
            if insert_sub_5:
                sub_folders.insert(5, os.path.join(os.sep, base, name))
            if insert_sub_6:
                sub_folders.insert(6, os.path.join(os.sep, base, name, ver))
            if insert_sub_7:
                sub_folders.insert(7, os.path.join(os.sep, author))
            if insert_sub_8:
                sub_folders.insert(8, os.path.join(os.sep, author, base))
            if insert_sub_9:
                sub_folders.insert(9, os.path.join(os.sep, author, base, name))
            if insert_sub_10:
                sub_folders.insert(10, os.path.join(os.sep, author, base, name, ver))
            if insert_sub_11:
                sub_folders.insert(11, os.path.join(os.sep, author, name))
            if insert_sub_12:
                sub_folders.insert(12, os.path.join(os.sep, author, name, ver))
            if insert_sub_13:
                sub_folders.insert(13, os.path.join(os.sep, name))
            if insert_sub_14:
                sub_folders.insert(14, os.path.join(os.sep, name, ver))
            
            list = set()
            sub_folders = [x for x in sub_folders if not (x in list or list.add(x))]
        except:
            sub_folders = ["None"]
            
        default_sub = sub_folder_value(content_type, desc)
        
        variable_mapping = {
            "Base model": base,
            "Author name": author,
            "Model name": name,
            "Model version": ver
        }

        if any(key in default_sub for key in variable_mapping.keys()):
            path_components = [variable_mapping.get(component.strip(os.sep), component.strip(os.sep)) for component in default_sub.split(os.sep)]
            default_sub = os.path.join(os.sep, *path_components)
            
        if folder_location == "None":
            folder_location = model_folder
            if default_sub != "None":
                folder_path = folder_location + default_sub
            else:
                folder_path = folder_location
        else:
            folder_path = folder_location
        relative_path = os.path.relpath(folder_location, model_folder)
        default_subfolder = f'{os.sep}{relative_path}' if relative_path != "." else default_sub if BtnDel == False else "None"
        if gl.isDownloading:
            item = gl.download_queue[0]
            if int(model_id) == int(item['model_id']):
                BtnDel = False
        BtnDownTxt = "Download model"
        if len(gl.download_queue) > 0:
            BtnDownTxt = "Add to queue"
            for item in gl.download_queue:
                if item['version_name'] == model_version and int(item['model_id']) == int(model_id):
                    BtnDownInt = False
                    break
        
        return  (
                gr.HTML.update(value=output_html), # Preview HTML 
                gr.Textbox.update(value=output_training, interactive=True), # Trained Tags
                gr.Textbox.update(value=output_basemodel), # Base Model Number
                gr.Button.update(visible=False if BtnDel else True, interactive=BtnDownInt, value=BtnDownTxt), # Download Button
                gr.Button.update(interactive=BtnImage), # Images Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=file_list, value=default_file, interactive=True), # File List
                gr.Textbox.update(value=cleaned_name(model_filename), interactive=True),  # Model File Name
                gr.Textbox.update(value=dl_url), # Download URL
                gr.Textbox.update(value=model_id), # Model ID
                gr.Textbox.update(value=sha256_value),  # SHA256
                gr.Textbox.update(interactive=True, value=folder_path if model_name else None), # Install Path
                gr.Dropdown.update(choices=sub_folders, value=default_subfolder, interactive=True) # Sub Folder List
        )
    else:
        return  (
                gr.HTML.update(value=None), # Preview HTML
                gr.Textbox.update(value=None, interactive=False), # Trained Tags
                gr.Textbox.update(value=''), # Base Model Number
                gr.Button.update(visible=False if BtnDel else True, value="Download model"), # Download Button
                gr.Button.update(interactive=False), # Images Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=None, value=None, interactive=False), # File List
                gr.Textbox.update(value=None, interactive=False),  # Model File Name
                gr.Textbox.update(value=None),  # Download URL
                gr.Textbox.update(value=None), # Model ID
                gr.Textbox.update(value=None),  # SHA256
                gr.Textbox.update(interactive=False, value=None), # Install Path
                gr.Dropdown.update(choices=None, value=None, interactive=False) # Sub Folder List
        )

def sub_folder_value(content_type, desc=None):
    use_LORA = getattr(opts, "use_LORA", False)
    if content_type in ["LORA", "LoCon"] and use_LORA:
        folder = getattr(opts, "LORA_LoCon_subfolder", "None")
    elif content_type == "Upscaler":
        for upscale_type in ["SWINIR", "REALESRGAN", "GFPGAN", "BSRGAN"]:
            if upscale_type in desc:
                folder = getattr(opts, f"{upscale_type}_subfolder", "None")
        folder = getattr(opts, "ESRGAN_subfolder", "None")
    else:
        folder = getattr(opts, f"{content_type}_subfolder", "None")
    if folder == None:
        return "None"
    return folder

def update_file_info(model_string, model_version, file_metadata):
    file_list = []
    is_LORA = False
    embed_check = False
    model_name = None
    model_id = None
    model_name, model_id = extract_model_info(model_string)
    
    if model_version and "[Installed]" in model_version:
        model_version = model_version.replace(" [Installed]", "")
    if model_id and model_version:
        for item in gl.json_data['items']:
            if int(item['id']) == int(model_id):
                content_type = item['type']
                if content_type == "LORA":
                    is_LORA = True
                desc = item['description']
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        for file in model['files']:
                            size = file['metadata'].get('size', 'Unknown')
                            format = file['metadata'].get('format', 'Unknown')
                            unique_file_name = f"{size} {format}"
                            file_list.append(unique_file_name)
                            pass
                        
                        if is_LORA and file_list:
                            extracted_formats = [file.split(' ')[1] for file in file_list]
                            if "SafeTensor" in extracted_formats and "PickleTensor" in extracted_formats:
                                embed_check = True
                        
                        for file in model['files']:
                            model_id = item['id']
                            file_name = file.get('name', 'Unknown')
                            sha256 = file['hashes'].get('SHA256', 'Unknown')
                            metadata = file.get('metadata', {})
                            file_size = metadata.get('size', 'Unknown')
                            file_format = metadata.get('format', 'Unknown')
                            file_fp = metadata.get('fp', 'Unknown')
                            sizeKB = file.get('sizeKB', 0)
                            sizeB = sizeKB * 1024
                            filesize = _download.convert_size(sizeB)

                            if f"{file_size} {file_format} {file_fp} ({filesize})" == file_metadata:
                                installed = False
                                folder_location = "None"
                                model_folder = os.path.join(contenttype_folder(content_type, desc))
                                if embed_check and file_format == "PickleTensor":
                                    if sizeKB <= 100:
                                        model_folder = os.path.join(contenttype_folder("TextualInversion"))
                                dl_url = file['downloadUrl']
                                gl.json_info = item
                                for root, _, files in os.walk(model_folder, followlinks=True):
                                    if file_name in files:
                                        installed = True
                                        folder_location = root
                                        break
                                
                                if not installed:
                                    for root, _, files in os.walk(model_folder, followlinks=True):
                                        for filename in files:
                                            if filename.endswith('.json'):
                                                with open(os.path.join(root, filename), 'r', encoding="utf-8") as f:
                                                    try:
                                                        data = json.load(f)
                                                        sha256_value = data.get('sha256')
                                                        if sha256_value != None and sha256_value.upper() == sha256:
                                                            folder_location = root
                                                            installed = True
                                                            break
                                                    except Exception as e:
                                                        print(f"Error decoding JSON: {str(e)}")
                                default_sub = sub_folder_value(content_type, desc)
                                if folder_location == "None":
                                    folder_location = model_folder
                                    if default_sub != "None":
                                        folder_path = folder_location + default_sub
                                    else:
                                        folder_path = folder_location
                                else:
                                    folder_path = folder_location
                                relative_path = os.path.relpath(folder_location, model_folder)
                                default_subfolder = f'{os.sep}{relative_path}' if relative_path != "." else default_sub if installed == False else "None"
                                BtnDownInt = not installed
                                BtnDownTxt = "Download model"
                                if len(gl.download_queue) > 0:
                                    BtnDownTxt = "Add to queue"
                                    for item in gl.download_queue:
                                        if item['version_name'] == model_version:
                                            BtnDownInt = False
                                            break
                                
                                return  (
                                        gr.Textbox.update(value=cleaned_name(file['name']), interactive=True),  # Model File Name Textbox
                                        gr.Textbox.update(value=dl_url), # Download URL Textbox
                                        gr.Textbox.update(value=model_id), # Model ID Textbox
                                        gr.Textbox.update(value=sha256), # sha256 textbox
                                        gr.Button.update(interactive=BtnDownInt, visible=False if installed else True, value=BtnDownTxt), # Download Button
                                        gr.Button.update(interactive=True if installed else False, visible=True if installed else False),  # Delete Button
                                        gr.Textbox.update(interactive=True, value=folder_path if model_name else None), # Install Path
                                        gr.Dropdown.update(value=default_subfolder, interactive=True) # Sub Folder List
                                )
    
    return  (
            gr.Textbox.update(value=None, interactive=False), # Model File Name Textbox
            gr.Textbox.update(value=None), # Download URL Textbox
            gr.Textbox.update(value=None), # Model ID Textbox
            gr.Textbox.update(value=None), # sha256 textbox
            gr.Button.update(interactive=False, visible=True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Delete Button
            gr.Textbox.update(interactive=False, value=None), # Install Path
            gr.Dropdown.update(choices=None, value=None, interactive=False) # Sub Folder List
    )

def get_headers():
    api_key = getattr(opts, "custom_api_key", "")
    try:
        user_agent = UserAgent().chrome
    except ImportError:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    headers = {
        'User-Agent': user_agent,
        'Sec-Ch-Ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Gpc': '1',
        'Upgrade-Insecure-Requests': '1',
    }
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    return headers

def request_civit_api(api_url=None):
    headers = get_headers()
    try:
        response = requests.get(api_url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "timeout"
    else:
        response.encoding = "utf-8"
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            print("The CivitAI servers are currently offline. Please try again later.")
            return "timeout"
    return data
