### 5. Conclusions

The study develops a mathematical model for estimating ship-route performance while comprehensively considering weather conditions and operational constraints. A calculation program written in C is used to estimate voyage distance, ETA, fuel consumption, basic costs and CO₂ emissions for multiple pre-planned routes.

The principal conclusions are as follows.

1. **Model verification.** Comparison with ship-model tests shows that the calm-water resistance model has an error below 2% under both full-load and ballast conditions. The predicted trends in weather-related speed loss are also consistent with previous research, supporting the applicability of the additional-resistance and speed-loss modules.

2. **Shortest-ETA route.** Under the weather forecasts used in the case study, Route 1 gives the shortest ETA. The shorter voyage time comes at the expense of higher fuel consumption, CO₂ emissions and cost because the vessel encounters headwinds, bow winds and higher waves. The paper reports that average fuel consumption and CO₂ emissions per nautical mile, as well as costs, are higher for this route than for the more economical alternatives.

3. **Minimum-fuel route.** Route 2 gives the lowest fuel consumption and CO₂ emissions, even though its voyage distance is longer than those of Routes 1 and 3. Its advantage comes from avoiding rough sea conditions and making better use of following and crosswinds. The lower additional resistance reduces fuel consumption and emissions per nautical mile. The authors conclude that the economic benefits of reduced fuel consumption and emissions outweigh the costs associated with the longer voyage.

4. **Effect of weather and constraints.** Wind and waves increase additional resistance to different degrees on each sailing leg. Engine power must be adjusted to the prevailing conditions. Under the shortest-ETA objective, maintaining an initial speed of 16 knots can cause the main engine to exceed its rated power when the vessel encounters Beaufort force 4 or higher headwind or bow wind, with significant wave height of at least 1.3 m. The engine-power constraint then requires a speed reduction of at least 0.3 knots. Under the minimum-fuel and minimum-emissions objectives, the vessel can use favorable weather conditions and reduce speed within the permitted voyage-time limit to lower fuel use and emissions.

Different objective functions therefore lead to different route choices. Weather conditions, engine-power limits and safety constraints jointly determine the trade-offs between fuel consumption, emissions and voyage time.

### Limitations and future work

The model has some limitations. The weather data account for wind speed, wind direction and significant wave height, but do not include ocean currents. The authors identify the inclusion of currents as an area for further development.
