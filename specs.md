# Optracks: a tracks analytic tool for optimizing flight moves and maybe creating new routes, for paragliding
## Features
- A map where top N tracks of a launch site are displayed.
- Raw tracks are processed into pattern-based tracks (transition, thermaling, figures of eight soaring, sounding).
- Pattern-based tracks can be kind of averaged to get the theoretical optimal track. 

## How?
- Either we create our own web application or we use an existing map with plugin. 

## Architecture
- A core source coding the pattern detection tool which is the core of the technology and added value.
- An interface to web data sources (e.g. xcontest.org). In the beginning, I will manually download tracks.
- A frontend serving the map and the user interactions (track selection etc.)
- A backend for retrieving tracks, communicating with data providers.
- No need for storing data thus no need for database?

## Stack
- Python for the backend
- Is it possible to use Python for the frontend? Cause I would put pattern detection tools in the frontend and run it client side, but since I know Python better I want it in Python. Or put this part in the backend but is it optimal in speed?

## Responses to Claude 'bout specs
### Track processing
- Top N is by distance.
- Now we do a MVP so now no advanced filtering options nor weather conditionning.
- I agree, we won't average but try to go with transition heatmap and hotspots for thermals, as done in https://thermal.kk7.ch/. But it will be a later feature.
- Launch site: doesn't matter for now i will provide tracks for mvp.
- Sounding: forget it now, we'll focus on thermaling and transitions.
- A thermal is detected when there is at least a complete turn. Reuse Python library if available.
- Figures of eight: let's add a threshold of 0.5 m/s averaged on 20s. For detecting figures of eight, we'll detect thermaling but with a change in the direction after each turn (from left to right, then right to left etc.)
- Straight ridge soaring is transition but with a 0 m/s threshold integrated over 120 seconds.

### Stack
- Ok for the database storing already processed tracks. But which one? Postgres?
- Ok for datasource risk, for now no need for interface to xcontest.
- Use existing libs. Do not use ML now, we'll go with heatmap/hotspots but idk algorithms for that.
- No notebook proto I hate them.
- You told me about cesiumJS, keplergl and folium and even MapLibre. I guess they are all map applications so why all these? Which one would be the best fit for me? I liked keplergl.


### Missing from the specs
- Don't take initiatives like that, listen to me and stfu