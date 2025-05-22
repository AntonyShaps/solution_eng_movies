import plotly.graph_objects as go
import networkx as nx
import requests
from PIL import Image
from io import BytesIO
import base64

# Movie data
movies = [
    {
        "title": "Inception",
        "image": "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg",
        "genre": "sci-fi",
        "popularity": 90
    },
    {
        "title": "The Matrix",
        "image": "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg",
        "genre": "sci-fi",
        "popularity": 85
    },
    {
        "title": "Titanic",
        "image": "https://upload.wikimedia.org/wikipedia/en/2/22/Titanic_poster.jpg",
        "genre": "love",
        "popularity": 95
    },
    {
        "title": "The Lord of the Rings",
        "image": "https://upload.wikimedia.org/wikipedia/en/0/0c/The_Lord_of_the_Rings_The_Fellowship_of_the_Ring_%282001%29_theatrical_poster.jpg",
        "genre": "fantasy",
        "popularity": 92
    },
    {
        "title": "John Wick",
        "image": "https://upload.wikimedia.org/wikipedia/en/9/98/John_Wick_TeaserPoster.jpg",
        "genre": "action",
        "popularity": 80
    }
]

genre_colors = {
    "sci-fi": "blue",
    "love": "pink",
    "fantasy": "green",
    "action": "red"
}

# Create graph
G = nx.Graph()
for movie in movies:
    G.add_node(movie["title"], **movie)

edges = [
    ("Inception", "The Matrix", 8),
    ("Inception", "John Wick", 5),
    ("The Matrix", "John Wick", 7),
    ("The Lord of the Rings", "Titanic", 2),
    ("The Lord of the Rings", "John Wick", 6),
    ("The Lord of the Rings", "Inception", 1),
    ("Titanic", "Inception", 4),
]

for src, dst, weight in edges:
    G.add_edge(src, dst, weight=weight)

# Get layout positions
pos = nx.spring_layout(G, seed=42)

# Create edges
edge_x = []
edge_y = []
edge_width = []
for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_width.append(edge[2]['weight'])

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=1, color='#888'),
    hoverinfo='none',
    mode='lines'
)

# Node images
image_traces = []
for node, data in G.nodes(data=True):
    x, y = pos[node]
    try:
        response = requests.get(data["image"], timeout=5)
        response.raise_for_status()  # raise error for 403, 404, etc.
        img = Image.open(BytesIO(response.content)).resize((50, 75))

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        img_uri = f"data:image/png;base64,{img_b64}"

        image_traces.append(
            dict(
                source=img_uri,
                xref="x", yref="y",
                x=x - 0.03, y=y + 0.05,
                sizex=0.06, sizey=0.1,
                xanchor="center", yanchor="middle",
                layer="above"
            )
        )
    except Exception as e:
        print(f"Could not load image for {data['title']}: {e}")

# Node hover + invisible scatter for borders & hover
node_x = []
node_y = []
node_text = []
node_color = []
node_size = []

for node, data in G.nodes(data=True):
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(data["title"])
    node_color.append(genre_colors.get(data["genre"], "gray"))
    node_size.append(data["popularity"] / 5)

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers',
    hoverinfo='text',
    text=node_text,
    marker=dict(
        showscale=False,
        color=node_color,
        size=node_size,
        line=dict(width=4, color=node_color),
        symbol="circle"
    )
)

# Final figure
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Movie Graph',
                    titlefont_size=20,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    images=image_traces
                ))

fig.show()
