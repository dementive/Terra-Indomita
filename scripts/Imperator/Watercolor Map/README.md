Hi, I've had the need to make a good quality watercolor map for a mod in Imperator Rome, one in which the sea floor elevation realistically resembles the land right next to it while having 0 information about the actual sea floor. So I made a generator that works for ck3 and Imperator. 

A frequent "problem" we modders usually have is that we go to great lengths to make an exquisite heightmap, specially if the map is based on some real part of the world and we can access satellite data, but then we have to hand paint or apply rough shaders to the watercolor map that defines the height below sea level. Sometimes if you are really talented, you can achieve a very good result, but other times (like in my case) one can't always wake up the inner Bob Ross.

The github page with instructions: https://github.com/sp-droid/myrepo/tree/main/Projects/Python/3imperatorrelated/10watercolorGen

Here you can find the entire program save for the heavy files, which you can download from the link "Download heavy files" inside. To run it, open the watercolor.ipynb with a notebook editor like VSCode or JupyterLab and run cell by cell. Be sure to drop your heightmap in the input folder. For ck3, you have to downscale your heightmap by TWO and color all WATER to BLACK rgb(0,0,0). For imperator the downscale factor is FOUR.

The only parameters you really have to tune correctly are in the **last cell (with instructions): equator, temperate_center and artic_center**

If you are using it on Imperator, I advise you to increase the contrast 10%, brightness 10% and then lighting 4-6% with an external tool like Gimp

You need to install Python and have the following modules:
Numpy, pandas, scipy, scikit-learn, tqdm, joblib, matplotlib, PIL and dill.

Model short explanation:
A multistep watercolor-maps from heightmap without sea floor generator.
- Tectonic convergent or divergent/transform zones. Based on data from the nearest land points, we input into a pre-trained neural network and obtain the boundaries.
- Sea floor elevation. ídem, but we add the boundary information to a different but also pre-trained neural network
- Peak detection. Downsample + Go through every pixel, looking for places where the elevation is high compared to the neighbors
- Diffusion limited aggregation to model erosion from the peaks in previous step. Apply gaussian blur and upsample
- Combine previous map with the sea floor elevation one, normalize sea from 0 to 127, land from 128 to 255
- Go through every pixel applying color based on numerous conditions

Some results:
- A Broken World [Imperator Rome]
![image](https://user-images.githubusercontent.com/52839915/176153458-1b0cf115-aacf-479c-a78a-673080512768.png)

![image](https://user-images.githubusercontent.com/52839915/176153592-7ab1716a-b08f-41e7-b10a-d3139bb0f887.png)

![image](https://user-images.githubusercontent.com/52839915/176153624-517f060d-52a9-4c4e-8855-4efd30d30cec.png)

![watercolor_rgb_waterspec_a](https://user-images.githubusercontent.com/52839915/176159887-87e91c3d-6ae2-4556-90cd-9641199e4d47.png)


- The Way of Kings [CK3]
![2](https://user-images.githubusercontent.com/52839915/176154828-6962e719-b899-4d0b-81e0-78279a9bb9b1.jpg)

![2B](https://user-images.githubusercontent.com/52839915/176154862-8339650b-6173-4adc-8168-f8304e6f5549.jpg)

![watercolor_rgb_waterspec_a](https://user-images.githubusercontent.com/52839915/176154880-35e0ca14-db25-435e-89e6-28d133e74ad0.jpg)


- Lord of the Rings: Realms in Exile [CK3]
![1](https://user-images.githubusercontent.com/52839915/176159456-e03b6eaf-26f8-42c1-8a86-28a4b5f6a1fd.jpg)

![2](https://user-images.githubusercontent.com/52839915/176159471-afbae7b7-7336-463e-86b4-40209cf30b6d.jpg)

![watercolor_rgb_waterspec_a](https://user-images.githubusercontent.com/52839915/176159484-c16611d5-24d1-405b-be7e-3ce2ac11f5ef.jpg)

Intermediate steps example [Vanilla CK3]:
![step1](https://user-images.githubusercontent.com/52839915/176160226-3f68c35e-f70a-43db-a3bf-42dcfbf55ae3.jpg)
![step2](https://user-images.githubusercontent.com/52839915/176160283-611d3a30-539c-4d62-bb5a-ee0e9053f6f1.jpg)
![step3](https://user-images.githubusercontent.com/52839915/176160294-492bf387-cc78-4496-ad07-5d4aeab84058.jpg)
![step4](https://user-images.githubusercontent.com/52839915/176160302-77633476-cabe-4928-9517-c7186566d34c.jpg)
![step5](https://user-images.githubusercontent.com/52839915/176160334-019b5774-f04f-4b97-93d1-d5df0d296ac2.jpg)
