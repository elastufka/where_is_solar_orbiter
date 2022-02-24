&nbsp;

## Units

All coordinates are given in Heliocentric Earth Ecliptic (HEE) coordinates. For clarity, they are displayed in AU although the data can also be downloaded in .csv format with units in km.

### Data update frequency

New coordinates are added once a day. 


This tool is based off of [the STEREO orbit tool](https://stereo-ssc.nascom.nasa.gov/where.shtml) and others like it.

# Solar Flares

This dataset is based on solar flares observed by Solar Orbiter's STIX; therefore flares seen by AIA or STEREO-A but not also by Solar Orbiter are not included. Solar flare coordinates are obtained from AIA and then reprojected into the Solar Orbiter and STEREO-A reference frames.

## Data Sources

STIX solar flares - [STIX Data Center](https://pub023.cs.technik.fhnw.ch/)
AIA solar flares - [HEK](https://www.lmsal.com/hek/)

## Calculations

The conversion of STIX peak counts to a [GOES-class proxy](https://pub023.cs.technik.fhnw.ch/wiki/index.php?title=GOES_Flux_vs_STIX_counts) is based on the empirically measured log-log relationship, which is updated to include data from new events on a bi-weekly basis. As of February 2022, the coefficients defined by the regression are stable to two significant digits, with a R-value of 0.84.

## About the plots

Solar coordinates are given in Helioprojective frames with units of arcseconds for AIA and STEREO-A, because the apparent solar radius from these perspectives is relatively (>10") constant, and in degrees for Solar Orbiter, as the size of the solar disk as seen from its elliptical orbit can vary by hundreds of arcseconds. Values for flare positions as seen by Solar Orbiter in the hovertext and the table are given in arcseconds, along with the relevant measurement of apparent solar radius for context.

### Data update frequency

New solar flares are added twice a week, following updates to the [STIX Data Center.](https://pub023.cs.technik.fhnw.ch/)

