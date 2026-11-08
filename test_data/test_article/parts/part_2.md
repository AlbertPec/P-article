### 2. Mathematical model

#### 2.1. Problem description

The research concerns a VLCC oil tanker. The proposed method estimates route performance under constraints on ship speed, main-engine rated power and navigational safety.

Three objective functions are considered separately:

1. shortest voyage ETA;
2. minimum voyage fuel consumption;
3. minimum CO₂ emissions.

For each pre-planned route, the model estimates how wind and waves affect speed, resistance and fuel consumption. It also calculates voyage distance, ETA, CO₂ emissions and basic costs. The purpose is to provide a quantitative basis for choosing a route that matches the voyage task and the operator's priorities.

#### 2.2. Calculation of ship navigation resistance

Total ship resistance consists mainly of calm-water resistance and additional resistance caused by wind and waves. The additional resistance is a key factor affecting speed loss, fuel consumption and CO₂ emissions.

##### 2.2.1. Ship resistance in calm water

Calm-water resistance \(R_{T,i}\) for each sailing leg consists primarily of frictional resistance \(R_{f,i}\) and residual resistance \(R_{r,i}\).

The frictional-resistance coefficient \(C_{f,i}\) is calculated using the Schoenherr formula. The roughness allowance \(\Delta C_f\) is calculated using the ITTC-1957 formula.

![Calm-water resistance equations](test-article/images/test-article.pdf-0002-09.png)

![Friction and residual resistance equations](test-article/images/test-article.pdf-0002-10.png)

The Reynolds number for sailing leg \(i\) is based on the designed waterline length \(L_{WL}\), the kinematic viscosity \(\nu\), and the hull-surface roughness \(K_S\). The roughness value used in the study is \(K_S = 150 \times 10^{-6}\), calculated using the ITTC method.

Residual resistance is calculated using a Lap-Keller graph. Polynomial fitting of the graph provides the residual-resistance coefficient \(C_r\), with an additional correction coefficient applied:

![Residual-resistance equation](test-article/images/test-article.pdf-0002-13.png)

The residual-resistance correction coefficient, length-to-beam correction and fitted parameters are determined from ship-model test data.
