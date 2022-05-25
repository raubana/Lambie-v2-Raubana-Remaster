TEXTURE_SAVEASYOUBAKE = True


# A good BAKINGMARGIN value depends on the size of the texture and the magnitude of the uv margin.
# You can multiply the size of the smallest dimension with the magnitude of the uv margin and round down to get this.
# This can be done automatically by setting the margin here to -1.
TEXTURE_BAKINGMARGIN = -1
AO_TEXTURE_BAKINGMARGIN = -1
# There's EXTEND and ADJACENT_FACES. Turns out that ADJACENT_FACES is best to make seams look nice.
TEXTURE_BAKINGMARGIN_TYPE = "ADJACENT_FACES"
AO_TEXTURE_BAKINGMARGIN_TYPE = "ADJACENT_FACES"


# You should benchmark auto_fill_margin to get the value to set here. Otherwise, leave as None.
AUTOFILLMARGIN_BENCHMARK_PARAMETERS = None


# Unless otherwise specified, these constants will affect ALL baking.
CYCLES_SAMPLES = 1  # Turns out this doesn't make a difference when baking in cycles. If you must, use BadAA instead.
CYCLES_BADAA = True
CYCLES_BADAA_SCALE = 2
CYCLES_MAXBOUNCES = 0
CYCLES_TILESIZE = 32  # Affects all baking, including AO. Lower this if Blender keeps crashing while baking.

# These constants affect just AO baking.
AO_CYCLES_SAMPLES = 1024 # should be very high, like 256 or higher. 1024 is optimal, imo. This is automatically
# scaled down by the BADAA scale when it's enabled.
AO_CYCLES_BADAA = True
AO_CYCLES_BADAA_SCALE = 4
AO_CYCLES_MAXBOUNCES = 4  # There is evidence to suggest this variable makes no difference while baking AO.


AO_DEFAULTSETTINGS = {
    "pose": "AOBakingPose",
    "enabled": ("Body", "HairClips")
}
# Everything from EVERYTHING will have AO baked with default settings plus
# any settings shown here unless "skip" is set to True.
AO_SETTINGS = {
    "DefaultGlasses": {"enabled": ("Hair", "LeftEye", "RightEye")},
    "DefaultPiercings": {"enabled": ("Hair", "LeftEye", "RightEye")},
    "Flower": {"enabled": ("Hair",)},
    "HairClips": {"enabled": ("Hair",)},
    "PiercingsNipples": {
        "enabled": ("Nipples",),
        "shapekeys": {
            "Body": {"misc_BreastSize": 0.1},
            "Nipples": {"misc_BreastSize": 0.1},
            "PiercingsNipples": {"misc_BreastSize": 0.1},
        }
    },
    "Body": {
        "enabled": ("Hair", "LeftEye", "RightEye"),
        "shapekeys": {"Body": {"util_AOBaking": 1.0}}
    },
    "ArmSocks": {
        "shapekeys": {"ArmSocks": {"misc_HideBeans": 1.0}}
    },
    "LatexSocks_Garters": {
        "enabled": ("LatexSocks",)
    },
    "Antlers": {"enabled": ("Hair",)},
    "Hair": {
        "enabled": ("LeftEye", "RightEye",),
        "shapekeys": {"Body": {"util_AOBaking": 1.0}}
    },
    "Horns": {"enabled": ("Hair",)},
    "LeftEye": {"disabled": ("Body",)},
    "PonyTail": {"enabled": ("Hair",)},
    "RightEye": {"disabled": ("Body",)},
    "Fluff": {
        "enabled": ("Hair", "LeftEye", "RightEye"),
        "shapekeys": {"Fluff": {"util_AOBaking": 1.0}}
    },
    "Nipples": {
        "disabled": ("Body",),
        "shapekeys": {"Nipples": {"misc_BreastSize": 1.0}}
    }
}
