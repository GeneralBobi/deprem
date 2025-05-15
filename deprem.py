import pandas as pd
import re
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# CSV dosyasının doğru yolu
file_path = "Earthquake_4.csv"
df = pd.read_csv(file_path)

# Sütunları temizle
df.columns = df.columns.str.strip()

# Magnitude'u float'a zorla dönüştür (bozuk verileri çıkar)
df['Magnitude'] = pd.to_numeric(df['Magnitude'], errors='coerce')
df = df.dropna(subset=['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude', 'Location'])

# Location sütunundan şehir çıkar
def extract_city(location):
    match = re.search(r"\(([^)]+)\)", str(location))
    return match.group(1) if match else None

df['City'] = df['Location'].apply(extract_city)
df = df.dropna(subset=['City'])

# Şehirlere göre deprem sayısını hesapla
def get_city_counts(dataframe):
    city_counts = dataframe['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']
    return city_counts

# Dash uygulaması
app = Dash(__name__)
app.title = "Türkiye Deprem Verileri"

# **Bunu ekle: Gunicorn vs için WSGI callable**
server = app.server

# Arayüz
app.layout = html.Div([
    html.H1("Deprem Şehir İstatistikleri", style={'textAlign': 'center'}),

    html.Label("Minimum Büyüklük Seç:", style={'marginTop': '20px'}),
    dcc.Slider(
        id='magnitude-slider',
        min=4.0,  # 4.0'dan başlatıyoruz çünkü daha küçük veri yok
        max=round(df['Magnitude'].max(), 1),
        step=0.1,
        value=4.0,  # Başlangıç değeri 4.0
        marks={i: str(i) for i in range(4, int(df['Magnitude'].max()) + 1)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    dcc.Graph(id='city-bar-chart')
], style={'width': '80%', 'margin': 'auto'})

# Callback fonksiyonu
@app.callback(
    Output('city-bar-chart', 'figure'),
    Input('magnitude-slider', 'value')
)
def update_chart(slider_value):
    filtered_df = df[df['Magnitude'] >= slider_value]
    city_counts = get_city_counts(filtered_df)

    fig = px.bar(
        city_counts.head(20),
        x='City',
        y='Count',
        title=f"{slider_value}+ Büyüklüğünde Depremler (İlk 20 Şehir)",
        labels={'Count': 'Deprem Sayısı'},
        color='Count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

# Lokal geliştirme için
if __name__ == '__main__':
    app.run_server(debug=True)
