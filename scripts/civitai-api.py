import requests
import json
import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks
import time
import threading
import urllib.request
import urllib.parse
import urllib.error
import os
import fnmatch
from tqdm import tqdm
import re
from collections import defaultdict
from requests.exceptions import ConnectionError
from modules.shared import opts, cmd_opts
from modules.paths import models_path
import shutil
from html import escape

recently_downloaded_model = None
json_data = None
json_info = None
previous_search_term = None
previous_tile_count = None
previous_inputs = None
inputs_changed = False
isDownloading = False
pageChange = False
page_count = 1
tile_count = 15

def download_file(url, file_name, preview_image_html, content_type):
    max_retries = 5
    retry_delay = 10
    
    if os.path.exists(file_name):
        os.remove(file_name)
    
    while True:
        if os.path.exists(file_name):
            downloaded_size = os.path.getsize(file_name)
            headers = {"Range": f"bytes={downloaded_size}-"}
            
        else:
            downloaded_size = 0
            headers = {}

        tokens = re.split(re.escape('\\'), file_name)
        file_name_display = tokens[-1]
        progress = tqdm(total=1000000000, unit="B", unit_scale=True, desc=f"Downloading {file_name_display}", initial=downloaded_size, leave=False)
        global isDownloading
        with open(file_name, "ab") as f:
            while isDownloading:
                try:
                    response = requests.get(url, headers=headers, stream=True)
                    total_size = int(response.headers.get("Content-Length", 0))
                    if total_size == 0:
                        total_size = downloaded_size
                        
                    progress.total = total_size 
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
                        if (isDownloading == False):
                            response.close
                            break
                    downloaded_size = os.path.getsize(file_name)
                    break
                
                except ConnectionError as e:
                    max_retries -= 1
                    if max_retries == 0:
                        raise e

                    time.sleep(retry_delay)

        progress.close()
        
        if (isDownloading == False):
            break
        
        isDownloading = False
        downloaded_size = os.path.getsize(file_name)
        if downloaded_size >= total_size:
            print(f"Model saved to: {file_name}")
            save_preview_image(preview_image_html, file_name, content_type)
            
        else:
            print(f"Error: File download failed. Retrying... {file_name_display}")

def save_preview_image(preview_image_html, file_name, content_type):
    model_folder = os.path.join(contenttype_folder(content_type))
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)
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
            with open(os.path.join(model_folder, filename), 'wb') as f:
                f.write(url.read())
    except urllib.error.URLError as e:
        print(f'Error downloading preview image: {e.reason}')

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

def download_file_thread(url, file_name, content_type, model_name, delete_old_ver, preview_image_html, create_json, trained_tags):
    global isDownloading, recently_downloaded_model
    
    recently_downloaded_model = model_name
    
    if isDownloading:
        isDownloading = False
        return
    isDownloading = True
    model_folder = os.path.join(contenttype_folder(content_type))
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)
    path_to_new_file = os.path.join(model_folder, file_name)
    
    thread = threading.Thread(target=download_file, args=(url, path_to_new_file, preview_image_html, content_type))

    thread.start()
    thread.join()
    
    return_values = update_model_list(*previous_inputs[:-1], delete_old_ver)
    
    if create_json == True:
        save_json_file(file_name, content_type, trained_tags)
    
    return return_values

def save_json_file(file_name, content_type, trained_tags):
    if not trained_tags:
        return trained_tags

    trained_tags = trained_tags.split(',')
    trained_tags = [tag.strip() for tag in trained_tags if not (tag.strip().startswith('<') and ':' in tag.strip() and tag.strip().endswith('>'))]
    trained_tags = ', '.join(trained_tags).strip()
    if trained_tags.endswith(','):
        trained_tags = trained_tags[:-1]

    model_folder = os.path.join(contenttype_folder(content_type))
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    path_to_new_file = os.path.join(model_folder, 
                                    file_name.replace(".ckpt", ".json")
                                    .replace(".safetensors", ".json")
                                    .replace(".pt", ".json")
                                    .replace(".yaml", ".json")
                                    .replace(".zip", ".json"))

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

def api_to_data(content_type, sort_type, period_type, use_search_term, search_term=None):
    global previous_tile_count, previous_search_term
    
    if search_term != previous_search_term or tile_count != previous_tile_count or inputs_changed == True:
        previous_search_term = search_term
        previous_tile_count = tile_count
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page=1"
    else:
        api_url = f"https://civitai.com/api/v1/models?limit={tile_count}&page={page_count}"
    
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

def model_list_html(json_data, model_dict, content_type, DeleteOld):
    global recently_downloaded_model
    allownsfw = json_data['allownsfw']
    HTML = '<div class="column civmodellist">'
    
    for item in json_data['items']:
        for k, model in model_dict.items():
            if model_dict[k].lower() == item['name'].lower():
                model_name = escape(item["name"].replace("'", "\\'"), quote=True)
                nsfw = ""
                installstatus = ""
                latest_version_installed = False
                
                if any(item['modelVersions']):
                    if len(item['modelVersions'][0]['images']) > 0:
                        if item["modelVersions"][0]["images"][0]['nsfw'] != "None" and not allownsfw:
                            nsfw = 'civcardnsfw'
                        imgtag = f'<img src={item["modelVersions"][0]["images"][0]["url"]}"></img>'
                    else:
                        imgtag = f'<img src="./file=html/card-no-preview.png"></img>'
                    
                    model_folder = os.path.join(contenttype_folder(content_type))
                    
                    if os.path.exists(model_folder):
                        existing_files = os.listdir(model_folder)
                        
                        for version in reversed(item['modelVersions']):
                            for file in version['files']:
                                file_name = file['name']
                                if file_name in existing_files:
                                    if version == item['modelVersions'][0]:
                                        latest_version_installed = True
                                        break
                                    elif not latest_version_installed:
                                        installstatus = "civmodelcardoutdated"

                            if latest_version_installed:
                                installstatus = "civmodelcardinstalled"
                                break
                        
                    if DeleteOld and latest_version_installed and model_name == recently_downloaded_model:
                        latest_version_files = [f['name'] for f in item['modelVersions'][0]['files']]
                        for version in item['modelVersions'][1:]:
                            for file in version['files']:
                                file_name = file['name']
                                if file_name.lower() in [f.lower() for f in latest_version_files]:
                                    continue
                                
                                base_model = version['baseModel']
                                model_folder = os.path.join(contenttype_folder(content_type))
                                if not os.path.exists(model_folder):
                                    os.makedirs(model_folder)
                                path_file = os.path.join(model_folder, file_name)
                                
                                if os.path.exists(path_file):
                                    print(f"Removed {path_file}")
                                    os.remove(path_file)
                                    
                                    base_name = os.path.splitext(path_file)[0]
                                    preview_image = base_name + '.preview.png'
                                    
                                    if os.path.exists(preview_image):
                                        print(f"Removed {preview_image}")
                                        os.remove(preview_image)
                                    

                HTML = HTML + f'<figure class="civmodelcard {nsfw} {installstatus}" onclick="select_model(\'{model_name}\')">' \
                             + imgtag \
                             + f'<figcaption>{item["name"]}</figcaption></figure>'
    
    HTML = HTML + '</div>'
    recently_downloaded_model = None
    return HTML

def update_prev_page(show_nsfw, content_type, delete_old_ver, sort_type, period_type, use_search_term, search_term):
    return update_next_page(show_nsfw, content_type, delete_old_ver, sort_type, period_type, use_search_term, search_term, isNext=False)

def update_next_page(show_nsfw, content_type, delete_old_ver, sort_type, period_type, use_search_term, search_term, isNext=True):
    global json_data, pages, previous_inputs, inputs_changed, pageChange
    
    pageChange = True
    
    current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, tile_count)
    
    if previous_inputs and current_inputs != previous_inputs:
        inputs_changed = True
    else:
        inputs_changed = False
    
    
    previous_inputs = current_inputs

    if inputs_changed == True:
        return_values = update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, delete_old_ver)
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
    HTML = model_list_html(json_data, model_dict, content_type, delete_old_ver)

    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=""),\
            gr.Dropdown.update(choices=[], value=""),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False)

def pagecontrol(json_data):
    pages_ctrl = f"{json_data['metadata']['currentPage']}/{json_data['metadata']['totalPages']}"
    hasNext = False
    hasPrev = False
    if 'nextPage' in json_data['metadata']:
        hasNext = True
    if 'prevPage' in json_data['metadata']:
        hasPrev = True
    return hasPrev,hasNext,pages_ctrl

def update_model_list(content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, delete_old_ver):
    global json_data, pages, previous_inputs, inputs_changed, pageChange
    
    if pageChange == False:
    
        current_inputs = (content_type, sort_type, period_type, use_search_term, search_term, show_nsfw, tile_count)
        
        if previous_inputs and current_inputs != previous_inputs:
            inputs_changed = True
        else:
            inputs_changed = False
        
        previous_inputs = current_inputs
    
    json_data = api_to_data(content_type, sort_type, period_type, use_search_term, search_term)
    if json_data is None:
        return
    
    if pageChange == True:
        pageChange = False
        
    json_data['allownsfw'] = show_nsfw
    (hasPrev, hasNext, pages) = pagecontrol(json_data)
    model_dict = {}
    for item in json_data['items']:
        temp_nsfw = item['nsfw']
        if (not temp_nsfw or show_nsfw):
            model_dict[item['name']] = item['name']
    
    HTML = model_list_html(json_data, model_dict, content_type, delete_old_ver)
    
    return  gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value="", interactive=True),\
            gr.Dropdown.update(choices=[], value=""),\
            gr.HTML.update(value=HTML),\
            gr.Button.update(interactive=hasPrev),\
            gr.Button.update(interactive=hasNext),\
            gr.Textbox.update(value=pages),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False),\
            gr.Button.update(interactive=False)
            
def update_model_versions(model_name=None, content_type=None):
    if model_name is not None and content_type is not None:
        global json_data
        versions_dict = defaultdict(list)
        installed_versions = []

        for item in json_data['items']:
            if item['name'] == model_name:
                for version in item['modelVersions']:
                    versions_dict[version['name']].append(item["name"])
                    for file in version['files']:
                        file_name = file['name']
                        model_folder = os.path.join(contenttype_folder(content_type))
                        existing_files = os.listdir(model_folder)
                        if file_name in existing_files:
                            installed_versions.append(version['name'])
                            break

        version_names = list(versions_dict.keys())
        display_version_names = [f"{v} [Installed]" if v in installed_versions else v for v in version_names]
        default_installed = next((f"{v} [Installed]" for v in installed_versions), None)
        default_value = default_installed or next(iter(version_names), None)

        return gr.Dropdown.update(choices=display_version_names, value=default_value)
    else:
        return gr.Dropdown.update(choices=[], value=None)

def update_dl_url(model_name=None, model_version=None, model_filename=None):
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
        return gr.Textbox.update(value=dl_url)
    else:
        return gr.Textbox.update(value=None)

def update_model_info(model_name=None, model_version=None):
    if model_version:
        model_version = model_version.replace(" [Installed]", "")
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
                gr.Textbox.update(value=output_basemodel)
    else:
        return  gr.HTML.update(value=None),\
                gr.Textbox.update(value=None),\
                gr.Dropdown.update(choices=[], value=None),\
                gr.Textbox.update(value='')

def request_civit_api(api_url=None, payload=None):
    if payload is not None:
        payload = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    try:
        response = requests.get(api_url, params=payload, timeout=(10,15))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Request error: ", e)
        exit()
    else:
        response.encoding  = "utf-8"
        data = json.loads(response.text)
    return data

def save_image_files(preview_image_html, model_filename, list_models, content_type, base_model):
    model_folder = os.path.join(contenttype_folder(content_type))
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)
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
        print(img_url, model_folder, filename)
        try:
            with urllib.request.urlopen(img_url) as url:
                with open(os.path.join(model_folder, filename), 'wb') as f:
                    f.write(url.read())
                    if i == 0 and not os.path.exists(os.path.join(model_folder, filenamethumb)):
                        shutil.copy2(os.path.join(model_folder, filename),os.path.join(model_folder, filenamethumb))
                    print("Downloaded images.")
                    
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    path_to_new_file = os.path.join(model_folder, f'{name}.html')
    with open(path_to_new_file, 'wb') as f:
        f.write(HTML.encode('utf8'))
    path_to_new_file = os.path.join(model_folder, f'{name}.civitai.info')
    with open(path_to_new_file, mode="w", encoding="utf-8") as f:
        json.dump(json_info, f, indent=2, ensure_ascii=False)

def update_global_slider_value(slider_value):
    global tile_count
    tile_count = slider_value

def update_global_page_count(page_value):
    global page_count
    current_page = page_value.split('/')[0]
    try:
        page_count = int(current_page)
    except:
        page_count = 1

def on_ui_tabs():
    global list_models, list_versions, list_html, get_prev_page, get_next_page, pages
    
    base_path = "extensions"
    lobe_directory = None

    for root, dirs, files in os.walk(base_path):
        for dir_name in fnmatch.filter(dirs, '*lobe*'):
            lobe_directory = os.path.join(root, dir_name)
            break
        if lobe_directory:
            break

    component_id = "lobe_active" if lobe_directory else None
    
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            with gr.Column(scale=1):
                content_type = gr.Dropdown(label='Content type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
            with gr.Column(scale=1, min_width=250):
                period_type = gr.Dropdown(label='Time period:', choices=["All Time", "Year", "Month", "Week", "Day"], value="All Time", type="value")
            with gr.Column(scale=1, min_width=250):
                sort_type = gr.Dropdown(label='Sort by:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Most Downloaded", type="value")
            with gr.Column(scale=1, min_width=250, elem_id=component_id):
                delete_old_ver = gr.Checkbox(label=f"Delete old version after download", value=False)
                create_json = gr.Checkbox(label=f"Save tags after download", value=False)
                show_nsfw = gr.Checkbox(label="NSFW content", value=False)
        with gr.Row():
            with gr.Column(scale=5):
                search_term = gr.Textbox(label="Search Term:", interactive=True, lines=1)
            with gr.Column(scale=3,min_width=80):
                use_search_term = gr.Radio(label="Search:", choices=["Model name", "User name", "Tag"],value="Model name")
            with gr.Column(scale=1,min_width=160 ):
                tile_slider = gr.Slider(label="Tile count:", min=5, max=50, value=15, step=1, max_width=100)
        with gr.Row():
            with gr.Column(scale=4):
                get_list_from_api = gr.Button(label="Refresh", value="Refresh")
            with gr.Column(scale=2,min_width=80):
                get_prev_page = gr.Button(value="Prev Page", interactive=False)
            with gr.Column(scale=2,min_width=80):
                get_next_page = gr.Button(value="Next Page", interactive=False)
            with gr.Column(scale=1,min_width=80):
                pages = gr.Textbox(label='Pages',show_label=False)
        with gr.Row():
            list_html = gr.HTML()
        with gr.Row():
            list_models = gr.Dropdown(label="Model:", choices=[], interactive=False, elem_id="quicksettings1", value=None)
            event_text = gr.Textbox(label="Event text",elem_id="eventtext1", visible=False, interactive=True, lines=1)
            list_versions = gr.Dropdown(label="Version:", choices=[], interactive=False, elem_id="quicksettings", value=None)
        with gr.Row():
            txt_list = ""
            trained_tags = gr.Textbox(label='Trained Tags (if any):', value=f'{txt_list}', interactive=False, lines=1)
            base_model = gr.Textbox(label='Base Model:', value='', interactive=False, lines=1)
            model_filename = gr.Textbox(label="Model Filename:", interactive=False, value=None)
            dl_url = gr.Textbox(value=None, visible=False)
        with gr.Row():
            save_text = gr.Button(value="Save Tags", interactive=False)
            save_images = gr.Button(value="Save Images", interactive=False)
            download_model = gr.Button(value="Download Model", interactive=False)
        with gr.Row():
            preview_image_html = gr.HTML()
        
        for event in [pages.change, pages.submit]:
            event(
            fn=update_global_page_count,
            inputs=[pages],
            outputs=[]
        )
        
        tile_slider.release(
            fn=update_global_slider_value,
            inputs=[tile_slider],
            outputs=[]
        )
        
        save_text.click(
            fn=save_json_file,
            inputs=[
                model_filename,
                content_type,
                trained_tags
                ],
            outputs=[trained_tags]
        )
        
        save_images.click(
            fn=save_image_files,
            inputs=[
                preview_image_html,
                model_filename,
                list_models,
                content_type,
                base_model
                ],
            outputs=[]
        )
        
        download_model.click(
            fn=download_file_thread,
            inputs=[
                dl_url,
                model_filename,
                content_type,
                list_models,
                delete_old_ver,
                preview_image_html,
                create_json,
                trained_tags
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,            
                get_prev_page,
                get_next_page,
                pages
            ]
        )
        
        list_models.change(
            fn=update_model_versions,
            inputs=[
                list_models,
                content_type
            ],
            outputs=[list_versions]
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
                base_model
            ]
        )
        
        model_filename.change(
            fn=update_dl_url,
            inputs=[
                list_models,
                list_versions, 
                model_filename
                ],
            outputs=[dl_url]
        )
        
        get_next_page.click(
            fn=update_next_page,
            inputs=[
                show_nsfw,
                content_type,
                delete_old_ver,
                sort_type,
                period_type,
                use_search_term,
                search_term
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_text,
                save_images,
                download_model
            ]
        )
        
        get_list_from_api.click(
            fn=update_model_list,
            inputs=[
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                show_nsfw,
                delete_old_ver
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_text,
                save_images,
                download_model
            ]
        )
        
        get_prev_page.click(
            fn=update_prev_page,
            inputs=[
                show_nsfw,
                content_type,
                delete_old_ver,
                sort_type,
                period_type,
                use_search_term,
                search_term
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_text,
                save_images,
                download_model
            ]
        )
        
        def update_models_dropdown(model_name, content_type):
            model_name = re.sub(r'\.\d{3}$', '', model_name)
            ret_versions=update_model_versions(model_name, content_type)
            (html,d, f, base_model) = update_model_info(model_name,ret_versions['value'])
            dl_url = update_dl_url(model_name, ret_versions['value'], f['value'])
            return gr.Dropdown.update(value=model_name),ret_versions ,html,dl_url,d,f,base_model
        
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
                model_filename
            ]
        )

        def unlock_buttons(list_models, trained_tags):
            if list_models:
                return  gr.Dropdown.update(interactive=True),\
                        gr.Button.update(interactive=True if trained_tags else False),\
                        gr.Button.update(interactive=True),\
                        gr.Button.update(interactive=True)
            else:
                return  gr.Dropdown.update(interactive=False, value=""),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False),\
                        gr.Button.update(interactive=False)
        
        list_models.change(
            fn=unlock_buttons,
            inputs=[
                list_models,
                trained_tags
                ],
            outputs=[
                list_versions,
                save_text,
                save_images,
                download_model
            ]
        )

    return (civitai_interface, "Civit AI", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)
