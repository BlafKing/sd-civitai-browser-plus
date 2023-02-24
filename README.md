# sd-civitai-browser
An extension to help download models from CivitAi without leaving WebUI

This version was forked from the originator by Vetchems who wasn't responding to pull requests.

To install use the normal install process in A1111 or check out this repo and copy the folder into your extensions folder like so:
![Screenshot 2023-02-23 at 9 15 54 PM](https://user-images.githubusercontent.com/305910/221075677-2fcbf89c-2685-40cb-8b37-b7bfcd17ffa2.png)

A111
 -> extensions
    -> sd-civitai-browser
       -> scripts
         -> civitai-api.py
         
It needs to be in this directory tree because it uses relative paths to copy things around.  That might be something we fix in future versions.
If you'd like for this to become the official fork let me know and we can circle the wagons here.  I'm happy to take pull requests.

The main things i've done are fix the problems relying on "onchange" for selects which don't trigger for single item select lists and added features to support Model Previews using https://github.com/Vetchems/sd-model-preview

