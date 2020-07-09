import sys, os, re
import geopandas as gpd
import shapefile as shp  # Requires the pyshp package
import matplotlib.pyplot as plt
from zipfile import ZipFile



def print_map(shapefile):
    s = gpd.read_file(shapefile)
    print(s)

    sf = shp.Reader(shapefile)

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



try:
    directory = sys.argv[1]
except Exception as e:
    print("need an input dir")
    raise SystemExit

tmp_dir="tmp"


lines = []


def print_line(d):
    format_line="{filename}\t{taxon_filename}\t{taxon_shape_file}\t{legend}\t{citation}\t{year}"
    format_line="{taxon_filename}\t{taxon_shape_file}\t{legend}\t{citation}\t{year}"
    print(format_line.format(**d))
    lines.append({ 'year': int(float(d['year'])), 'line': format_line.format(**d) })


# print_line({
#     'filename':'filename', 
#     'taxon_filename':'taxon_filename',
#     'taxon_shape_file':'taxon_shape_file', 
#     'legend':'legend', 
#     'citation':'citation', 
#     'year':'year'})

for filename in os.listdir(directory):
    if filename.endswith(".zip"): 
        # print(os.path.join(directory, filename))
        try:
            with ZipFile(os.path.join(directory, filename), 'r') as zipObj:
                zipObj.extractall(tmp_dir)
                shapefile = gpd.read_file(os.path.join(tmp_dir,'data_0.shp'))
                # print_map(os.path.join(tmp_dir,'data_0.shp'))
                # print(shapefile.columns)
                for index,row in shapefile.iterrows():
                    if 'Extant' in row['LEGEND']:
                        print_line({
                            'filename':filename, 
                            'taxon_filename':re.sub('_',' ',re.sub(r'(redlist-species-data--|\.zip|--\(\d{4}-\d{2}-\d{2}\s{1}\d{1,2}\:\d{2}\:\d{2}\))', '', filename)),
                            'taxon_shape_file':row['BINOMIAL'], 
                            'legend':row['LEGEND'], 
                            'citation':row['CITATION'], 
                            'year':row['YEAR']})

        except Exception as e:
            print("ERROR: {} {}".format(filename,e))

        
        lines.sort(key=lambda x: x['year'], reverse=False)
        print(lines)




exit(0)

# also see:
# https://matplotlib.org/basemap/users/intro.html
# https://basemaptutorial.readthedocs.io/en/latest/shapefile.html
