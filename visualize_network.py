import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse
from collections import Counter

parser = argparse.ArgumentParser(description='Visualize The Apothecary Diaries character network')
parser.add_argument('--filter', type=str, default='full', 
                    help='Filter type: "full", "season1", "season2", or arc name (e.g., "Introduction Arc")')
args = parser.parse_args()

df = pd.read_csv("apothecary_diaries_data.csv", skiprows=4)
df.columns = df.columns.str.strip()

print(f"Dataset loaded successfully!")
print(f"Filter: {args.filter}")

if args.filter.lower() == 'season1':
    df = df[df['SEASON'] == 1]
    filter_label = "Season 1"
elif args.filter.lower() == 'season2':
    df = df[df['SEASON'] == 2]
    filter_label = "Season 2"
elif args.filter.lower() != 'full':
    df = df[df['ARC'] == args.filter]
    filter_label = args.filter
else:
    filter_label = "Full Dataset (Seasons 1-2)"

print(f"Total interactions: {len(df)}")
print(f"\nFirst few rows:")
print(df.head())

G = nx.Graph()

for _, row in df.iterrows():
    char1 = row['ACTING CHARACTER']
    char2 = row['RECIEVING CHARACTER']
    
    if pd.notna(char1) and pd.notna(char2):
        relation_type = row['RELATIONSHIP CATEGORY']
        sentiment = row['NEW SENTIMENT']
        strength = row['SENTIMENT STRENGTH']
        
        if G.has_edge(char1, char2):
            G[char1][char2]['weight'] += 1
        else:
            G.add_edge(char1, char2, 
                      weight=1,
                      relation=relation_type,
                      sentiment=sentiment,
                      strength=strength)

print(f"\nNetwork Statistics:")
print(f"Number of characters (nodes): {G.number_of_nodes()}")
print(f"Number of relationships (edges): {G.number_of_edges()}")
print(f"Network density: {nx.density(G):.4f}")

degree_cent = nx.degree_centrality(G)
betweenness_cent = nx.betweenness_centrality(G)
closeness_cent = nx.closeness_centrality(G)

print(f"\nTop 5 Characters by Degree Centrality:")
for char, score in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {char}: {score:.4f}")

print(f"\nTop 5 Characters by Betweenness Centrality:")
for char, score in sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {char}: {score:.4f}")

plt.figure(figsize=(16, 12))

pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

node_sizes = [degree_cent[node] * 3000 for node in G.nodes()]

nx.draw_networkx_nodes(G, pos, 
                       node_size=node_sizes,
                       node_color='lightblue',
                       alpha=0.7,
                       edgecolors='black',
                       linewidths=1.5)

nx.draw_networkx_edges(G, pos, 
                       width=1.0,
                       alpha=0.3,
                       edge_color='gray')

nx.draw_networkx_labels(G, pos, 
                        font_size=10,
                        font_weight='bold',
                        font_family='sans-serif')

plt.title(f"The Apothecary Diaries - Character Relationship Network\n{filter_label} (Node size = Degree Centrality)", 
          fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()

filename_safe = filter_label.replace(' ', '_').replace('/', '_')
plt.savefig(f'network_visualization_{filename_safe}.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved as 'network_visualization_{filename_safe}.png'")

plt.show()

plt.figure(figsize=(10, 6))
degrees = [G.degree(node) for node in G.nodes()]
plt.hist(degrees, bins=20, edgecolor='black', alpha=0.7)
plt.xlabel('Degree', fontsize=12)
plt.ylabel('Number of Characters', fontsize=12)
plt.title(f'Degree Distribution - {filter_label}', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
plt.savefig(f'degree_distribution_{filename_safe}.png', dpi=300, bbox_inches='tight')
print(f"Degree distribution saved as 'degree_distribution_{filename_safe}.png'")
plt.show()
