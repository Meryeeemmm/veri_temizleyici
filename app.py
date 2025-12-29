import json
import sys
import ctypes
from rapidfuzz import fuzz

# --- AYARLAR ---
JSON_DOSYA = "DOSYA_ADI_GİR.json"
BENZERLIK_ESIGI = 85
PROGRESS_LOG_EVERY = 50  # her 50 veri karşılaştırmada ilerleme logu

# --- BLOK AYARLARI ---
BLOK_BOYUTU = 50
KAYMA_MIKTARI = 10  # kaç geriden başlasın

# ---------------- Windows Uyku Modu Engelle ---------------- #
if sys.platform == "win32": 
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

# --- Fonksiyonlar ---
def normalize(text):
    if not text:
        return ""
    return text.strip().lower()

def metin_birlestir(veri):
    return (
        normalize(veri.get("base_question", "")) + " " +
        normalize(veri.get("alt_question1", "")) + " " +
        normalize(veri.get("alt_question2", "")) + " " +
        normalize(veri.get("full_answer", "")) + " " +
        normalize(veri.get("short_answer", ""))
    )

def load_data():
    try:
        with open(JSON_DOSYA, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[2]["data"]  # tablo yapısı buradan geliyor
    except Exception as e:
        print(f"Veri yüklenirken hata oluştu: {e}")
        return []

# --- Ana Program ---
def main():
    print("Kodlar çalışıyor... Lütfen bekleyin, işlem sürebilir.")

    veriler = load_data()
    if not veriler:
        print("Hiç veri bulunamadı. İşlem durduruldu.")
        return

    birlesik = []
    id_to_item = {}

    for item in veriler:
        vid = item["veri_id"]
        text = metin_birlestir(item)
        birlesik.append((vid, text))
        id_to_item[vid] = item

    tam_ciftler = []
    benzer_ciftler = []
    silinecek_idler = set()
    silme_sebebi_map = {}  # id2 -> id1 haritası

    # --- YENİ BLOKLU + 10 GERİDEN KAYMALI KARŞILAŞTIRMA ---
    toplam = len(birlesik)
    baslangic = 0

    while baslangic < toplam:
        bitis = min(baslangic + BLOK_BOYUTU, toplam)
        print(f"\n{baslangic} - {bitis} arası kontrol ediliyor...")

        for i in range(baslangic, bitis):
            id1, text1 = birlesik[i]

            if i % PROGRESS_LOG_EVERY == 0:
                print(f"{i}/{toplam} veri karşılaştırıldı...")

            for j in range(i + 1, bitis):
                id2, text2 = birlesik[j]

                if text1 == text2:
                    tam_ciftler.append({
                        "id1": id1,
                        "text1": text1,
                        "id2": id2,
                        "text2": text2
                    })
                    silinecek_idler.add(id2)
                    silme_sebebi_map[id2] = id1
                else:
                    skor = fuzz.token_set_ratio(text1, text2)
                    if skor >= BENZERLIK_ESIGI:
                        benzer_ciftler.append({
                            "id1": id1,
                            "text1": text1,
                            "id2": id2,
                            "text2": text2,
                            "score": skor
                        })

        # 50 ileri git ama 10 geriden başla
        baslangic += (BLOK_BOYUTU - KAYMA_MIKTARI)

    # --- CLEAN ve REMOVED VERİLER ---
    clean_list = []
    removed_list = []

    for vid, item in id_to_item.items():
        if vid in silinecek_idler:
            removed_item = item.copy()
            removed_item["_silme_sebebi_id"] = silme_sebebi_map.get(vid)
            removed_list.append(removed_item)
        else:
            clean_list.append(item)

    # --- DOSYALARI YAZ ---
    with open("duplicate_pairs.json", "w", encoding="utf-8") as f:
        json.dump(tam_ciftler, f, ensure_ascii=False, indent=4)

    with open("similar_pairs.json", "w", encoding="utf-8") as f:
        json.dump(benzer_ciftler, f, ensure_ascii=False, indent=4)

    with open("clean_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_list, f, ensure_ascii=False, indent=4)

    with open("removed_items.json", "w", encoding="utf-8") as f:
        json.dump(removed_list, f, ensure_ascii=False, indent=4)

    print("\nİŞLEM TAMAMLANDI!")
    print(f"{len(tam_ciftler)} adet TAM aynı veri bulundu → duplicate_pairs.json dosyasına kaydedildi.")
    print(f"{len(benzer_ciftler)} adet BENZER veri bulundu → similar_pairs.json dosyasına kaydedildi.")
    print(f"{len(removed_list)} adet veri temizlerken silindi → removed_items.json dosyasına kaydedildi.")
    print(f"{len(clean_list)} adet temiz veri oluşturuldu → clean_data.json dosyasına kaydedildi.")

    print("\nOluşan dosyalar:")
    print(" → duplicate_pairs.json")
    print(" → similar_pairs.json")
    print(" → clean_data.json")
    print(" → removed_items.json  (SİLİNEN VERİLER, silme sebebi ekli)")

    # --- ÇIKIŞ / GELİŞMİŞ SORGULAMA SİSTEMİ ---
    while True:
        komut = input(
            "\nENTER: Çıkış | id45 / veriid45: ID ara | duplicate | similar | removed | clean : "
        ).strip().lower()

        # ---- ÇIKIŞ ----
        if komut == "":
            break

        # ---- ID SORGULAMA (TÜM LİSTELERDE) ----
        if komut.startswith("id") or komut.startswith("veriid"):
            if komut.startswith("id"):
                sorgu_id = komut[2:].strip()
            else:
                sorgu_id = komut[6:].strip()

            if not sorgu_id.isdigit():
                print("⚠️ Geçersiz ID komutu. Lütfen sayısal bir ID girin (örn: id12 veya veriid12).")
                continue

            bulundu = False
            for kaynak_adi, liste in [
                ("TEMİZ VERİ", clean_list),
                ("SİLİNEN VERİ", removed_list),
            ]:
                for item in liste:
                    if str(item.get("veri_id")) == sorgu_id:
                        print(f"\n📌 BULUNAN KAYIT ({kaynak_adi}):")
                        print(json.dumps(item, ensure_ascii=False, indent=4))
                        bulundu = True
                        break
            if not bulundu:
                print("❌ Bu ID bulunamadı.")

        # ---- TAM AYNI VERİLER ----
        elif komut == "duplicate":
            if not tam_ciftler:
                print("⚠️ Hiç tam aynı veri yok.")
            else:
                print("\n📄 TAM AYNI VERİLER:\n")
                for cift in tam_ciftler:
                    print(f"{cift['id1']} ve {cift['id2']} aynı")

        # ---- BENZER VERİLER ----
        elif komut == "similar":
            if not benzer_ciftler:
                print("⚠️ Hiç benzer veri yok.")
            else:
                print("\n📄 BENZER VERİLER:\n")
                for cift in benzer_ciftler:
                    print(f"{cift['id1']} ve {cift['id2']} benzer (Skor: {int(cift['score'])})")  # tam sayı

        # ---- SİLİNEN VERİLER ----
        elif komut == "removed":
            if not removed_list:
                print("⚠️ Hiç silinen veri yok.")
            else:
                print("\n📄 SİLİNEN VERİLER (ID LİSTESİ):\n")
                for item in removed_list:
                    print(
                        f"{item.get('veri_id')} → sebep ID: {item.get('_silme_sebebi_id')}"
                    )

        # ---- TEMİZ VERİLER ----
        elif komut == "clean":
            if not clean_list:
                print("⚠️ Hiç temiz veri yok.")
            else:
                print("\n📄 TEMİZ VERİLER (ID LİSTESİ):\n")
                for item in clean_list:
                    print(item.get("veri_id"))

        # ---- HATALI KOMUT ----
        else:
            print("\n❗ Geçersiz komut. Kullanım örnekleri:")
            print("  id45 / veriid45 → ID sorgula")
            print("  duplicate       → Tam aynı veriler")
            print("  similar         → Benzer veriler")
            print("  removed         → Silinen veriler")
            print("  clean           → Temiz veriler")
            print("  ENTER           → Çıkış")


if __name__ == "__main__":
    main()
