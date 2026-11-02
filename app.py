import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Dashboard UTS Pemodelan Statistik", layout="wide")

# 2. CSS KHUSUS PRINT PDF (Mencegah Grafik Terpotong & Menyembunyikan Menu Web)
st.markdown("""
    <style>
    @media print {
        /* Sembunyikan Header, Footer, dan Sidebar bawaan Streamlit */
        header, footer, [data-testid="stSidebar"], [data-testid="stHeader"] {
            display: none !important;
        }
        /* Mencegah pemotongan elemen di tengah halaman */
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        .element-container, img, figure {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        body {
            background-color: white !important;
            color: black !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Identitas Pengembang
WATERMARK_TEXT = "Pengembang : Heri Santoso MTI 08 NIM 26.01.85.7007"

st.title("📊 Dashboard Analisis & Eksplorasi Data Penjualan")
st.caption(f"**{WATERMARK_TEXT}**")
st.markdown("---")

sns.set_theme(style="whitegrid")

try:
    # Membaca dataset
    df = pd.read_csv('DATA PENJUALAN.csv')
    
    # PREPARASI DATA
    df_clean = df.copy()
    df_clean['Order_Date'] = pd.to_datetime(df_clean['Order_Date'])
    df_clean['Customer_Age'] = df_clean['Customer_Age'].fillna(df_clean['Customer_Age'].median())
    df_clean['Delivery_Days'] = df_clean['Delivery_Days'].fillna(df_clean['Delivery_Days'].median())
    df_clean['Inventory_Level'] = df_clean['Inventory_Level'].fillna(df_clean['Inventory_Level'].median())
    df_clean['Customer_Rating'] = df_clean['Customer_Rating'].fillna(df_clean['Customer_Rating'].mean())
    df_clean['Customer_Name'] = df_clean['Customer_Name'].fillna('Unknown')
    df_clean['Customer_Gender'] = df_clean['Customer_Gender'].fillna(df_clean['Customer_Gender'].mode()[0])
    df_clean['Product_Name'] = df_clean['Product_Name'].fillna('Unknown Product')
    df_clean['Payment_Method'] = df_clean['Payment_Method'].fillna(df_clean['Payment_Method'].mode()[0])
    df_clean['Promotion_Code'] = df_clean['Promotion_Code'].fillna('NO_PROMO')
    df_clean['Return_Reason'] = df_clean['Return_Reason'].fillna('No Return')
    df_clean = df_clean.drop_duplicates()
    
    st.success("✅ Data Penjualan Berhasil Diproses & Dibersihkan!")

    # KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    total_sales = df_clean['Sales_Amount'].sum()
    total_profit = df_clean['Profit'].sum()
    margin = (total_profit / total_sales) * 100
    total_trans = len(df_clean)
    
    col1.metric("Total Transaksi", f"{total_trans:,}")
    col2.metric("Total Omzet (Sales)", f"${total_sales:,.2f}")
    col3.metric("Total Profit", f"${total_profit:,.2f}")
    col4.metric("Profit Margin", f"{margin:.2f}%")
    
    st.markdown("---")
    
    # 1. Kelompok Transaksi
    st.subheader("1. Kelompok Transaksi: Tren Jumlah Transaksi Penjualan Per Bulan")
    df_clean['YearMonth'] = df_clean['Order_Date'].dt.to_period('M').astype(str)
    monthly_trend = df_clean.groupby('YearMonth')['Transaction_ID'].count().reset_index()
    
    fig1, ax1 = plt.subplots(figsize=(10, 3.5))
    ax1.plot(monthly_trend['YearMonth'], monthly_trend['Transaction_ID'], marker='o', color='b', linewidth=2)
    ax1.set_ylabel("Jumlah Transaksi")
    ax1.set_xlabel("Bulan (Tahun-Bulan)")
    plt.xticks(rotation=45)
    fig1.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig1)

    st.markdown("---")

    # 2. Kelompok Pelanggan
    st.subheader("2. Kelompok Pelanggan: Demografi & Segmen Pelanggan")
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 3.5))
    sns.histplot(df_clean['Customer_Age'], kde=True, ax=axes2[0], color='teal', bins=20)
    axes2[0].set_title('Distribusi Usia Pelanggan')
    sns.countplot(data=df_clean, x='Customer_Gender', ax=axes2[1], palette='Set2')
    axes2[1].set_title('Distribusi Gender Pelanggan')
    sns.countplot(data=df_clean, x='Customer_Segment', ax=axes2[2], palette='Set1')
    axes2[2].set_title('Distribusi Segmen Pelanggan')
    fig2.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig2)

    st.markdown("---")

    # 3. Kelompok Produk
    st.subheader("3. Kelompok Produk: Total Kuantitas Penjualan per Kategori Produk")
    top_categories = df_clean.groupby('Product_Category')['Quantity'].sum().reset_index().sort_values(by='Quantity', ascending=False)
    
    fig3, ax3 = plt.subplots(figsize=(10, 3.5))
    sns.barplot(data=top_categories, x='Quantity', y='Product_Category', palette='viridis', ax=ax3)
    ax3.set_xlabel("Total Kuantitas Terjual")
    ax3.set_ylabel("Kategori Produk")
    fig3.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig3)

    st.markdown("---")

    # 4. Kelompok Penjualan & Keuntungan
    st.subheader("4. Kelompok Penjualan & Profitabilitas: Omzet vs Profit per Kategori")
    profit_by_cat = df_clean.groupby('Product_Category')[['Sales_Amount', 'Profit']].sum().reset_index()
    
    fig4, ax4 = plt.subplots(figsize=(10, 3.5))
    profit_by_cat.plot(x='Product_Category', y=['Sales_Amount', 'Profit'], kind='bar', ax=ax4)
    ax4.set_ylabel("Jumlah ($)")
    ax4.set_xlabel("Kategori Produk")
    plt.xticks(rotation=0)
    fig4.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig4)

    st.markdown("---")

    # 5. Kelompok Distribusi & Pembayaran
    st.subheader("5. Kelompok Distribusi & Pembayaran: Kanal Penjualan dan Pengiriman")
    fig5, axes5 = plt.subplots(1, 2, figsize=(14, 3.5))
    sns.countplot(data=df_clean, x='Sales_Channel', ax=axes5[0], palette='Blues_r')
    axes5[0].set_title('Distribusi per Sales Channel')
    sns.countplot(data=df_clean, x='Shipping_Method', ax=axes5[1], palette='Greens_r')
    axes5[1].set_title('Distribusi Metode Pengiriman')
    fig5.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig5)

    st.markdown("---")

    # 6. Kelompok Status & Evaluasi
    st.subheader("6. Kelompok Status & Evaluasi: Alasan Retur dan Rating Pelanggan")
    fig6, axes6 = plt.subplots(1, 2, figsize=(14, 3.5))
    return_data = df_clean[df_clean['Return_Flag'] == 'Yes']
    sns.countplot(data=return_data, y='Return_Reason', ax=axes6[0], order=return_data['Return_Reason'].value_counts().index, palette='Reds_r')
    axes6[0].set_title('Alasan Utama Pengembalian Produk (Retur)')
    sns.histplot(df_clean['Customer_Rating'], kde=True, ax=axes6[1], color='orange', bins=10)
    axes6[1].set_title('Distribusi Customer Rating')
    fig6.text(0.99, 0.01, WATERMARK_TEXT, fontsize=8, color='gray', ha='right', va='bottom', fontstyle='italic')
    st.pyplot(fig6)

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat atau memproses data: {e}")
