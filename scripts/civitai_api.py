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

gl.init()

def git_tag():
    try:
        return subprocess.check_output([os.environ.get('GIT', "git"), "describe", "--tags"], shell=False, encoding='utf8').strip()
    except:
        return "None"

ver = git_tag()

def update_dl_url(trained_tags, model_name=None, model_version=None, model_id=None):
    if model_version:
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
                gr.Button.update(interactive=True if model_id else False), # Save Images Button
                gr.Button.update(interactive=True if model_id else False) # Download Button
        )
    else:
        return  (
                gr.Textbox.update(value=None), # Download URL
                gr.Button.update(interactive=True if trained_tags else False), # Save Tags Button
                gr.Button.update(interactive=True if model_id else False), # Save Images Button
                gr.Button.update(interactive=True if model_id else False) # Download Button
        )

def contenttype_folder(content_type):
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
        if gl.save_tags:
            folder = os.path.join(models_path,"LyCORIS")
            return folder
        try:
            parsed_version = version.parse(ver) 
            if version.parse(ver) >= version.parse("1.5"):
                folder = cmd_opts.lora_dir
        except version.InvalidVersion or parsed_version < version.parse("1.5"):
            if "lyco_dir" in cmd_opts:
                folder = f"{cmd_opts.lyco_dir}"
            elif "lyco_dir_backcompat" in cmd_opts:
                folder = f"{cmd_opts.lyco_dir_backcompat}"
            else:
                folder = os.path.join(models_path,"LyCORIS")          
            
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
    query = {'types': content_type, 'sort': sort_type, 'period': period_type}
    
    if use_search_term != "None" and search_term:
        if use_search_term == "User name":
            query.update({'username': search_term})
        elif use_search_term == "Tag":
            query.update({'tag': search_term})
        else:
            query.update({'query': search_term})
                
    return request_civit_api(f"{api_url}", query )

def api_next_page(next_page_url=None):
    if next_page_url is None:
        try: gl.json_data['metadata']['nextPage']
        except: return
        next_page_url = gl.json_data['metadata']['nextPage']
        next_page_url = re.sub(r'limit=\d+', f'limit={gl.tile_count}', next_page_url)
    return request_civit_api(next_page_url)

def model_list_html(json_data, model_dict, content_type):
    gl.contentChange = False
    HTML = '<div class="column civmodellist">'
    sorted_models = {}
    
    for item in json_data['items']:
        for k, model in model_dict.items():
            if model_dict[k].lower() == item['name'].lower():
                model_name = escape(item["name"].replace("'", "\\'"), quote=True)
                nsfw = ""
                installstatus = ""
                baseModel = ""
                latest_version_installed = False
                model_folder = os.path.join(contenttype_folder(content_type))
                
                if 'baseModel' in item['modelVersions'][0]:
                    baseModel = item['modelVersions'][0]['baseModel']
                if 'updatedAt' in item['modelVersions'][0]:
                    date = item['modelVersions'][0]['updatedAt'].split('T')[0]
                
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
                    
                    existing_files = []
                    for root, dirs, files in os.walk(model_folder):
                        for file in files:
                            existing_files.append(file)
                    
                    for version in reversed(item['modelVersions']):
                        file_found = False
                        for file in version.get('files', []):
                            file_name = file['name']
                            if file_name in existing_files:
                                file_found = True
                                if version == item['modelVersions'][0]:
                                    latest_version_installed = True
                                    break
                                elif not latest_version_installed:
                                    installstatus = "civmodelcardoutdated"
                        
                        if file_found and latest_version_installed:
                            installstatus = "civmodelcardinstalled"
                            break
                
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

def update_prev_page(show_nsfw, content_type, sort_type, period_type, use_search_term, search_term, page_count):
    return update_next_page(show_nsfw, content_type, sort_type, period_type, use_search_term, search_term, page_count, isNext=False)

def update_next_page(show_nsfw, content_type, sort_type, period_type, use_search_term, search_term, page_count, isNext=True):
    
    if gl.json_data is None or gl.json_data == "timeout":
        timeOut = True
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, page_count, timeOut, isNext)
        timeOut = False
        
        return return_values
        
    gl.pageChange = True
    
    current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, gl.tile_count)
    
    if gl.previous_inputs and current_inputs != gl.previous_inputs:
        gl.inputs_changed = True
    else:
        gl.inputs_changed = False
    
    
    gl.previous_inputs = current_inputs

    if gl.inputs_changed or gl.contentChange:
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, page_count)
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
        gl.json_data['allownsfw'] = show_nsfw
        (hasPrev, hasNext, pages) = pagecontrol(gl.json_data)
        model_dict = {}
        try:
            gl.json_data['items']
        except TypeError:
            return gr.Dropdown.update(choices=[], value=None)

        for item in gl.json_data['items']:
            model_dict[item['name']] = item['name']
        HTML = model_list_html(gl.json_data, model_dict, content_type)

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
    return hasPrev,hasNext,pages_ctrl

def update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, page_count, timeOut=None, isNext=None):
    if gl.pageChange == False:
    
        current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, gl.tile_count)
        
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
        gl.json_data['allownsfw'] = show_nsfw
        (hasPrev, hasNext, pages) = pagecontrol(gl.json_data)
        model_dict = {}
        for item in gl.json_data['items']:
            model_dict[item['name']] = item['name']
        
        HTML = model_list_html(gl.json_data, model_dict, content_type)
    
    gl.contentChange = False
    
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

def update_model_versions(model_name, content_type):
    if model_name is not None and content_type is not None:
        versions_dict = defaultdict(list)
        installed_versions = []
        folder_location = "None"
        sub_folders = ["None"]
        model_folder = os.path.join(contenttype_folder(content_type))
        gl.main_folder = model_folder
        for root, dirs, _ in os.walk(model_folder):
            for d in dirs:
                sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                if sub_folder:
                    sub_folders.append(f'\{sub_folder}')
        folder_location = model_folder
        if gl.json_data != None and gl.json_data != "timeout":
            for item in gl.json_data['items']:
                if item['name'] == model_name:
                    for version in item['modelVersions']:
                        versions_dict[version['name']].append(item["name"])
                        for root, dirs, files in os.walk(model_folder):
                            for file in files:
                                for version_file in version['files']:
                                    if version_file['name'] == file:
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
        for item in gl.json_data['items']:
            if item['name'] == model_name:
                model_uploader = item['creator']['username']
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
                
                            size = file['metadata'].get('size', 'Unknown')
                            format = file['metadata'].get('format', 'Unknown')
                            fp = file['metadata'].get('fp', 'Unknown')
                            sizeKB = file.get('sizeKB', 0) * 1024
                            filesize = _download.convert_size(sizeKB)
                            
                            unique_file_name = f"{size} {format} {fp} ({filesize})"
                            file_list.append(unique_file_name)
                            
                        model_url = model['downloadUrl']
                        img_html = '<div class="sampleimgs">'
                        for pic in model['images']:
                            nsfw = None
                            if pic['nsfw'] not in ["None", "Soft"]:
                                nsfw = 'class="civnsfw"'
                            img_html = img_html + f'<div {nsfw} style="display:flex;align-items:flex-start;"><img src={pic["url"]} style="width:20em;"></img>'
                            if pic['meta']:
                                img_html = img_html + '<div style="text-align:left;line-height: 1.5em;">'
                                for key, value in pic['meta'].items():
                                    img_html = img_html + f'{escape(str(key))}: {escape(str(value))}</br>'
                                img_html = img_html + '</div>'
                            img_html = img_html + '</div>'
                        img_html = img_html + '</div>'
                        output_html = f"<p><b>Model</b>: {escape(str(model_name))}<br><b>Version</b>: {escape(str(model_version))}<br><b>Uploaded by</b>: {escape(str(model_uploader))}<br><b>Base Model</b>: {escape(str(output_basemodel))}</br><b>Tags</b>: {escape(str(tags))}<br><b>Trained Tags</b>: {escape(str(output_training))}<br>{escape(str(allow))}<br><a href={model_url}><b>Download Here</b></a></p><br><br>{model_desc}<br><div align=center>{img_html}</div>"
                
                default_file = file_list[0] if file_list else None
                        
        return  (
                gr.HTML.update(value=output_html), # Model Preview
                gr.Textbox.update(value=output_training), # Trained Tags
                gr.Textbox.update(value=output_basemodel), # Base Model Number
                gr.Button.update(visible=BtnDown, interactive=BtnDown), # Download Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=file_list, value=default_file, interactive=True) # File List
        )
    else:
        return  (
                gr.HTML.update(value=None), # Model Preview
                gr.Textbox.update(value=None), # Trained Tags
                gr.Textbox.update(value=''), # Base Model Number
                gr.Button.update(visible=BtnDown), # Download Button
                gr.Button.update(visible=BtnDel, interactive=BtnDel), # Delete Button
                gr.Dropdown.update(choices=None, value=None, interactive=False) # File List
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
                            metadata = file.get('metadata', {})
                            file_size = metadata.get('size', 'Unknown')
                            file_format = metadata.get('format', 'Unknown')
                            file_fp = metadata.get('fp', 'Unknown')
                            file_id = file.get('id', 'Unknown')
                            sizeKB = file.get('sizeKB', 0) * 1024
                            filesize = _download.convert_size(sizeKB)
                            
                            if f"{file_size} {file_format} {file_fp} ({filesize})" == file_metadata:
                                return  (
                                        gr.Textbox.update(value=file['name']),  # Update model_filename Textbox
                                        gr.Textbox.update(value=file_id)  # Update ID Textbox
                                )
    return  (
            gr.Textbox.update(value=None),  # Update model_filename Textbox
            gr.Textbox.update(value=None)  # Update ID Textbox
    )

def request_civit_api(api_url=None, payload=None):
    if payload is not None:
        payload = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    try:
        response = requests.get(api_url, params=payload, timeout=(10,30))
        response.raise_for_status()
    except:
        return "timeout"
    else:
        response.encoding  = "utf-8"
        data = json.loads(response.text)
    return data