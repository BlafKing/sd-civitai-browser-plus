import requests
import json
import gradio as gr
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import os
import re
from collections import defaultdict
from packaging import version
from modules.shared import cmd_opts, opts
from modules.paths import models_path
from html import escape 
import scripts.civitai_global as gl
import scripts.civitai_download as _download
import time

gl.init()

def update_dl_url(trained_tags, model_id=None, model_name=None, model_version=None):    
    if model_version and "[Installed]" in model_version:
        model_version = model_version.replace(" [Installed]", "")
    
    if model_id:
        dl_url = None
        for item in gl.json_data['items']:
            if item['name'] == model_name:
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        for file in model['files']:
                            if int(file['id']) == int(model_id):
                                dl_url = file['downloadUrl']
                                gl.json_info = model
                                
        return  (
                gr.Textbox.update(value=dl_url), # Download URL
                gr.Button.update(interactive=True if trained_tags else False), # Save Tags Button
                gr.Button.update(interactive=True if model_version else False), # Save Images Button
                gr.Button.update(interactive=True if model_version else False) # Download Button
        )
    else:
        return  (
                gr.Textbox.update(value=None), # Download URL
                gr.Button.update(interactive=True if trained_tags else False), # Save Tags Button
                gr.Button.update(interactive=True if model_version else False), # Save Images Button
                gr.Button.update(interactive=True if model_version else False) # Download Button
        )

def contenttype_folder(content_type):
    use_LORA = getattr(opts, "use_LORA", False)
    if content_type == "modelFolder":
        folder = os.path.join(models_path)
    
    if content_type == "Checkpoint":
        if cmd_opts.ckpt_dir:
            folder = cmd_opts.ckpt_dir
        else:            
            folder = os.path.join(models_path,"Stable-diffusion")
            
    elif content_type == "Hypernetwork":
        folder = cmd_opts.hypernetwork_dir
        
    elif content_type == "TextualInversion":
        folder = cmd_opts.embeddings_dir
        
    elif content_type == "AestheticGradient":
        folder = "extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings"
        
    elif content_type == "LORA":
        folder = cmd_opts.lora_dir
        
    elif content_type == "LoCon":
        if "lyco_dir" in cmd_opts:
            folder = f"{cmd_opts.lyco_dir}"
        elif "lyco_dir_backcompat" in cmd_opts:
            folder = f"{cmd_opts.lyco_dir_backcompat}"
        else:
            folder = os.path.join(models_path,"LyCORIS")    
        if use_LORA:
            folder = cmd_opts.lora_dir      
            
    elif content_type == "VAE":
        if cmd_opts.vae_dir:
            folder = cmd_opts.vae_dir
        else:
            folder = os.path.join(models_path,"VAE")
            
    elif content_type == "Controlnet":
        if cmd_opts.ckpt_dir:
            folder = os.path.join(os.path.join(cmd_opts.ckpt_dir, os.pardir), "ControlNet")
        else:            
            folder = os.path.join(models_path,"ControlNet")
            
    elif content_type == "Poses":
        if cmd_opts.ckpt_dir:
            folder = os.path.join(os.path.join(cmd_opts.ckpt_dir, os.pardir), "Poses")
        else:            
            folder = os.path.join(models_path,"Poses")
            
    return folder

def api_to_data(content_type, sort_type, period_type, use_search_term, page_count, search_term=None, timeOut=None, isNext=None):
    
    if page_count in ("0", ""):
        page_count = "1"
    
    page_value = page_count.split('/')[0]
    if search_term != gl.previous_search_term or gl.tile_count != gl.previous_tile_count or gl.inputs_changed or gl.contentChange:
        gl.previous_search_term = search_term
        gl.previous_tile_count = gl.tile_count
        api_url = f"https://civitai.com/api/v1/models?limit={gl.tile_count}&page=1"
    else:
        api_url = f"https://civitai.com/api/v1/models?limit={gl.tile_count}&page={page_value}"
    
    if timeOut:
        if isNext:
            next_page = str(int(page_value) + 1)
        else:
            next_page = str(int(page_value) - 1)
        api_url = f"https://civitai.com/api/v1/models?limit={gl.tile_count}&page={next_page}"
    
    period_type = period_type.replace(" ", "")
    query = {'sort': sort_type, 'period': period_type}
    
    types_query_str = ""
    if content_type:
        types_query_str = "".join([f"&types={type}" for type in content_type])
    
    query_str = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
    
    if types_query_str:
        query_str += types_query_str

    if use_search_term != "None" and search_term:
        if use_search_term == "User name":
            query_str += f"&username={urllib.parse.quote(search_term)}"
        elif use_search_term == "Tag":
            query_str += f"&tag={urllib.parse.quote(search_term)}"
        else:
            query_str += f"&query={urllib.parse.quote(search_term)}"
    
    full_url = f"{api_url}&{query_str}"

    return request_civit_api(full_url)

def api_next_page(next_page_url=None):
    if next_page_url is None:
        try: gl.json_data['metadata']['nextPage']
        except: return
        next_page_url = gl.json_data['metadata']['nextPage']
        next_page_url = re.sub(r'limit=\d+', f'limit={gl.tile_count}', next_page_url)
    return request_civit_api(next_page_url)

def model_list_html(json_data, model_dict):
    gl.contentChange = False
    HTML = '<div class="column civmodellist">'
    sorted_models = {}
        
    for item in json_data['items']:
        for k, model in model_dict.items():
            if model_dict[k].lower() == item['name'].lower():
                model_name = escape(item["name"].replace("'", "\\'"), quote=True)
                
                if model_name:
                    selected_content_type = item['type']
                        
                if not selected_content_type:
                    print("Model name not found in json_data. (model_list_html)")
                    return
                
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
                        imgtag = f'<img src={item["modelVersions"][0]["images"][0]["url"]}"></img>'
                    else:
                        imgtag = f'<img src="./file=html/card-no-preview.png"></img>'

                    model_folder = os.path.join(contenttype_folder(selected_content_type))
                    existing_files = []
                    existing_files_sha256 = []
                    
                    for root, dirs, files in os.walk(model_folder):
                        for file in files:
                            existing_files.append(file)
                            if file.endswith('.json'):
                                json_path = os.path.join(root, file)
                                with open(json_path, 'r') as f:
                                    try:
                                        json_data = json.load(f)
                                        if isinstance(json_data, dict):
                                            sha256 = json_data.get('sha256')
                                            if sha256:
                                                existing_files_sha256.append(sha256.upper())
                                        else:
                                            print(f"Invalid JSON data in {json_path}. Expected a dictionary.")
                                    except json.JSONDecodeError as e:
                                        print(f"Error decoding JSON in {json_path}: {str(e)}")
                    
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
                model_card = f'<figure class="civmodelcard {nsfw} {installstatus}" base-model="{baseModel}" date="{date}" onclick="select_model(\'{model_name}\')">' \
                            + imgtag \
                            + f'<figcaption>{item["name"]}</figcaption></figure>'
                
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

def update_prev_page(content_type, sort_type, period_type, use_search_term, search_term, page_count):
    return update_next_page(content_type, sort_type, period_type, use_search_term, search_term, page_count, isNext=False)

def update_next_page(content_type, sort_type, period_type, use_search_term, search_term, page_count, isNext=True):
    
    if gl.json_data is None or gl.json_data == "timeout":
        timeOut = True
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, page_count, timeOut, isNext)
        timeOut = False
        
        return return_values
        
    gl.pageChange = True
    
    current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, gl.tile_count)
    
    if gl.previous_inputs and current_inputs != gl.previous_inputs:
        gl.inputs_changed = True
    else:
        gl.inputs_changed = False
    
    
    gl.previous_inputs = current_inputs

    if gl.inputs_changed or gl.contentChange:
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, page_count)
        return return_values
    
    if isNext:
        gl.json_data = api_next_page()
    else:
        if gl.json_data['metadata']['prevPage'] is not None:
            gl.json_data = api_next_page(gl.json_data['metadata']['prevPage'])
        else:
            gl.json_data = None
            
    if gl.json_data is None:
        return
    
    if gl.json_data == "timeout":
        HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
        page_value = page_count.split('/')[0]
        hasPrev = page_value not in [0, 1]
        hasNext = page_value == 1 or hasPrev
        model_dict = {}
        pages=page_count
        
    if gl.json_data != None and gl.json_data != "timeout":
        (hasPrev, hasNext, pages) = pagecontrol(gl.json_data)
        model_dict = {}
        try:
            gl.json_data['items']
        except TypeError:
            return gr.Dropdown.update(choices=[], value=None)

        for item in gl.json_data['items']:
            model_dict[item['name']] = item['name']
        HTML = model_list_html(gl.json_data, model_dict)

    return  (
            gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=""), # Model List
            gr.Dropdown.update(choices=[], value=""), # Version List
            gr.HTML.update(value=HTML), # Model Cards HTML
            gr.Button.update(interactive=hasPrev), # Prev Button
            gr.Button.update(interactive=hasNext), # Next Button
            gr.Textbox.update(value=pages), # Pages
            gr.Button.update(interactive=False), # Save Tags Button
            gr.Button.update(interactive=False), # Save Images Button
            gr.Button.update(interactive=False), # Download Button
            gr.Textbox.update(interactive=False, value=None), # Install Path
            gr.Dropdown.update(choices=[], value="") # Sub Folder List
    )

def pagecontrol(json_data):
    pages_ctrl = f"{json_data['metadata']['currentPage']}/{json_data['metadata']['totalPages']}"
    hasNext = False
    hasPrev = False
    if 'nextPage' in json_data['metadata']:
        hasNext = True
    if 'prevPage' in json_data['metadata']:
        hasPrev = True
    return hasPrev, hasNext, pages_ctrl

def update_model_list(content_type, sort_type, period_type, use_search_term, search_term, page_count, timeOut=None, isNext=None, from_ver=False, from_installed=False):
    if not from_ver and not from_installed:
        gl.ver_json = None
        if not gl.pageChange:
        
            current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, gl.tile_count)
            
            if gl.previous_inputs and current_inputs != gl.previous_inputs:
                gl.inputs_changed = True
            else:
                gl.inputs_changed = False
            
            gl.previous_inputs = current_inputs
        
        gl.json_data = api_to_data(content_type, sort_type, period_type, use_search_term, page_count, search_term, timeOut, isNext)
        if gl.json_data == "timeout":
            HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
            page_value = page_count.split('/')[0]
            hasPrev = page_value not in [0, 1]
            hasNext = page_value == 1 or hasPrev
            model_dict = {}
            pages=page_count
        
        if gl.json_data is None:
            return
        
        if gl.pageChange:
            gl.pageChange = False
        
        if gl.json_data != None and gl.json_data != "timeout":
            (hasPrev, hasNext, pages) = pagecontrol(gl.json_data)
            model_dict = {}
            for item in gl.json_data['items']:
                model_dict[item['name']] = item['name']
            
            HTML = model_list_html(gl.json_data, model_dict)
        
        gl.contentChange = False
    
    if from_ver:
        hasPrev = False
        hasNext = False
        pages = ""
        model_dict = {}
        for item in gl.ver_json['items']:
            model_dict[item['name']] = item['name']
        HTML = model_list_html(gl.ver_json, model_dict)
        gl.json_data = gl.ver_json
    
    if from_installed:
        (hasPrev, hasNext, pages) = pagecontrol(gl.ver_json)
        model_dict = {}
        for item in gl.ver_json['items']:
            model_dict[item['name']] = item['name']
        
        HTML = model_list_html(gl.ver_json, model_dict)
        gl.json_data = gl.ver_json
    
    return  (
            gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value="", interactive=True), # Model List
            gr.Dropdown.update(choices=[], value=""), # Version List
            gr.HTML.update(value=HTML), # HTML Tiles
            gr.Button.update(interactive=hasPrev), # Prev Page Button
            gr.Button.update(interactive=hasNext), # Next Page Button
            gr.Textbox.update(value=pages), # Page Count
            gr.Button.update(interactive=False), # Save Tags
            gr.Button.update(interactive=False), # Save Images
            gr.Button.update(interactive=False), # Download Button
            gr.Textbox.update(interactive=False, value=None), # Install Path
            gr.Dropdown.update(choices=[], value="", interactive=False), # Sub Folder List
            gr.Dropdown.update(choices=[], value="", interactive=False) # File List
    )

def update_model_versions(model_name):
    if model_name is not None:
        selected_content_type = None
        for item in gl.json_data['items']:
            if item['name'] == model_name:
                selected_content_type = item['type']
                break
        
        if selected_content_type is None:
            print("Model name not found in json_data. (update_model_versions)")
            return

        versions_dict = defaultdict(list)
        installed_versions = []
        folder_location = "None"
        sub_folders = ["None"]

        model_folder = os.path.join(contenttype_folder(selected_content_type))
        gl.main_folder = model_folder
        existing_files_sha256 = []
        for root, dirs, files in os.walk(model_folder):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    with open(json_path, 'r') as f:
                        json_data = json.load(f)
                        sha256 = json_data.get('sha256')
                        if sha256:
                            existing_files_sha256.append(sha256.upper())

        for root, dirs, _ in os.walk(model_folder):
            for d in dirs:
                sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                if sub_folder:
                    sub_folders.append(f'{os.sep}{sub_folder}')
        
        folder_location = model_folder

        for item in gl.json_data['items']:
            if item['name'] == model_name:
                for version in item['modelVersions']:
                    versions_dict[version['name']].append(item["name"])
                    for root, dirs, files in os.walk(model_folder):
                        for file in files:
                            for version_file in version['files']:
                                file_sha256 = version_file.get('hashes', {}).get('SHA256', "").upper()
                                if version_file['name'] == file or file_sha256 in existing_files_sha256:
                                    installed_versions.append(version['name'])
                                    if root != model_folder:
                                        folder_location = root
                                    break

        default_subfolder = folder_location.replace(model_folder, '')
        default_subfolder = default_subfolder if default_subfolder else "None"
        version_names = list(versions_dict.keys())
        display_version_names = [f"{v} [Installed]" if v in installed_versions else v for v in version_names]
        default_installed = next((f"{v} [Installed]" for v in installed_versions), None)
        default_value = default_installed or next(iter(version_names), None)
        
        return  (
                gr.Dropdown.update(choices=display_version_names, value=default_value, interactive=True), # Version List
                gr.Textbox.update(interactive=True, value=folder_location if model_name else None), # Install Path
                gr.Dropdown.update(choices=sub_folders, value=default_subfolder, interactive=True) # Sub Folder List
        )
    else:
        return  (
                gr.Dropdown.update(choices=[], value=None, interactive=False), # Version List
                gr.Textbox.update(interactive=False, value=None), # Install Path
                gr.Dropdown.update(choices=[], value="", interactive=False) # Sub Folder List
        )

def update_model_info(model_name=None, model_version=None):
    if model_version and "[Installed]" in model_version:
        BtnDown = False
        BtnDel = True
        model_version = model_version.replace(" [Installed]", "")
    else:
        BtnDown = True
        BtnDel = False
    if gl.isDownloading:
        BtnDown = False
        BtnDel = False
    if model_name and model_version:
        output_html = ""
        output_training = ""
        output_basemodel = ""
        img_html = ""
        model_desc = ""
        dl_dict = {}
        allow = {}
        file_list = []
        model_filename = None
        file_id_value = None
        sha256_value = None
        for item in gl.json_data['items']:
            if item['name'] == model_name:
                model_uploader = item['creator']['username']
                uploader_avatar = item['creator']['image']
                if uploader_avatar is None:
                     uploader_avatar = ''
                else:
                    uploader_avatar = f'<div class="avatar"><img src={uploader_avatar}></div>'
                tags = item['tags']
                if item['description']:
                    model_desc = item['description']
                if item['allowNoCredit']:
                    allow['allowNoCredit'] = item['allowNoCredit']
                if item['allowCommercialUse']:
                    allow['allowCommercialUse'] = item['allowCommercialUse']
                if item['allowDerivatives']:
                    allow['allowDerivatives'] = item['allowDerivatives']
                if item['allowDifferentLicense']:
                    allow['allowDifferentLicense'] = item['allowDifferentLicense']
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        if model['trainedWords']:
                            output_training = ",".join(model['trainedWords'])
                            output_training = re.sub(r'<[^>]*:[^>]*>', '', output_training)
                            output_training = re.sub(r', ?', ', ', output_training)
                            output_training = output_training.strip(', ')
                        if model['baseModel']:
                            output_basemodel = model['baseModel']
                        for file in model['files']:
                            dl_dict[file['name']] = file['downloadUrl']
                            
                            if not model_filename:
                                model_filename = file['name']
                                file_id_value = file.get('id', 'Unknown')
                                sha256_value = file['hashes'].get('SHA256', 'Unknown')
                            
                            size = file['metadata'].get('size', 'Unknown')
                            format = file['metadata'].get('format', 'Unknown')
                            fp = file['metadata'].get('fp', 'Unknown')
                            sizeKB = file.get('sizeKB', 0) * 1024
                            filesize = _download.convert_size(sizeKB)
                            
                            unique_file_name = f"{size} {format} {fp} ({filesize})"
                            file_list.append(unique_file_name)
                            
                        model_url = model['downloadUrl']
                        model_main_url = f"https://civitai.com/models/{item['id']}"
                        img_html = '<div class="sampleimgs"><input type="radio" name="zoomRadio" id="resetZoom" class="zoom-radio" checked>'
                        first_image = True
                        for index, pic in enumerate(model['images']):
                            # Change width value in URL to original image width
                            image_url = re.sub(r'/width=\d+', f'/width={pic["width"]}', pic["url"])
                            
                            if first_image:                                
                                # Set a data attribute on the first image to designate it as preview
                                preview_attr = f'data-preview-img={image_url}'
                                first_image = False
                            else: 
                                preview_attr = ''
                            nsfw = 'class="model-block"'
                            
                            if pic['nsfw'] not in ["None", "Soft"]:
                                nsfw = 'class="civnsfw model-block"'

                            img_html = img_html + f'''
                            <div {nsfw} style="display:flex;align-items:flex-start;">
                                <input type="radio" name="zoomRadio" id="zoomRadio{index}" class="zoom-radio">
                                <label for="zoomRadio{index}" class="zoom-img-container">
                                    <img {preview_attr} data-sampleimg="true" src={image_url}>
                                </label>
                                <label for="resetZoom" class="zoom-overlay"></label>
                            '''
                            if pic['meta']:
                                img_html = img_html + '<div style="margin:1em 0em 1em 1em;text-align:left;line-height: 1.5em;"><dl>'
                                # Define the preferred order of keys
                                preferred_order = ["prompt", "negativePrompt", "seed", "Size", "Model", "clipSkip", "sampler", "steps", "cfgScale"]
                                # Loop through the keys in the preferred order and add them to the HTML
                                for key in preferred_order:
                                    if key in pic['meta']:
                                        value = pic['meta'][key]
                                        img_html += f'<dt>{escape(str(key))}</dt><dd>{escape(str(value))}</dd>'
                                
                                # Check if there are remaining keys in pic['meta']
                                remaining_keys = [key for key in pic['meta'] if key not in preferred_order]
                                
                                # Add the rest
                                if remaining_keys:
                                    img_html += f"""
                                    <div class="tabs">
                                        <div class="tab">
                                            <input type="checkbox" class="accordionCheckbox" id="chck{index}">
                                            <label class="tab-label" for="chck{index}">More details...</label>
                                            <div class="tab-content">
                                    """
                                    for key, value in pic['meta'].items():
                                        if key not in preferred_order:
                                            img_html += f'<dt>{escape(str(key))}</dt><dd>{escape(str(value))}</dd>'
                                    img_html = img_html + '</div></div></div>'
                                
                                img_html += '</dl></div>'
                            
                            img_html = img_html + '</div>'
                        img_html = img_html + '</div>'
                        output_html = f'''
                        <div class="model-block">
                            <h2><a href={model_main_url} target="_blank">{escape(str(model_name))}</a></h2>
                            <h3 class="model-uploader">Uploaded by <a href="https://civitai.com/user/{escape(str(model_uploader))}" target="_blank">{escape(str(model_uploader))}</a>{uploader_avatar}</h3>
                            <dl>
                                <dt>Version</dt>
                                <dd>{escape(str(model_version))}</dd>
                                <dt>Base Model</dt>
                                <dd>{escape(str(output_basemodel))}</dd>
                                <dt>CivitAI Tags</dt>
                                <dd>{escape(str(tags))}</dd>
                                <dt>License</dt>
                                <dd>{escape(str(allow))}</dd>
                                <dt>Download Link</dt>
                                <dd><a href={model_url} target="_blank">{model_url}</a></dd>
                            </dl>
                            <div class="model-description">
                                <h2>Description</h2>
                                {model_desc}
                            </div>
                        </div>
                        <div align=center>{img_html}</div>
                        '''
                                        
                default_file = file_list[0] if file_list else None
                        
        return  (
                gr.HTML.update(value=output_html), # Model Preview
                gr.Textbox.update(value=output_training), # Trained Tags
                gr.Textbox.update(value=output_basemodel), # Base Model Number
                gr.Button.update(visible=BtnDown, interactive=BtnDown), # Download Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=file_list, value=default_file, interactive=True), # File List
                gr.Textbox.update(value=model_filename),  # Model File Name
                gr.Textbox.update(value=file_id_value),  # Model ID
                gr.Textbox.update(value=sha256_value)  # SHA256
        )
    else:
        return  (
                gr.HTML.update(value=None), # Model Preview
                gr.Textbox.update(value=None), # Trained Tags
                gr.Textbox.update(value=''), # Base Model Number
                gr.Button.update(visible=BtnDown), # Download Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=None, value=None, interactive=False), # File List
                gr.Textbox.update(value=None),  # Model File Name
                gr.Textbox.update(value=None),  # Model ID
                gr.Textbox.update(value=None)  # SHA256
        )

def update_file_info(model_name, model_version, file_metadata):
    if model_version and "[Installed]" in model_version:
        model_version = model_version.replace(" [Installed]", "")
    if model_name and model_version:
        for item in gl.json_data['items']:
            if item['name'] == model_name:
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        for file in model['files']:
                            file_id = file.get('id', 'Unknown')
                            sha256 = file['hashes'].get('SHA256', 'Unknown')
                            metadata = file.get('metadata', {})
                            file_size = metadata.get('size', 'Unknown')
                            file_format = metadata.get('format', 'Unknown')
                            file_fp = metadata.get('fp', 'Unknown')
                            sizeKB = file.get('sizeKB', 0) * 1024
                            filesize = _download.convert_size(sizeKB)

                            if f"{file_size} {file_format} {file_fp} ({filesize})" == file_metadata:
                                return  (
                                        gr.Textbox.update(value=file['name']),  # Update model_filename Textbox
                                        gr.Textbox.update(value=file_id),  # Update ID Textbox
                                        gr.Textbox.update(value=sha256)
                                )
    
    return  (
            gr.Textbox.update(value=None),  # Update model_filename Textbox
            gr.Textbox.update(value=None),  # Update ID Textbox
            gr.Textbox.update(value=None)
    )

def request_civit_api(api_url=None):
    try:
        response = requests.get(api_url, timeout=(10,30))
        response.raise_for_status()
    except Exception as e:
        print(f"Error: {e}")
        return "timeout"
    else:
        response.encoding = "utf-8"
        data = json.loads(response.text)
    return data
