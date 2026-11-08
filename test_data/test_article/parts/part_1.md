### Abstract

Taking a T300k VLCC oil tanker as the research object, this study establishes a ship-route estimation model with minimum fuel consumption, CO₂ emissions and shortest estimated time of arrival (ETA) as objective functions. The model comprehensively considers weather conditions, the main engine's rated-power limit and navigational safety.

After verifying the model, the authors combine weather-forecast data with current maritime-market conditions to evaluate several pre-planned routes. The results show that pre-planned Route 1 gives the shortest ETA, while Route 2 gives the lowest fuel consumption. Route 1 saves 36.58 hours compared with Route 2, but Route 2 reduces fuel consumption and CO₂ emissions substantially. Under the shortest-ETA objective, maintaining the initial speed can cause the main engine to exceed its rated power when the vessel encounters a headwind or bow wind of Beaufort force 4 or higher.

The proposed method evaluates fuel consumption, speed loss, CO₂ emissions and costs across alternative routes and objective functions. It can therefore support shipping companies in selecting routes that improve operational efficiency.

**Keywords:** weather conditions; constraints; ship speed loss; route estimation model.

### 1. Introduction

More than 80% of global trade is transported by sea. Shipping provides a relatively low-cost and reliable means of international transport, but it also faces increasing pressure to reduce emissions. In 2018, the International Maritime Organization (IMO) approved a target to reduce CO₂ emissions per transport unit by 40% by 2030 and 70% by 2050, compared with 2008 levels.

To improve energy efficiency, operators need reliable estimates of fuel consumption, CO₂ emissions and voyage costs for routes planned by the captain. Route selection should account for the voyage task, hydro-meteorological conditions and the vessel's structural characteristics.

Previous research on ship-route estimation has mainly addressed two areas:

- route design that accounts for ship safety and crew comfort;
- fleet routing and scheduling intended to maximize fleet profitability.

Earlier studies have examined collision avoidance, navigational risk, liner-fleet deployment, route planning using linear and mixed-integer programming, multi-criteria route selection, energy consumption and risk assessment. Other work has applied methods such as Dijkstra's algorithm to identify routes with favorable seakeeping performance.

However, many route-estimation approaches do not jointly account for severe weather, main-engine rated power, navigational safety, fuel consumption, emissions and voyage economics. Routes selected mainly through the captain's experience may therefore be neither the most economical nor the fastest.

This paper develops a route-estimation model that considers the main engine's rated-power limit and navigational safety while accounting for the vessel's seakeeping characteristics. It compares pre-planned routes between a departure port and a destination port using indicators such as speed, fuel consumption, ETA, CO₂ emissions and basic voyage cost.
