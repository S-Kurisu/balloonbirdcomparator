# balloonbirdcomparator
A Python program that compares weather balloon data with common bird species locations.
The program combines a weather balloon dataset with a bird location dataset in order to create maps spanning the last 24 hours.
These maps contain data points of the weather balloons and the datapoints of common bird species within the last day.
The weather balloon data is accessed through an API request from Windborne Systems and the bird data is accessed through an API request from eBird.

The program is split into 2 files: a GUI file that creates the interface of the maps and a Plot_Coord file that sends an API request and plots the data received onto a map.
The code utilizes multiprocessing in order to process the API calls at a faster rate.
