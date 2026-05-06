import os

for root, dirs, files in os.walk("/home/a/Desktop/GAME/actually_usefull_textures"):
    for file in files:
        print(file)