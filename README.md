````markdown
# Veri Tekrar ve Benzerlik Kontrol Sistemi

Bu proje, JSON formatındaki verileri analiz ederek **tam aynı** ve **benzer** kayıtları tespit eden bir Python uygulamasıdır. Ayrıca gereksiz tekrarları siler ve temiz veri seti oluşturur.

---

## Özellikler

- JSON dosyasındaki verileri bloklar halinde karşılaştırır.
- **Tam aynı verileri** ve **benzer verileri** tespit eder.
- Silinen verileri `_silme_sebebi_id` ile kaydeder.
- Temiz veri (`clean_data.json`) oluşturur.
- Windows sistemlerde ekranın kapanmasını engelleyen özellik içerir.
- Konsol üzerinden gelişmiş sorgulama yapabilirsiniz:
  - ID sorgulama (`id12` veya `veriid12`)
  - Tam aynı verileri listeleme (`duplicate`)
  - Benzer verileri listeleme (`similar`)
  - Silinen verileri listeleme (`removed`)
  - Temiz verileri listeleme (`clean`)

---

## Kullanım

1. Gereksinimler:
   - Python 3.10+
   - `rapidfuzz` kütüphanesi

2. Terminalden virtual environment’i aktifleştirin (varsa):

```powershell
& .venv/Scripts/Activate.ps1
````

3. Kodun başında `DOSYA_ADI_GİR.json` yerine analiz edilecek JSON dosyasının adını girin.

4. Programı çalıştırın:

```powershell
python <dosya_adı>.py
```

5. İşlem tamamlandıktan sonra oluşan dosyalar:

* `duplicate_pairs.json` → Tam aynı veriler
* `similar_pairs.json` → Benzer veriler
* `clean_data.json` → Temiz veri seti
* `removed_items.json` → Silinen veriler (sebep ID ekli)

---

## Alanlar

Kod, verileri birleştirerek aşağıdaki alanları kontrol eder:

* `base_question`
* `alt_question1`
* `alt_question2`
* `full_answer`
* `short_answer`

---

## Örnek Komutlar (Konsol Sorgulama Modu)

```text
ENTER           → Çıkış
id45 / veriid45 → Belirli ID sorgula
duplicate       → Tam aynı verileri göster
similar         → Benzer verileri göster
removed         → Silinen verileri listele
clean           → Temiz veri ID’lerini göster
```

---

## Ayarlar

* `BENZERLIK_ESIGI` → Benzerlik skor eşiği (varsayılan: 85)
* `BLOK_BOYUTU` → Her blokta kaç veri karşılaştırılacak
* `KAYMA_MIKTARI` → Bir sonraki bloğa geçerken kaç geriden başlanacak
* `PROGRESS_LOG_EVERY` → Kaç veri karşılaştırmada bir ilerleme logu gösterilecek

---

## Önemli Notlar

* JSON verisi `veri_id` ve kontrol edilecek alanlara sahip olmalıdır.
* Kod, büyük veri setlerinde bloklu ve kaymalı karşılaştırma yaparak performansı optimize eder.
* Windows dışı sistemlerde ekran kapanmasını engelleyen özellik devre dışıdır.
