import gradio as gr
from modules import script_callbacks, shared
import os
import fnmatch
import re
from modules.shared import opts
import scripts.civitai_global as gl
import scripts.civitai_download as _download
import scripts.civitai_file_manage as _file
import scripts.civitai_api as _api

gl.init()

def insert_sub(model_name, version_name):
    insert_sub = getattr(opts, "insert_sub", True)
    try:
        sub_folders = ["None"]
        try:
            version = version_name.replace(" [Installed]", "")
        except:
            version = version_name
        
        if model_name is not None:
            selected_content_type = None
            for item in gl.json_data['items']:
                if item['name'] == model_name:
                    selected_content_type = item['type']
            
            model_folder = os.path.join(_api.contenttype_folder(selected_content_type))
            for root, dirs, _ in os.walk(model_folder):
                for d in dirs:
                    sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                    if sub_folder:
                        sub_folders.append(f'{os.sep}{sub_folder}')
        
        sub_folders.remove("None")
        sub_folders = sorted(sub_folders)
        sub_folders.insert(0, "None")
        if insert_sub:
            sub_folders.insert(1, os.path.join(os.sep, model_name))
            sub_folders.insert(2, os.path.join(os.sep, model_name, version))
        
        list = set()
        sub_folders = [x for x in sub_folders if not (x in list or list.add(x))]
        
        return gr.Dropdown.update(choices=sub_folders)
    except:
        return gr.Dropdown.update(choices=None)

def on_ui_tabs():    
    use_LORA = getattr(opts, "use_LORA", False)
    base_path = "extensions"
    lobe_directory = None

    for root, dirs, files in os.walk(base_path):
        for dir_name in fnmatch.filter(dirs, '*lobe*'):
            lobe_directory = os.path.join(root, dir_name)
            break

    component_id = "lobe_toggles" if lobe_directory else "toggles"
    toggle1 = None if lobe_directory else "toggle1"
    toggle2 = None if lobe_directory else "toggle2"
    toggle3 = None if lobe_directory else "toggle3"
    
    if use_LORA:
        tag_choices = ["Checkpoint", "Hypernetwork", "TextualInversion", "AestheticGradient", "LORA", "VAE", "Controlnet", "Poses"] 
    else:
        tag_choices = ["Checkpoint", "Hypernetwork", "TextualInversion", "AestheticGradient", "LORA", "LoCon", "VAE", "Controlnet", "Poses"]
    
    with gr.Blocks() as civitai_interface:
        with gr.Tab("Browser"):
            with gr.Row():
                with gr.Column(scale=2, min_width=200):
                    content_type = gr.Dropdown(label='Content Type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value=None, type="value", multiselect=True)
                with gr.Column(scale=2, min_width=200):
                    period_type = gr.Dropdown(label='Time Period:', choices=["All Time", "Year", "Month", "Week", "Day"], value="All Time", type="value")
                with gr.Column(scale=2, min_width=200):
                    sort_type = gr.Dropdown(label='Sort By:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Most Downloaded", type="value")
                with gr.Column(scale=2, min_width=200):
                    base_filter = gr.Dropdown(label='Filter Base Model:', multiselect=True, choices=["SD 1.4","SD 1.5","SD 2.0","SD 2.1", "SDXL 0.9", "SDXL 1.0", "Other"], value=None, type="value")
                with gr.Column(scale=1, min_width=200, elem_id=component_id):
                    create_json = gr.Checkbox(label=f"Save tags after download", value=False, elem_id=toggle1)
                    toggle_date = gr.Checkbox(label="Divide cards by date", value=False, elem_id=toggle2)
                    show_nsfw = gr.Checkbox(label="NSFW content", value=False, elem_id=toggle3)
            with gr.Row():
                with gr.Column(scale=3,min_width=300):
                    search_term = gr.Textbox(label="Search Term (press ctrl+Enter or alt+Enter to search):", interactive=True, lines=1)
                with gr.Column(scale=2,min_width=120):
                    use_search_term = gr.Radio(label="Search:", choices=["Model name", "User name", "Tag"],value="Model name")
                with gr.Column(scale=1,min_width=160 ):
                    size_slider = gr.Slider(minimum=4, maximum=20, value=8, step=0.25, label='Tile size:')
                with gr.Column(scale=1,min_width=160 ):
                    tile_slider = gr.Slider(label="Tile count:", minimum=1, maximum=100, value=15, step=1, max_width=100)
            with gr.Row():
                with gr.Column(scale=5):
                    refresh = gr.Button(label="Refresh", value="Refresh", elem_id="refreshBtn")
                with gr.Column(scale=3,min_width=80):
                    get_prev_page = gr.Button(value="Prev Page", interactive=False)
                with gr.Column(scale=3,min_width=80):
                    get_next_page = gr.Button(value="Next Page", interactive=False)
                with gr.Column(scale=1,min_width=50):
                    pages = gr.Textbox(label='Pages', show_label=False)
            with gr.Row():
                list_html = gr.HTML(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Please press \'Refresh\' to load selected content!</div>')
            with gr.Row():
                download_progress = gr.HTML(value='<div style="min-height: 0px;"></div>', elem_id="DownloadProgress")
            with gr.Row():
                list_models = gr.Dropdown(label="Model:", choices=[], interactive=False, elem_id="quicksettings1", value=None)
                list_versions = gr.Dropdown(label="Version:", choices=[], interactive=False, elem_id="quicksettings", value=None)
                file_list = gr.Dropdown(label="File:", choices=[], interactive=False, elem_id="file_list", value=None)
            with gr.Row():
                with gr.Column(scale=4):
                    install_path = gr.Textbox(label="Download Folder:", visible=True, interactive=False, max_lines=1)
                with gr.Column(scale=2):
                    sub_folder = gr.Dropdown(label="Sub Folder:", choices=[], interactive=False, value=None)
            with gr.Row():
                with gr.Column(scale=13):
                    trained_tags = gr.Textbox(label='Trained Tags (if any):', value=None, interactive=False, lines=1)
                with gr.Column(scale=1, min_width=120):
                    base_model = gr.Textbox(label='Base Model:', value='', interactive=False, lines=1)
                with gr.Column(scale=5):
                    model_filename = gr.Textbox(label="Model Filename:", interactive=False, value=None)
            with gr.Row():
                save_tags = gr.Button(value="Save Tags", interactive=False)
                save_images = gr.Button(value="Save Images", interactive=False)
                download_model = gr.Button(value="Download Model", interactive=False)
                cancel_model = gr.Button(value="Cancel Download", interactive=False, visible=False)
                delete_model = gr.Button(value="Delete Model", interactive=False, visible=False)
            with gr.Row():
                preview_html = gr.HTML(elem_id="civitai_preview_html")
        with gr.Tab("Update Models"):
            with gr.Row():
                selected_tags = gr.CheckboxGroup(elem_id="selected_tags", label="Scan for:", choices=tag_choices)
            with gr.Row():
                save_all_tags = gr.Button(value="Update assigned tags", interactive=True, visible=True)
                cancel_all_tags = gr.Button(value="Cancel updating tags", interactive=False, visible=False)
            with gr.Row():
                tag_progress = gr.HTML(value='<div style="min-height: 0px;"></div>')
            with gr.Row():
                ver_search = gr.Button(value="Scan for available updates", interactive=True, visible=True)
                cancel_ver_search = gr.Button(value="Cancel updates scan", interactive=False, visible=False)
                load_to_browser = gr.Button(value="Load outdated models to browser", interactive=False, visible=False)
            with gr.Row():
                version_progress = gr.HTML(value='<div style="min-height: 0px;"></div>')
            with gr.Row():
                load_installed = gr.Button(value="Load all installed models", interactive=True, visible=True)
                cancel_installed = gr.Button(value="Cancel loading models", interactive=False, visible=False)
                load_to_browser_installed = gr.Button(value="Load installed models to browser", interactive=False, visible=False)
            with gr.Row():
                installed_progress = gr.HTML(value='<div style="min-height: 0px;"></div>')
                
        #Invisible triggers/variables
        model_id = gr.Textbox(value=None, visible=False)
        dl_url = gr.Textbox(value=None, visible=False)
        event_text = gr.Textbox(elem_id="eventtext1", visible=False)
        download_start = gr.Textbox(value=None, visible=False)
        download_finish = gr.Textbox(value=None, visible=False)
        tag_start = gr.Textbox(value=None, visible=False)
        tag_finish = gr.Textbox(value=None, visible=False)
        ver_start = gr.Textbox(value=None, visible=False)
        ver_finish = gr.Textbox(value=None, visible=False)
        installed_start = gr.Textbox(value=None, visible=None)
        installed_finish = gr.Textbox(value=None, visible=None)
        delete_finish = gr.Textbox(value=None, visible=False)
        current_model = gr.Textbox(value=None, visible=False)
        current_sha256 = gr.Textbox(value=None, visible=False)
                                                                                    
        def changeInput():
            gl.contentChange = True
            
        def ToggleDate(toggle_date):
            gl.sortNewest = toggle_date
            
        def select_subfolder(sub_folder):
            if sub_folder == "None":
                newpath = gl.main_folder
            else:
                newpath = gl.main_folder + sub_folder
            return gr.Textbox.update(value=newpath)
        
        toggle_date.input(
            fn=ToggleDate,
            inputs=[toggle_date]
        )
        
        def update_tile_count(slider_value):
            gl.tile_count = slider_value
        
        tile_slider.release(
            fn=update_tile_count,
            inputs=[tile_slider],
            outputs=[]
        )
        
        content_type.change(
            fn=changeInput,
            inputs=[]
        )
        
        sub_folder.select(
            fn=select_subfolder,
            inputs=[sub_folder],
            outputs=[install_path]
        )
        
        ver_search.click(
            fn=_file.start_ver_search,
            inputs=[ver_start],
            outputs=[
                ver_start,
                ver_search,
                cancel_ver_search,
                version_progress
                ]
        )
        
        ver_start.change(
            fn=_file.file_scan,
            inputs=[
                selected_tags,
                ver_finish,
                tag_finish,
                installed_finish
                ],
            outputs=[
                version_progress,
                ver_finish
                ]
        )
        
        ver_finish.change(
            fn=_file.finish_ver_search,
            outputs=[
                ver_search,
                cancel_ver_search,
                load_to_browser
            ]
        )
        
        load_to_browser.click(
            fn=_file.load_to_browser,
            outputs=[
                ver_search,
                cancel_ver_search,
                load_to_browser,
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
                sub_folder,
                file_list,
                version_progress
            ]
        )
        
        cancel_ver_search.click(
            fn=_file.cancel_scan
        )
        
        load_installed.click(
            fn=_file.start_installed_models,
            inputs=[installed_start],
            outputs=[
                installed_start,
                load_installed,
                cancel_installed,
                installed_progress
            ]
        )
        
        installed_start.change(
            fn=_file.file_scan,
            inputs=[
                selected_tags,
                ver_finish,
                tag_finish,
                installed_finish
                ],
            outputs=[
                installed_progress,
                installed_finish
            ]
        )
        
        installed_finish.change(
            fn=_file.finish_installed_models,
            outputs=[
                load_installed,
                cancel_installed,
                load_to_browser_installed
            ]
        )
        
        load_to_browser_installed.click(
            fn=_file.load_to_browser,
            outputs=[
                load_installed,
                cancel_installed,
                load_to_browser_installed,
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
                sub_folder,
                file_list,
                installed_progress
            ]
        )
        
        save_all_tags.click(
            fn=_file.save_tag_start,
            inputs=[tag_start],
            outputs=[
                tag_start,
                save_all_tags,
                cancel_all_tags,
                tag_progress
            ]
        )
        
        tag_start.change(
            fn=_file.file_scan,
            inputs=[
                selected_tags,
                ver_finish,
                tag_finish,
                installed_finish
                ],
            outputs=[
                tag_progress,
                tag_finish
            ]
        )
        
        tag_finish.change(
            fn=_file.save_tag_finish,
            outputs=[
                save_all_tags,
                cancel_all_tags
            ]
        )
        
        cancel_all_tags.click(
            fn=_file.cancel_scan
        )
        
        download_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => updateCard(modelName)"
        )
        
        delete_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => updateCard(modelName)"
        )

        list_html.change(
            fn=None,
            inputs=[show_nsfw],
            _js="(hideAndBlur) => toggleNSFWContent(hideAndBlur)"
        )
        
        show_nsfw.change(
            fn=None,
            inputs=[show_nsfw],
            _js="(hideAndBlur) => toggleNSFWContent(hideAndBlur)"
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
        
        model_filename.change(
            fn=insert_sub,
            inputs=[
                list_models,
                list_versions
                ],
            outputs=[sub_folder]
        )
        
        download_model.click(
            fn=_download.download_start,
            inputs=[
                download_start,
                list_models,
                model_filename,
                list_versions,
                current_sha256,
                model_id
                ],
            outputs=[
                download_model,
                cancel_model,
                download_start,
                download_progress
            ]
        )
        
        download_start.change(
            fn=_download.download_create_thread,
            inputs=[
                download_finish,
                dl_url,
                model_filename,
                preview_html,
                create_json,
                trained_tags,
                install_path,
                list_models,
                list_versions
                ],
            outputs=[
                download_progress,
                current_model,
                download_finish
            ]
        )
        
        cancel_model.click(
            fn=_download.download_cancel,
            inputs=[
                delete_finish,
                list_models,
                list_versions,
                model_filename,
                current_sha256
                ],
            outputs=[
                download_model,
                cancel_model,
                download_progress
            ]
        )
        
        download_finish.change(
            fn=_download.download_finish,
            inputs=[
                model_filename,
                list_versions,
                list_models
                ],
            outputs=[
                download_model,
                cancel_model,
                delete_model,
                download_progress,
                list_versions
            ]
        )
        
        delete_model.click(
            fn=_file.delete_model,
            inputs=[
                delete_finish,
                model_filename,
                list_models,
                list_versions,
                current_sha256
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
        
        save_tags.click(
            fn=_file.save_json,
            inputs=[
                model_filename,
                install_path,
                trained_tags
                ],
            outputs=[trained_tags]
        )
        
        save_images.click(
            fn=_file.save_images,
            inputs=[
                preview_html,
                model_filename,
                list_models,
                install_path
                ],
            outputs=[]
        )
        
        list_models.select(
            fn=_api.update_model_versions,
            inputs=[
                list_models
            ],
            outputs=[
                list_versions,
                install_path,
                sub_folder
            ]
        )
        
        list_versions.change(
            fn=_api.update_model_info,
            inputs=[
                list_models,
                list_versions
                ],
            outputs=[
                preview_html,
                trained_tags,
                base_model,
                download_model,
                delete_model,
                file_list,
                model_filename,
                model_id,
                current_sha256
            ]
        )
        
        file_list.input(
            fn=_api.update_file_info,
            inputs=[
                list_models,
                list_versions,
                file_list
            ],
            outputs=[
                model_filename,
                model_id,
                current_sha256,
                download_model,
                delete_model
            ]
        )
        
        model_id.change(
            fn=_api.update_dl_url,
            inputs=[
                trained_tags,
                model_id,
                list_models,
                list_versions
                ],
            outputs=[
                dl_url,
                save_tags,
                save_images,
                download_model
                ]
        )
        
        get_next_page.click(
            fn=_api.update_next_page,
            inputs=[
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
            fn=_api.update_model_list,
            inputs=[
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
                sub_folder,
                file_list
            ],
        )
        
        get_prev_page.click(
            fn=_api.update_prev_page,
            inputs=[
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
        
        def update_models_dropdown(model_name):
            model_name = re.sub(r'\.\d{3}$', '', model_name)
            (ret_versions, install_path, sub_folder) = _api.update_model_versions(model_name)
            (html, tags, _, DwnButton, _, filelist, filename, id, current_sha256) = _api.update_model_info(model_name,ret_versions['value'])
            (dl_url, _, _, _) = _api.update_dl_url(tags, id['value'], model_name, ret_versions['value'])
            return  gr.Dropdown.update(value=model_name),ret_versions,html,dl_url,tags,filename,install_path,sub_folder, DwnButton, filelist, id, current_sha256
        
        event_text.change(
            fn=update_models_dropdown,
            inputs=[
                event_text
                ],
            outputs=[
                list_models,
                list_versions,
                preview_html,
                dl_url,
                trained_tags,
                model_filename,
                install_path,
                sub_folder,
                download_model,
                file_list,
                model_id,
                current_sha256
            ]
        )

    return (civitai_interface, "Civit AI", "civitai_interface"),

def on_ui_settings():
    section = ("civitai_browser_plus", "Civit AI")

    if not (hasattr(shared.OptionInfo, "info") and callable(getattr(shared.OptionInfo, "info"))):
        def info(self, info):
            self.label += f" ({info})"
            return self
        shared.OptionInfo.info = info
    
    shared.opts.add_option("use_aria2", shared.OptionInfo(True, "Download models using Aria2", section=section).info("Disable to use the old download method"))
    shared.opts.add_option("disable_dns", shared.OptionInfo(False, "Disable Async DNS for Aria2", section=section).info("Useful for users who use PortMaster or other software that controls the DNS"))
    shared.opts.add_option("show_log", shared.OptionInfo(False, "Show Aria2 Logs in CMD", section=section).info("Requires Web-UI Restart"))
    shared.opts.add_option("split_aria2", shared.OptionInfo(64, "Number of connections to use for downloading a model", gr.Slider, lambda: {"maximum": "64", "minimum": "1", "step": "1"}, section=section).info("Only applies to Aria2"))
    shared.opts.add_option("insert_sub", shared.OptionInfo(True, "Insert [/Model Name] & [/Model Name/Version Name] as default sub folder options", section=section))
    shared.opts.add_option("use_LORA", shared.OptionInfo(False, "Use LORA directory for LoCon's", section=section).info("SD-WebUI v1.5 and higher treats LoCON's the same as LORA's, so they can be placed in the LORA folder."))
    shared.opts.add_option("unpack_zip", shared.OptionInfo(False, "Automatically unpack .zip after downloading", section=section))
    
script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_ui_settings(on_ui_settings)
