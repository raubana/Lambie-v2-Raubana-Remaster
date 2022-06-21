# Lambie v2 Raubana Remaster
A **VERY NSFW** repo of a VRChat avatar originally made by Shiba, improved by Ikeiwa, and now improved by me! A part of [FoxHoleVR](https://foxholevr.com/). 

**18+ ONLY! SERIOUSLY, THIS IS SO NOT SAFE FOR WORK, I'M ALMOST TOO TERRIFIED TO PUT IT ON MY GITHUB.**

This is NOT for sale/resale, but is free to be distributed and/or modified. Just don't forget to support and give attribution to the original creators, Shiba and Ikeiwa!

Also, if you'd be so kind, please [throw a little "support" my way](https://ko-fi.com/raubana), too. I am very broke ;-;


## Change Log:

### v0.3.2 - 6/21/2022
[TL;DR VIDEO]()
- Finally go around to making an update video and writing the change logs for the previous two updates.
- Deleted the "attempt_resume" keyword argument from the do_the_things script, as the method doesn't have this argument.


### v0.3.1 patch - 6/20/2022
[SOME VIDEO, I DUNNO](https://youtu.be/z4U0Z9s_1wg) 
- Some quick fixes for bad enough mistakes...
- Added in the nipple albedo texture I forgot to include during the v0.3 early release.
- Fixed an error in the NotificationHandler code. My bad.
- Also fixed an error in the AO baking code. Also my bad.


### v0.3 - 6/14/2022
- This is an early release. It is likely buggy.
- Redid the master UV Map again and rebaked the textures.
- Updated the albedo texture for the nipples.
- Other minor changes.

# Unity Changes
- Added the first real Unity Project Template!

# Blender Changes
- Added a script called "PhysBoneShapePreview". Running it will setup a drawing hook that runs every frame, and can only be reset by closing Blender. Bones that have custom float properties named either "pb_r_h" (for PhysBone Radius Head) or "pb_r_t" (for PhysBone Radius Tail) will have a simple PhysBone collision model drawn. This is helpful for lining up the bones of a model (and what will eventually become PhysBones) to its mesh.
- Added a script called "ShrinkBodyPart". With it you can easily create shrink and/or hide shape keys.
- Modified the ponytail mesh and vertex weights. It now curves nicely.
- Simplified the tail so that it only has three bones instead of five.
- Split each Ear bone into two, Ear1 and Ear2. Updated the default piercings to work with these new vertex groups.
- Redid the rigging and weights for the tongue.
- Deleted the "palettes" of the mouth.
- Added a poker face shape key.
- Modified the antlers and horns to grow as their size shape key increases, rather than shrink.
- The goat horns now curve around when they grow.
- Added some new "shrink" shape keys.
- Added a vagina shape key to the body suit.

# Python Changes
- Added the keyword argument "attempt_resume" to all baking methods. When set, the code will attempt to skip ahead, using the arguments' values to determine where to resume. Right now the list of acceptable values for this keyword argument are as follows:
  - None if NOT attempting to resume.
  - A list or a tuple when attempting to resume, where the first element is a string with the name of where to resume at.
  - For all baking operations, these are the accepted values:
    - [ "baking", tile_x(int), tile_y(int) ]
	- [ "baking", tile_x(int), tile_y(int), object_name(str) ]
	- [ "stitching" ]
	- [ "before pp" ]
	- [ "resize" ]
	- [ "margin" ]
	- [ "blur" ] (AO ONLY)
	- [ "after pp" ]
- Added the keyword argument "skip_blur" to the AO baking method. This defaults to True.
- Added the keyword argument "skip_color_bleed" to the auto-fill margin bench-marking method. This defaults to True.
- Added the keyword argument "post_cleanup" to the specular and smoothness merging method.
- Set arguments - "use_selected_to_active" and "use_clear" - to the baking operations to prevent exceptions/errors from occurring at runtime.
- Deleted the **blur_once** method. Replaced the one instance of it being used with a PIL version within the AO baking code.
- Added a filepath cleaning method called **clean_filepath**. Added it to many different locations through-out the code where files are loaded/writed/saved.
- Updated the **reset_everything** method to reset hiding for every object and the armature. Also added resetting shape keys and transforms.
- Added the antlers and the horns to the UV settings so they're at full size during the unwrapping process.
- Modified the AO settings to use the newer "shrink" shape keys.
- Removed "HairClips" from the enabled objects of the default AO baking settings.
- Tweaked other values in the baking constants file.
- Modified instances of arithmetic where division is performed, followed by rounding down, to instead use the newer "floor division" operator ('/' to '//').
- The auto-fill benchmark is now slightly more verbose.
- Increased default size of the AO texture from (1024,1024) to (2048,2048).
- Minor tweaks to some notification messages.

Notes:
1. The code that automatically calculates the baking margin sizes when also doing stitching/tiling seems to be wrong right now. You're better off specifying the size yourself (in pixels).
2. It's been decided not to include the original male genitals. They will likely be remade from scratch sometime in the future.
3. Discovered that 8 bits colors for the normal maps is not enough. All normal map textures will be changed to 16 bits in the future. For now this will have to be fixed manually.
4. The "attempt resume" function is experimental and may not run as expected.


### v0.2 - 6/5/2022
[TL;DR VIDEO](https://youtu.be/o5PUjDnJuso)

- Added some meshes!
  - Choker (custom)
  - Bikini Top (custom)
  - Bikini Bottom (originally called "Thong", from Ikeiwa's remaster, but now modified by me)
  - Body Suit (originally from Shiba's v2 Lambie, but now modified by me)
- Added the new meshes to the *EVERYTHING* constant in the blender constants file.
- Added AO settings for the new meshes in the baking constants file.
- Added a Stitching/Tiling system to the baking code. When enabled (using *CYCLES_STITCHING* or *AO_CYCLES_STITCHING*), the textures will be baked onto tiles (of a size determined by the constants *CYCLES_STITCHING_TILESIZE* or *AO_CYCLES_STITCHING_TILESIZE* respectively). Using this functionality requires more time (usually), but reduces the memory (RAM) requirements significantly by offloading most of the data to the hard drive before/during/after baking. After all the tiles are baked, they're stitched together and the result is saved as the new texture.
  - Only (well, mostly) objects with UV polygons within the texture space for the current tile will be baked. This saves A LOT of time.
  - In the case where there are no UV polygons in a tile, no tile image will be saved. A check is performed during stitching and clean up so only the tile images that exist will be stitched together/deleted.
  - Notifications for which object is baking have been disabled. Notifications for which tile is baking have been added.
- Removed the baking constants *TEXTURE_SAVEASYOUBAKE*, as the feature now defaults to being on.
- Renamed Bad AA to Bad MSAA, as it's more accurate.
- Fixed a bug with the baking code where it didn't scale down the number of samples properly whenever Bad MSAA is enabled. Yeah, the scale may be linear, but the number of samples is *exponential*. Whoops. This fix should significantly reduce the number of samples acquired during AO baking when Bad MSAA is enabled, reducing baking time significantly.
- Added a feature to the unwrapping code so you can specify which shape key should be active before a specific object is unwrapped. Doing this results in the object being unwrapped as if that shape key is the only one that's on. The settings for this can be set with the new *UV_UNWRAP_SETTINGS* constant in the UV constants file. If not set, the code will default to Basis (if it exists).
  - Currently the only objects that are affected by this change are the ones with the misc_BreastSize shape key: Body, Bikini Top, Nipples, and Nipple Piercings. They're set to have misc_BreastSize as the active shape key during unwrapping. This helps increase the level of detail for the textures on and around the breasts, as the UV islands for the breasts were originally unwrapping waaay too small.
- Added new keyword arguments to the **make_master_uv_map** method: skip_minimize_stretch and skip_final_touches.
- Used the Surface Deform modifier to update/add many shape keys. This was mostly used for the misc_Breathe shape keys, but proved useful for others.
- Modified the **use_physics_to_optimize_master_uv_map** method to shake for a little longer between scaling tests.
- Modified the UV physics sim code so the sprites appear darker when they're asleep.
- Modified the UV physics sim code so the sprites appear yellow when any part of any of its shapes are outside the simulation space, and red when the whole body is outside the simulation space.
- Modified the UV physics sim code so every physics body is being checked every physics iteration for any parts that may be outside of the simulation space.
- Fixed a bug with the *fake_radius* variable in the UVSimIsland objects. It was supposed to calculate the radius, but has been calculating the diameter instead.
- Added a new method **safely_delete_file**. This is used by the baking methods to clean up tile images after baking using the new stitching feature, and also the Specular and Smoothness images after the data from the two files have been merged and saved as a new image.
- Modified the Notification system to keep track of when the last notification was queued. This change removed the need for tracking when the next notification will be sent and, instead, provide mush easier ways to check when to send the next notification.
- Added a new notification constant *FREQ_SILENT* which determines the delay between notifications given the next one is going to be silent.
- Modified the Bikini Bottom mesh so it doesn't clip through the tail as much.
- Fixed some of the vertex weights on the Bikini Bottom.
- Renamed the "Collar" Bone to "Collar_root". This was done to prevent it from being renamed on export due to it sharing the name of the Collar object (or maybe it was the other way around, I can't remember...).
- Tweaked the misc_HideBeans shape key on the arm socks to work a little better.
- Renamed the mesh for the Fluff from "Body_mesh.001" to "Fluff_mesh" (could have sworn I already fixed this, but w/e).
- Tweaked many UV Seams of many models.
- Changed the AO settings to replace tuples with sets. Minor change, really.
- Added bulge... stuff. You know what I mean.
- Other minor tweaks. I can't keep track of everything, sheesh.

Notes:
1. I still haven't tested this in VRC.
2. There is still some symmetry problems with the Bikini Bottom.
3. It was discovered that the code for Minimizing Stretch hasn't been working. Because of this, it's been disabled to save time.
4. It was also discovered that having Rotation enabled when using the Pack UV Islands operator could cause some of the islands to become seriously warped (mostly the nipples). This has also been disabled.
5. Although not new, it was also known that the functionality of the methods **make_master_uv_map** and **use_physics_to_optimize_master_uv_map** when the keyword leave_all_selected is set to True hasn't been working, either. Again, this has been disabled.


### v0.1.8 - 5/30/2022
[TL;DR VIDEO](https://youtu.be/SbX9-GDhu5E)

- Not a huge update, but one worth posting. It's finally time!
- Added automated exporting of your Avatar as an FBX. Features include:
	- An optional warning and explanation of what is about to happen, as well as a quick math test to ensure the user knows what they're about to do.
	- Saving a temporary copy of the Blender file to ensure the original isn't modified.
	- Deleting any UV Map from the Meshes of the temp. file that isn't going to be exported.
	- Removing all Materials then setting the correct Material to all of the meshes before export.
	- Optionally merging the Meshes together and then deleting any empty Empties.
	- Finally, exporting an FBX within the same directory as the Blender file (with optimal settings) before reloading the original Blender file.
	- *Note: The temp. file will remain in case the user wants to see what the output was or if they want to edit it further.*
- Some constants were added and others were moved around. Nothing crazy, though.
- That's... that's about it. :I


### v0.1.7 - 5/25/2022
[TL;DR VIDEO](https://youtu.be/1yhHw0WMBkE)

#### ANNOUNCEMENT - The Big Code Migration!
- There was a big transition during this update where most of the python code inside of the blender file was moved outside to their own python files. This was a necessary change for the sake of making things more streamlined, as the script was getting too bloated. I lost track of a few changes along the way :(
- The "DoEverything" script has been removed and a "RunTheExternalCode" script now exists in its place, since most of the code was moved outside the Blender file.
- There was an exception, however, which was the code for automatically installing/updating the python modules. That still remains inside of the Blender file as the script named "AutoInstallModules". Again, you will need to run Blender in administrative mode for this script to execute correctly. Check out the v0.1.6 update for more details about how to use this...
- There were many stylistic changes to the code after the move. Pycharm - the IDE I use outside of Blender - recommends a very specific formatting style based on PEP. Dunno much about it, but I do know that there are standards for writing python scripts and I was not following them very well. To be concise, a bunch of the methods, classes, variables, and arguments were renamed *slightly*. For example, **autoFillMargin** became **auto_fill_margin**.
- Because of the move, a bunch of the code was no longer compatible with Blender as it was. I had to kinda force Blender to run the external code properly, which resulted in a bunch of changes to the code both inside the Blender file and outside of it. It's all kind of dumb, and I imagine there are programmers out there who would look at my code and cringe, but... I mean, it works, and I tried my best.

#### New Python Modules
- A few new modules were recently added:
  - SciPy - a science and mathematics module which is used here for finding the best-fit curve for a given set of data points. It's needed for the new benchmarking system.
  - matplotlib - a graphing library for displaying data graphically. This is optional, but the code isn't setup to deal with it not being installed just yet...
  - PyQt5 - a graphics library for displaying windows containing UIs and much more. matplotlib requires one of a few possible libraries in order to display graphs, and this is a good pick IMO.

#### Everything Else!
- Updated **auto_fill_margin** to work with alpha values between 0 and 1. This new algorithm is more expensive but the result is quite beautiful.
- Because of how long the new **auto_fill_margin** method takes to execute, a lot more stuff was added to help make this as quick as possible:
  - The multiprocessing system. This can use multiple CPU cores to allow the method to execute a little quicker. By default this is disabled and only one process will be used for the entire method. To really take advantage of this new system, you will need to first run...
  - The new benchmarking system. At the top of the **do_the_things** method inside of the "do_the_things.py" file there are commented-out method calls for using this system (as well as the others), plus notes about what they do and which order to run them. When the benchmark is executed, the results of the benchmark are exported to a file named "benchmark.txt" inside the "the_methods" folder. You should only need to run the benchmark once unless you expect different results, in which case you'll want to delete the "benchmark.txt" file first. (If you forget and end up running the benchmark while the "benchmark.txt" file already exists, that's okay; the benchmark system will not overwrite the file, but will instead add the new data to the end of it. Just edit the file to delete the older benchmark data, and finally save.)
  - The predictive timing system. A method called **generate_bestfit_parameters** can be executed to calculate approximate curves for the data collected during the benchmark. The resulting parameters for these curves are printed to the console for you to copy and paste as the value for the *AUTOFILLMARGIN_BENCHMARK_PARAMETERS* constant located in the "bake.py" file inside of the "constants" folder. Once set, these values can be used by **auto_fill_margin** to predict how long each number of processes would take to execute for the given state, and will use the one predicted to take the least amount of time.
  - The graphing system. You can graphically display the results of your benchmark and/or your curves on a graph. Very useful for testing and debugging.
- The updates printed to the console by **auto_fill_margin** now indicate how many processes are being used for the given operation.
- Added a method called **bleed_opaque_into_non_opaque** which can be executed first inside the **auto_fill_margin** method to help improve the results a bit, since the color of the transparent/translucent pixels do affect the final results a bit.
- Added new constants for margin settings used during baking. These new constants can be found in the "bake.py" file inside the "constants" folder:
  - *[AO_]TEXTURE_BAKINGMARGIN* - Sets the size of the margin outside of the UV islands in pixels. Set this to 0 to disable. Set this to -1 to calculate the value automatically based on the *UV_MARGIN* value and the dimensions of the texture. I'd recommend -1.
  - *[AO_]TEXTURE_BAKINGMARGIN_TYPE* - Here you can set the type of margin-filling-method you want during baking. The options are "EXTEND" and "ADJACENT_FACES". I've found "ADJACENT_FACES" to be my new favorite.
- Added a sort of Multisample Anti-Aliasing for baking (I'm calling it "Bad AA"). When enabled, this will bake at a higher resolution based on the scale set in the "bake.py" file inside the "constants" folder. The texture will be scaled back down before it is post-processed. Be aware that Bad AA requires a LOT more memory and tends to cause Blender to crash (for me it does, anyway). New constants were added for this system inside the "bake.py" file inside the "constants" folder, such as *[AO_]CYCLES_BADAA* and *[AO_]CYCLES_BADAA_SCALE*.
- The baking methods take into consideration the Bad AA settings to automatically adjust other settings. For example, the number of samples performed per pixel is divided by the scale used for Bad AA when it's enabled.
- Because of the crashes, I've added a new constant called *CYCLES_TILESIZE* in the "bake.py" file inside the "constants" folder to set the size of the tiles used during baking. This constant is used by ALL baking operations. To be completely honest, I'm not it makes any difference. I really need to figure out what's causing the crashes... In the meantime, just keep this value relatively low and, after a crash, try, try again!
- The baking methods no longer save outputs between post-processing operations when *TEXTURE_SAVEASYOUBAKE* is enabled.
- Inside the "do_the_things.py" file you can now specify if you want post-processing done after baking a given texture. This is done by setting the "skip_pp" keyword-argument to True or False.
- Fixed the normal map baking! The normal values are now rotated the correct direction based on the original and the final angles of the UV faces.
- Added a keyword-argument called "bake_type" to the generic baking method... which sets the baking type used... during baking... This was added to help with fixing the problem listed above.
- Added a **coords_are_in_image** convenience method for telling if a given set of coordinates are a valid pixel location inside of a given texture.
- Notifications can now be marked as silent, meaning you can receive an update without being pinged! Because of this, the notification system is being used much more frequently now in order to keep you updated, but the overall number of pings has decreased! After all, only a small number of the notifications need your immediate attention. You're welcome :) (As a bonus, I threw in a custom notification sound for your bot. Look in the "Extras" folder for the "telegram_bot_notif.mp3" file.)
- There are now notifications inside the baking methods which indicate when a post-processing operation is being executed. These notifications are silent.
- Added a feature to the notification system where it will delay sending a notification for a moment in case another notification might be queued shortly after, to help reduce the number of notifications being sent by combining quickly queued notifications together.
- The UV Sim system no longer pads the walls of the simulation space with the sim radius. This means more usable space, and more efficient texture/UV map combinations.
- Created a new class called ProgressPrinter which is used to print progress updates to the console (you know, like 35%... 40%... 45%... etc...). This new class has replaced much of the progress printing code through out many of the python files.
- Unlike the old progress printing systems, the new ProgressPrinter class focuses strictly on time to determine when to print an update. Currently it's set to print every 5 seconds or more.
- Tweaked the code that prints deltas to instead use the delta symbol (Δ). Also added showing the delta of the delta, for funzies.
- Fixed a bug in the AO baking code where the armature wouldn't change pose.
- Fixed a context error bug with **reset_everything**.
- Tweaked the general shader node.
- The AO texture now defaults to a size of 1024x1024 (from 2048x2048) because of all the other changes allowing it to be a lower resolution while still maintaining a nice appearance.
- Disabled Persistent Data and Use Spacial Splits in the Blender file, as it made little difference during baking and used up more of the already scarce memory.
- A few seams were tweaked and/or changed on the models, and, as a result, the Master UV map has been redone.
- Other minor tweaks.

Notes:
1. Crashing while baking is still a problem. I'm still figuring that out.
2. The notification system was tweaked quite a bit to work with all the new changes, and for some reason, sometimes, you'll get multiple "... still running..." notifications in a row.
3. Naturally, there is likely to be some change I've missed. If there's anything you notice not listed here, please let me know.
4. If you discover any problems not listed here, please let me know.


### v0.1.6 - 5/11/2022
[TL;DR VIDEO](https://youtu.be/DZ_PoFp0PWI)

QUICK-NOTES:
1. I didn't do so good about keeping a comprehensive list of every little change this time around, so I might miss something.
2. Modify/Use the scripts at your own risk.
3. If you're gonna use a script, don't forget to open the System Console first. While this window is in focus, CTRL+C will force a Python script to crash, and CTRL+BREAK will cause ALL OF BLENDER to close instantly.
4. There are a bunch of labels that have been added through-out the Blender file that the scripts need to work, so be careful which things you rename and/or what you name them.
5. All textures must be in sRGB color space before being loaded into Blender. After that, the color space can be set within the Texture Node.
6. My brain is mush now.

- Went back to having as few Materials as possible within the Blender file, as the high number of Materials was slowing things waaaaay down.
- The ambient occlusion files and folder has/have been deleted.
- All UV maps named "AO_UVMap" have been deleted.
- Added texture atlas files for the Ambient Occlusion, Albedo, Specular, Smoothness, SpecularSmoothness, Emissions and the Normals. The baked textures will save in the correct color space automatically when using the script.
- All baked texture atlas files have a new naming convention. For example, "Lambie_MasterAtlas_AmbientOcclusion".
- All baked texture atlas files are now found in "Texture/Baked/".
- The Eyes and Body folders were moved to the Raw Textures folder.
- The general shader is now setup for quickly testing a finished texture atlas.
- Changed the general shader to have the ambient occlusion affect the emissions.
- Added a script to the Blender file called "AutoInstallModules". While Blender is opened in Administrator mode, running this script will install/update the following python modules for use in Blender:
  - PIL/Pillow
  - Pymunk
  - Pygame
  - opencv-python
- *Please note that the above modules won't be available for use until after installation, followed by restarting Blender.*
- Added a script to the Blender file called "DoEverything" which does... well, not *everything* per-say, but it does A LOT. Here are most of the features:
  - Constants are located at the top in all caps. These represent settings that will affect how the script executes. Some important ones not listed anywhere else are:
    - *NOTIFICATIONS* : When True, and all other required constants are setup correctly, the notification system will be enabled. This will send occasional updates to your Telegram account, allowing you to know the progress of your script without having to check from your computer.
    - *NOTIFICATIONS_FREQ* : How many seconds there are between notifications being sent to the user. If multiple notifications are queued between this interval, then they're sent together as a single notification.
    - *NOTIFICATIONS_REMINDERS* : When True, the notification system will send you a reminder notification that the script is still running, but only after enough time has passed since the last notification.
    - *NOTIFICATIONS_REMINDERFREQ* : How many seconds there are between reminder notifications. The timer for this resets after every notification.
    - *NOTIFICATIONS_TELEGRAM_YOURID* : Your personal Telegram account ID number. Required for notifications to work. KEEP THIS A SECRET!
    - *NOTIFICATIONS_TELEGRAM_BOTTOKEN* : The bot token for your personal Telegram bot that will be sending you the notifications. Required for notifications to work. KEEP THIS A SECRET!
    - *(NOTIFICATIONS_HANDLER : Don't mess with this, but it's the actual thing that keeps track and sends the notifications. You can call "add_notification(message)" on it if you want, but I wouldn't do anything else with it.)*
    - *VERBOSE_LEVEL* : An integer that determines how detailed and/or frequent the messages are in the system console. Higher numbers means more detailed and more frequent messages.
    - *EVERYTHING* : This is a tuple containing the names of every Object in the collection/scene/blender file/whatever that are considered part of your model. This tuple is used by many methods.
    - *ARMATURE_NAME* : The name of the armature object for your model.
    - *CYCLES_SAMPLES* : How many samples to use when baking textures (excluding ambient occlusion; see *AO_CYCLES_SAMPLES*).
    - *(CYCLES_MAXBOUNCES : How many light bounces you'll allow when baking textures (excluding ambient occlusion; see AO_CYCLES_MAXBOUNCES). Is usually best to leave this at 0.)*
    - *UV_\** : See the section on makeMasterUVMap below for details.
    - *TEXTURE_SAVEASYOUBAKE* : When True, the texture being baked will be exported as-is just after an object finishes baking. This is useful for getting a preview of your results early, but can slow things down a little.
    - *TEXTURE_SIZE* : The dimensions of the texture files. Generally a good idea to use powers of 2 and to keep the width and the height the same.
    - *(TEXTURE_EXTENSION : The bit of text at the end of a file's name that indicates the file format for the textures. Should be ".png".)*
    - *(TEXTURE_FILEFORMAT : Similar to TEXTURE_EXTENSION, but is used internally as a struct member for Blender's API. Should be "PNG".)*
    - *(TEXTURE_FOLDER : The location where baked textures are stored. Should be bpy.path.abspath("//Textures/Baked/").)*
    - *(TEXTURE_\*_NAME : The name of the texture file for the given material property. It's best to leave these alone unless you know what you're doing.)*
    - *AO_TEXTURE_SIZE* : The dimensions of the ambient occlusion texture. Can be different from *TEXTURE_SIZE* but should use powers of 2 and have identical width and height. Since AO usually isn't very detailed, having a lower texture size than in *TEXTURE_SIZE* is useful for speeding things up without making a huge difference in overall appearance.
    - *AO_CYCLES_SAMPLES* : How many samples to use when baking ambient occlusion. Since AO can't be filtered or post-processed without creating problems, it's best to have this set very high. Minimum would be like 256, but I'd recommend 1024.
    - *AO_CYCLES_MAXBOUNCES* : The maximum number of light bounces you'll allow when baking ambient occlusion. Low values look terrible. I recommend 32.
    - *AO_DEFAULTSETTINGS* : The default settings used for every object during ambient occlusion baking. See *AO_SETTINGS* for details.
    - *AO_SETTINGS* : A dictionary of Object names and their settings to be used during ambient occlusion baking. The final settings for an Object are a combination of the default settings in *AO_DEFAULTSETTINGS* and those specified for that object in *AO_SETTINGS*, if it exists. Otherwise it'll just use the default settings.
      - The keys are the names of the Objects. The value for every key is a dictionary of the settings for that Object.
        - "skip" : If set to True, this Object will not have its ambient occlusion baked at all. Not recommended since, right now, the margin is filled with values from other Objects and this will spill into the uv faces for this Object.
        - "pose" : The pose the armature should be in when baking the ambient occlusion for this Object. This is the name of the pose located within the pose library for the armature.
        - "enabled" : A tuple of names for Objects that should be enabled while this Objects' AO is baked. The Object being baked will always be enabled. This is merged with the names found in the default settings, if "enabled" also exists in it.
        - "disabled" : A tuple of names for Objects that should NOT be enabled while this Objects' AO is baked. Even if the name of an Object is in "enabled", it will still be disabled during AO baking if it's in "disabled". This is merged with the names in the default settings, if "disabled" also exists in it.
        - "shapekeys" : A dictionary of Object names whose value is a dictionary of shape key names and the value of those shape keys. For example, *"shapekeys" : { "ArmSocks" : { "misc_HideBeans" : 1.0 } }* would specify that the Object ArmSocks should have the shape key misc_HideBeans set to 1.0 while our Object is baking its AO.
      - All settings modified before baking AO for an Object are reset after.
    - *(DISPLACEMENT_\* : Yeah, don't touch these. They're for blurring textures and filling in the margin and stuff. )*
	- *OVERSIZE_SPRITE_SCALE* : Used by the UV Physics Simulation. This values sets the scale of the islands while its sprite is being generated. Higher values means more detail, but will require more memory and higher transform operation costs.
  - Contains a method called **doTheThings** which can be found at the bottom of the script. In it you can change parameters and comment/uncomment lines of code to control what is executed and how it executes when the method runs. By default, this method will be called every time the script runs.
  - Contains a method called **makeMasterUVMap** which takes all of the objects listed in the constant *EVERYTHING* and makes a UV map that's shared between all of them. This will leave all other UV maps alone, but will replace/create one named "Master_UVMap" (or whatever is set in the constant *UV_NAME*).
    - This method comes with two parameters:
      - *stop_after_unwrap=False* : When True, the method will not perform any further operations on the master UV map once the models have finished being unwrapped. Otherwise, it will perform Minimize Stretch, Pack, and Average Island Scale operations afterwards.
      - *leave_all_selected=False* : When True, after the method finishes executing, edit mode will be active and the Objects will be selected, along with the master UV map.
    - This method will run Minimize Stretch on the individual islands using the settings in the constants *UV_MINIMIZESTRETCH_ITERATIONS* and *UV_MINIMIZESTRETCH_ITERATIONS*. The total number of iterations ran is the product of the two constants, but having them separate allows the user to control how often the console can update with the progress vs how much python slows everything down.
	- This method will attempt to reduce UV stretching on a per-island basis. This makes the overall level of detail (how many pixels exist for a given area) closer to being uniform throughout the island.
    - This method will automatically pack the islands using the margin set in the constant *UV_MARGIN*.
    - This method will attempt to keep the relative island sizes the same when compared to each other and their polygons on the mesh.
  - Contains a method called **usePhysicsToOptimizeMasterUVMap** which uses a 2D physics engine to attempt to pack the master UV map as tightly as possible while maintaining the margin set in the constant *UV_MARGIN*.
    - This method comes with six parameters:
      - *skip_mixing=False* : When True, the method will skip over the mixing step.
      - *skip_shaking_up=False* : When True, the method will skip over the shaking up step.
      - *skip_scaling=False* : When True, the method will skip over the scaling step.
      - *skip_maximize_radius=False* : When True, the method will skip over the maximize radius step.
      - *auto_apply=False* : When True, the end result will automatically be applied to the master UV map (RISKY). Otherwise, the simulation window will prompt the user to select what to do next.
      - *leave_all_selected=False* : When True, after the method finishes executing, edit mode will be active and the objects will be selected, along with the master UV map.
    - This method opens a window for a simulation where the islands in the master UV map will each be given a physics body. It runs a series of steps, in-order, depending on if the step is enabled: Mix, Shake Up, Scale, Maximize Radius, and/or Apply.
    - The simulation has an emergency stop function where, if you hit the ESC key while the window is in focus or press the X button at the top-right corner, it will close the window and the script will deliberately crash.
    - The Mixing step will first shrink the bodies down a bit, then will spend some time spinning the bodies around the center of the simulation, allowing them to bump and bounce around. This is it average and randomize the distribution of the islands. After a bit the bodies will continue to be mixed while they slowly grow back to normal size.
    - The Shake Up step shakes the bodies randomly to spread them out. The intensity of the shaking will slowly go down as this step progresses until it eventually ends.
    - The Scaling step (arguably the most important one) will gradually test increasing scales for the bodies. It will do this so long as it can have an iteration that ends with all of the bodies touching nothing. If there are too many unsuccessful iterations, the direction of scaling will switch and the bodies will very gradually decrease in scale until either there's a successful iteration or the scale becomes too low. If the scale gets too low, the script will deliberately crash.
    - The Maximize Radius step will gradually increase the radius around the bodies used for collision detection. The effect is similar to blowing up a balloon or adding layers to a jawbreaker. This is done without changing the scale of the bodies, so the end result will be that the margin around each island is increased, wherever it physically can be. Put simply, it spaces things out nicely.
    - The Apply stage simply applies the current simulation state to the master UV map. See the details above about how auto_apply works for more.
    - There are a few constants that affect how this method works:
        - *UVSIM_EXPORTVIDEO* : When True, cv2 is imported (python's OpenCV wrapper) and the simulation will be exported to a video named "output.avi". Using this is usually not recommended as it slows things down, but it's fun for showing off your simulation afterwards.
        - *UVSIM_PRETTY* : When True, anti-aliasing will be used on text and lines, and slightly more expensive (but nicer looking) transform operations will be used on the sprites.
        - *UVSIM_CINEMATICS* : When True, additional pauses will occur throughout the steps to allow for an easier viewing experience. This costs a bunch more time, but is really nice for exported videos.
        - *UVSIM_SHOWCENTERDEBUG* : When True, circles are drawn to indicate several spots that are the various "centers" of the bodies. Two represent Center of Gravity, while one represents the center of the sprite. Only really useful for developers.
        - *UVSIM_FORCEDEBUG* : When True, debug will be forced to render.
        - *UVSIM_FORCESHOWCOLLISIONS* : When True, the collision debug will be setup and forced to render during runtime.
        - *UVSIM_KEEPITSIMPLE* : When True, certain aspects of the simulation rendering that are known to slow things down will be suppressed (mostly used to turn off drawing the radius debug, since it's pretty expensive).
        - *UVSIM_HOLLOWOUTFATISLANDS* : When True, thicker bodies will only have the faces at and near the edges of the island created. This reduces the number of shapes needed to be simulated and can improve performance, although at a higher risk of tunneling.
  - Contains the method **bakeAO** which will bake an ambient occlusion texture for all objects listed in the *EVERYTHING* constant using the master UV map. A quick blur pass is applied to help improve the overall look of this texture after baking is finished.
  - Contains the method **loadAO** which loads the ambient occlusion texture into memory and sets it up within the general shader.
  - Contains the method **resetAO** which deletes the ambient occlusion texture from memory and resets that part of the general shader changed by loadAO. Should be called if resetEverything isn't, since this method (resetAO) is called inside that method (resetEverything).
  - Contains the method **bakeAlbedo** which will bake an albedo texture for all objects listed in the *EVERYTHING* constant using the master UV map. If ambient occlusion is loaded when this method runs, it will be baked into this texture.
  - Contains the method **bakeSpecular** which will bake a specular texture for all objects listed in the *EVERYTHING* constant using the master UV map. If ambient occlusion is loaded when this method runs, it will be baked into this texture.
  - Contains the method **bakeSmoothness** which will bake a smoothness texture for all objects listed in the *EVERYTHING* constant using the master UV map. If ambient occlusion is loaded when this method runs, it will be baked into this texture.
  - Contains the method **bakeEmissions** which will bake an emissions texture for all objects listed in the *EVERYTHING* constant using the master UV map. If ambient occlusion is loaded when this method runs, it will be baked into this texture.
  - Contains the method **bakeNormals** which will bake a normal map texture for all objects listed in the *EVERYTHING* constant using the master UV map.
  - *Note that, for all baking methods, the texture will be saved to the hard-drive before being automatically deleted from memory.*
  - *Note that, for all baking methods, the margin will automatically be filled in using a custom method after baking finishes.*
  - Contains the method **mergeSpecularAndSmoothness** which temporarily loads the specular and smoothness textures into memory (if they exist) and created a new one where, for every pixel, the color value is copied from the specular texture but the alpha is set as the color value from the smoothness texture.
  - Contains the method **resetEverything** which you should run before any other method within doTheThings, but is optional for after all the other methods. It more-or-less returns the state of Blender to a more familiar/expected one.
  - There's a bunch more stuff located in this script, but I don't want to go through all of it, and really no one else needs to know how it all works anyway...
- Renamed the internal text file "File" to "ShrinkToHide" as that was a script that originally came with the Blender file and is designed to do just that.
- Modified a bunch of the seams for a bunch of the Meshes.
- Tweaked the general shader.
- Renamed Collection to AvatarCollection. This will be used for exporting the finished model as an FBX, so look out for that feature in a future update!
- Added a few test textures and models to debugging the scripts.


### v0.1.5 - 4/25/2022
[TL;DR VIDEO (this one is quite long, really)](https://youtu.be/xkZAqEyfSL0)
- Took first steps towards baking a master texture atlas. This should help optimize the avatar in Unity and VRChat, although this is not ready yet.
- Took steps towards allowing people to fully modify the avatar without needing to pay for software like Substance Painter.
- Accessed the Substance Painter files to export high resolution textures, including albedo maps WITHOUT baked in ambient occlusion.
- Added the high res textures to the Blender file and deleted the old image files as they're now redundant, with the exception of the ones for the nipples and the eyes.
- Modified the Blender file for AO baking. Changes include:
  - Grouped the original textures into group nodes to be shared between materials.
  - Made a group node for the general shader. It is shared between every material so they can all be affected by shader changes simultaneously.
  - Modified the general shader to use the AO to reduce albedo, specular, and smoothness values.
  - Added custom seams to every object. Please note that these may not match with the seams found on the original UVs for that object.
  - Removed the pins from the UVs on certain objects. Watch out for that...
  - Made individual materials for every object. This was done to allow for easily customizing specific objects without having to touch anything else.
  - Made individual AO textures for every object. This ensures every object's AO can be baked individually and appear correct, since batch AO baking doesn't allow for nuance when it comes to selecting which models will occlude ambient light or not.
  - Made individual AO UV Maps for every object, named "AO_UVMap". These were unwrapped using the custom seams, optimized to use as much of its texture as possible, then relaxed using Minimize UV Stretch.
  - Renamed the original UVMap for every object to "Original_UVMap".
  - Modified the sharp/smooth shading for parts of some objects to help reduce/remove black spots and artifacts generated during AO baking.
  - Modified some of the vertices on some objects to reduce clipping.
  - Added a special shape key to some objects named "util_AOBaking" to help with (you'll never guess) baking AO. (Also "AO Face", lul)
  - Added a pose library to the armature. Made a default pose and an AO baking pose.
- Baked AO textures for every object. All baking was done with the max bounce Full Global Illumination preset, 1024 samples, and no clamping.
- Changed the default glasses, the piercings, and the hair clips to no longer use the original textures, since they're not needed - aside from the AO, each one has uniform textures, so setting the inputs to the general shader is enough (It's all getting baked into one atlas anyway, so who cares).
- Organized all the new textures into a folder called "Raw Textures".
- Fixed the vertex weights on the latex garters.
- Reorganized all of the shape keys.
- Added misc_ArmsSlim shape keys to the body and the arm socks. This reduces the thickness of the forearms. Exact change was ( 0.85, 1.0, 0.75 ) scale set to the forearm bones.
- Added vrc.v_lookup and vrc.v_lookdown shape keys to the body. These were made from the eye tracking shape keys.
- Added a nose_Flare shape key to the body.
- Added a nose_Scrunch shape key to the body and the default piercings.
- Added a misc_Breathe shape key to the body and the fluff.
- Removed the deltas around the muzzle for the eye squeeze shape keys.
- Repaired the symmetry of the eyes_Smile shape key.
- Redid the eyes_Lewd shape key, since repairing its symmetry was too difficult.
- Redid the HideBeans shape key from scratch since I apparently broke it at some point on the arm socks.
- Renamed the "HideBeans" shape key to "misc_HideBeans" on the arm socks.
- Renamed the "AntlerSize" shape key to "misc_AntlerSize" on the antlers.
- Renamed the "HornSize" shape key to "misc_HornSize" on the horns.
- Deleted some weird polygons floating inside of the ponytail's hair tie.
- Switched all textures to use extend instead of repeat.

Notes:
1. This still isn't ready for baking to a master texture atlas.
2. I upgraded from Blender v3.1.0 to v3.1.2 while working on this. Based on what I've read, this should help with some of the AO baking artifacts.
3. I enabled the Material Utilities addon while working on this. It probably won't affect the file but I felt it was important to share, just in case... plus it was really useful.
4. The Blender file now takes a while to load and requires a lot of memory because of the massive texture files, plus every material needs to be compiled separately at load time. Your GPU usage will likely increase as well.
5. Any changes done to the general shader will affect all materials that use it. This may mean having to wait for all of the shaders to compile. This slows things down a bit.
6. Because of the high memory requirements, it's recommended not clicking out of Blender while an unsaved texture is baking or exists. I can't be certain of this but Blender might unload it if Blender isn't in focus. You should probably also stop anything extra running in the background to free up the CPU, RAM, and GPU for Blender.
7. For the love of all that's good and Holy, please, if you're going to bake stuff, DO NOT FORGET TO SAVE YOUR TEXTURES!! By default it's going to sit in memory, NOT overwrite the image file.
8. I may have forgot something here. Please let me know if something is wrong or needs attention.


### v0.1.4 - 4/16/2022
[TL;DR VIDEO](https://youtu.be/gqvzrNFIj6M)
- Added some new shape keys! We've now got mouth_Grin, mouth_CheekySmile, and eyes_Smile. Also added in eye tracking blend shapes.
- Added a Tongue_root and Tongue bone to the armature. The Tongue bone is left disconnected from the Tongue_root to allow for stretching.
- Also modified the tongue to be affected by these new bones. This is to allow for well timed and controlled animations during specific expressions so the tongue doesn't clip through parts of the mouth. Speaking of which...
- Modified the mouth_Blep and mouth_Lewd shape keys to stop the tongue from automatically exiting the mouth.
- Made sure the new Tongue vertex weights were symmetrical. I gotchu, fam.
- Cleaned up all of the viseme and expression shape keys so that only the relevant parts of the face move. A whole bunch had problems where the shape key was thought to be symmetrical but was a bunch of vertices were moved to the same spot when snapped to symmetry.
- Repaired the mouth_BigScaredFrown and mouth_BigStupidGrin shape keys.
- Improved the vrc.v_blink shape key and copied it to the eyes_Closed shape key.
- Fixed some weird issues with the inside corners of the eyes for the eyes_Sexy shape key.
- Redid the eyes_Angry shape key from scratch. Now the forehead moves with the eyebrows.
- Modified the eyes_Raised shape key so the forehead moves with the eyebrows.
- Modified the eyes_Sexy shape key so the forehead moves with the eyebrows slightly.
- Made the ring piercings smoother by adding more polygons.
- Cut up the N-Gons in the Collar mesh to make them into quads.
- Connected a bunch of bones in the ponytail armature that weren't connected for some reason.
- Moved the ponytail armature back into the main armature and moved the PonyTail object to the HeadStuff grouping.
- Tweaked the ponytail bones so they're nice and centered inside the ponytail mesh.
- Connected the Neck bone to the Head bone.
- Disconnected the Collar bone from the Neck bone and connected it to the Chest bone instead.
- Changed the normal map for the eyes to the "B2" variant. Still noticing some weirdness though.
- Removed a bunch of unused vertex groups from the Fluff Object.
- Renamed the body albedo textures to use a Body_AlbedoTransparency_VARIANT convention.
- Renamed the hair albedo textures to use a Hair_AlbedoTransparency_VARIANT convention.
- Renamed "Nipples_Albedo_Deer" to "Nipples_AlbedoTransparency_Deer".

Known Issues:
1. The eyes_Smile shape key is not symmetrical. Every attempt to snap to symmetry fails to work. Will need to be manually repaired in the future.
2. The eyes_Lewd shape key is very much not symmetrical. Will need to be manually repaired in the future.


### v0.1.3 - 4/5/2022
[TL;DR VIDEO](https://youtu.be/Pb3Ra5HmcqQ)
- Added nipples and nipple piercings! For the nipples, I'm using the first version of my [Lambie v2 Seamless Nipples asset](https://raubana.gumroad.com/l/lambie2_nipples_v2) (BTW, the newer versions are better and there are free updates). For the piercings, I reused the models from my free "nips and tips" asset posted on the FoxHoleVR Discord, which I also made symmetrical.
- Added a Misc grouping, which is where the Fluff Object and the Nipples Object exist.
- Fixed the ponytail mesh.
- Tweaked the ponytail armature to more accurately match that of the ponytail model.
- Lightly corrected the antlers' position, as it was offset.
- Updated color space on pretty much everything!


### v0.1.2 - 4/3/2022
- Finished fixing/updating all visemes and facial expression, as well as making sure they were all symmetrical.
- That's about it, really... Oh, and I did a [test](https://youtu.be/koyTyDUYci4).


### v 0.1.1 - 4/2/2022
[TL;DR VIDEO](https://youtu.be/WGvrvBIfjzU)

- Everything that can be symmetrical should be 100% symmetrical now! You should no longer need to use topology mirroring.
- Made ALL shape keys on ALL Meshes symmetrical.
- Reorganized many objects - mostly the ones for the head - to clean up the model a bit. The ponytail also sits outside of the HeadStuff Object now. Couldn't figure out a way to make it work within the HeadStuff Object that was clean.
- Redid the mouth so that the facial shape keys (such as the visemes) look better (I still need to go through and update 95% of the shape keys that were affected by this change).
- Redid the AA, CH, DD, E, and FF visemes from scratch.
- Added eyes! One unique Object (and model) for each eye so they can be reskined separately in Unity, should someone desire to.
- Added a shader for the eyes. It's nothing special, and doesn't look anything like the one in Unity, but it gets the job done.
- Renamed the eye bones, plus added "_hack" child bones that the eyes are parented to so they can be easily animated (Just don't forget that the eye shader the Lambies come with makes the eyes look at the camera from certian angles and distances, meaning you'll also need to tweak your Material parameters in order to animate the eyes properly).
- Renamed the breast bones to Breast_root.L/R and Breast.L/R.
- Removed the spacer shape keys from the body (the ones that don't do anything).
- Renamed the Slim shape key to SlimBody.
- Added the "misc_" prefix to the BreastSize, SlimBody, and Vagina shape keys.
- Added a shape key called misc_SmoothBody which smooths out the body.
- Moved the fluff Meshes and the "fluff_" shape keys into a unique Object.
- Renamed fluff_Pubes and fluff_PubesPPFix to fluff_Pubic and fluff_Pubic_PPFix, respectively.
- Tweaked the pubic fluff to move to a correct position during changes to the misc_SlimBody and misc_SmoothBody shape keys.
- Made the area where the labia shows up smoother, then fixed the misc_Vagina shape key that broke because of that change.
- Cleaned up a bunch of orphan data from the Blender file.


### v 0.1 - 4/1/2022
[TL;DR VIDEO](https://youtu.be/1p84gk1ri6w)

- All Meshes - and their vertex group's weights - are now 99% symmetrical (I still need to work on the shape keys, though). Seriously! Assuming you continue to use the symmetry features of Blender, you should have much fewer symmetry problems with this model.
- Fixed vertex weight problems with the left elbow - it used to poke through the arm sock while bent, but not anymore!
- Fixed vertex weight problems with the right ear - it had a blotch of high weight inside the ear, but not anymore!
- Fixed spelling errors.
- Renamed Objects, Meshes, and Materials to more standardized names. OBJECT_mesh, Clothing_material, etc...
- Added custom-made shaders in the Blender file for every material to give an idea of what the model will look like once exported into Unity. Note: it's not 100% identical, and also depends on which shader and parameter values are used within Unity.
- Changed all clothing Objects to use the same Clothing Material.
- Moved some stuff into their own Objects:
  - collar
  - default piercings
  - default glasses
  - hair clips
  - flower
  - antlers
  - goat horns
  - ponytail
- Moved the ponytail bones into a unique Armature.
- Changed the "Hide" shape keys for the antlers and the goat horns to "Size" shape keys: they change the size of the Meshes instead of hiding them away in the avatar's head.
- Reorganized most Objects into groupings: "Clothing", "Accessories", and "HeadStuff".
- Renamed all bones/vertex groups:
  - Bones that ended with "_L" are now ".L", and "_R" to ".R". This is a Blender convention which can allow changes to one vertex group's weights to be mirrored on its counter-part, keeping them both symmetrical.
  - The collar was renamed to just "Collar".
  - Renamed all ponytail bones to more standard, English names. PonyTail_root, PonyTail_x...
  - Similar changes following the same formulas were applied to other bones and their children.
- Renamed and reorganized all shape keys to use more standardized conventions.
- Moved the mouth and eye compontants of the "LewdFace" shape key into their own shape keys.
- Removed some shape keys, mostly ones that aren't useful anymore, such as the ones that hide stuff away.
- Removed redundant vertex groups from all Objects.
- Removed the bikini bottom.
- Removed the latex suit.
- Applied the 90 degree rotation to the main armature.

Notes:
1. I probably forgot some things... I may go back and fix some of these things, so watch out for that!
2. This model hasn't been tested yet, but seems okay within Blender.
3. I plan to make a template Unity project for this avatar. It's going to be great!
4. In the future, more shape keys will be added and some existing ones will be modified. I might even remove some.
5. In the future, more bones will be added to the armature and some existing ones will be modified.
6. In the future, more Meshes will be added.
7. In the future, more Textures will be added and some existing ones will be modified.
8. There may even be some future changes I forgot to list here.
