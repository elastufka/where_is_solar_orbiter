# where_is_solar_orbiter
Dash app for displaying location of Solar Orbiter and other spacecraft

[https://where-is-solar-orbiter.herokuapp.com/](https://where-is-solar-orbiter.herokuapp.com/)

## Updating the data

_update_trajectories.py_ is a script containing the necessary steps for updating the Google Sheet containing the trajectory data. 

Updating trajectories requires local SPICE kernels, which can be downloaded via _heliopy.spice_ or from the public Bitbuckets maintained by NAIF. It is recommended to use the Bitbuckets plus a cron job that pulls the contents every week or so in order to keep these current, as there is no documentation about how frequently heliopy updates their kernels.

Running this script in a cron job means that environment variables, such as for Google credentials and SPICE kernel locations, will not be available unless loaded into crontab itself or via another script. This also means that python_setup.py won't be run beforehand, so for now the required functions have been copy-pasted into this script from the libraries where they usually live.
