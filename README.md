# geo-wizard
## Geo-Wizard synthetic dataset

We created synthetic straight line gpx files and attempted mission map data to study forms of scoring mission goodness-of-straight-line. 

## Mission Across Wales 2019

The code below generates 10 metre interval [gpx files](https://www.google.com/maps/d/edit?mid=1CEfPsf9b0YsAvp4JIoxUAg_aD2j7FdE&ll=52.71208849842348%2C-3.318586465116484&z=10) for the original straight line plus attempted mission with a zero mean and 10 metre standard deviation.

```
python generate-gpx.py \
--start_lat 52.80476458134001 \
--start_lon -3.1642720853547304 \
--end_lat 52.748098260804426 \
--end_lon -3.9358359202433366 \
--interval 10 \
--mean 0 \
--stddev 10 \
--planned_filename MIssion_Across_Wales_1.gpx \
--executed_filename MIssion_Across_Wales_1_0_mean_10_stdev.gpx \
--creator DanielSikar \
--name "GeoWizardSynthetic_MIssion_Across_Wales_1" \
--author_link https://www.github.com/dsikar \
--author_text GeoWizard \
--author_type text/html  
```


## Mission Across England 2024

![Planned straight line](images/straight-line-map.png)

The map can be accessed via this [link](https://www.google.com/maps/d/edit?mid=1CEfPsf9b0YsAvp4JIoxUAg_aD2j7FdE&ll=55.171963961229764%2C-1.6774702774991779&z=9).

The following image shows the original straight blue line plus an orange line. This is a simulated walk where the path deviated from the original with zero mean and 100 metres standard deviation. The mauve line is a simulated walk where the path deviates from the original with zero mean and 50 metres standard deviation.

![Added attempted walks](images/straight-line-and-walksx2_0_mean_100_stdev_50_stdev.png)

A detail view can be accessed via this [link](https://www.google.com/maps/d/edit?mid=1CEfPsf9b0YsAvp4JIoxUAg_aD2j7FdE&ll=55.20287313889983%2C-2.5403373008985253&z=15)

To generate data, clone the repository, then from the scripts directory run:

```
python generate-gpx.py \
--start_lat 55.6112176200343 \
--start_lon -1.702550745082108 \
--end_lat 54.97818870154609 \
--end_lon -3.001548002556341 \
--interval 100 \
--mean 0 \
--stddev 50 \
--planned_filename planned_trail.gpx \
--executed_filename executed_trail_0_mean_50_stdev.gpx \
--creator DanielSikar \
--name "GeoWizardSynthetic_0_mean_50_stdev" \
--author_link https://www.github.com/dsikar \
--author_text GeoWizard \
--author_type text/html   
```

Note, the coordinates can be obtained from google maps, by clicking on start/end mission points, right clicking and clicking on coordinates to copy to clipboard.

The script will generate two files, the planned and the executed trail. In the example given, start point is Bamburgh Beach and end point is the M6 near Mossband. Both generated gpx files contain altitude data. The interval is 100 metres between points with a mean of 0 and a standard deviation of 50 metres. The additonal parameters are filenames and metadata for the gpx files.

## Future work

There are discussions around optimal scoring approaches for attempted straight line walks. [[1]](https://gis.stackexchange.com/questions/16322/measuring-straightness-of-curve-segment-represented-as-polyline) [[2]](https://www.reddit.com/r/GeoWizard/comments/nz7exq/a_better_way_to_rank_missions/). 

We intend to implement the current approaches and add our own, to include altitude data. 

If you would like to contribute, please clone, add your code and create a pull request.

The authors: daniel.sikar, maeve.hutchinson, naman.singh @city.ac.uk




