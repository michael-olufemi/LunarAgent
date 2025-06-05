# edeniss2020 Dataset

## Overview
The edeniss2020 dataset is a time series dataset. It consists of equidistant sensor readings stemming from 97 sensors in the [EDEN ISS](https://eden-iss.net/) research greenhouse.

EDEN ISS was a (almost) closed loop research greenhouse build under the lead of the German Aerospace Center to study Controlled Environment Agriculture (CEA) techniques and plant growth for future long-term space missions. EDEN ISS was deployed in Antarctica in 2018 next to the german Neumayer III polar station and has been in operation for four years. 

The data contained in the edeniss2020 dataset was recorded during the third mission year in 2020 between 2020/01/01 and 2020/12/30. Every sensor within the dataset is related to one of the following Subsystems
|Acronym | Description |
|--|--|
| AMS&#x2011;FEG | Atmosphere Management System (AMS) of the Future Exploration Greenhouse (FEG) |
| AMS&#x2011;SES | Atmosphere Management System AMS of the Service Section (SES)|
| ICS | Illumination Control System |
| NDS | Nutrient Delivery System |
| TCS | Thermal Control System|


## Specification
|Item|Description  |
|--|--|
| Number of Files | 97 |
| Start Date | 2020/01/01 00:00:05 |
| End Date | 2020/12/30 23:55:00 |
| Sampling Rate | 1/300 Hz (5min) |

## Contents
The dataset includes the following files:
- `ams-feg/*.csv`: Sensor readings related to the AMS-FEG
- `ams-ses/*.csv`: Sensor readings related to the AMS-SES
- `ics/*.csv`: Temperature readings related to the ICS
- `nds/*.csv`: Sensor readings related to the NDS
- `tcs/*.csv`: Sensor readings related to the 
- `edeniss2020.csv`: Description and Units of the measurements.
- `README.md`: This file.

| Subsystem | Sensor | #sensors | Note |
|--|--|--|--|
| AMS-FEG | CO2 | 2 |  |
|  | Photosynthetic Active Radiation (PAR) | 2 |   |
|  | Relative Humidity (RH) | 2 |   |
|  | Temperature (T) | 3 |   |
| AMS-SES | CO2 | 2 |
|  | Photosynthetic Active Radiation (PAR) | 1 |   |
|  | Relative Humidity (RH) | 1 |   |
|  | Temperature (T) | 3 |   |
|  | Vapor Pressure Deficit (VPD) | 1 |   |
| ICS | Temperature (T) | 38 | Measured at the LED lamp above each growth tray |  |
| NDS | Electrical Conductivity (EC) | 4 | EC of the nutrient solutions |
|  | Level (H) | 2 | Level of the solution in the nutrient solution tanks |
|  | PH-Value (PH) | 4 | PH Value of the nutrient solutions | 
|  | Pressure \(P\) | 8 | Pressure in the piping from the tanks to the growth racks in the FEG |
|  | Temperature (T) | 4 | Temperature of the nutrient solutions. |
|  | Volume (V) | 2 | Volume up to the level sensor |
| TCS | Pressure \(P\) | 3 |
|  | Relative Humidity (RH) | 2 |
|  | Temperature (T) | 12 |
|  | Valve (VALVE) | 3 |



## Usage
The dataset can be used for uni- and multivariate analysis. 

To read a uni-variate time series with pandas do:

```python
import pandas as pd

# Example of loading ams-feg/co2-1.csv

data = pd.read_csv('./ams-feg/co2-1.csv')
print(data.head())

```

To read the data for a whole subsystem (e.g. AMS-FEG) as a multivariate time series:
```python
import pandas as pd
import glob

SUBSYSTEM = 'ams-feg'

combined_df = pd.DataFrame()
for i, file in enumerate(glob.glob(f'./{SUBSYSTEM}/*.csv')):
    df = pd.read_csv(file, header=0, usecols=[0, 1])
    if i == 0:
        combined_df = df
    else:
        combined_df = pd.merge(combined_df, df, on='time')

combined_df = combined_df.sort_values(by='time').reset_index(drop=True)

print(combined_df)
```

## License
Creative Commons Attribution 4.0 International (CC BY 4.0 Deed)

## Citation

If you use this dataset, please cite it as follows:
```
Rewicki, F., Norman, T., Vrakking, V., (2024). edeniss2020. Zenodo. http://doi.org/10.5281/zenodo.11485183
```

## Acknowledgements
tba

## Contact
Ferdinand Rewicki: <ferdinand.rewicki@dlr.de>

## Version History
* v1.0 Initial Version


