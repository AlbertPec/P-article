### 4. Route-estimation results and analysis

#### 4.1. Shipping-market conditions and route information

Shipping-market conditions vary over time, particularly fuel prices and charter rates. For the case study, the authors use the following market assumptions:

- VLCC time-charter rate: 1,400 USD/day;
- CO₂ emission fee: 10 USD/t;
- HFO price: 53 USD per metric tonne;
- MDO price: 654.5 USD per metric tonne.

Fuel consumption and emissions during port entry and departure, loading and unloading are excluded.

The study compares three pre-planned routes from Tarifa port to Dos Bocas port:

- Tarifa: 36.131753° N, 5.380438° W;
- Dos Bocas: 19.829503° N, 91.92854° W.

The weather data cover August 2019 and were downloaded from the European Centre for Medium-Range Weather Forecasts (ECMWF). The dataset includes the \(u\) and \(v\) components of the wind vector and significant wave height. Weather variables at route turning points are obtained by interpolation using each point's longitude, latitude and time. True wind direction and Beaufort number are then derived from the wind-vector components. Relative wind direction is calculated from the ship's course and true wind direction, assuming the vessel follows the planned route without deviation.

![Pre-planned route information — Figure 7](test-article/images/test-article.pdf-0006-11.png)

**Figure 7.** Information on the pre-planned routes.

The route comparison reveals that Routes 1 and 3 are shorter than Route 2. However, Route 2 encounters lower Beaufort numbers and has many legs with following or crosswinds. Routes 1 and 3 encounter less favorable conditions, including Beaufort force 7 headwinds or bow-quartering winds. Such conditions increase additional resistance and involuntary speed loss. Engine-power and safety constraints can then require further speed reductions.

**Table 7.** Weather conditions on each sailing leg of the pre-planned routes.

![Table 7](images/table_007.png)

*Note: Weather-forecast data are from the European Centre for Medium-Range Weather Forecasts.*

The vessel's main characteristics are listed in Table 8.

**Table 8.** Main characteristic parameters of the VLCC.

![Table 8](images/table_008.png)

For the route-estimation calculations, the initial speed is 16 knots and the ETA limit is 340 hours. The authors use the weather information in Table 7 and the vessel parameters in Table 8 to estimate voyage distance, ETA, fuel consumption, basic costs and CO₂ emissions for all three routes under the different objective functions.
