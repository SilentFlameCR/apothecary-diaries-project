import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse
from collections import Counter

parser = argparse.ArgumentParser(description='Analyze structural balance in The Apothecary Diaries')
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

G_signed = nx.Graph()
edge_sentiments = {}
edge_counts = Counter()

for idx, row in df.iterrows():
    u = row['ACTING CHARACTER']
    v = row['RECIEVING CHARACTER']
    sentiment = row['NEW SENTIMENT']
    
    if pd.isna(u) or pd.isna(v) or u == v:
        continue
    
    edge = tuple(sorted([u, v]))
    edge_counts[edge] += 1
    
    sign = 0
    if pd.notna(sentiment):
        if str(sentiment).strip().lower() == 'positive':
            sign = 1
        elif str(sentiment).strip().lower() == 'negative':
            sign = -1
    
    if edge not in edge_sentiments:
        edge_sentiments[edge] = []
    edge_sentiments[edge].append(sign)

for edge, signs in edge_sentiments.items():
    positive_count = sum(1 for s in signs if s == 1)
    negative_count = sum(1 for s in signs if s == -1)
    
    if positive_count > negative_count:
        dominant_sign = 1
    elif negative_count > positive_count:
        dominant_sign = -1
    else:
        dominant_sign = 1 if positive_count > 0 else 0
    
    avg_sign = sum(signs) / len(signs) if signs else 0
    
    G_signed.add_edge(edge[0], edge[1], 
                     sign=dominant_sign,
                     avg_sentiment=avg_sign,
                     interaction_count=edge_counts[edge],
                     positive_count=positive_count,
                     negative_count=negative_count)

print(f"\n{'='*80}")
print(f"SIGNED NETWORK STATISTICS")
print(f"{'='*80}")
print(f"  Total nodes: {G_signed.number_of_nodes()}")
print(f"  Total edges: {G_signed.number_of_edges()}")

positive_edges = [(u, v) for u, v, d in G_signed.edges(data=True) if d['sign'] == 1]
negative_edges = [(u, v) for u, v, d in G_signed.edges(data=True) if d['sign'] == -1]
neutral_edges = [(u, v) for u, v, d in G_signed.edges(data=True) if d['sign'] == 0]

print(f"  Positive edges: {len(positive_edges)} ({len(positive_edges)/G_signed.number_of_edges()*100:.1f}%)")
print(f"  Negative edges: {len(negative_edges)} ({len(negative_edges)/G_signed.number_of_edges()*100:.1f}%)")
print(f"  Neutral edges: {len(neutral_edges)} ({len(neutral_edges)/G_signed.number_of_edges()*100:.1f}%)")

triangles = [clique for clique in nx.enumerate_all_cliques(G_signed) if len(clique) == 3]

balanced_triangles = 0
unbalanced_triangles = 0
triangle_details = []

for triangle in triangles:
    a, b, c = triangle
    
    sign_ab = G_signed[a][b]['sign']
    sign_bc = G_signed[b][c]['sign']
    sign_ac = G_signed[a][c]['sign']
    
    product = sign_ab * sign_bc * sign_ac
    
    is_balanced = (product > 0) or (product == 0)
    
    if is_balanced:
        balanced_triangles += 1
    else:
        unbalanced_triangles += 1
    
    triangle_details.append({
        'nodes': triangle,
        'signs': (sign_ab, sign_bc, sign_ac),
        'product': product,
        'balanced': is_balanced
    })

print(f"\n{'='*80}")
print(f"STRUCTURAL BALANCE ANALYSIS")
print(f"{'='*80}")
print(f"  Total triangles: {len(triangles)}")
print(f"  Balanced triangles: {balanced_triangles} ({balanced_triangles/len(triangles)*100:.1f}%)")
print(f"  Unbalanced triangles: {unbalanced_triangles} ({unbalanced_triangles/len(triangles)*100:.1f}%)")

if len(triangles) > 0:
    balance_ratio = balanced_triangles / len(triangles)
    print(f"  Balance ratio: {balance_ratio:.4f}")
    
    if balance_ratio > 0.8:
        print(f"  Network status: HIGHLY BALANCED")
    elif balance_ratio > 0.5:
        print(f"  Network status: MODERATELY BALANCED")
    else:
        print(f"  Network status: UNBALANCED")

print(f"\n{'='*80}")
print(f"TRIANGLE BREAKDOWN")
print(f"{'='*80}")

triangle_types = Counter()
for detail in triangle_details:
    signs = detail['signs']
    pos_count = sum(1 for s in signs if s == 1)
    neg_count = sum(1 for s in signs if s == -1)
    
    if pos_count == 3:
        triangle_types['All Positive (+++)'] += 1
    elif pos_count == 2 and neg_count == 1:
        triangle_types['Two Positive, One Negative (++-)'] += 1
    elif pos_count == 1 and neg_count == 2:
        triangle_types['One Positive, Two Negative (+--)'] += 1
    elif neg_count == 3:
        triangle_types['All Negative (---)'] += 1
    else:
        triangle_types['Contains Neutral'] += 1

for ttype, count in triangle_types.most_common():
    balanced_marker = "✓ BALANCED" if ttype in ['All Positive (+++)', 'One Positive, Two Negative (+--)'] else "✗ UNBALANCED"
    print(f"  {ttype:<40} {count:>3} {balanced_marker}")

if unbalanced_triangles > 0:
    print(f"\n{'='*80}")
    print(f"SAMPLE UNBALANCED TRIANGLES")
    print(f"{'='*80}")
    unbalanced = [d for d in triangle_details if not d['balanced']][:5]
    for detail in unbalanced:
        nodes = detail['nodes']
        signs = detail['signs']
        print(f"  {nodes[0]} -- {nodes[1]} -- {nodes[2]}")
        print(f"    Signs: {signs[0]:+d}, {signs[1]:+d}, {signs[2]:+d} (Product: {detail['product']})")

char_sentiment_profile = {}
for node in G_signed.nodes():
    pos_edges = 0
    neg_edges = 0
    neutral_edges = 0
    
    for neighbor in G_signed.neighbors(node):
        sign = G_signed[node][neighbor]['sign']
        if sign == 1:
            pos_edges += 1
        elif sign == -1:
            neg_edges += 1
        else:
            neutral_edges += 1
    
    total = pos_edges + neg_edges + neutral_edges
    char_sentiment_profile[node] = {
        'positive': pos_edges,
        'negative': neg_edges,
        'neutral': neutral_edges,
        'pos_ratio': pos_edges / total if total > 0 else 0,
        'neg_ratio': neg_edges / total if total > 0 else 0
    }

print(f"\n{'='*80}")
print(f"CHARACTER SENTIMENT PROFILES")
print(f"{'='*80}")
print(f"{'Character':<20} {'Positive':<12} {'Negative':<12} {'Neutral':<12} {'Pos %':<10}")
print(f"{'-'*80}")
for char in sorted(char_sentiment_profile.keys(), key=lambda x: char_sentiment_profile[x]['pos_ratio'], reverse=True):
    profile = char_sentiment_profile[char]
    print(f"{char:<20} {profile['positive']:<12} {profile['negative']:<12} {profile['neutral']:<12} {profile['pos_ratio']*100:>6.1f}%")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

sentiment_counts = [len(positive_edges) if isinstance(positive_edges, list) else positive_edges, 
                    len(negative_edges) if isinstance(negative_edges, list) else negative_edges]
sentiment_labels = ['Positive', 'Negative']
colors = ['#2ecc71', '#e74c3c']

axes[0, 0].pie(sentiment_counts, labels=sentiment_labels, autopct='%1.1f%%', 
               colors=colors, startangle=90, textprops={'fontsize': 12})
axes[0, 0].set_title(f'Edge Sentiment Distribution - {filter_label}', fontsize=14, fontweight='bold')

balance_counts = [balanced_triangles, unbalanced_triangles]
balance_labels = ['Balanced', 'Unbalanced']
balance_colors = ['#3498db', '#e67e22']

if len(triangles) > 0:
    axes[0, 1].pie(balance_counts, labels=balance_labels, autopct='%1.1f%%',
                   colors=balance_colors, startangle=90, textprops={'fontsize': 12})
    axes[0, 1].set_title(f'Triangle Balance - {filter_label}', fontsize=14, fontweight='bold')
else:
    axes[0, 1].text(0.5, 0.5, 'No triangles found', ha='center', va='center', fontsize=14)
    axes[0, 1].set_title(f'Triangle Balance - {filter_label}', fontsize=14, fontweight='bold')

if len(triangle_types) > 0:
    types = list(triangle_types.keys())
    counts = list(triangle_types.values())
    axes[1, 0].barh(types, counts, color='steelblue', edgecolor='black')
    axes[1, 0].set_xlabel('Count', fontsize=12)
    axes[1, 0].set_title(f'Triangle Type Distribution - {filter_label}', fontsize=14, fontweight='bold')
    axes[1, 0].invert_yaxis()
    axes[1, 0].grid(axis='x', alpha=0.3)

top_chars = sorted(char_sentiment_profile.keys(), key=lambda x: G_signed.degree(x), reverse=True)[:10]
pos_counts = [char_sentiment_profile[c]['positive'] for c in top_chars]
neg_counts = [char_sentiment_profile[c]['negative'] for c in top_chars]

x = range(len(top_chars))
width = 0.35

axes[1, 1].bar([i - width/2 for i in x], pos_counts, width, label='Positive', color='#2ecc71', edgecolor='black')
axes[1, 1].bar([i + width/2 for i in x], neg_counts, width, label='Negative', color='#e74c3c', edgecolor='black')
axes[1, 1].set_xlabel('Character', fontsize=12)
axes[1, 1].set_ylabel('Number of Edges', fontsize=12)
axes[1, 1].set_title(f'Character Sentiment Profile - {filter_label}', fontsize=14, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(top_chars, rotation=45, ha='right')
axes[1, 1].legend()
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
filename_safe = filter_label.replace(' ', '_').replace('/', '_')
plt.savefig(f'structural_balance_analysis_{filename_safe}.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved as 'structural_balance_analysis_{filename_safe}.png'")

plt.show()

balance_df = pd.DataFrame(triangle_details)
balance_df.to_csv(f'triangle_balance_{filename_safe}.csv', index=False)
print(f"Triangle balance data saved as 'triangle_balance_{filename_safe}.csv'")

print(f"\n{'='*80}")
print("Structural balance analysis complete!")
print(f"{'='*80}")
