
pops = ["priest", "merchant", "architect", "artist"]

for i in range(4):
	for x in range(5):
		x += 1
		if x <= 1: 
			print(f"country_has_{x}_{pops[i - 1]}_tt:0 \"[THIS.GetCountry.GetName|Y] has at least #Y {x}#! {pops[i - 1]}\"")
		else:
			print(f"country_has_{x}_{pops[i - 1]}_tt:0 \"[THIS.GetCountry.GetName|Y] has at least #Y {x}#! {pops[i - 1]}s\"")
