Hi, I made this for Imperator but it works for ck3 too. It's a normal map but using a combination of linear, exponential and constant gradients + averages of nearest points instead of just using the minimum distance. The only drawback is the need to iterate over the image, which can be time consuming. To account for it i've also used paralellization and it's quite fast. On default settings takes around a minute to work on ck3's map on my pc (i7 4790k). 

https://github.com/sp-droid/myrepo/raw/main/Projects/Python/3imperatorrelated/9flowmapGen

**In the link above you will find**:
- Program folder
- main.ipynb notebook with the code, fine tuned for ck3
- **To open and run the notebook it's recommended to have either JupyterLab, Visual Studio Code or any code editor that can run notebooks**
- Be sure you have the following libraries installed for it to work, aside from **Python3: numpy, PIL, tqdm and joblib**
- An example of input, ck3's heightmap, downscaled by a factor of 4, white (255,255,255) under sea level, black (0,0,0) above + gaussian blur with radius=1, although the last thing is not necessary at all.
![normal_input2](https://user-images.githubusercontent.com/52839915/175094023-2860834a-66a6-487c-8b12-456b15b10aa1.png)
- Rivers can be done automatically too but I didn't need it for now, if u implement it be sure to open an issue/throw a pull request! (rivers near the coast will flow towards it properly tho)

I've attached an example output for ck3, ![image](https://user-images.githubusercontent.com/52839915/175093775-eafbe03c-b025-4ecf-8577-585f2a701617.png) along with ck3's real flowmap to compare ![image](https://user-images.githubusercontent.com/52839915/175093858-a5b5e927-4258-48a5-9421-95446e458170.png)
Then a basic flowmap using a normal map online generator ![image](https://user-images.githubusercontent.com/52839915/175093908-4bb28cbc-3684-4381-b11d-b3f404572cd4.png)
Lastly an example with a world map from imperator ![image](https://user-images.githubusercontent.com/52839915/175093934-d2353273-4e32-46cb-b122-710305fb6fee.png)

This was made in large part thanks to Carlberg & MattAlexi messages about flowmaps, they were useful to design the algorithm  