import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_weather_effect_df(df):
    weather_effect_df = df.groupby('weathersit')['cnt'].sum().reset_index()
    return weather_effect_df

def create_holiday_effect_df(df):
    holiday_effect_df = df.groupby(by="holiday", as_index=False).agg({
        "date": "max",
        "cnt": "sum",
    })
    holiday_effect_df = df.groupby('holiday')['cnt'].mean().reset_index()
    return holiday_effect_df

def create_yearly_trend_df(df):
    yearly_trend_df = df.groupby('year')['cnt'].sum().reset_index()
    yearly_trend_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    
    return yearly_trend_df

def convert_normalized_columns(df):
    df['temp'] = df['temp'] * 41  # Maksimum suhu = 41°C
    df['hum'] = df['hum'] * 100  # Maksimum kelembaban = 100%
    df['windspeed'] = df['windspeed'] * 67  # Maksimum kecepatan angin = 67
    return df

def create_monthly_rentals_df(df):
    monthly_rentals_df = df.resample(rule='M', on='date').agg({
        "registered": "sum",
        "casual": "sum",
        "cnt": "sum"
    })
    monthly_rentals_df = monthly_rentals_df.reset_index()
    monthly_rentals_df.rename(columns={
        "registered": "total_registered",
        "casual": "total_casual",
        "cnt": "total_rentals"
    }, inplace=True)
    
    return monthly_rentals_df

all_df = pd.read_csv("all_data.csv")

df = convert_normalized_columns(all_df)

datetime_columns = ["date"]
all_df.sort_values(by="date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["date"].min()
max_date = all_df["date"].max()

with st.sidebar:
    # menambahkan loga perusahanaan
    st.image("https://miro.medium.com/v2/resize:fit:1100/format:webp/1*btecI8i1yNczHsGP3z_sCg.png")

    # mengambil start_date & end-date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = all_df[(all_df["date"] >= str(start_date)) &
                 (all_df["date"] <= str(end_date))]

holiday_effect_df = create_holiday_effect_df(df)
weather_effect_df = create_weather_effect_df(df)
yearly_trend_df = create_yearly_trend_df(df)
monthly_rentals_df = create_monthly_rentals_df(df)

# **1. Visualisasi Pengaruh Hari Libur terhadap Penggunaan Sepeda**
st.title("Bike Sharing Data Visualization :sparkles:")
st.subheader("Impact of Holiday on Bike Usage")

fig, ax = plt.subplots(figsize=(16,8))
sns.barplot(x=holiday_effect_df['holiday'], y=holiday_effect_df['cnt'], palette=['blue', 'red'], ax=ax)
ax.set_xticklabels(['Not On Holiday', 'Holiday'])
ax.set_xlabel("Day Type")
ax.set_ylabel("Average Bike Usage")
ax.set_title("Impact of Holiday on Bike Usage")
holiday_count = all_df.groupby('holiday')['cnt'].mean()
for i, v in enumerate(holiday_count.values):
    plt.text(i, v + 1, f"{v:.0f}", ha='center', va='bottom', fontsize=12)
st.pyplot(fig)


# **2. Visualisasi Pengaruh Cuaca**
st.subheader("Total Bike Rentals by Weathersit")
weathersit_colors = {
    'Clear': 'lightskyblue',
    'Cloudy': 'lightgreen',
    'Light Snow/Rain': 'gold',
    'Heavy Rain/Ice Pallets': 'lightcoral'
}

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=weather_effect_df['weathersit'], y=weather_effect_df['cnt'], palette=weathersit_colors, ax=ax)
ax.set_xlabel("Weathersit")
ax.set_ylabel("Total Rentals")
ax.set_title("Total Bike Rentals by Weathersit")
ax.set_xticklabels(ax.get_xticklabels())
weathersit_count =  all_df.groupby('weathersit').cnt.sum()
sizes = weathersit_count.values
for i, value in enumerate(sizes):
    plt.text(i, value + 500, str(value), ha='center', va='bottom')
plt.tight_layout()

st.pyplot(fig)


# **3. Tren Penggunaan Sepeda dari Tahun ke Tahun**
st.subheader("Tren Penggunaan Sepeda per Tahun")

col1, col2, = st.columns(2)
with col1:
    total_orders = yearly_trend_df['total_rentals'].min()
    st.metric("Tahun 2011", value=total_orders)

with col2:
    total_revenue = yearly_trend_df['total_rentals'].max()
    st.metric("Tahun 2012", value=total_revenue)

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(x=yearly_trend_df['year'], y=yearly_trend_df['total_rentals'], marker="o", linewidth=2, color='blue', ax=ax)
ax.set_xlabel("Tahun")
ax.set_ylabel("Total Penyewaan Sepeda")
ax.set_title("Tren Penggunaan Sepeda dari Tahun ke Tahun")

st.subheader("Tren Penggunaan Sepeda per Bulan")
monthly_rentals_df = create_monthly_rentals_df(df)

selected_year = st.selectbox("Pilih Tahun", df['year'].unique())
filtered_monthly_df = monthly_rentals_df[monthly_rentals_df['date'].dt.year == int(selected_year)]

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=filtered_monthly_df['date'], y=filtered_monthly_df['total_rentals'], marker="o", linewidth=2, color='green', ax=ax)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penyewaan Sepeda")
ax.set_title(f"Tren Penggunaan Sepeda Bulanan ({selected_year})")

st.pyplot(fig)