import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse
from collections import Counter, defaultdict

parser = argparse.ArgumentParser(description='Analyze triadic closure drivers in The Apothecary Diaries')
parser.add_argument('--filter', type=str, default='full', 
                    help='Filter type: "full", "season1", "season2", or arc name')
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

df = df.sort_values(['SEASON', 'EPISODE', 'ID']).reset_index(drop=True)

print(f"Total interactions: {len(df)}")

G = nx.Graph()
closure_driver_count = Counter()
activity_count = Counter()
closure_details = defaultdict(list)

print("\n" + "="*80)
print("TEMPORAL TRIADIC CLOSURE ANALYSIS")
print("="*80)

for idx, row in df.iterrows():
    u = row['ACTING CHARACTER']
    v = row['RECIEVING CHARACTER']
    
    if pd.isna(u) or pd.isna(v) or u == v:
        continue
    
    activity_count[u] += 1
    activity_count[v] += 1
    
    if not G.has_edge(u, v):
        common_neighbors = set()
        if G.has_node(u) and G.has_node(v):
            common_neighbors = set(G.neighbors(u)) & set(G.neighbors(v))
        
        for x in common_neighbors:
            closure_driver_count[x] += 1
            closure_details[x].append({
                'triangle': (u, x, v),
                'episode': row['EPISODE'],
                'season': row['SEASON'],
                'new_edge': (u, v)
            })
        
        G.add_edge(u, v, 
                  relation=row['RELATIONSHIP CATEGORY'],
                  sentiment=row['NEW SENTIMENT'],
                  strength=row['SENTIMENT STRENGTH'],
                  episode=row['EPISODE'],
                  season=row['SEASON'])
    else:
        G[u][v]['weight'] = G[u][v].get('weight', 1) + 1

normalized_driver_score = {}
for char in G.nodes():
    if activity_count[char] > 0:
        normalized_driver_score[char] = closure_driver_count[char] / activity_count[char]
    else:
        normalized_driver_score[char] = 0

print(f"\nNetwork Statistics:")
print(f"  Characters (nodes): {G.number_of_nodes()}")
print(f"  Relationships (edges): {G.number_of_edges()}")
print(f"  Total triangles in final network: {sum(nx.triangles(G).values()) // 3}")
print(f"  Clustering coefficient: {nx.average_clustering(G):.4f}")

print(f"\n{'='*80}")
print(f"TOP 10 TRIADIC CLOSURE DRIVERS (Raw Count)")
print(f"{'='*80}")
print(f"{'Character':<20} {'Closures Driven':<20} {'Total Interactions':<20}")
print(f"{'-'*80}")
for char, count in closure_driver_count.most_common(10):
    print(f"{char:<20} {count:<20} {activity_count[char]:<20}")

print(f"\n{'='*80}")
print(f"TOP 10 NORMALIZED CLOSURE DRIVERS (Closures / Interactions)")
print(f"{'='*80}")
print(f"{'Character':<20} {'Normalized Score':<20} {'Closures':<15} {'Interactions':<15}")
print(f"{'-'*80}")
for char, score in sorted(normalized_driver_score.items(), key=lambda x: x[1], reverse=True)[:10]:
    closures = closure_driver_count[char]
    interactions = activity_count[char]
    print(f"{char:<20} {score:<20.4f} {closures:<15} {interactions:<15}")

if 'Maomao' in closure_driver_count:
    print(f"\n{'='*80}")
    print(f"MAOMAO'S TRIADIC CLOSURE ANALYSIS")
    print(f"{'='*80}")
    maomao_closures = closure_driver_count['Maomao']
    maomao_interactions = activity_count['Maomao']
    maomao_score = normalized_driver_score['Maomao']
    
    print(f"  Total closures driven: {maomao_closures}")
    print(f"  Total interactions: {maomao_interactions}")
    print(f"  Normalized driver score: {maomao_score:.4f}")
    print(f"  Rank (raw count): {sorted(closure_driver_count.values(), reverse=True).index(maomao_closures) + 1}")
    print(f"  Rank (normalized): {sorted(normalized_driver_score.values(), reverse=True).index(maomao_score) + 1}")
    
    if len(closure_details['Maomao']) > 0:
        print(f"\n  Sample triangles closed by Maomao:")
        for detail in closure_details['Maomao'][:5]:
            u, x, v = detail['triangle']
            print(f"    S{detail['season']}E{detail['episode']}: Triangle ({u}, Maomao, {v}) - edge {detail['new_edge']} formed")

degree_cent = nx.degree_centrality(G)
betweenness_cent = nx.betweenness_centrality(G)
closeness_cent = nx.closeness_centrality(G)

print(f"\n{'='*80}")
print(f"CENTRALITY MEASURES")
print(f"{'='*80}")
print(f"\nTop 5 by Degree Centrality:")
for char, score in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {char:<20} {score:.4f}")

print(f"\nTop 5 by Betweenness Centrality:")
for char, score in sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {char:<20} {score:.4f}")

print(f"\nTop 5 by Closeness Centrality:")
for char, score in sorted(closeness_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {char:<20} {score:.4f}")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

top_chars = [char for char, _ in closure_driver_count.most_common(10)]
raw_counts = [closure_driver_count[char] for char in top_chars]

axes[0, 0].barh(top_chars, raw_counts, color='steelblue', edgecolor='black')
axes[0, 0].set_xlabel('Number of Closures Driven', fontsize=12)
axes[0, 0].set_title(f'Raw Triadic Closure Drivers - {filter_label}', fontsize=14, fontweight='bold')
axes[0, 0].invert_yaxis()
axes[0, 0].grid(axis='x', alpha=0.3)

top_norm_chars = [char for char, _ in sorted(normalized_driver_score.items(), key=lambda x: x[1], reverse=True)[:10]]
norm_scores = [normalized_driver_score[char] for char in top_norm_chars]

axes[0, 1].barh(top_norm_chars, norm_scores, color='coral', edgecolor='black')
axes[0, 1].set_xlabel('Normalized Score (Closures / Interactions)', fontsize=12)
axes[0, 1].set_title(f'Normalized Closure Drivers - {filter_label}', fontsize=14, fontweight='bold')
axes[0, 1].invert_yaxis()
axes[0, 1].grid(axis='x', alpha=0.3)

top_degree_chars = [char for char, _ in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]]
degree_scores = [degree_cent[char] for char in top_degree_chars]

axes[1, 0].barh(top_degree_chars, degree_scores, color='mediumseagreen', edgecolor='black')
axes[1, 0].set_xlabel('Degree Centrality', fontsize=12)
axes[1, 0].set_title(f'Degree Centrality - {filter_label}', fontsize=14, fontweight='bold')
axes[1, 0].invert_yaxis()
axes[1, 0].grid(axis='x', alpha=0.3)

top_between_chars = [char for char, _ in sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:10]]
between_scores = [betweenness_cent[char] for char in top_between_chars]

axes[1, 1].barh(top_between_chars, between_scores, color='mediumpurple', edgecolor='black')
axes[1, 1].set_xlabel('Betweenness Centrality', fontsize=12)
axes[1, 1].set_title(f'Betweenness Centrality - {filter_label}', fontsize=14, fontweight='bold')
axes[1, 1].invert_yaxis()
axes[1, 1].grid(axis='x', alpha=0.3)

plt.tight_layout()
filename_safe = filter_label.replace(' ', '_').replace('/', '_')
plt.savefig(f'triadic_closure_analysis_{filename_safe}.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved as 'triadic_closure_analysis_{filename_safe}.png'")

plt.show()

comparison_df = pd.DataFrame({
    'Character': list(G.nodes()),
    'Closures_Driven': [closure_driver_count[c] for c in G.nodes()],
    'Total_Interactions': [activity_count[c] for c in G.nodes()],
    'Normalized_Score': [normalized_driver_score[c] for c in G.nodes()],
    'Degree_Centrality': [degree_cent[c] for c in G.nodes()],
    'Betweenness_Centrality': [betweenness_cent[c] for c in G.nodes()],
    'Closeness_Centrality': [closeness_cent[c] for c in G.nodes()]
})

comparison_df = comparison_df.sort_values('Normalized_Score', ascending=False)
comparison_df.to_csv(f'character_metrics_{filename_safe}.csv', index=False)
print(f"Character metrics saved as 'character_metrics_{filename_safe}.csv'")

print(f"\n{'='*80}")
print("Analysis complete!")
print(f"{'='*80}")
