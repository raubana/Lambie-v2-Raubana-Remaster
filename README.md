# Lambie v2 Raubana Remaster
A **VERY NSFW** repo of a VRChat avatar originally made by Shiba, improved by Ikeiwa, and now improved by me! A part of [FoxHoleVR](https://foxholevr.com/). 

**18+ ONLY! SERIOUSLY, THIS IS SO NOT SAFE FOR WORK, I'M ALMOST TOO TERRIFIED TO PUT IT ON MY GITHUB.**

This is NOT for sale/resale, but is free to be distributed and/or modified. Just don't forget to support and give attribution to the original creators, Shiba and Ikeiwa! Mostly Shiba, though. :)

Also, if you'd be so kind, please [throw a little "support" my way](https://ko-fi.com/raubana), too. I am very broke ;-;


## Change Log:

### v0.1.2 - 4/3/2022
- Finished fixing/updating all visemes and facial expression, as well as making sure they were all symmetrical.
- That's about it, really... Oh, and I did a (test)[https://cdn.discordapp.com/attachments/805718574680506399/960265731902173274/lambie_raubana_remaster_visemes_test.webm].


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
6. In the future, more Meshes will be added added.
7. In the future, more Textures will be added and some existing ones will be modified.
8. There may even be some future changes I forgot to list here.