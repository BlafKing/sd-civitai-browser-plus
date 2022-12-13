import requests
import json
import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks

# Set the URL for the API endpoint
api_url = "https://civitai.com/api/v1/models?limit=50"
json_data = None

def api_to_data(sort_type, search_model, search_term=None):
    if search_model and search_term:
        search_term = search_term.replace(" ","%20")
        return request_civit_api(f"{api_url}&types=Checkpoint&sort={sort_type}&query={search_term}")
    else:
        return request_civit_api(f"{api_url}&types=Checkpoint&sort={sort_type}")

def api_next_page(next_page_url=None):
    global json_data
    try: json_data['metadata']['nextPage']
    except: return
    if json_data['metadata']['nextPage'] is not None:
        next_page_url = json_data['metadata']['nextPage']
    if next_page_url is not None:
        return request_civit_api(next_page_url)

def update_next_page():
    global json_data
    json_data = api_next_page()
    model_dict = {}
    try: json_data['items']
    except TypeError: return gr.Dropdown.update(choices=[], value=None)
    for item in json_data['items']:
        model_dict[item['name']] = item['name']
    return gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None)


def update_model_list(sort_type, search_model, search_term):
    global json_data
    json_data = api_to_data(sort_type, search_model, search_term)
    model_dict = {}
    for item in json_data['items']:
        model_dict[item['name']] = item['name']
    return gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None)

def update_model_versions(model_name=None):
    if model_name:
        global json_data
        versions_dict = {}
        for item in json_data['items']:
            if item['name'] == model_name:

                for model in item['modelVersions']:
                    versions_dict[model['name']] = item['name']
        return gr.Dropdown.update(choices=[k for k, v in versions_dict.items()], value=None)
    else:
        return gr.Dropdown.update(choices=[], value=None)

def update_model_info(model_name=None, model_version=None):
    if model_name and model_version:
        global json_data
        output_html = ""
        output_training = ""
        img_html = ""
        for item in json_data['items']:
            if item['name'] == model_name:
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        if model['trainedWords']:
                            output_training = " # ".join(model['trainedWords'])
                        model_url = model['downloadUrl']
                        img_html = '<HEAD><style>img { display: inline-block; }</style></HEAD><div class="column">'
                        for pic in model['images']:
                            img_html = img_html + f'<img src={pic["url"]} width=400px></img>'
                        img_html = img_html + '</div>'
                        output_html = f"<B>Model:</b> {model_name}<br><b>Version:</b> {model_version}<br><a href={model_url}><b>Download Here</b></a><br><br><div align=center>{img_html}</div>"



        return gr.HTML.update(value=output_html), gr.Textbox.update(value=output_training)
    else:
        return gr.HTML.update(value=None), gr.Textbox.update(value=None)


def request_civit_api(api_url=None):
    # Make a GET request to the API
    response = requests.get(api_url)

    # Check the status code of the response
    if response.status_code != 200:
      print("Request failed with status code: {}".format(response.status_code))
      exit()

    data = json.loads(response.text)
    return data

def on_ui_tabs():
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            sort_type = gr.Radio(label='Sort List by:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Newest", type="value")
        with gr.Row():
            search_model = gr.Checkbox(label="Search by term?", value=False)
            search_term = gr.Textbox(interactive=True, lines=1)
        with gr.Row():
            get_list_from_api = gr.Button(label="Get List", value="Get List")
            get_next_page = gr.Button(value="Next Page")
        with gr.Row():
            list_models = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="quicksettings", value=None)
            list_versions = gr.Dropdown(label="Version", choices=[], interactive=True, elem_id="quicksettings", value=None)
        with gr.Row():
            txt_list = ""
            dummy = gr.Textbox(label='Trained Tags (if any)', value=f'{txt_list}', interactive=False, lines=1)
        with gr.Row():
            preview_image_html = gr.HTML()
        get_list_from_api.click(
            fn=update_model_list,
            inputs=[
            sort_type,
            search_model,
            search_term,
            ],
            outputs=[
            list_models,
            ]
        )

        list_models.change(
            fn=update_model_versions,
            inputs=[
            list_models,
            ],
            outputs=[
            list_versions,
            ]
        )

        list_versions.change(
            fn=update_model_info,
            inputs=[
            list_models,
            list_versions,
            ],
            outputs=[
            preview_image_html,
            dummy,
            ]
        )
        get_next_page.click(
            fn=update_next_page,
            inputs=[
            ],
            outputs=[
            list_models,
            ]
        )

    return (civitai_interface, "CivitAi", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)