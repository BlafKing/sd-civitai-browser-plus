
![CivitAI Browser-05+](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/95afcc41-56f0-4398-8779-51cb2a9e2f55)

---
### Extension for [Automatic1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)


<h1>Features 🚀</h1>
<h3>Browse all models from CivitAI 🧩</h3>

* Explore a wide range of models at your fingertips.

<h3>Check for updates and installed models 🔄</h3>

* Easily spot new updates and identify already installed models while browsing.
* Ability to scan all installed models for available updates.

<h3>Download any Model, any version, and any file 📥</h3>

* Get the specific model version and file you need hassle-free.
* Download queue to avoid waiting for finished downloads.

<h3>Automatically assign tags to installed models 🏷️</h3>

* Assign tags by scanning all installed models for automatic use in image generation.

<h3>Quick Model Info Access 📊</h3>

* A button for each model card in txt2img and img2img to load it into the extension.
* A button under each image in model info to send its generation info to txt2img.

<h3>High-speed downloads with Aria2 🚄</h3>

* Maximize your bandwidth for lightning-fast downloads.

<h3>Sleek and Intuitive User Interface 🖌️</h3>

* Enjoy a clutter-free, user-friendly interface, designed to enhance your experience.

<h3>Actively maintained with feature requests welcome 🛠️</h3>

* Feel free to send me your feature requests, and I'll do my best to implement them!

<h1></h1>

<details>
<summary><h1>Known Issues 🐛</h1></summary>

<h3>Unable to download / Frozen download:</h3>

**If you're experiencing issues with broken or frozen downloads, there are two possible solutions you can try:**

1. **Revert to the old download method**:
   A solution could be to disable the "Download models using Aria2" feature.  
This will switch back to the old download method, which may resolve the issue.

   ![Revert to old download method](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/982b0ebb-0cac-4053-8060-285533e0e176)

2. **Disable Async DNS for Aria2**:
   If you're using a DNS manager program like PortMaster, try turning on the "Disable Async DNS for Aria2" option.

   ![Disable Async DNS for Aria2](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/3cf7fab3-0df5-4995-9543-d9824b7931ff)

These settings can be found under the "Settings" tab in Web-UI and then under the "CivitAI Browser+" tile.

</details>

<h1></h1>

# How to install 📘

<h3>Automatic Installation:</h3>

![HowTo](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/91a8f636-0fd5-4964-8fb4-830a5c22254a)


<h3>Manual Installation:</h3>

1. Download the latest version from this site and unpack the .zip  
![2023-09-25 13_06_31](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/12e46c6b-74b5-4ed5-bf55-cb76c5f75c62)

2. Navigate to your extensions folder (Your SD folder/webui/extensions)
3. Place the unpacked folder inside the extensions folder
4. Restart SD-WebUI

# Preview 👀

https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/44c5c7a0-4854-4043-bfbb-f32fa9df5a74


# Star History 🌟

<a href="https://star-history.com/#BlafKing/sd-civitai-browser-plus&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=BlafKing/sd-civitai-browser-plus&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=BlafKing/sd-civitai-browser-plus&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=BlafKing/sd-civitai-browser-plus&type=Date" />
  </picture>
</a>

# Changelog 📋

<h3>v3.6.0</h3>

* Feature: Ability to set custom default sub folders.
* Feature: Automatically fetches latest available Basemodels.
* Bug fix: Lag fixed on SD-WebUI Forge/Gradio 4+, thanks to [@BenjaminSymons](https://github.com/BenjaminSymons) and [@channelcat](https://github.com/channelcat)!
* Bug fix: Version ID has been suffixed to filename to avoid detecting different models as installed.
* Bug fix: Filename comparing to detect installed models is no longer case sensitive.
* Bug fix: CivitAI button on model cards correctly works again.
* Bug fix: Correct image path now gets used when local images in HTML are used.
* Bug fix: Any trailing or leading spaces get removed from model/version names now.

---
<h3>v3.5.4</h3>

* Feature: Added support for DoRA (Requires SD-WebUI v1.9)
* Bug fix: No longer rescans models that were previously not found on CivitAI
* Bug fix: Fixed placement of HTML & api_info files when custom images location was used.
* Bug fix: Fixed incorrect json naming.

---
<h3>v3.5.3</h3>

* New Setting: Send model from the cards CivitAI button to the browser, instead of showing a popup.
* Bug fix: No longer fetch HTML info when the file already exists and overwrite is off. 
* Bug fix: Fix NSFW models update functions.
* Bug fix: Fixed CivitAI button on NSFW model cards.

---
<h3>v3.5.2</h3>

* Bug fix: NSFW filtering fixed.

---
<h3>v3.5.1</h3>

* Temp fix: Quick fix for the new NSFW system.
   - NSFW models may be returned when NSFW is disabled, this is an issue with the public CivitAI API.
   - Search results currently do not get influenced by the NSFW setting, also an issue with the API.
* Bug fix: Better automatic coloring for white theme.

---
<h3>v3.5.0</h3>

* Bug fix: Extension now works again with the latest CivitAI API version!
* Cleanup: Re-wrote backend API handling code.

---
<h3>v3.4.3</h3>

* Bug fix: Hotfix for a change in the public API which broke searching.
* Bug fix: Fixed incorrect permission display on model page.

---
<h3>v3.4.2</h3>

* Feature: Ability to set-up a custom proxy for API requests and downloads.
* Feature: Use image API for prompt info, should speed up loading.
* Feature: Optimized javascript code, improved webpage speed for some users.
* New setting: Proxy settings to set-up custom proxy.
* New setting: Toggle for saving description to model json file. (this displays description on the cards)
* Bug fix: Broken default sub folder option fixed [#217](https://github.com/BlafKing/sd-civitai-browser-plus/issues/217)

---
<h3>v3.4.1</h3>

* Feature: Local images now work in HTML files as preview. (credit: [mx](https://github.com/mx))
* Feature: Updated available base models.
* Bug fix: Fixed prompt info and model selection after CivitAI API update.
* Bug fix: Fixed "/" missing from default path/sub-folder.

---
<h3>v3.4.0</h3>

* Feature: (BETA) Download queue! rearrange download order and remove models from queue
   - Will likely contain bugs, still not completely finished.
* Feature: Customizable sub folder insertion options, choose what sub folder options you want!
* New setting: Toggle per prompt example image buttons
* New setting: Insert sub folder options
* Bug fix: Add to queue fixed, now properly gets enabled.
* Bug fix: Symlinks now get correctly recognized and used.
* Bug fix: No longer creates accidental sub folder when bulk downloading.

---
<h3>v3.3.1</h3>

* Feature: Ability to send individual parts of image generation data to txt2img.
* Feature: Added compatibility for [stable-diffusion-webui-forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) fork.
* New setting: Use local images in the HTML 
   - Does not work in combination with the "Use local HTML file for model info" option!
* New setting: Store the HTML and api_info in the custom images location
* Bug fix: New HTML model info now scales with width so it should always fit.
* Bug fix: Various bug fixes to the "Update model info & tags" function.
* Bug fix: Auto save all images now uses correctly uses custom image path if set.
* Bug fix: "Save model info" button should no longer return errors.
* Bug fix: Old download method (non Aria2) should now work again.

---
<h3>v3.3.0</h3>

* Feature: New txt2img and img2img model info overlay on CivitAI button press.
* Feature: Base Model as sub folder option.
* Feature: Ability to multi-download to selected folder.
* Feature: Use the same folder as older versions when updating using multi-download.
* Feature: txt2img and img2img CivitAI buttons can use local HTML file, toggle in settings.
* Note: Save images no longer saves .html and API info, save model info does this instead now.
* New setting: Save API info of model when saving model info.
* New setting: Automatically save all images after download.
* New setting: Use local HTML file for model info.
* Bug fix: better JSON decode, now forces UTF-8
* Bug fix: Now uses the proper default file when using multi-download
* Bug fix: Hide early access models fix, now works when published_at does not exist in API.
* Bug fix: Fix attempt for queue clearing upon download fail.

---
<h3>v3.2.5</h3>

* Bug fix: Removed default API Key since it gets blocked after many downloads.
   - Because of this it's now required for some downloads to use a personal CivitAI key, this can be set in the the settings tab of SD-WebUI under the CivitAI Browser+ tab.
* Bug fix: Fixed bug when selecting a model from txt2img/img2img that doesn't exist on CivitAI.
* Bug fix: Changed model selection to Model ID instead of model name
   - This previously caused issues when 2 models were named the same.
* Bug fix: Fixed an issue where the default file was not properly used by default.
* Bug fix: Fixed some tiles not being selectable due to having "'" in its title
* Bug fix: Now automatically removes residual Aria2 files.

---
<h3>v3.2.4</h3>

* Bug fix: Fix version detection for non standard SD-WebUI versions.
* Bug fix: Retry to fetch ModelID if previously not found in update functions.
* Bug fix: Style fix for when the Lobe theme is used in SD-WebUI
* Bug fix: Better required packages import error catching.
* Bug fix: Fixed CivitAI button scaling in txt2img and img2img tabs.
* Bug fix: Added ability to handle models that have no hashes saved.

---
<h3>v3.2.3</h3>

* Bug fix: Generate hash toggle in update models was inverted (silly mistake, sry bout that)
* Bug fix: Better error detection if no model IDs were retrieved during update functions.
* Bug fix: Better error handling if a local model does not exist on CivitAI

---
<h3>v3.2.2</h3>

* Bug fix: Fixed an `api_response` issue in the update model functions
* Bug fix: Reverted automatically retrieving base models to fix startup issues
* Bug fix: Better error description if a model no longer exists on CivitAI
* Bug fix: Primary file is now used as default file.
* Bug fix: Search after updating models no longer returns errors.

---
<h3>v3.2.1</h3>

* Feature: Extension now automatically retrieves latest base models from CivitAI.
* Bug fix: Hotfix for functionality with SD.Next

---
<h3>v3.2.0</h3>

* Feature: A toggle for One-Time hash generation for externally downloaded models.
* Feature: Updated extension settings layout for SD-WebUI 1.7.0 and higher.
* Bug fix: Set default value of Lora & LoCON combination based on SD-WebUI version.
* Bug fix: LORA models with embedding files now get placed inside embeddings folder.
* Bug fix: Better tile count handling to avoid issues with incorrect tile count.
* Bug fix: Better settings saving/loading to prevent writing issues.

---
<h3>v3.1.1</h3>

* Bug fix: Early Access models now get correctly hidden/detected.
* Bug fix: Better timeout/offline server detection for options in "Update Models" tab.
* Bug fix: Better error detection if required packages were not installed/imported.
* Bug fix: Download button now displays as "Add to queue" during active download.

---
<h3>v3.1.0</h3>

* Feature: Send to txt2img, Send any image in the model info to txt2img.
* Feature: Added new Base model filters: 
   - SD 1.5 LCM, SDXL 1.0 LCM, SDXL Distilled, SDXL Turbo, SVD, SVD XT
* Feature: Hide installed models filter toggle.
* Feature: Better display of permissions and tags in model info.
* New setting: Append sub folders to custom image path.
* New setting: Toggle gif/video playback, Disable if videos are causing high CPU usage.
* Bug fix: Better handling if hash is not found.

---
<h3>v3.0</h3>

* Feature: Download queue! Ability to add downloads to a queue. (Finally!)
* Feature: Checkboxes to download multiple models at once.
   - This will automatically use the first version and first file of the selected model(s).
   - Will use the default sub folders per content type defined in sub folder settings.
* Feature: "Select all" button to select all downloadable models at once.
* Feature: "Open on CivitAI" button when viewing a models metadata in txt2img or img2img.
   - Will only display if the model's info has been saved to the .json after v3.0
* Feature: Ability to rename model filename
   - Note that it's not recommended to change the filename since some checks rely on it.
* Bug fix: Fixed display of saved .html files.
* Bug fix: Removed potential illegal characters from file name/path name.
* Bug fix: Fixed case sensitive sorting of sub folders.

---
<h3>v2.1.0</h3>

* Feature: "Overwrite any existing previews, tags or descriptions" Toggle in Update tab.
* Feature: Added content type "All" to model scanning to select all content types.

---
<h3>v2.0.1</h3>

* Bug fix: Folders starting with "." now no longer show sub folders.
* Bug fix: Added headers to simulate browser request. (May fix issues for users from Russia)

---
<h3>v2.0</h3>

* Feature: New button on each model card in txt2img and img2img to view it in the extension.
<details>
<summary> Preview</summary>

![ezgif-3-b1f0de4dd2](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/536a693a-c30c-438e-a34f-1aec54e4e7ee)

</details>

* Feature: NSFW toggle now properly impacts search results.
* Feature: Ability to set [\Model Name] & [\Model Name\Version Name] as default sub folders.
* New setting: Hide sub folders that start with a '.'
* Bug fix: Preview HTML is now emptied when loading a new page.
* Bug fix: Buttons now correctly display when loading new page.
* Bug fix: Fixed compatibility with SD.Next. (again)
* Bug fix: Emptied tags, base model, and filename upon loading new page.
* Bug fix: Filter change detection fixed

---
<h3>v1.16</h3>

* Feature: Ability to download/update model preview images in Update Models tab.
* Feature: "Update model tags" changed to "Update model info & tags".
  - The option now saves tags, description and base model version.
  - This also applies to the browser, saved tags is changed to save model info.
* Bug fix: Archived models are now hidden since they cannot be used.

---
<h3>v1.15.2</h3>

* New setting: Custom save images location
* New setting: Default sub folders
   - Any sub folders you have will be able to be selected as default, per content type.
   - If a content type doesn't appear, then it means there are no subfolders in that type.
* Bug fix: Unreleased models caused a crash, now hidden by default since they can't be used.

---
<h3>v1.15.1</h3>

* New setting: Show console logs during update scanning.
* Bug fix: Scan for update no longer prints incorrect info about outdated models.
* Bug fix: Removed bad logic which triggered the same function multiple times.
* Cleanup: Optimized functions and improved the speed of selecting models.

---
<h3>v1.15</h3>

* Feature: Filter option to show favorited models. (requires personal API key)
* Feature: Back to top button when viewing model details.
* New setting: Page navigation as header. (keeps page navigation always visible at the top)
* Bug fix: Aria2 now restarts when UI is reloaded.
* Bug fix: SHA256 error fixed if .json files don't contain it.
* Bug fix: Cleaned up javascript code.

---
<h3>v1.14.7</h3>

* New setting: Hide early access models (EA models are only downloadable by supporters)
* New setting: Personal CivitAI API key (Text field to insert personal API key)
  - Useful for CivitAI supporters, you can use your own API Key to allow downloading Early Access models
* Bug fix: Extension now works with `no gradio queue` flag.
* Bug fix: Auto disable Aria2 on MacOS due to incompatibility.
* Bug fix: Now properly works on SD.Next again.
* Bug fix: Download progression and cancelling is no longer broken on old download method.
* Bug fix: Extension now correctly downloads models where it is required to be logged in.
* Bug fix: Extension no longer attempts to install already installed requirements.

---
<h3>v1.14.6</h3>

* Bug fix: Removed pre-load of default page, caused issues for some users.
* Bug fix: Fixed internal model naming, caused issues when model names included '
* Bug fix: Different host for .svg icons, caused issues with MalwareBytes.
* Bug fix: Preview saving was broken due to passing the wrong file path.

---
<h3>v1.14.5</h3>

* Feature: Base Model filter now impacts search results.
* Feature: Ability to input model URL into search bar to find corresponding model.
* Bug fix: Adetailer models now get placed in the correct folder

---
<h3>v1.14.4</h3>

* Bug fix: Page slider broke the Next Page button when loaded from "Update Models".
* Bug fix: "Save settings as default" button inserted broken .json data.
* Bug fix: Triggering "Scan for available updates" twice resulted in an error.

---
<h3>v1.14.3</h3>

* Bug fix: LORA content type was broken when "Treat LoCon as LORA" was turned on.

---
<h3>v1.14.2</h3>

* Feature: Custom page handling when scanning models.
* Bug fix: Model scan feature now works for large model count (+900)
* Bug fix: Better broken .json error handling

---
<h3>v1.14.1</h3>

* Bug fix: Gifs did not display properly.
* Bug fix: Video's no longer save as preview since they cannot be used.
* Bug fix: Filter window was not hidden by default.

---
<h3>v1.14</h3>

* Feature: Redesign of UI.
* Feature: New dropdown with filter settings.
* Feature: Button to save current filter settings as default. (requires restart)
* Feature: Tag box can now be typed in to save custom tags.
* Feature: Delete function removes any unpacked files.

---
<h3>v1.13</h3>

* Feature: Updated available content types: 
  - Upscaler
  - MotionModule
  - Wildcards
  - Workflows
  - Other
* Feature: Videos can now also be displayed on preview cards and in the model info.
* Feature: Automatically scans upscaler type by looking through model's description.
* Feature: Automatically identify correct folder for wildcards based on extension.
* Bug fix: Version ID got saved instead of correct Model ID after download.

---
<h3>v1.12.5</h3>

* Bug fix: [Installed] tag was only assigned to latest installed version.
* Bug fix: Folder location didn't update when selecting different version/file.
* Bug fix: Version scanning didn't properly scan sha256 in uppercase.

---
<h3>v1.12.4</h3>

* Feature: You can now refresh by pressing Ctrl+Enter and Alt+Enter.
* Bug fix: Auto unpack feature was unpacking unintended archives, now only unpacks .zip.

---
<h3>v1.12.3</h3>

* New setting: Option to toggle automatically unpacking .zip models.
* Bug fix: Error wasn't catched when file path was incorrect.

---
<h3>v1.12.2</h3>

* Feature: Able to download multiple files from each version.
* Bug fix: Models did not get deleted properly when in nested folders.
* Bug fix: Wrong sha256 was being saved after downloading.
* Bug fix: Wrong default folder was used when installed model got selected.

---
<h3>v1.12.1</h3>

* Feature: File deletion now uses both SHA256 and file name to detect correct file.
* New setting: Option to toggle automatically inserting 2 default sub folders.
* New setting: Option to toggle installing LoCON's in LORA folder.
* Bug fix: Default file was incorrect when selecting a model.
* Bug fix: Next Page caused an error when changing content type.

---
<h3>v1.12</h3>

* Feature: Ability to load all selected installed models into browser in Update Models tab.
* Feature: Installed/outdated models check is now done using SHA256 + file name.
* Feature: Ability to select multiple content Types when searching and scanning.
* Feature: Greatly improved speed of model scanning if model ID is saved in .json

---
<h3>v1.11.2</h3>

* Feature: Redesign of model page by [ManOrMonster](https://github.com/ManOrMonster)
* <details><summary>Model page changes (https://github.com/BlafKing/sd-civitai-browser-plus/pull/33)</summary>
   
   - Redesigned the look of the model page.
   - Added link to model page on CivitAI. Click on model name to open.
   - Added link to uploader/creator page on CivitAI. Click creator name to open.
   - Added CivitAI avatar display.
   - Separate description section.
   - First sample image is marked with data attribute and downloaded as preview image instead of grabbing first in model HTML. This guarantees that the first sample image (not avatar or image in description) is used when downloading the model.
   - Sample images are marked with data attribute so that only they are downloaded when using "Save Images" (no description images or avatar).
   - Removed trained tags from info since they are displayed above.
   - Each sample image has its own section.
   - Sample images zoom in when clicked, zoom out when clicking anywhere.
   - Forced width is removed from sample image URLs so that nice big images can be viewed.
   - Metadata is arranged so that the most commonly used data is at the top, no more searching for prompts.
   - Extra metadata is in accordion labeled "More details...". This is especially useful to hide insanely large ComfyUI JSON.

</details>

---
<h3>v1.11.1</h3>

* Feature: Error detection during Aria2 downloads.
* Bug fix: Avoid starting Aria2 RPC multiple times with better port check.
* Bug fix: Fixed dynamic tile status updates after deleting/downloading.
---

<h3>v1.11</h3>

* Feature: Ability to scan all installed models for available updates.
* Feature: Model ID and sha256 get saved to .json after scanning or downloading a model.
* Bug fix: Fixed crash when base model is not found.
* Bug fix: No longer overwrite sha256 and model ID in existing .json.
---

<h3>v1.10.1</h3>

* Bug fix: Fixed pathing for Unix systems
* Bug fix: Extra checks to prevent deleting unintentional files.
* Feature: Models get moved to trash instead of fully deleted.
---
<h3>v1.10</h3>

* Feature: Update tags for all installed models!
* Feature: Tabs for Browsing and updating Tags.
* Feature: Buttons to select which folders to update tags in.
---
<h3>v1.9.4</h3>

* Feature: Added Civit AI settings tab
  - New setting: Disable downloading with Aria2. (will use old download method instead)
  - New setting: Disable using Async DNS. (can fix issues for some users who use DNS managing programs)
  - New setting: Show Aria2 logs in the CMD.
  - New setting: Set the amount of connections when downloading a model with Aria2.  
    (The optimal connection count is different per user, try to find the lowest option which still gives you full bandwidth speed)
---
<h3>v1.9.3</h3>

* Feature: Included Motrix Aria2 version.
* Feature: Max connections per server set to 64 and split file set 64.
* Feature: Aria2 is now shipped with this extension for Linux as well.
---

<h3>v1.9.2</h3>

* Cleanup: Split up script into multiple files for improved oversight/readability.
* Cleanup: Centered model icons
---

<h3>v1.9.1</h3>

* Bug fix: Added back old download function if aria2 fails.
---

<h3>v1.9</h3>

* Feature: Faster downloads by using Aria2.
* Feature: More info about current download: Speed, ETA, File Size and % completion.
---

<h3>v1.8.1</h3>

* Feature: Sub Folder list now contains 2 default options: `/{Model name}` & `/{Model name}/{Version name}`
---

<h3>v1.8</h3>

* Feature: Ability to download different file types per version.
* Feature: NSFW Toggle is now dynamic.
* Feature: Version list now dynamically updates after download.
* Cleanup: Rearranged/Resized UI elements.
* Bug fix: Downloading models now uses file ID instead of names.
* Bug fix: NSFW Toggle no longer hides images tagged as "Soft".
* Bug fix: Fixed each model load running twice.
---

<h3>v1.7.2</h3>

* Bug fix: Download button did not get re-enabled properly.
* Bug fix: Tile status did not get updated properly when download failed.
---

<h3>v1.7.1</h3>

* Feature: Base Model filtering dims tiles instead of hiding.
* Bug fix: NSFW Blur increases with tile size.
* Bug fix: Dynamic tile status after installation & deletion now correctly detects other versions.
---

<h3>v1.7</h3>

* Feature: Introduced seperate download progress bar, browse while downloading.
* Feature: no more force refresh after installing, cancelling and deleting.
* Feature: Added toggle to sort Tiles by date.
* Feature: Dynamic changing of tile borders after installation & deletion.
* Removal: 'Auto delete old version' removed since it relied on a reload.
---

<h3>v1.6</h3>

* Bug fix: Page count is now always correclty read when refreshing.  
(You can fill in the page number you'd like to visit and press refresh to go to that page)
* Feature: 'Filter Base Model' to dynamically hide any unselected Base models.  
(Please note: This does not impact search results, since the CivitAI API does not yet support this)
---

<h3>v1.5</h3>

* Feature: Slider to change tile size.
* Feature: Download Folder textbox which can be used to define a custom download path.
* Feature: Sub Folder Dropdown to select any available subfolder(s) as download location.
* Feature: Display a timed out message instead of an error icon.
* Bug fix: Nested files can now be detected as installed or outdated.
* Bug fix: Auto selects corresponding folder of any installed models.
* Bug fix: Better cancellation logic to prevent downloads from continuing.
---

<h3>v1.4</h3>

* Feature: Download progress bar is now on web page instead of CMD.
* Feature: Added Cancel and Delete buttons.
* Feature: Download button will now change according to circumstances:
  - Cancel button if there's a current download.
  - Delete button if the selected version is installed.
* Cleanup: Better margin fixes with theme detection.
* Bug fix: Delete option now also removes .json files.
* Bug fix: Buttons are now disabled during download. (except cancel button)
---

<h3>v1.3.1</h3>

* Bug fix: Fixed tag saving bugs/oversights.
* Bug fix: Trained tags display now do not include the model itself.
---

<h3>v1.3</h3>

* Feature: 'Save Tags' button saves tags to a .json file which gets used in image creaton.  
  (If a LORA with saved tags is used it will automatically input all tags into the txt box in image creation)
* Feature: 'Save tags after download' toggle to automatically save .json tags.
* Cleanup: Removed "Get model info" button.
* Cleanup: Removed download link box.
* Cleanup: Removed "No" from search options.
* Cleanup: Added border radius to cards.
* Cleanup: Improved padding based on if Lobe theme is being used.
---

<h3>v1.2</h3>

* Feature: Automatically saves preview image when downloading a model.
* Feature: Added [installed] text suffix for any versions that are installed in the 'Version' tab.
* Cleanup: Changed 'Model Filename' from a dropbox to a textbox.
* Cleanup: Made bottom textboxes non typeable.
* Cleanup: Disabled bottom buttons when no model is selected.
* Bug fix: Margin error on the latest tile.
* Bug fix: Version checking is now case sensitive.
* Bug fix: Default verison in version tab shows installed version.
---

<h3>v1.1</h3>

* Feature: Dropdown box which can filter by time period.
* Cleanup: 'Content type' changed from buttons to a dropdown box.
* Bug fix: Fixed tiles not reloading when already pressed.
---

<h3>v1.0</h3>

* Feature: 'Refresh' now reloads the current page unless any options have been changed.
* Feature: Made the page refresh after a download and made it load during one.
* Feature: Orange glow for any outdated installed packages.
* Feature: 'Delete old version after download' option.
* Feature: Ability to manually fill in a page number to load the corresponding page.
* Cleanup: Removed new folder option.
* Cleanup: Made the glow around frames always visible without hovering.
* Pulled fork from: [SignalFlagZ's Fork](https://github.com/SignalFlagZ/sd-civitai-browser) [v1.1.0](https://github.com/SignalFlagZ/sd-civitai-browser/releases/tag/1.1.0)
