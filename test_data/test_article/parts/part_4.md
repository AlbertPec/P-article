### 2.3. Calculation of sailing time

Voyage time depends on both route distance and ship speed. Routes may differ not only in length but also in the wind and wave conditions encountered. These conditions can have a substantial effect on speed.

The route is therefore divided into sailing legs according to weather information, including relative wind direction and Beaufort number. Total sailing time is the sum of the times required for all legs:

![Total sailing-time equation](test-article/images/test-article.pdf-0003-19.png)

where \(N\) is the total number of sailing legs and \(Dis_i\) is the distance of sailing leg \(i\), in nautical miles.

### 2.4. Calculation of fuel consumption and emissions

#### 2.4.1. Calculation of voyage fuel consumption

Total voyage fuel consumption has two components:

- diesel-generator fuel consumption \(F_{GE}\), which depends on sailing time;
- main-engine fuel consumption \(F_{ME}\), which is the major contributor to propulsion fuel use.

The total fuel consumption is given by:

![Total voyage fuel-consumption equation](test-article/images/test-article.pdf-0004-03.png)

The diesel-generator fuel consumption is calculated as follows:

![Diesel-generator fuel-consumption equation](test-article/images/test-article.pdf-0004-05.png)

The generator's hourly fuel consumption depends on its power and specific fuel-oil consumption. For the vessel configuration used in the study, generator load is assumed to remain almost constant during the voyage. The values are:

- specific fuel-oil consumption: 190 g/kW·h;
- generator power: 800 kW.

The main-engine fuel consumption is calculated for each sailing leg:

![Main-engine fuel-consumption equation](test-article/images/test-article.pdf-0004-12.png)

![Main-engine fuel-consumption parameters](test-article/images/test-article.pdf-0004-13.png)

The main-engine hourly fuel consumption depends on the engine's specific fuel-oil consumption and delivered power. Engine load is expressed as a percentage of the rated power:

![Main-engine load equation](test-article/images/test-article.pdf-0004-15.png)

![Engine-load relation](test-article/images/test-article.pdf-0004-16.png)

Within the limits imposed by rated engine power and navigational safety, the required main-engine power for each sailing leg consists of calm-water power and additional power needed to overcome weather-related resistance.

![Calm-water and weather-related engine power](test-article/images/test-article.pdf-0004-19.png)

![Engine power calculation](test-article/images/test-article.pdf-0004-20.png)

![Propulsion-efficiency relations](test-article/images/test-article.pdf-0004-21.png)

The propulsion efficiency is a function of main-engine power and ship-model test data. Shaft efficiency is generally taken as 0.99.

Additional resistance power and total main-engine power are calculated using:

![Additional resistance power equation](test-article/images/test-article.pdf-0004-24.png)

![Total main-engine power equation](test-article/images/test-article.pdf-0004-25.png)

The empirical coefficient \(n\) depends on ship type and loading condition.

**Table 5.** Values of \(n\) in the Kwon method.

![Table 5](images/table_005.png)

#### 2.4.2. Calculation of voyage emissions

Ship emissions are closely related to fuel consumption. A shorter route does not necessarily produce lower emissions because wind and waves may increase resistance and fuel use.

Total CO₂ emissions consist of emissions from the main engine and diesel generators:

![CO2 emissions equations](test-article/images/test-article.pdf-0004-30.png)

![Main-engine and generator emissions](test-article/images/test-article.pdf-0004-31.png)

![Emission-factor relations](test-article/images/test-article.pdf-0004-32.png)

The emission factors for the main engine and diesel generator are applied to the corresponding fuel consumption. The fuel-specific factors are taken from ISO 8217 (2010).

**Table 6.** CO₂ emission factors for marine fuels (ISO 8217).

![Table 6](images/table_006.png)
