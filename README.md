# The Apothecary Diaries - Network Analysis

Social network analysis of character relationships from The Apothecary Diaries (Seasons 1-2).

## Usage

### Run with full dataset (default)
```bash
python visualize_network.py
```

### Filter by season
```bash
python visualize_network.py --filter season1
python visualize_network.py --filter season2
```

### Filter by arc
```bash
python visualize_network.py --filter "Introduction Arc"
python visualize_network.py --filter "Lakan Arc"
python visualize_network.py --filter "Perfume Arc"
python visualize_network.py --filter "Shi Clan Rebellion Arc"
```

## Available Arcs
- Introduction Arc
- Lakan Arc
- Perfume Arc
- Shi Clan Rebellion Arc

## Output Files

The script generates two visualizations:
- `network_visualization_[filter].png` - Character relationship network graph
- `degree_distribution_[filter].png` - Degree distribution histogram

## Network Metrics Computed

- **Degree Centrality** - Number of direct connections
- **Betweenness Centrality** - Influence as a bridge between characters
- **Closeness Centrality** - Proximity to all other characters
- **Network Density** - How interconnected the network is

## Installation

```bash
pip install -r requirements.txt
```

## Example Results

**Full Dataset:**
- 11 characters, 19 relationships
- Maomao: Degree Centrality = 1.0, Betweenness = 0.69
- Network Density = 0.35

**Season 1:**
- 9 characters, 14 relationships
- Maomao: Degree Centrality = 1.0, Betweenness = 0.66

**Introduction Arc:**
- 7 characters, 9 relationships
- Maomao: Degree Centrality = 1.0, Betweenness = 0.70
