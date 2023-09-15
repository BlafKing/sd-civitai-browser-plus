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

def delete_model(delete_finish, content_type, model_filename, model_name, list_versions):
    max_delete = 3
    gr_components = _api.update_model_versions(model_name, content_type)
    
    (model_name, ver_value, ver_choices) = _file.card_update(gr_components, model_name, list_versions, False)
    
    model_folder = os.path.join(_api.contenttype_folder(content_type))
    path_file = None
    base_name = os.path.splitext(model_filename)[0]

    for root, dirs, files in os.walk(model_folder):
        for file in files:
            file_base_name = os.path.splitext(file)[0]
            if base_name == file_base_name or f"{base_name}.preview" == file_base_name:
                path_file = os.path.join(root, file)
                if os.path.isfile(path_file):
                    try:
                        send2trash(path_file)
                        print(f"Model moved to trash: {path_file}")
                    except:
                        os.remove(path_file)
                        print(f"Model deleted: {path_file}")
            
    number = _download.random_number(delete_finish)
    
    return (
            gr.Button.update(interactive=False, visible=True),  # Download Button
            gr.Button.update(interactive=False, visible=False),  # Cancel Button
            gr.Button.update(interactive=False, visible=False),  # Delete Button
            gr.Textbox.update(value=number),  # Delete Finish Trigger
            gr.Textbox.update(value=model_name),  # Current Model 
            gr.Dropdown.update(value=ver_value, choices=ver_choices)  # Version List
    )

def save_preview(preview_html, file_name, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', preview_html)
    
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

def save_images(preview_html, model_filename, content_type, install_path):
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    img_urls = re.findall(r'src=[\'"]?([^\'" >]+)', preview_html)
    
    name = os.path.splitext(model_filename)[0]

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    HTML = preview_html
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
        json.dump(gl.json_info, f, indent=2, ensure_ascii=False)

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
        with open(path_to_new_file, 'r') as f:
            content = json.load(f)
        content["activation text"] = trained_tags
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
    return hash_value

def save_all_json(file_path):
    model_hash = gen_sha256(file_path)

    api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{model_hash}"
    
    try:
        response = requests.get(api_url, timeout=20)
        
        if response.status_code == 200:
            data = response.json()

            trained_words = data.get("trainedWords", "")

            if not trained_words:
                return

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
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = {}

                existing_data["activation text"] = trained_tags
                with open(json_file, 'w') as f:
                    json.dump(existing_data, f)
            else:
                content = {"activation text": trained_tags}
                with open(json_file, 'w') as f:
                    json.dump(content, f)

            print(f"Tags saved as JSON in {json_file}")
        else:
            print(f"Failed to fetch tags for {file_path}")
    
    except requests.exceptions.Timeout:
        print(f"Request timed out for {file_path}. Skipping...")
    except Exception as e:
        print(f"An error occurred for {file_path}: {str(e)}")
        
def save_all_tags(items, tag_finish, progress=gr.Progress()):
    gl.save_tags = True
    number = _download.random_number(tag_finish)
    if not items:
        progress(0, desc=f"No folder selected.")
        time.sleep(2)
        return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                gr.Textbox.update(value=number))
    
    folders_to_check = []
    for item in items:
        folder = _api.contenttype_folder(item)
        if folder:
            folders_to_check.append(folder)

    total_files = 0
    files_done = 0

    for folder in folders_to_check:
        files = list_files([folder])
        total_files += len(files)

    if total_files == 0:
        progress(1, desc=f"No files in selected folder.")
        time.sleep(2)
        gl.save_tags = False
        return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                        gr.Textbox.update(value=number))
        
    for folder in folders_to_check:
        files = list_files([folder])
        for file_path in files:
            if gl.cancel_status:
                progress(files_done / total_files, desc=f"Saving tags cancelled.")
                time.sleep(2)
                gl.save_tags = False
                
                return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
                        gr.Textbox.update(value=number))
            file_name = os.path.basename(file_path)
            progress(files_done / total_files, desc=f"Processing file: {file_name}")
            save_all_json(file_path)
            files_done += 1

    progress(1, desc=f"All files are processed!")
    time.sleep(2)
    gl.save_tags = False
    return (gr.HTML.update(value='<div style="min-height: 0px;"></div>'),
            gr.Textbox.update(value=number))

def save_tag_start(tag_start):
    number = _download.random_number(tag_start)
    return (
        gr.Textbox.update(value=number),
        gr.Button.update(interactive=False, visible=False),
        gr.Button.update(interactive=True, visible=True),
        gr.HTML.update(value='<div style="min-height: 100px;"></div>')
    )

def save_tag_finish():
    return (
        gr.Button.update(interactive=True, visible=True),
        gr.Button.update(interactive=False, visible=False)
    )

def cancel_tag():
    gl.cancel_status = True
    
    while True:
        if not gl.save_tags:
            gl.cancel_status = False
            return
        else:
            time.sleep(0.5)
            continue
