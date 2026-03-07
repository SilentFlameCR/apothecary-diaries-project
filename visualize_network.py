import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

df = pd.read_csv("apothecary_diaries_data.csv", skiprows=4)

df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
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

plt.title("The Apothecary Diaries - Character Relationship Network\n(Node size = Degree Centrality)", 
          fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()

plt.savefig('network_visualization.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'network_visualization.png'")

plt.show()

plt.figure(figsize=(10, 6))
degrees = [G.degree(node) for node in G.nodes()]
plt.hist(degrees, bins=20, edgecolor='black', alpha=0.7)
plt.xlabel('Degree', fontsize=12)
plt.ylabel('Number of Characters', fontsize=12)
plt.title('Degree Distribution', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
plt.savefig('degree_distribution.png', dpi=300, bbox_inches='tight')
print("Degree distribution saved as 'degree_distribution.png'")
plt.show()
