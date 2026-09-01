# FBRef Scraper

[fbref.com](https://fbref.com) üzerinden futbol verisi çeken bir web scraper projesi. Gerçek bir tarayıcı (Chrome) kullanarak sayfaları açar, tabloları parse eder ve sonuçları JSON olarak kaydeder.

## Neler Çekilebilir?

Proje 4 farklı sayfa tipini destekler:

### Maç Raporu (`match`)
Tek bir maçın detaylı raporunu çeker:
- Maç genel bilgileri (tarih, stadyum, hakem, skor)
- Takım istatistikleri (şut, isabetli şut, kurtarış, topa sahip olma vb.)
- Oyuncu istatistikleri (her iki takımın tüm oyuncuları)
- Maç olayları (gol, asist, kart, oyuncu değişikliği)
- Kadrolar ve dizilişler

### Oyuncu Sayfası (`player`)
Bir oyuncunun profil sayfasını çeker:
- Oyuncu bilgileri (isim, mevki, boy, kilo, ayak, doğum tarihi vb.)
- Kariyer istatistik tabloları (standart, şut, pas, defans vb. tüm tablolar)

### Kulüp Sayfası (`club`)
Bir kulübün sezonluk sayfasını çeker:
- Kulüp bilgileri
- Kulübün o sezon oynadığı tüm turnuvalardaki istatistik tabloları (lig, kupa, avrupa vb. her turnuva için ayrı)

### Lig / Turnuva Sayfası (`league`)
Bir lig veya turnuvanın (Şampiyonlar Ligi dahil) sayfasını çeker:
- Lig bilgileri
- Puan durumu (UCL gibi turnuvalarda grup tabloları dahil, çoklu tablo desteği)
- Takım istatistikleri (for/against)
- Fikstür ve oynanmış maçların linkleri
- Liderlik tabloları (gol kralı, asist kralı vb. 35 kategori)
- Uyruk dağılımı

## Kurulum

Proje [uv](https://docs.astral.sh/uv/) ile yönetiliyor. Python 3.11+ gerektirir.

```bash
git clone https://github.com/erdemalti0/fbref_scrapper
cd fbref_scrapper
uv sync
```

Tarayıcı olarak bilgisayarınızda Chrome yüklü olmalı (nodriver gerçek Chrome kullanır, headless çalışmaz — fbref headless tarayıcıları engeller).

## Kullanım

```bash
python main.py <tip> <url>
```

| Tip      | Açıklama            | Örnek URL                                                              |
|----------|---------------------|------------------------------------------------------------------------|
| `match`  | Maç raporu          | `https://fbref.com/en/matches/675b328b/...`                            |
| `player` | Oyuncu sayfası      | `https://fbref.com/en/players/e6af3cc7/Clarence-Seedorf`               |
| `club`   | Kulüp sezon sayfası | `https://fbref.com/en/squads/.../Galatasaray-Stats`                    |
| `league` | Lig/turnuva sayfası | `https://fbref.com/en/comps/9/Premier-League-Stats`                    |

Örnek:

```bash
python main.py league https://fbref.com/en/comps/9/Premier-League-Stats
```

URL ile tip uyuşmazsa (örneğin `match` tipine oyuncu linki verilirse) program tarayıcıyı açmadan hata verir. Detaylar için:

```bash
python main.py --help
```

## Çıktılar

Çekilen veriler `storage/` klasörüne JSON olarak kaydedilir:

```
storage/
├── players/    # oyuncu raporları
├── clubs/      # kulüp raporları
├── leagues/    # lig/turnuva raporları
└── *.json      # maç raporları
```

Dosya adları sayfadaki ID'lerden gelir (ör. `9_2026-2027.json` Premier League 2026-2027 sezonu).

Loglar `logs/scraper.log` dosyasında rotasyonlu olarak tutulur ve konsola da yazılır.

## Proje Yapısı

```
core/                       # tarayıcı, tip tanımları (pydantic), yardımcı fonksiyonlar, storage, logger
scrapers/
├── match_report/           # maç raporu scraper'ları
├── player_page/            # oyuncu sayfası scraper'ları
├── club_page_by_season/    # kulüp sayfası scraper'ları
└── league_page/            # lig/turnuva scraper'ları
main.py                     # CLI giriş noktası
```

Her scraper modülü kendi içinde `if __name__ == "__main__"` bloğuyla bağımsız test edilebilir.

## Teknolojiler

- **nodriver** — Chrome tabanlı tarayıcı otomasyonu
- **BeautifulSoup** — HTML parse
- **pydantic** — veri modelleri ve JSON serileştirme

## Lisans

MIT
