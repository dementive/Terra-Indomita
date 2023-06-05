import pandas as pd

# Check for color conflicts in definition.csv file
# Make sure the top of the file is formatted like this or it won't work
"""
1;;42;3;128;Roma;x;;;;;;;;;;;;;;;;;;;
1;42;3;128;Roma;x;;;;;;;;;;;;;;;;;;;
2;84;6;1;Tiber;x;;;;;;;;;;;;;;;;;;;
3;126;9;129;Satricum;x;;;;;;;;;;;;;;;;;;;
"""

def fix_conflicts(csvfile=""):
	data = pd.read_csv(csvfile, sep=";")
	df = pd.DataFrame(data)
	r_column = df.iloc[:, 1]
	g_column = df.iloc[:, 2]
	b_column = df.iloc[:, 3]
	merged_list = zip(r_column, g_column, b_column)
	color_list = [i for i in merged_list]

	color_list_2 = []
	for i, color in enumerate(color_list):
		if color not in color_list_2:
			color_list_2.append(color)
		else:
			print(f"{color} is duplicated on line: {i + 2}")

	li = df.values.tolist()

if __name__ == '__main__':
	fix_conflicts(csvfile="definition.csv")
