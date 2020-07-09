import sys
import geopandas as gpd
import shapefile as shp  # Requires the pyshp package
import matplotlib.pyplot as plt


try:
    infile = sys.argv[1]
except Exception as e:
    # print(e)
    print("need a shp file")
    raise SystemExit

shapefile = gpd.read_file(infile)
print(shapefile)




sf = shp.Reader(infile)

plt.figure()

for shape in sf.shapeRecords():
    for i in range(len(shape.shape.parts)):
        i_start = shape.shape.parts[i]
        if i==len(shape.shape.parts)-1:
            i_end = len(shape.shape.points)
        else:
            i_end = shape.shape.parts[i+1]
        x = [i[0] for i in shape.shape.points[i_start:i_end]]
        y = [i[1] for i in shape.shape.points[i_start:i_end]]
        plt.plot(x,y)

plt.show()


# also see:
# https://matplotlib.org/basemap/users/intro.html
# https://basemaptutorial.readthedocs.io/en/latest/shapefile.html
