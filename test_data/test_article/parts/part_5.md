## PART 5 — Voyage costs and route-estimation optimization

### 2.5. Calculation of navigation costs

A complete voyage involves many costs. This study includes only:

- charter costs;
- fuel costs;
- CO₂ emission costs.

Total voyage cost is:

\[
C_{total} = P_{cRental} \cdot T_{total}
+ P_{cFuel} \cdot F_{total}
+ P_{cEmi} \cdot E_{total}
\]

where \(P_{cRental}\) is the daily charter rate, \(P_{cFuel}\) is the fuel price and \(P_{cEmi}\) is the CO₂ emission fee.

### 2.6. Ship route-estimation model

When a vessel receives a voyage task, the captain and navigating officer plan a route using nautical charts, port information, hydro-meteorological forecasts, the voyage requirements and the ship's characteristics. This initial route is planned with safety in mind and is referred to here as a **pre-planned route**.

Different routes may encounter different wind and wave conditions. Consequently, they can produce different resistance, speed loss, ETA, fuel consumption, emissions and costs.

To reduce subjectivity in route selection, the authors formulate objective functions and constraints that account for engine rated power and navigational safety. The model can identify the route with the shortest ETA or the lowest fuel consumption and CO₂ emissions.

**Shortest-ETA objective function:**

![Shortest-ETA objective function](test-article/images/test-article.pdf-0004-40.png)

**Minimum-fuel-consumption and minimum-emissions objective functions:**

![Minimum fuel and emissions objective functions](test-article/images/test-article.pdf-0005-03.png)

**Model constraints:**

![Route-estimation constraints](test-article/images/test-article.pdf-0005-05.png)

The constraints include significant wave height \(H_{s,i}\), maximum and minimum ship speeds, main-engine power \(P_{ME,i}\), maximum rated engine power \(P_{max,ME}\), and the ETA limit required by the voyage task.

The constrained multivariable nonlinear optimization problem is solved for each pre-planned route. The resulting estimates include voyage distance, ETA, fuel consumption, costs and CO₂ emissions. The model also examines how weather affects speed, additional resistance, engine power and main-engine fuel consumption per nautical mile.
