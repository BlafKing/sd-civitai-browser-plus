import requests
import json
import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks
import time
import subprocess
import threading
import urllib.request
import urllib.parse
import urllib.error
import os
import random
import fnmatch
import re
from collections import defaultdict
from packaging import version
from requests.exceptions import ConnectionError
from modules.shared import opts, cmd_opts
from modules.paths import models_path
import shutil
from html import escape 

cancel_status = None
recent_model = None
json_data = None
json_info = None
last_dwn = None
last_start = None
last_del = None
main_folder = None
previous_search_term = None
previous_tile_count = None
previous_inputs = None
sortNewest = False
contentChange = False
inputs_changed = False
isDownloading = False
pageChange = False
tile_count = 15

def git_tag():
    try:
        return subprocess.check_output([os.environ.get('GIT', "git"), "describe", "--tags"], shell=False, encoding='utf8').strip()
    except:
        return "None"

ver = git_tag()

class TimeOutFunction(Exception):
    pass

def start_download(model_name, model_filename):
    global last_start, recent_model, cancel_status, current_download
    current_download = model_filename
    cancel_status = False
    recent_model = model_name
    number = str(random.randint(10000, 99999))

    while number == last_start:
        number = str(random.randint(10000, 99999))
    
    last_start = number 
    return  (
            gr.Button.update(interactive=False, visible=False), # Download Button
            gr.Button.update(interactive=True, visible=True), # Cancel Button
            gr.Textbox.update(value=number), # Download Start Trigger
            gr.HTML.update(value='<div style="min-height: 100px;"></div>') # Download Progress
    )

def finish_download():
    global cancel_status
    cancel_status = False
    return  (
            gr.Button.update(interactive=False, visible=True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>'), # Download Progress
            gr.Textbox.update(value=None) # Current Model
    )
    
def download_cancel(content_type, model_name, list_versions):
    global cancel_status
    cancel_status = True
    
    while True:        
        if not isDownloading:
            delete_file(content_type, current_download, model_name, list_versions)
            break
        else:
            time.sleep(0.5)
                
    cancel_status = False
    return  (
            gr.Button.update(interactive=False, visible=True), # Download Button
            gr.Button.update(interactive=False, visible=False), # Cancel Button
            gr.HTML.update(value='<div style="min-height: 0px;"></div>') # Download Progress
    )

def download_file(url, file_path, preview_image_html, install_path, progress=gr.Progress()):
    global isDownloading, total_size
    max_retries = 5
    if os.path.exists(file_path):
        os.remove(file_path)
    downloaded_size = 0
    tokens = re.split(re.escape('\\'), file_path)
    file_name_display = tokens[-1]
    
    def convert_size(size):
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"
    
    while True:
        if cancel_status:
            return
        if os.path.exists(file_path):
            downloaded_size = os.path.getsize(file_path)
            headers = {"Range": f"bytes={downloaded_size}-"}
        else:
            headers = {}
        with open(file_path, "ab") as f:
            while isDownloading:
                try:
                    if cancel_status:
                        return
                    try:
                        if cancel_status:
                            return
                        response = requests.get(url, headers=headers, stream=True, timeout=4)
                        total_size = int(response.headers.get("Content-Length", 0))
                    except:
                        raise TimeOutFunction("Timed Out")
                    
                    if total_size == 0:
                        total_size = downloaded_size

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            if cancel_status:
                                return
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            progress(downloaded_size / total_size, desc=f"Downloading: {file_name_display} {convert_size(downloaded_size)} / {convert_size(total_size)}")
                            if isDownloading == False:
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
                        return
                    time.sleep(5)

        if (isDownloading == False):
            break
        
        isDownloading = False
        downloaded_size = os.path.getsize(file_path)
        if downloaded_size >= total_size:
            if not cancel_status:
                print(f"Model saved to: {file_path}")
                save_preview_image(preview_image_html, file_path, install_path)
            
        else:
            progress(0, desc="Download failed, please try again.")
            print(f"Error: File download failed: {file_name_display}")
            time.sleep(2)
            if os.path.exists(file_path):
                os.remove(file_path)

def download_file_thread(url, file_name, preview_image_html, create_json, trained_tags, install_path, list_models, progress=gr.Progress()):
    global isDownloading, last_dwn
    
    number = str(random.randint(10000, 99999))
    while number == last_dwn:
        number = str(random.randint(10000, 99999))

    last_dwn = number
    
    if isDownloading:
        isDownloading = False
        return
    
    isDownloading = True
    if not os.path.exists(install_path):
        os.makedirs(install_path)
        
    path_to_new_file = os.path.join(install_path, file_name)
    
    thread = threading.Thread(target=download_file, args=(url, path_to_new_file, preview_image_html, install_path, progress))

    thread.start()
    thread.join()
    
    if create_json and not cancel_status:
        save_json_file(file_name, install_path, trained_tags)
    
    if not cancel_status:
        modelName = list_models
    else:
        modelName = None
    
    if os.path.exists(path_to_new_file):
        actual_size = os.path.getsize(path_to_new_file)
        if 'total_size' in globals():
            if actual_size != total_size:
                print(f"{path_to_new_file} Is not the right size ({actual_size} | {total_size}) Removing it.")
                os.remove(path_to_new_file)
        else:
            print(f"Error occured during download, Removing: {path_to_new_file}")
            os.remove(path_to_new_file)
    
    if isDownloading:
        isDownloading = False

    return  (
            gr.HTML.update(),
            gr.Textbox.update(value=modelName),
            number
    )

def update_dl_url(trained_tags, model_name=None, model_version=None, model_filename=None):
    if model_version:
        model_version = model_version.replace(" [Installed]", "")
    if model_filename:
        global json_data
        dl_dict = {}
        dl_url = None
        for item in json_data['items']:
            if item['name'] == model_name:
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        for file in model['files']:
                            if file['name'] == model_filename:
                                dl_url = file['downloadUrl']
                                global json_info
                                json_info = model
                                
        return  gr.Textbox.update(value=dl_url),\
                gr.Dropdown.update(interactive=True if model_filename else False),\
                gr.Button.update(interactive=True if trained_tags else False),\
                gr.Button.update(interactive=True if model_filename else False),\
                gr.Button.update(interactive=True if model_filename else False)
    else:
        return  gr.Textbox.update(value=None),\
                gr.Dropdown.update(interactive=True if model_filename else False),\
                gr.Button.update(interactive=True if trained_tags else False),\
                gr.Button.update(interactive=True if model_filename else False),\
                gr.Button.update(interactive=True if model_filename else False)

def delete_file(content_type, model_filename, model_name, list_versions):
    global last_del
    adjusted_ver = list_versions.replace(" [Installed]", "")
    model_folder = os.path.join(contenttype_folder(content_type))
    path_file = None
    for root, dirs, files in os.walk(model_folder):
        if model_filename in files:
            path_file = os.path.join(root, model_filename)
            break
        
    number = str(random.randint(10000, 99999))

    while number == last_del:
        number = str(random.randint(10000, 99999))
    
    last_del = number 
    
    if path_file:
        os.remove(path_file)
        print(f"Removed: {path_file}")
        
        base_name = os.path.splitext(path_file)[0]
        preview_image = base_name + '.preview.png'

        if os.path.exists(preview_image):
            print(f'Removed: "{preview_image}"')
            os.remove(preview_image)
            
        json_file = base_name + '.json'
        if os.path.exists(json_file):
            print(f'Removed: "{json_file}"')
            os.remove(json_file)
    
    return  gr.Button.update(interactive=False, visible=True),\
            gr.Button.update(interactive=False, visible=False),\
            gr.Button.update(interactive=False, visible=False),\
            gr.Textbox.update(value=number),\
            gr.Textbox.update(value=model_name),\
            gr.Dropdown.update(value=adjusted_ver)

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
        if version.parse(ver) >= version.parse("1.5"):
            folder = cmd_opts.lora_dir
        elif "lyco_dir" in cmd_opts:
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
    global previous_tile_count, previous_search_term
    
    if page_count in ("0", ""):
        page_count = "1"
    
    page_value = page_count.split('/')[0]
    if search_term != previous_search_term or tile_count != previous_tile_count or inputs_changed or contentChange:
        previous_search_term = search_term
        previous_tile_count = tile_count
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page=1"
    else:
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page={page_value}"
    
    if timeOut:
        if isNext:
            next_page = str(int(page_value) + 1)
        else:
            next_page = str(int(page_value) - 1)
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page={next_page}"
    
    period_type = period_type.replace(" ", "")
    query = {'types': content_type, 'sort': sort_type, 'period': period_type}
    if use_search_term != "None" and search_term:
        match use_search_term:
            case "User name":
                query |= {'username': search_term }
            case "Tag":
                query |= {'tag': search_term }
            case _:
                query |= {'query': search_term }
                
    return request_civit_api(f"{api_url}", query )

def api_next_page(next_page_url=None):
    global json_data
    if next_page_url is None:
        try: json_data['metadata']['nextPage']
        except: return
        next_page_url = json_data['metadata']['nextPage']
        next_page_url = re.sub(r'limit=\d+', f'limit={tile_count}', next_page_url)
    return request_civit_api(next_page_url)

def model_list_html(json_data, model_dict, content_type):
    global contentChange 
    contentChange = False
    allownsfw = json_data['allownsfw']
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
                
                if sortNewest:
                    if date not in sorted_models:
                        sorted_models[date] = []
                
                if any(item['modelVersions']):
                    if len(item['modelVersions'][0]['images']) > 0:
                        if item["modelVersions"][0]["images"][0]['nsfw'] != "None" and not allownsfw:
                            nsfw = 'civcardnsfw'
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
                
                if sortNewest:
                    sorted_models[date].append(model_card)
                else:
                    HTML += model_card
    
    if sortNewest:
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
    global json_data, pages, previous_inputs, inputs_changed, pageChange
    
    if json_data is None or json_data == "timeout":
        timeOut = True
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, page_count, timeOut, isNext)
        timeOut = False
        
        return return_values
        
    pageChange = True
    
    current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, tile_count)
    
    if previous_inputs and current_inputs != previous_inputs:
        inputs_changed = True
    else:
        inputs_changed = False
    
    
    previous_inputs = current_inputs

    if inputs_changed or contentChange:
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, page_count)
        return return_values
    
    if isNext:
        json_data = api_next_page()
    else:
        if json_data['metadata']['prevPage'] is not None:
            json_data = api_next_page(json_data['metadata']['prevPage'])
        else:
            json_data = None
            
    if json_data is None:
        return
    
    if json_data == "timeout":
        HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
        page_value = page_count.split('/')[0]
        hasPrev = page_value not in [0, 1]
        hasNext = page_value == 1 or hasPrev
        model_dict = {}
        pages=page_count
        
    if json_data != None and json_data != "timeout":
        json_data['allownsfw'] = show_nsfw
        (hasPrev, hasNext, pages) = pagecontrol(json_data)
        model_dict = {}
        try:
            json_data['items']
        except TypeError:
            return gr.Dropdown.update(choices=[], value=None)

        for item in json_data['items']:
            temp_nsfw = item['nsfw']
            if (not temp_nsfw or show_nsfw):
                model_dict[item['name']] = item['name']
        HTML = model_list_html(json_data, model_dict, content_type)

    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=""),\
            gr.Dropdown.update(choices=[], value=""),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False),\
            gr.Textbox.update(interactive=False, value=None),\
            gr.Dropdown.update(choices=[], value="")

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
    global json_data, pages, previous_inputs, inputs_changed, pageChange, contentChange
    if pageChange == False:
    
        current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, tile_count)
        
        if previous_inputs and current_inputs != previous_inputs:
            inputs_changed = True
        else:
            inputs_changed = False
        
        previous_inputs = current_inputs
    
    json_data = api_to_data(content_type, sort_type, period_type, use_search_term, page_count, search_term, timeOut, isNext)
    if json_data == "timeout":
        HTML = '<div style="font-size: 24px; text-align: center; margin: 50px !important;">The Civit-API has timed out, please try again.<br>The servers might be too busy or down if the issue persists.</div>'
        page_value = page_count.split('/')[0]
        hasPrev = page_value not in [0, 1]
        hasNext = page_value == 1 or hasPrev
        model_dict = {}
        pages=page_count
    
    if json_data is None:
        return
    
    if pageChange:
        pageChange = False
    
    if json_data != None and json_data != "timeout":
        json_data['allownsfw'] = show_nsfw
        (hasPrev, hasNext, pages) = pagecontrol(json_data)
        model_dict = {}
        for item in json_data['items']:
            temp_nsfw = item['nsfw']
            if (not temp_nsfw or show_nsfw):
                model_dict[item['name']] = item['name']
        
        HTML = model_list_html(json_data, model_dict, content_type)
    
    contentChange = False
    
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
            gr.Dropdown.update(choices=[], value="", interactive=False) # Sub Folder List
    )

def update_model_versions(model_name, content_type):
    global json_data, main_folder
    if model_name is not None and content_type is not None:
        versions_dict = defaultdict(list)
        installed_versions = []
        folder_location = "None"
        sub_folders = ["None"]
        model_folder = os.path.join(contenttype_folder(content_type))
        main_folder = model_folder
        for root, dirs, _ in os.walk(model_folder):
            for d in dirs:
                sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                if sub_folder:
                    sub_folders.append(f'\{sub_folder}')
        folder_location = model_folder
        if json_data != None and json_data != "timeout":
            for item in json_data['items']:
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
        return  gr.Dropdown.update(choices=display_version_names, value=default_value),\
                gr.Textbox.update(interactive=True, value=folder_location if model_name else None),\
                gr.Dropdown.update(choices=sub_folders, value=default_subfolder, interactive=True)
    else:
        return  gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(interactive=False, value=None),\
                gr.Dropdown.update(choices=[], value="", interactive=False)

def update_model_info(model_name=None, model_version=None):
    if model_version and "[Installed]" in model_version:
        BtnDown = False
        BtnDel = True
        model_version = model_version.replace(" [Installed]", "")
    else:
        BtnDown = True
        BtnDel = False
    if isDownloading:
        BtnDown = False
        BtnDel = False
    if model_name and model_version:
        global json_data
        output_html = ""
        output_training = ""
        output_basemodel = ""
        img_html = ""
        model_desc = ""
        dl_dict = {}
        allow = {}
        allownsfw = json_data['allownsfw']
        for item in json_data['items']:
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
                        model_url = model['downloadUrl']
                        img_html = '<div class="sampleimgs">'
                        for pic in model['images']:
                            nsfw = None
                            if pic['nsfw'] != "None" and not allownsfw:
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
                        
        return  gr.HTML.update(value=output_html),\
                gr.Textbox.update(value=output_training),\
                gr.Dropdown.update(choices=[k for k, v in dl_dict.items()], value=next(iter(dl_dict.keys()), None)),\
                gr.Textbox.update(value=output_basemodel),\
                gr.Button.update(visible=BtnDown, interactive=BtnDown),\
                gr.Button.update(visible=BtnDel, interactive=BtnDel)
    else:
        return  gr.HTML.update(value=None),\
                gr.Textbox.update(value=None),\
                gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(value=''),\
                gr.Button.update(visible=BtnDown),\
                gr.Button.update(visible=BtnDel, interactive=BtnDel)

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

def save_preview_image(preview_image_html, file_name, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', preview_image_html)
    
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
    except urllib.error.URLError as e:
        print(f'Error downloading preview image: {e.reason}')

def save_image_files(preview_image_html, model_filename, content_type, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', preview_image_html)
    
    name = os.path.splitext(model_filename)[0]

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    HTML = preview_image_html
    for i, img_url in enumerate(img_urls):
        filename = f'{name}_{i}.png'
        filenamethumb = f'{name}.png'
        if content_type == "TextualInversion":
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
        json.dump(json_info, f, indent=2, ensure_ascii=False)

def save_json_file(file_name, install_path, trained_tags):
    if not trained_tags:
        return trained_tags

    trained_tags = trained_tags.split(',')
    trained_tags = [tag.strip() for tag in trained_tags if not (tag.strip().startswith('<') and ':' in tag.strip() and tag.strip().endswith('>'))]
    trained_tags = ', '.join(trained_tags).strip()
    if trained_tags.endswith(','):
        trained_tags = trained_tags[:-1]

    if not os.path.exists(install_path):
        os.makedirs(install_path)

    file_name = (file_name.replace(".ckpt", ".json")
                 .replace(".safetensors", ".json")
                 .replace(".pt", ".json")
                 .replace(".yaml", ".json")
                 .replace(".zip", ".json"))
    
    path_to_new_file = os.path.join(install_path, file_name)

    if os.path.exists(path_to_new_file):
        with open(path_to_new_file, 'r') as f:
            content = json.load(f)
        content["activation text"] = trained_tags
    else:
        content = {"activation text": trained_tags}

    with open(path_to_new_file, 'w') as f:
        json.dump(content, f)

    print(f"Tags saved to: {path_to_new_file}")

    return trained_tags

def update_global_slider_value(slider_value):
    global tile_count
    tile_count = slider_value

def on_ui_tabs():    
    base_path = "extensions"
    lobe_directory = None

    for root, dirs, files in os.walk(base_path):
        for dir_name in fnmatch.filter(dirs, '*lobe*'):
            lobe_directory = os.path.join(root, dir_name)
            break
        if lobe_directory:
            break

    component_id = "lobe_toggles" if lobe_directory else "toggles"
    toggle1 = None if lobe_directory else "toggle1"
    toggle2 = None if lobe_directory else "toggle2"
    toggle3 = None if lobe_directory else "toggle3"
    
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            with gr.Column(scale=1, min_width=200):
                content_type = gr.Dropdown(label='Content Type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
            with gr.Column(scale=1, min_width=200):
                period_type = gr.Dropdown(label='Time Period:', choices=["All Time", "Year", "Month", "Week", "Day"], value="All Time", type="value")
            with gr.Column(scale=1, min_width=200):
                sort_type = gr.Dropdown(label='Sort By:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Most Downloaded", type="value")
            with gr.Column(scale=1, min_width=200):
                base_filter = gr.Dropdown(label='Filter Base Model:', multiselect=True, choices=["SD 1.4","SD 1.5","SD 2.0","SD 2.1", "SDXL 0.9", "SDXL 1.0", "Other"], value=None, type="value")
            with gr.Column(scale=1, min_width=250, elem_id=component_id):
                create_json = gr.Checkbox(label=f"Save tags after download", value=False, elem_id=toggle1)
                toggle_date = gr.Checkbox(label="Divide cards by date", value=False, elem_id=toggle2)
                show_nsfw = gr.Checkbox(label="NSFW content", value=False, elem_id=toggle3)
        with gr.Row():
            with gr.Column(scale=3,min_width=300):
                search_term = gr.Textbox(label="Search Term:", interactive=True, lines=1)
            with gr.Column(scale=2,min_width=120):
                use_search_term = gr.Radio(label="Search:", choices=["Model name", "User name", "Tag"],value="Model name")
            with gr.Column(scale=0.75,min_width=160 ):
                size_slider = gr.Slider(minimum=4, maximum=20, default=8, step=0.25, label='Tile size:')
            with gr.Column(scale=0.75,min_width=160 ):
                tile_slider = gr.Slider(label="Tile count:", min=5, max=50, value=15, step=1, max_width=100)
        with gr.Row():
            with gr.Column(scale=5):
                refresh = gr.Button(label="Refresh", value="Refresh")
            with gr.Column(scale=3,min_width=80):
                get_prev_page = gr.Button(value="Prev Page", interactive=False)
            with gr.Column(scale=3,min_width=80):
                get_next_page = gr.Button(value="Next Page", interactive=False)
            with gr.Column(scale=1,min_width=50):
                pages = gr.Textbox(label='Pages', show_label=False)
        with gr.Row():
            list_html = gr.HTML(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Please press \'Refresh\' to load selected content!</div>')
            download_start = gr.Textbox(value=None, visible=False)
            download_finish = gr.Textbox(value=None, visible=False)
            delete_finish = gr.Textbox(value=None, visible=False)
            current_model = gr.Textbox(value=None, visible=False)
        with gr.Row():
            download_progress = gr.HTML(value='<div style="min-height: 0px;"></div>', elem_id="DownloadProgress")
        with gr.Row():
            list_models = gr.Dropdown(label="Model:", choices=[], interactive=False, elem_id="quicksettings1", value=None)
            event_text = gr.Textbox(label="Event text",elem_id="eventtext1", visible=False, interactive=True, lines=1)
            list_versions = gr.Dropdown(label="Version:", choices=[], interactive=False, elem_id="quicksettings", value=None)
            install_path = gr.Textbox(label="Download Folder:", visible=True, interactive=False, max_lines=1)
            sub_folder = gr.Dropdown(label="Sub Folder:", choices=[], interactive=False, value=None)
        with gr.Row():
            txt_list = ""
            trained_tags = gr.Textbox(label='Trained Tags (if any):', value=f'{txt_list}', interactive=False, lines=1)
            base_model = gr.Textbox(label='Base Model:', value='', interactive=False, lines=1)
            model_filename = gr.Textbox(label="Model Filename:", interactive=False, value=None)
            dl_url = gr.Textbox(value=None, visible=False)
        with gr.Row():
            save_tags = gr.Button(value="Save Tags", interactive=False)
            save_images = gr.Button(value="Save Images", interactive=False)
            download_model = gr.Button(value="Download Model", interactive=False)
            cancel_model = gr.Button(value="Cancel Download", interactive=False, visible=False)
            delete_model = gr.Button(value="Delete Model", interactive=False, visible=False)
        with gr.Row():
            preview_image_html = gr.HTML()
        
        def changeInput():
            global contentChange
            contentChange = True
            
        def ToggleDate(toggle_date):
            global sortNewest
            sortNewest = toggle_date
            
        def select_subfolder(sub_folder):
            if sub_folder == "None":
                newpath = main_folder
            else:
                newpath = main_folder + sub_folder
            return gr.Textbox.update(value=newpath)
        
        toggle_date.input(
            fn=ToggleDate,
            inputs=[toggle_date]
        )
        
        content_type.input(
            fn=changeInput,
            inputs=[]
        )
        
        sub_folder.select(
            fn=select_subfolder,
            inputs=[sub_folder],
            outputs=[install_path]
        )
        
        download_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => installedCard(modelName)"
        )
        
        list_html.change(
            fn=None,
            inputs=[base_filter],
            _js="(baseModelValue) => filterByBaseModel(baseModelValue)"
        )
        
        base_filter.change(
            fn=None,
            inputs=[base_filter],
            _js="(baseModelValue) => filterByBaseModel(baseModelValue)"
        )
        
        list_html.change(
            fn=None,
            inputs=[size_slider],
            _js="(size) => updateCardSize(size, size * 1.5)"
        )

        size_slider.change(
            fn=None,
            inputs=[size_slider],
            _js="(size) => updateCardSize(size, size * 1.5)"
        )
        
        download_model.click(
            fn=start_download,
            inputs=[
                list_models,
                model_filename
                ],
            outputs=[
                download_model,
                cancel_model,
                download_start,
                download_progress
            ]
        )
        
        download = download_start.change(
            fn=download_file_thread,
            inputs=[
                dl_url,
                model_filename,
                preview_image_html,
                create_json,
                trained_tags,
                install_path,
                list_models
                ],
            outputs=[
                download_progress,
                current_model,
                download_finish
            ]
        )
        
        delete_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => removedCard(modelName)"
        )
        
        delete_model.click(
            fn=delete_file,
            inputs=[
                content_type,
                model_filename,
                list_models,
                list_versions
                ],
            outputs=[
                download_model,
                cancel_model,
                delete_model,
                delete_finish,
                current_model,
                list_versions
            ]
        )
        
        cancel_model.click(
            fn=download_cancel,
            cancels=[download],
            inputs=[
                content_type,
                list_models,
                list_versions
                ],
            outputs=[
                download_model,
                cancel_model,
                download_progress
            ]
        )
        
        download_finish.change(
            fn=finish_download,
            inputs=[],
            outputs=[
                download_model,
                cancel_model,
                download_progress
            ]
        )
        
        tile_slider.release(
            fn=update_global_slider_value,
            inputs=[tile_slider],
            outputs=[]
        )
        
        save_tags.click(
            fn=save_json_file,
            inputs=[
                model_filename,
                install_path,
                trained_tags
                ],
            outputs=[trained_tags]
        )
        
        save_images.click(
            fn=save_image_files,
            inputs=[
                preview_image_html,
                model_filename,
                content_type,
                install_path
                ],
            outputs=[]
        )
        
        list_models.change(
            fn=update_model_versions,
            inputs=[
                list_models,
                content_type
            ],
            outputs=[
                list_versions,
                install_path,
                sub_folder
            ]
        )
        
        list_versions.change(
            fn=update_model_info,
            inputs=[
                list_models,
                list_versions
                ],
            outputs=[
                preview_image_html,
                trained_tags,
                model_filename,
                base_model,
                download_model,
                delete_model
            ]
        )
        
        model_filename.change(
            fn=update_dl_url,
            inputs=[
                trained_tags,
                list_models,
                list_versions,
                model_filename
                ],
            outputs=[
                dl_url,
                list_versions,
                save_tags,
                save_images,
                download_model
                ]
        )
        
        sort_type.input(
            fn=None
        )
        
        get_next_page.click(
            fn=update_next_page,
            inputs=[
                show_nsfw,
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model,
                install_path,
                sub_folder
            ]
        )
        
        refresh.click(
            fn=update_model_list,
            inputs=[
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                show_nsfw,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model,
                install_path,
                sub_folder
            ],
        )
        
        get_prev_page.click(
            fn=update_prev_page,
            inputs=[
                show_nsfw,
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model
            ]
        )
        
        def update_models_dropdown(model_name, content_type):
            model_name = re.sub(r'\.\d{3}$', '', model_name)
            (ret_versions, install_path, sub_folder)=update_model_versions(model_name, content_type)
            (html,d, f, _, DwnButton, _) = update_model_info(model_name,ret_versions['value'])
            (dl_url, _, _, _, _) = update_dl_url(None, model_name, ret_versions['value'], f['value'])
            return  gr.Dropdown.update(value=model_name),ret_versions ,html,dl_url['value'],d,f,install_path['value'],sub_folder, DwnButton
        
        event_text.change(
            fn=update_models_dropdown,
            inputs=[
                event_text,
                content_type
                ],
            outputs=[
                list_models,
                list_versions,
                preview_image_html,
                dl_url,
                trained_tags,
                model_filename,
                install_path,
                sub_folder,
                download_model
            ]
        )

    return (civitai_interface, "Civit AI", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)
