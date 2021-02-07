NWP Data Processing Toolkit
===========================

## Usage

`./iconmanage.py` for downloading, caching and querying NWP data from DWD.

`./iconmanage.py download {now|zero} 1 2 3` will download NWP forecasts of
1/2/3 hours after model run(option `zero`) or from now on(option `now`).

The "download" action downloads the grib forecasts and converts them into a .icondb database.

To query the database, use the action "query" with a lat and longitude. 
example: `./iconmanage.py query 45.268012 7.768123`
