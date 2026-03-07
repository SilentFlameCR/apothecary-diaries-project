# The Apothecary Diaries - Network Analysis

Social network analysis of character relationships from The Apothecary Diaries (Seasons 1-2).

This project analyzes **degree centrality**, **betweenness centrality**, **triadic closure**, and **structural balance** to answer the research question:

> **"How much influence does Maomao exert over the empire's political network?"**

## Installation

```bash
pip install -r requirements.txt
```

## Analysis Scripts

### 1. Basic Network Visualization (`visualize_network.py`)

Creates network graphs and computes basic centrality metrics.

**Usage:**
```bash
# Full dataset (default)
python visualize_network.py

# Filter by season
python visualize_network.py --filter season1
python visualize_network.py --filter season2

# Filter by arc
python visualize_network.py --filter "Introduction Arc"
python visualize_network.py --filter "Lakan Arc"
python visualize_network.py --filter "Perfume Arc"
python visualize_network.py --filter "Shi Clan Rebellion Arc"
```

**Output:**
- `network_visualization_[filter].png` - Network graph (node size = degree centrality)
- `degree_distribution_[filter].png` - Degree distribution histogram

**Metrics Computed:**
- Degree Centrality
- Betweenness Centrality
- Closeness Centrality
- Network Density

### 2. Triadic Closure Analysis (`analyze_triadic_closure.py`)

**Measures which characters drive triadic closure over time.**

This script processes interactions temporally to identify when a character acts as a bridge that later causes two of their neighbors to connect, forming a triangle.

**Definition:**
```
DriverScore(x) = closures driven by x / total interactions involving x
```

A character drives closure when:
1. Character X is connected to both A and B
2. A and B are not yet connected
3. Later, an edge between A and B appears
4. X gets credit for driving that triangle closure

**Usage:**
```bash
python analyze_triadic_closure.py --filter full
python analyze_triadic_closure.py --filter season1
python analyze_triadic_closure.py --filter "Introduction Arc"
```

**Output:**
- `triadic_closure_analysis_[filter].png` - 4-panel visualization:
  - Raw closure driver counts
  - Normalized closure driver scores
  - Degree centrality comparison
  - Betweenness centrality comparison
- `character_metrics_[filter].csv` - Complete metrics table

**Key Results (Full Dataset):**
- **Maomao:** 7 closures driven (rank #1 raw), 0.0393 normalized score (rank #2)
- **Gyokuyou:** 4 closures driven, 0.1290 normalized score (rank #1 - most efficient)
- Maomao closed triangles connecting: Gyokuyou-Jinshi, Emperor-Jinshi, Lakan-Jinshi, Jinshi-Lihaku, Shisui-Xiaolan

### 3. Structural Balance Analysis (`analyze_structural_balance.py`)

**Analyzes signed edges (positive/negative sentiment) and triangle balance.**

Uses structural balance theory:
- **Balanced triangles:** All positive (+++) or one positive with two negative (+--)
- **Unbalanced triangles:** Two positive with one negative (++-)

**Usage:**
```bash
python analyze_structural_balance.py --filter full
python analyze_structural_balance.py --filter season1
```

**Output:**
- `structural_balance_analysis_[filter].png` - 4-panel visualization:
  - Edge sentiment distribution (pie chart)
  - Triangle balance ratio (pie chart)
  - Triangle type breakdown (bar chart)
  - Character sentiment profiles (grouped bar chart)
- `triangle_balance_[filter].csv` - Detailed triangle data

**Key Results (Full Dataset):**
- **78.9% positive edges**, 15.8% negative, 5.3% neutral
- **72.7% balanced triangles** (moderately balanced network)
- **Unbalanced triangles:** Maomao-Gyokuyou-Lihua, Maomao-Jinshi-Lakan, Gyokuyou-Lihua-Emperor
- **Maomao's profile:** 90% positive edges (9 positive, 1 negative)

## Available Filters

### Seasons
- `season1` - Season 1 only
- `season2` - Season 2 only
- `full` - Both seasons (default)

### Arcs
- `"Introduction Arc"`
- `"Lakan Arc"`
- `"Perfume Arc"`
- `"Shi Clan Rebellion Arc"`

## Research Findings Summary

### Maomao's Influence Metrics

| Metric | Value | Rank | Interpretation |
|--------|-------|------|----------------|
| **Degree Centrality** | 1.0000 | #1 | Connected to every character |
| **Betweenness Centrality** | 0.6852 | #1 | Critical bridge in network |
| **Closeness Centrality** | 1.0000 | #1 | Closest to all characters |
| **Closures Driven (Raw)** | 7 | #1 | Most triangle formations |
| **Closures Driven (Normalized)** | 0.0393 | #2 | High efficiency per interaction |
| **Positive Edge Ratio** | 90% | - | Mostly positive relationships |

### Answer to Research Question

**Maomao exerts DOMINANT influence over the empire's political network:**

1. **Perfect degree centrality (1.0)** - She's the only character connected to everyone
2. **Highest betweenness (0.69)** - She's the essential bridge between all factions
3. **Top closure driver (7 triangles)** - She actively connects disparate characters
4. **Highly positive relationships (90%)** - Her influence is constructive, not antagonistic

This quantitatively demonstrates that Maomao is the **central hub** of the political network, serving as the primary connector between the Emperor, consorts, military officers, and other key figures.

## File Structure

```
project/
├── apothecary_diaries_data.csv          # Raw interaction data
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
├── visualize_network.py                  # Basic network visualization
├── analyze_triadic_closure.py            # Temporal closure analysis
├── analyze_structural_balance.py         # Signed network analysis
└── [output files generated by scripts]
```

## Citation

For academic use, please cite the data source and methodology based on COMP4601/4602 social network analysis standards.
