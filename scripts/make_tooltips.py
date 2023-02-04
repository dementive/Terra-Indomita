
pops = ["priest", "merchant", "architect", "artist"]

for i in range(4):
	for x in range(5):
		x += 1
		if x <= 1: 
			print(f"add_{x}_{pops[i - 1]}_tt:0 \"Add {x} {pops[i - 1]} to [THIS.GetProvince.GetName|Y]\"")
		else:
			print(f"add_{x}_{pops[i - 1]}_tt:0 \"Add {x} {pops[i - 1]}s to [THIS.GetProvince.GetName|Y]\"")
