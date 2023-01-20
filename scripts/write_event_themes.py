# Write themes from military tradition art

import os

def write_themes_in_dir(path, outfile, outfile2):
	pic_li = []

	for file in os.scandir(path=path):
		filename = file.name.replace(".dds", "")
		if filename != "_default":
			pic_li.append(filename)

	with open(outfile, "w") as file:
		for i in pic_li:
			file.write(f"{i}_event_theme = {{\n\ticon = \"gfx/interface/icons/military_traditions/{i}.dds\"\n\tsoundeffect = \"event:/SFX/Events/Generic/sfx_event_generic_uncategorized\"\n}}\n")

	with open(outfile2, "w") as file:
		for i in pic_li:
			file.write(f"{i}_event = {{\n\ttheme = {i}_event_theme\n\tpicture = \"\"\n}}\n")

if __name__ == '__main__':
	# Vanilla
	write_themes_in_dir("C:\\Program Files (x86)\\Steam\\steamapps\\common\\ImperatorRome\\game\\gfx\\interface\\icons\\military_traditions", "vanilla_out/00_mil_theme_pictures.txt", "vanilla_out/00_mil_pictures.txt")

	# Indomita
	write_themes_in_dir("C:\\Users\\demen\\Documents\\Paradox Interactive\\Imperator\\mod\\Terra-Indomita\\gfx\\interface\\icons\\military_traditions", "mod_out/00_mod_mil_theme_pictures.txt", "mod_out/00_mod_mil_pictures.txt")
