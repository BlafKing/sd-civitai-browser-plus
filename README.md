
![CivitAI Browser-05+](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/95afcc41-56f0-4398-8779-51cb2a9e2f55)

---
### Extension for [Automatic1111's Stable Difussion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)


<h1>Features 🚀</h1>
<h3>Browse all models from CivitAI 🧩</h3>

* Explore a wide range of models at your fingertips.

<h3>Check for updates and installed models 🔄</h3>

* Easily spot new updates and identify already installed models while browsing.
* Ability to scan all installed models for available updates.

<h3>Download any Model, any version, and any file 📥</h3>

* Get the specific model version and file you need hassle-free.

<h3>Automatically assign tags to installed models 🏷️</h3>

* Assign tags by scanning all installed models for automatic use in image generation.

<h3>High-speed downloads with Aria2 🚄</h3>

* Maximize your bandwidth for lightning-fast downloads.

<h3>Sleek and Intuitive User Interface 🖌️</h3>

* Enjoy a clutter-free, user-friendly interface, designed to enhance your experience.

<h3>Actively maintained with feature requests welcome 🛠️</h3>

* Feel free to send me your feature requests, and I'll do my best to implement them!

<h1></h1>

<details>
<summary><h1>Known Issues 🐛</h1></summary>

<details>
<summary><h3>Unable to download / Frozen download</h3></summary>

**If you're experiencing issues with broken or frozen downloads, there are two possible solutions you can try:**

1. **Revert to the old download method**:
   A solution could be to disable the "Download models using Aria2" feature.  
This will switch back to the old download method, which may resolve the issue.

   ![Revert to old download method](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/982b0ebb-0cac-4053-8060-285533e0e176)

2. **Disable Async DNS for Aria2**:
   If you're using any DNS manager program like PortMaster, try turning on the "Disable Async DNS for Aria2" option.

   ![Disable Async DNS for Aria2](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/3cf7fab3-0df5-4995-9543-d9824b7931ff)

These settings can be found under the "Settings" tab in Web-UI and then under the "Civit AI" tile.

</details>

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

https://github.com/BlafKing/sd-civitai-browser/assets/9644716/ea873c3e-a7e4-44a8-907a-e9bddf13bc55


(Theme used: [Lobe](https://github.com/canisminor1990/sd-webui-lobe-theme))  

# Changelog 📋

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
* New setting: option to toggle automatically inserting 2 default sub folders.
* New setting: option to toggle installing LoCON's in LORA folder.
* Bug fix: default file was incorrect when selecting a model.
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
