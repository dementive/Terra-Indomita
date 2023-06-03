import numpy as np

"""
    Automatically place city, fort, and great_work locators.
    will still have to go into map editor and manually do some locators after running but most should be good
"""

prov = {}

file = open("city_locators.txt","r")
contents = file.read().splitlines()
file.close()
for line in range(8, len(contents)-4, 6):
    ids = int(contents[line].split("=")[1])  # Get the province id's
    temp = contents[line+1].split(" ")[1:-1]
    prov[ids] = {}
    prov[ids]['city'] = [float(temp[0]), float(temp[2])]

file = open("fort_locators.txt","r")
contents = file.read().splitlines()
file.close()
for line in range(8, len(contents)-4, 6):
    ids = int(contents[line].split("=")[1])
    temp = contents[line+1].split(" ")[1:-1]
    prov[ids]['fort'] = [float(temp[0]), float(temp[2])]

for ids in prov:
    rand = np.random.choice([True, False])
    if rand:
        prov[ids]['new'] = list((np.array(prov[ids]['city'])+np.array(prov[ids]['fort'])+ np.random.choice([7, 7.25 , 8, 8.5, 9, 9.5]))/2)
        prov[ids]['new_great'] = list((np.array(prov[ids]['city'])+np.array(prov[ids]['fort'])- np.random.choice([7, 7.25 , 8, 8.5, 9, 9.5]))/2)
    else:
        prov[ids]['new'] = list((np.array(prov[ids]['city'])+np.array(prov[ids]['fort'])- np.random.choice([7, 7.25 , 8, 8.5, 9, 9.5]))/2)
        prov[ids]['new_great'] = list((np.array(prov[ids]['city'])+np.array(prov[ids]['fort'])+ np.random.choice([7, 7.25 , 8, 8.5, 9, 9.5]))/2)

with open('city_locators_new.txt','w') as file:
    file.write('game_object_locator={\n\tname="city"\n\tclamp_to_water_level=no\n\trender_under_water=no\n\tgenerated_content=no\n\tlayer="cities_layer"\n\tinstances={')
    for ids in prov:
        a, b = prov[ids]['new']
        a = "{0:.6f}".format(a)
        b = "{0:.6f}".format(b)
        file.write('\n\t\t{\n\t\t\tid='+str(ids))
        file.write(f'\n\t\t\tposition={{ {a} 0.000000 {b} }}')
        file.write(f'\n\t\t\trotation={{ 0.000000 {round(np.random.uniform(-1,0),4)} 0.000000 {round(np.random.uniform(-1,1),4)} }}')
        file.write('\n\t\t\tscale={ 1.000000 1.000000 1.000000 }')
        file.write('\n\t\t}')
    file.write('\n\t}\n}')

with open('fort_locators_new.txt','w') as file:
    file.write('game_object_locator={\n\tname="fort"\n\tclamp_to_water_level=no\n\trender_under_water=no\n\tgenerated_content=no\n\tlayer="forts_layer"\n\tinstances={')
    for ids in prov:
        a, b = prov[ids]['new']
        a = "{0:.6f}".format(a)
        b = "{0:.6f}".format(b)
        file.write('\n\t\t{\n\t\t\tid='+str(ids))
        file.write(f'\n\t\t\tposition={{ {a} 0.000000 {b} }}')
        file.write(f'\n\t\t\trotation={{ 0.000000 {round(np.random.uniform(-1,0),4)} 0.000000 {round(np.random.uniform(-1,1),4)} }}')
        file.write('\n\t\t\tscale={ 1.000000 1.000000 1.000000 }')
        file.write('\n\t\t}')
    file.write('\n\t}\n}')

with open('great_work_locators_new.txt','w') as file:
    file.write('game_object_locator={\n\tname="great_work"\n\tclamp_to_water_level=no\n\trender_under_water=no\n\tgenerated_content=no\n\tlayer="monument_layer"\n\tinstances={')
    for ids in prov:
        a, b = prov[ids]['new_great']
        a = "{0:.6f}".format(a)
        b = "{0:.6f}".format(b)
        file.write('\n\t\t{\n\t\t\tid='+str(ids))
        file.write(f'\n\t\t\tposition={{ {a} 0.000000 {b} }}')
        file.write(f'\n\t\t\trotation={{ 0.000000 {round(np.random.uniform(-1,0),4)} 0.000000 {round(np.random.uniform(-1,1),4)} }}')
        file.write('\n\t\t\tscale={ 1.000000 1.000000 1.000000 }')
        file.write('\n\t\t}')
    file.write('\n\t}\n}')
