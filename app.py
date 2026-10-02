import streamlit as st

st.set_page_config(page_title="Sigara Vergi Hesaplayıcı", layout="wide")

st.title("🚬 Sigara Vergi Hesaplayıcı")

# KDV Bilgilendirme Notu
st.caption("ℹ️ *Not: Hesaplamalarda KDV oranı mevzuat gereği varsayılan olarak **%20** kabul edilmiştir.*")
st.markdown("---")

KDV_ORANI = 0.20  # %20 KDV
DAL_SAYISI = 20   # 1 paket = 20 dal

# ==========================================
# 1 PAKET İÇİN GİRDİLER VE HESAPLAMA
# ==========================================
st.subheader("1 Paket Sigara İçin Parametreler ve Değerler")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    perakende_fiyat = st.number_input(
        "Perakende Fiyat (TL/Paket)",
        min_value=0.0,
        value=120.00,
        step=1.0,
        format="%.2f",
        help="1 paketin tavsiye edilen raf satış fiyatı"
    )

with col2:
    gv_orani_yuzde = st.number_input(
        "GV Oranı (%)",
        min_value=0.0,
        value=57.60,
        step=0.5,
        format="%.2f",
        help="Gümrük Vergisi Oranı"
    )
    gv_orani = gv_orani_yuzde / 100.0

with col3:
    nispi_otv_yuzde = st.number_input(
        "Nispi ÖTV Oranı (%)",
        min_value=0.0,
        value=42.00,
        step=0.5,
        format="%.2f",
        help="Nispi ÖTV Oranı"
    )
    nispi_otv_orani = nispi_otv_yuzde / 100.0

with col4:
    asgari_maktu_dal = st.number_input(
        "Asgari Maktu ÖTV (TL/Dal)",
        min_value=0.0,
        value=2.2953,
        step=0.01,
        format="%.4f",
        help="1 dal sigara için asgari maktu tutar"
    )

with col5:
    maktu_otv_paket = st.number_input(
        "Maktu ÖTV (TL/Paket)",
        min_value=0.0,
        value=23.7404,
        step=0.01,
        format="%.4f",
        help="1 paket için sabit maktu ÖTV tutarı"
    )

# 1 Paket Vergi Hesabı
taban_otv_1_paket = asgari_maktu_dal * DAL_SAYISI
hesaplanan_nispi_1_paket = perakende_fiyat * nispi_otv_orani

# Nispi ÖTV ile Taban ÖTV (Asgari Sınır) Karşılaştırması
otv_1_tek = max(hesaplanan_nispi_1_paket, taban_otv_1_paket)

# Maktu ÖTV doğrudan paket başına eklenir
otv_2_tek = maktu_otv_paket
toplam_otv_1_paket = otv_1_tek + otv_2_tek

# CIF Kıymeti Hesaplama
if (1 + gv_orani) > 0 and perakende_fiyat > 0:
    cif_kiymeti_1_paket = ((perakende_fiyat / (1 + KDV_ORANI)) - toplam_otv_1_paket) / (1 + gv_orani)
    if cif_kiymeti_1_paket < 0:
        cif_kiymeti_1_paket = 0.0
else:
    cif_kiymeti_1_paket = 0.0

gumruk_vergisi_1_paket = cif_kiymeti_1_paket * gv_orani
kdv_matrahi_1_paket = cif_kiymeti_1_paket + gumruk_vergisi_1_paket + toplam_otv_1_paket
kdv_1_paket = kdv_matrahi_1_paket * KDV_ORANI
toplam_vergi_1_paket = gumruk_vergisi_1_paket + toplam_otv_1_paket + kdv_1_paket

# 1 Paket Kart Gösterimi
st.info("💡 **1 Paket Sigara İçin Hesaplanan Sonuçlar**")
res_c1, res_c2, res_c3, res_c4, res_c5 = st.columns(5)
res_c1.metric("Hesaplanan CIF Kıymeti", f"{cif_kiymeti_1_paket:,.2f} TL")
res_c2.metric("Gümrük Vergisi (GV)", f"{gumruk_vergisi_1_paket:,.2f} TL")
res_c3.metric("Toplam ÖTV", f"{toplam_otv_1_paket:,.2f} TL")
res_c4.metric("KDV (%20)", f"{kdv_1_paket:,.2f} TL")
res_c5.metric("Toplam Vergi Yükü", f"{toplam_vergi_1_paket:,.2f} TL")

st.markdown("---")

# ==========================================
# TOPLAM HESAPLAMA
# ==========================================
st.subheader("Toplam")

col_paket, _ = st.columns([2, 2])
with col_paket:
    paket_adedi = st.number_input(
        "Toplam İthal Edilecek Paket Adedi",
        min_value=1,
        value=10000,
        step=500
    )

toplam_dal_sayisi = paket_adedi * DAL_SAYISI
toplam_cif = cif_kiymeti_1_paket * paket_adedi
toplam_gv = gumruk_vergisi_1_paket * paket_adedi
toplam_otv = toplam_otv_1_paket * paket_adedi
toplam_kdv = kdv_1_paket * paket_adedi
genel_toplam_vergi = toplam_gv + toplam_otv + toplam_kdv
toplam_gumruklenmis_deger = toplam_cif + genel_toplam_vergi

# GK 235/3 Kapsamında İthalat Vergilerinin 2 Katı Hesabı
gk_235_3_ceza_tutari = genel_toplam_vergi * 2

st.write(f"📦 **Toplam Sigara Sayısı:** `{toplam_dal_sayisi:,}` dal ({paket_adedi:,} paket)")

t1, t2, t3, t4 = st.columns(4)
t1.metric("Toplam CIF (Gümrük Kıymeti)", f"{toplam_cif:,.2f} TL")
t2.metric("Toplam Gümrük Vergisi", f"{toplam_gv:,.2f} TL")
t3.metric("Toplam ÖTV", f"{toplam_otv:,.2f} TL")
t4.metric("Toplam KDV", f"{toplam_kdv:,.2f} TL")

vergi_orani = (toplam_vergi_1_paket / perakende_fiyat * 100) if perakende_fiyat > 0 else 0

# Sonuç ve GK 235/3 Alanlarını Yan Yana Gösterme
sonuc_col1, sonuc_col2 = st.columns(2)

with sonuc_col1:
    st.success(f"""
### 📊 Sonuç:
* **Vergiler Toplamı:** **{genel_toplam_vergi:,.2f} TL**
* **Gümrüklenmiş Değer:** **{toplam_gumruklenmis_deger:,.2f} TL**
* **1 Paketin Vergi Yükü Oranı:** %{vergi_orani:.1f}
""")

with sonuc_col2:
    st.warning(f"""
### ⚖️ Yaptırım / Ceza Hesabı:
* **Gümrük Kanunu 235/3 uyarınca tahsili gereken vergi tutarı:**
## **{gk_235_3_ceza_tutari:,.2f} TL**
*(Gümrük vergilerinin 2 katı olarak hesaplanmıştır.)*
""")