import matplotlib.pyplot as plt
import pandas as pd

def show_plot(column="Sum", items=999, csvfile="onactionstats.csv", minimum_value=0.2):
	data = pd.read_csv(csvfile, sep=";")
	df = pd.DataFrame(data)
	df = df.iloc[:items]

	indexes_to_drop = []
	for i in df.index:
		if df[column][i] < minimum_value:
			indexes_to_drop.append(i)
	df.drop(df.index[indexes_to_drop], inplace=True)

	df = df.sort_values(column, ascending=False)
	X = df["#ID"]
	Y = df[column]
	max_y = Y[0]
	cap = 0.1 if max_y < 5 else 0.5
	max_y += cap

	fig, ax = plt.subplots()
	sc = plt.scatter(X, Y, color='green')

	annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
						bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)

	def update_annot(ind):
		pos = sc.get_offsets()[ind["ind"][0]]
		annot.xy = pos
		z = ind["ind"][0]
		value = f"{Y[z]}"
		key = "".join([X[n] for n in ind["ind"]])
		text = "Event ID: " + key + "\n" + f"{column}: " + value

		annot.set_text(text)
		annot.get_bbox_patch().set_facecolor("grey")
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			cont, ind = sc.contains(event)
			if cont:
				update_annot(ind)
				annot.set_visible(True)
				fig.canvas.draw_idle()
			else:
				if vis:
					annot.set_visible(False)
					fig.canvas.draw_idle()

	ax.set_xlabel("Events")
	ax.set_ylabel(column)
	plt.xticks([])
	fig.canvas.mpl_connect("motion_notify_event", hover)

	red_threshold = 2.5
	yellow_threshold = 1.0

	x_red_dots = X[Y >= red_threshold]
	y_red_dots = Y[Y >= red_threshold]
	x_yellow_dots = X[(Y >= yellow_threshold) & (Y < red_threshold)]
	y_yellow_dots = Y[(Y >= yellow_threshold) & (Y < red_threshold)]

	plt.plot(x_red_dots, y_red_dots, marker='o', color='red', linestyle='None')
	plt.plot(x_yellow_dots, y_yellow_dots, marker='o', color='yellow', linestyle='None')
	ax.set_ylim([0, max_y])
	plt.show()


if __name__ == '__main__':
	#show_plot(csvfile="onactionstats.csv")
	show_plot(csvfile="eventstats.csv")
