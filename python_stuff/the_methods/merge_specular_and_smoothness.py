import common
import constants

import notifications

try:
    import PIL
    from PIL import Image, ImageDraw
except:
    common.general.safe_print("WARNING: Missing module 'PIL'. Please run auto_install_modules.")


def run( post_cleanup=True ):
    common.general.safe_print("\n")
    common.general.safe_print(" ===   Merging Specular and Smoothness Maps   === ")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification(
        "\U0001f533 Merging specular and smoothness maps", is_silent=False)

    # Blender pisses me off sometimes... they insisted on having the program exporting ALL
    # transparent images using premultiplied alpha instead of straight alpha, which is standard.
    # Gotta do something else here to make this work.
    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Loading images into memory...")

    spec_img = PIL.Image.open( common.general.clean_filepath(
        constants.texture.TEXTURE_BAKED_FOLDER + \
        constants.texture.TEXTURE_SPECULAR_NAME + \
        constants.texture.TEXTURE_EXTENSION
    ))
    smooth_img = PIL.Image.open( common.general.clean_filepath(
        constants.texture.TEXTURE_BAKED_FOLDER + \
        constants.texture.TEXTURE_SMOOTHNESS_NAME + \
        constants.texture.TEXTURE_EXTENSION
    ))
    specsmooth_img = PIL.Image.new("RGBA", constants.texture.TEXTURE_SIZE)

    spec_pixels = spec_img.load()
    smooth_pixels = smooth_img.load()
    specsmooth_pixels = specsmooth_img.load()

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done. Applying alpha to the specular map...")

    progressprinter = common.general.ProgressPrinter(float(constants.texture.TEXTURE_SIZE[0] * constants.texture.TEXTURE_SIZE[1]))
    for y in range(constants.texture.TEXTURE_SIZE[1]):
        for x in range(constants.texture.TEXTURE_SIZE[0]):
            progressprinter.update(x + (y * constants.texture.TEXTURE_SIZE[0]))

            specular = spec_pixels[x, y]
            # https://handlespixels.wordpress.com/2018/02/06/understanding-gamma-correction/
            smoothness = \
                int(((smooth_pixels[x, y] / 255.0) ** 2.2) * 255)  # I'm too lazy to figure this out any further, fuck it.

            specsmooth_pixels[x, y] = specular + (smoothness,)

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done. Saving resulting image...")

    specsmooth_img.save( common.general.clean_filepath(
        constants.texture.TEXTURE_BAKED_FOLDER + \
        constants.texture.TEXTURE_SPECULARSMOOTHNESS_NAME + \
        constants.texture.TEXTURE_EXTENSION
    ))

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Cleaning up images...")

    if post_cleanup:
        common.general.safely_delete_file(constants.texture.TEXTURE_BAKED_FOLDER + constants.texture.TEXTURE_SPECULAR_NAME + constants.texture.TEXTURE_EXTENSION)
        common.general.safely_delete_file(constants.texture.TEXTURE_BAKED_FOLDER + constants.texture.TEXTURE_SMOOTHNESS_NAME + constants.texture.TEXTURE_EXTENSION)

    if constants.other.VERBOSE_LEVEL >= 1: common.general.safe_print(" - Done.")

    if notifications.constants.ENABLED: notifications.constants.HANDLER.add_notification("\U00002714 Merge complete", is_silent=False)
