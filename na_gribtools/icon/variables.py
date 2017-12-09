#!/usr/bin/env python3

##############################################################################

ICON_SINGLE_LEVEL = "single_level"
ICON_PRESSURE_LEVEL = "pressure_level"
ICON_LEVEL_1_85 = "model_level_1-85"
ICON_LEVEL_86_90 = "model_level_86_90"

ICON_VARIABLES = {
    # variables that we are interested in
    # see: https://www.dwd.de/DE/leistungen/opendata/help/inhalt_allgemein/opendata_content_de_en_pdf.pdf?__blob=publicationFile

    # id             name           level                        band
    "t_2m":         ("t_2m",        ICON_SINGLE_LEVEL,           1          ),
    "td_2m":        ("td_2m",        ICON_SINGLE_LEVEL,          1          ),
    "tot_prec":     ("tot_prec",    ICON_SINGLE_LEVEL,           1          ),
    "ww":           ("ww",          ICON_SINGLE_LEVEL,           1          ),
    "clct":         ("clct",        ICON_SINGLE_LEVEL,           1          ),
    "vmax_10m":     ("vmax_10m",    ICON_SINGLE_LEVEL,           1          ),
    "p_surface":    ("ps",          ICON_SINGLE_LEVEL,           1          ),
    "qv_surface":   ("qv_s",        ICON_SINGLE_LEVEL,           1          ),
}

ICON_VARIABLE_INDEXES = sorted(ICON_VARIABLES.keys())

##############################################################################

# verification code

__ICON_ALL_VARIABLES =[\
    "alb_rad", "asob_s", "aswdifd_s", "aswdifu_s", "aswdir_s", "cape_con",
    "clc", "clch", "clcl", "clcm", "clct", "clct_mod", "fi", "fr_ice",
    "h_snow", "hbas_con", "htop_con", "hzerocl", "invariant_data", "p",
    "pmsl", "ps", "qv", "qv_s", "rain_con", "rain_gsp", "relhum", "rho_snow",
    "snow_con", "snow_gsp", "t", "t_2m", "t_g", "t_snow", "t_so", "td_2m",
    "tke", "tmax_2m", "tmin_2m", "tot_prec", "u", "u_10m", "v", "v_10m",
    "vmax_10m", "w", "w_snow", "w_so", "ww", "z0"
] # just a list of all possible variables

assert set([i[1][0] for i in ICON_VARIABLES.items()]).issubset(\
    set(__ICON_ALL_VARIABLES)) 
