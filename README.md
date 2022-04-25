# Lambie v2 Raubana Remaster
A **VERY NSFW** repo of a VRChat avatar originally made by Shiba, improved by Ikeiwa, and now improved by me! A part of [FoxHoleVR](https://foxholevr.com/). 

**18+ ONLY! SERIOUSLY, THIS IS SO NOT SAFE FOR WORK, I'M ALMOST TOO TERRIFIED TO PUT IT ON MY GITHUB.**

This is NOT for sale/resale, but is free to be distributed and/or modified. Just don't forget to support and give attribution to the original creators, Shiba and Ikeiwa!

Also, if you'd be so kind, please [throw a little "support" my way](https://ko-fi.com/raubana), too. I am very broke ;-;


## Change Log:
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