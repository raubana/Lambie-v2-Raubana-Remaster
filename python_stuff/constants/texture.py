import bpy

TEXTURE_SIZE = (4096,4096)
AO_TEXTURE_SIZE = (2048,2048)
TEXTURE_EXTENSION = ".png"
TEXTURE_FILEFORMAT = "PNG"
TEXTURE_FOLDER = bpy.path.abspath("//Textures/")
TEXTURE_BAKED_FOLDER = TEXTURE_FOLDER + "Baked/"
TEXTURE_MISC_FOLDER = TEXTURE_FOLDER + "Misc/"

TEXTURE_AO_NAME = "Lambie_MasterAtlas_AmbientOcclusion"
TEXTURE_ALBEDO_NAME = "Lambie_MasterAtlas_Albedo"
TEXTURE_SPECULAR_NAME = "Lambie_MasterAtlas_Specular"
TEXTURE_SMOOTHNESS_NAME = "Lambie_MasterAtlas_Smoothness"
TEXTURE_SPECULARSMOOTHNESS_NAME = "Lambie_MasterAtlas_SpecularSmoothness"
TEXTURE_EMISSIONS_NAME = "Lambie_MasterAtlas_Emissions"
TEXTURE_NORMALS_NAME = "Lambie_MasterAtlas_Normals"