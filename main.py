import os
import random
import requests
from bs4 import BeautifulSoup
import tweepy
import time

# --- FUNGSI 1: MENDAPATKAN POSTINGAN DARI URL ---
# (DIMODIFIKASI: Hanya mengambil teks, dari URL baru)
def get_random_post_text(url="https://raw.githubusercontent.com/Buzz-News/xdate/main/post.txt"):
    """
    Membaca konten dari URL, memisahkan postingan berdasarkan '---',
    dan memilih satu blok postingan utuh secara acak.

    Args:
        url (str): URL file .txt yang berisi postingan.

    Returns:
        str: Sebuah string teks postingan.
             Mengembalikan None jika URL tidak bisa diakses atau kosong.
    """
    try:
        print(f"Mengambil data postingan dari: {url}")
        response = requests.get(url)
        response.raise_for_status() # Cek jika ada error HTTP
        
        content = response.text

        # Memisahkan postingan berdasarkan '---' dan membersihkan spasi/baris baru
        posts = [post.strip() for post in content.split('---') if post.strip()]

        if not posts:
            print("Tidak ada postingan yang ditemukan dari URL.")
            return None

        # Memilih satu blok postingan secara acak
        random_block = random.choice(posts)
        # Mengembalikan seluruh blok sebagai teks postingan
        return random_block.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses URL '{url}': {e}")
        return None
    except Exception as e:
        print(f"Terjadi error saat memproses data dari URL: {e}")
        return None

# --- (FUNGSI BARU): MENDAPATKAN URL GAMBAR RANDOM DARI FOLDER GITHUB ---
def get_random_image_url_from_folder(api_url="https://api.github.com/repos/Buzz-News/xdate/contents/date"):
    """
    Mengambil daftar file dari folder di GitHub via API,
    memfilter file gambar, dan memilih satu URL gambar secara acak.

    Args:
        api_url (str): URL GitHub API untuk folder 'contents'.

    Returns:
        str: Sebuah URL download gambar.
             Mengembalikan None jika terjadi error atau tidak ada gambar.
    """
    try:
        print(f"Mengambil data gambar dari GitHub API: {api_url}")
        # Menggunakan API v3 untuk mendapatkan konten folder dalam format JSON
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        files = response.json()
        
        # Pastikan responsnya adalah list (daftar file)
        if not isinstance(files, list):
            print(f"Error: GitHub API tidak mengembalikan list. Respon: {files}")
            return None

        image_urls = []
        # Loop melalui setiap item di folder
        for file in files:
            # Pastikan itu adalah file (bukan sub-folder)
            if file['type'] == 'file':
                # Ambil 'download_url' yang merupakan link langsung ke file mentah
                dl_url = file.get('download_url')
                if dl_url and dl_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    image_urls.append(dl_url)

        if not image_urls:
            print("Tidak ada file gambar (.png, .jpg, .jpeg, .gif, .webp) yang ditemukan di folder.")
            return None

        # Pilih satu URL gambar secara acak dari daftar
        chosen_image_url = random.choice(image_urls)
        print(f"Memilih gambar acak: {chosen_image_url}")
        return chosen_image_url

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses GitHub API '{api_url}': {e}")
        return None
    except Exception as e:
        print(f"Terjadi error saat memproses data dari GitHub API: {e}")
        return None

# --- FUNGSI 2: MENGAMBIL KEYWORD TRENDING ---
# (TETAP SAMA, TIDAK DIUBAH)
def get_trending_keywords(url="https://getdaytrends.com/indonesia/", count=5):
    """
    Mengambil keyword trending teratas dari URL yang diberikan.
    Logika disesuaikan untuk getdaytrends.com.

    Args:
        url (str): URL dari situs web trending topics.
        count (int): Jumlah keyword teratas yang akan diambil.

    Returns:
        list: Sebuah list berisi keyword trending.
              Mengembalikan list kosong jika terjadi error.
    """
    try:
        print(f"Mengambil trending keywords dari: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Akan memunculkan error jika status code bukan 200

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Logika baru: getdaytrends.com menggunakan <table>
        trend_table = soup.find('table') 
        
        if not trend_table:
            print("Tidak dapat menemukan tabel tren (<table>) di halaman.")
            return []

        # Ambil semua link di dalam tabel
        trends_links = trend_table.find_all('a')
        
        keywords = []
        for trend in trends_links:
            text = trend.text
            # Filter link "View details" atau link tidak relevan lainnya
            if text and text != "View details" and not text.isdigit():
                keywords.append(text)
            
            if len(keywords) >= count:
                break
        
        print(f"Berhasil mendapatkan keywords: {keywords}")
        return keywords

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses URL: {e}")
        return []
    except Exception as e:
        print(f"Terjadi error saat mengambil trending keywords: {e}")
        return []


# --- FUNGSI 3: MEMPOSTING KONTEN KE X.COM ---
# (TETAP SAMA, TIDAK DIUBAH)
def post_to_x(text_to_post, image_url=None):
    """
    Memposting teks dan (opsional) gambar ke akun X.com menggunakan API.

    Args:
        text_to_post (str): Teks yang akan dijadikan tweet.
        image_url (str, optional): URL gambar yang akan diunggah.
    """
    try:
        # Otentikasi
        auth = tweepy.OAuth1UserHandler(
            os.getenv('X_API_KEY'), os.getenv('X_API_SECRET'),
            os.getenv('X_ACCESS_TOKEN'), os.getenv('X_ACCESS_TOKEN_SECRET')
        )
        api_v1 = tweepy.API(auth)
        client_v2 = tweepy.Client(
            bearer_token=os.getenv('X_BEARER_TOKEN'),
            consumer_key=os.getenv('X_API_KEY'),
            consumer_secret=os.getenv('X_API_SECRET'),
            access_token=os.getenv('X_ACCESS_TOKEN'),
            access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET')
        )

        media_id = None
        if image_url:
            print(f"Mengunduh gambar dari: {image_url}")
            filename = 'temp_image.jpg'
            # Menambahkan User-Agent untuk menghindari blokir (opsional tapi disarankan)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(image_url, stream=True, headers=headers)

            if response.status_code == 200:
                with open(filename, 'wb') as image_file:
                    for chunk in response.iter_content(1024):
                        image_file.write(chunk)

                print("Mengunggah gambar ke X.com...")
                media = api_v1.media_upload(filename=filename)
                media_id = media.media_id_string
                print(f"Gambar berhasil di-upload. Media ID: {media_id}")
                os.remove(filename)
            else:
                print(f"Gagal mengunduh gambar. Status code: {response.status_code}")

        # Membuat tweet
        print("Membuat tweet...")
        if media_id:
            response = client_v2.create_tweet(text=text_to_post, media_ids=[media_id])
        else:
            response = client_v2.create_tweet(text=text_to_post)

        print(f"?? Berhasil memposting tweet! ID Tweet: {response.data['id']}")

    except Exception as e:
        print(f"? Error saat memposting ke X.com: {e}")

# --- FUNGSI UTAMA ---
if __name__ == "__main__":

    # --- LOGIKA PENUNDA WAKTU RANDOM ---
    # (TETAP SAMA, TIDAK DIUBAH)
    max_delay_seconds = 4 * 60 * 60 
    random_delay = random.randint(0, max_delay_seconds)
    
    print(f"Cron terpicu. Menunggu selama {random_delay} detik (sekitar {random_delay/3600:.2f} jam) untuk merandomisasi waktu posting.")
    time.sleep(random_delay)
    print("Waktu tunggu selesai. Memulai skrip posting.")
    # --- AKHIR LOGIKA PENUNDA WAKTU ---


    print("="*45)
    print("Memulai proses auto-posting ke X.com...")
    print("="*45)

    # --- (DIMODIFIKASI) ---
    # Langkah 1: Memanggil fungsi untuk mengambil teks postingan acak
    print("Langkah 1: Mengambil teks postingan acak...")
    post_text = get_random_post_text()
    
    # Langkah 2: Memanggil fungsi untuk mengambil URL gambar acak
    print("Langkah 2: Mengambil URL gambar acak...")
    image_url = get_random_image_url_from_folder()
    # --- (AKHIR MODIFIKASI) ---

    if post_text:
        # Langkah 3: Mengambil dan menambahkan trending keywords
        print("Langkah 3: Mengambil trending keywords...")
        trending_keywords = get_trending_keywords()
        if trending_keywords:
            # Membersihkan keyword (menghilangkan spasi) dan menambahkan #
            hashtags = " ".join([f"#{keyword.replace(' ', '')}" for keyword in trending_keywords])
            post_text += f"\n\n{hashtags}"

        print("\n--- KONTEN DIPILIH ---")
        print("Teks Postingan:")
        print(post_text)
        if image_url:
            print(f"\nURL Gambar: {image_url}")
        else:
            print("\nTidak ada gambar yang valid ditemukan untuk postingan ini.")
        print("----------------------\n")

        # Langkah 4: Posting ke X.com
        print("Langkah 4: Memposting ke X.com...")
        post_to_x(post_text, image_url)
    else:
        print("Tidak ada postingan yang bisa dipilih dari URL. Proses dihentikan.")

    print("\n" + "="*45)
    print("Proses selesai.")
    print("="*45)