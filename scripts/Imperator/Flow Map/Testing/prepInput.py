from PIL import Image, ImageFilter

heightmap = Image.open('input/heightmap.png')

white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 0, 128)

width, height = heightmap.size

out_heightmap = heightmap.convert('RGB')

# Find black pixels on heightmap and turn them white
# Then take all pixels that are not black into black

for x in range(width):
	for y in range(height):
		current_color = out_heightmap.getpixel( (x,y) )

		if current_color == black:
			out_heightmap.putpixel( (x,y), white)
		else:
			out_heightmap.putpixel( (x,y), black)


# # Resize 1/4 size
out_heightmap = out_heightmap.resize( [int(0.25 * s) for s in out_heightmap.size] )

out_heightmap = out_heightmap.filter(ImageFilter.GaussianBlur(radius = 1))

out_heightmap = out_heightmap.save("output/heightmap.png")


# Process pixels and mark everything that is a river (or touching a white pixel to include navigable rivers)
def iterate_rivermap(mode="first_pass"):
	for x in range(width):
		for y in range(height):
			cur_pixel = rivers_out.getpixel((x,y))
			if mode == "first_pass":
				if cur_pixel == white:
					rivers_out.putpixel( (x, y), black)
				if cur_pixel == pink:
					rivers_out.putpixel( (x, y), white)
			if mode == "second_pass":
				if cur_pixel == white:
					#On the second pass check if at least 4 adjacent pixels of a white pixel, which was just marked, are pink
					# if found, set it to pink like other rivers
					adj = 0
					try: 
						one = rivers_out.getpixel((x + 1,y))
						two = rivers_out.getpixel((x ,y + 1))
						three = rivers_out.getpixel((x - 1,y))
						four = rivers_out.getpixel((x ,y - 1))

						bottom_left = rivers_out.getpixel((x - 1,y - 1))
						bottom_right = rivers_out.getpixel((x + 1,y - 1))
						top_left = rivers_out.getpixel((x - 1,y + 1))
						top_right = rivers_out.getpixel((x + 1,y + 1))
					except IndexError:
						pass
					if one == pink: adj += 1
					if two == pink: adj += 1 
					if three == pink: adj += 1 
					if four == pink: adj += 1
					if bottom_left == pink: adj += 1
					if bottom_right == pink: adj += 1 
					if top_left == pink: adj += 1 
					if top_right == pink: adj += 1

					if adj >= 5:
						# river pixel that should be pink
						rivers_out.putpixel( (x, y), pink)

#iterate_rivermap()
#iterate_rivermap("second_pass")

# rivers1 = rivers_out
#rivers_out = rivers_out.save("output/rivers_out.png")

# for x in range(width):
# 	for y in range(height):
# 		current_color = rivers_out.getpixel( (x,y) )

# 		if current_color != black and current_color != white:
# 			rivers_out.putpixel( (x,y), white)
# 		if current_color == black:
# 			rivers_out.putpixel( (x,y), white)
# 		if current_color == white:
# 			rivers_out.putpixel( (x,y), black)

# rivers1 = rivers_out
# rivers_out = rivers_out.save("output/rivers_out.png")
# # # Resize 1/4 size
# rivers1 = rivers1.resize( [int(0.25 * s) for s in rivers1.size] )

# rivers1 = rivers1.save("output/outmap3.png")


# outmap1 = out_heightmap
# outmap1 = outmap1.save("output/outmap1.png")
# # Add gaussian blur with radius 1

# #out_heightmap = out_heightmap.filter(ImageFilter.GaussianBlur(radius = 1))

# # Change all black pixels (water) to rgb(255, 255, 255)
# width, height = out_heightmap.size
# out_heightmap = out_heightmap.convert('RGB')

# # Process every pixel
# for x in range(width):
# 	for y in range(height):
# 		current_color = out_heightmap.getpixel( (x,y) )

# 		if current_color == black or current_color == pink:
# 			out_heightmap.putpixel( (x,y), white)
# 		else:
# 			out_heightmap.putpixel( (x,y), black)

# outmap2 = out_heightmap
# out_heightmap = out_heightmap.save("output/outmap2.png")

# # Resize 1/4 size
# outmap2 = outmap2.resize( [int(0.25 * s) for s in outmap2.size] )

# outmap2 = outmap2.save("output/outmap3.png")
