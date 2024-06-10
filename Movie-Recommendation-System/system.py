from sklearn.preprocessing import MinMaxScaler      # 1-5 mengimpor modul-modul yang diperlukan
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

csv_file = 'dataset/imdb_sample.csv'    # nama file dataset
imdb_init = pd.read_csv(csv_file)   # membaca dataset

def similarities(idx):  # fungsi untuk preprocessing dan proses rekomendasi
    imdb = csv_new()    # update dataset (barangkali menggunakan input preferensi)
    cv = CountVectorizer(dtype=np.uint8)    # modul untuk data mining pada data teks kata-kata dalam 8 bit integer
    MMS = MinMaxScaler()    # modul untuk mengubah skala data numerik menjadi dalam skala 0 sampai 1
    dtm = cv.fit_transform(imdb['genres']).toarray()    # data mining kolom genre pada dataset
    
    rating = np.array(imdb['averageRating'])    # pengambilan data rating 
    rating = rating.reshape(-1, 1)  # dimensi diubah sehingga kolom pada list tidak menyertakan index
    rating = MMS.fit_transform(rating)  # mengubah skala menjadi 0 sampai 1
    new_matrix = np.concatenate((dtm, rating), axis=1)  # data rating digabungkan dengan data genre menjadi 1 matriks
    
    startYear = np.array(imdb['startYear'])     # pengambilan data tahun rilis
    startYear = startYear.reshape(-1, 1)    # dimensi diubah sehingga kolom pada list tidak menyertakan index
    startYear = MMS.fit_transform(startYear)    # mengubah skala menjadi 0 sampai 1
    new_matrix = np.concatenate((new_matrix, startYear), axis=1)    # data rating digabungkan dengan data genre dan rating menjadi 1 matriks
    
    similarities = cosine_similarity(new_matrix, dense_output=False)    # data yng tlah melewti tahap preprocessing siap digunakan dengan fungsi cosine_similarity, ouput jarang/sparse agar data kemiripan genre yang bernilai 0 tidak perlu diambil
    
    return similarities[idx]    # proses rekomendasi cosine similarity dengan input parameter idx (index film pilihan)


def build_recommendations(title):   # fungsi proses tokenization dan sorting hasil rekomendasi
    imdb = csv_new()    # update dataset
    try:    # coba, jika terjadi eror atau data tidak ditemukan maka proses akan diabaikan dan langsung mengeksekusi 'except:' pada baris 53
        title = title.lower()   # mengecilkan huruf karena case-sensitive
        tv_shows = ['tvSeries', 'tvMovie', 'tvMiniSeries', 'video', 'tvSpecial']    # variabel tipe-tipe film tv
        sorted_title_found = True in [True for t in imdb['sortedTitle'] if t.lower() == title]  # mengecek apakah parameter title dari input ada di dataset dengan iterasi for loop (judul pada dataset juga diubah menjadi huruf kecil)
        if sorted_title_found:
            idx = imdb[imdb['sortedTitle'].apply(lambda x: x.lower()) == title].index[0]    # ambil index ini jika ditemukan di kolom sortedTitle
        else:
            idx = imdb[imdb['primaryTitle'].apply(lambda x: x.lower()) == title].index[0]   # ambil index ini jika ditemukan di kolom primaryTitle
                                                                                            # hal diatas dilakukan karena pada dataset banyak judul yang berbeda antara primaryTitle dan sortedTitle salah satunya karena perbedaan bahasa
        recommendations = imdb['sortedTitle'].iloc[similarities(idx).argsort()[::-1]][0:500]    # alokasi judul hasil similarities(idx) dan sorting dimulai dari hasil cosine similarity terbesar dengan jumlah 500
                                                                                                # dikarenakan tipe film akan berbeda-beda, agar jika dalam 20 rekomendasi kekurangan misal tipe tv, maka bisa dicari yang selanjutnya dalam 500 data tersebut 
        if imdb.iloc[idx]['titleType'] in tv_shows:     # jika input merupakan film tipe tv
            tv_recommendations = {rec: [imdb['tconst'].iloc[rec], imdb['sortedTitle'].iloc[rec]] for rec in     # hanya tampilkan tipe tv saja dari 500 rekomendasi
                                  recommendations.index if imdb['titleType'].iloc[rec] in tv_shows}
            return pd.DataFrame(tv_recommendations).transpose().iloc[1:21]      # alokasikan dari data ke 1 sampai 21 karena yang pertama (paling mirip) adalah film pada input itu sendiri

        else:       # jika yang lainnya
            movie_recommendations = {rec: [imdb['tconst'].iloc[rec], imdb['sortedTitle'].iloc[rec]] for rec in  # tampilkan tipe movie saja dari 500 rekomendasi
                                     recommendations.index if imdb['titleType'].iloc[rec] == 'movie'}
            return pd.DataFrame(movie_recommendations).transpose().iloc[1:21]   # sama seperti baris 47
    except:
        return None     # jika 'Try:' tidak berhasil


def get_recommendations(title):     # fungsi untuk memulai rekomendasi dan mengelola output dari proses rekomendasi
    recommendations = build_recommendations(title)  # memproses perekomendasian
    if recommendations is None:     
        return recommendations      # return None untuk mengeksekusi teks "Data tidak ditemukan" pada GUI
    else:
        recommendations.rename(columns={0: 'tconst', 1: 'title'}, inplace=True) # menyiapkan output kolom tconst dan title
        recommendations.reset_index(drop=True, inplace=True)    # mengubah index baru untuk output dari dataset
        recommendations['urls'] = [f'https://www.imdb.com/title/{title_id}/' for title_id in recommendations['tconst']] # menyiapkan link url dengan perbedaan pada id film (tconst) untuk setiap film rekomendasi
        return recommendations.drop('tconst', axis=1)   # mereturn data pada variabel recommendations beserta kolom 'urls' dan menghapus kolom 'tconst' karena tidak diperlukan lagi

def preference_maker(new_data):     # fungsi untuk membuat data sementara pada dataset dari input preferensi (parameter new_data pada main.py)
    imdb = csv_new()
    new_data_frame = pd.DataFrame(new_data)
    combined_data = pd.concat([imdb, new_data_frame], ignore_index=True)
    combined_data.to_csv(csv_file, index=False)     # data baru otomatis ditambahkan pada baris terakhir dataset
    
def csv_new():      # fungsi untuk mengupdate dataset yang diperlukan jika kita membuat data sementara pada dataset
    imdb_new = pd.read_csv(csv_file)
    return imdb_new
    
def preference_get():   # fungsi untuk mendapatkan index data preferensi baru
    imdb = csv_new()
    preference = str(imdb.loc[imdb.index[-1], 'sortedTitle'])   # alokasi pada [-1] (minus artinya dimulai dari belakang, -1 adalah yang terakhir)
    return preference
    
def preference_delete():    # fungsi untuk menghapus data preferensi sementara
    imdb = csv_new()
    if not imdb.empty:  
        df = imdb.iloc[:-1] 
        df.to_csv(csv_file, index=False)

def get_movie_data():   # fungsi untuk mengambl data judul dari dataset dan menyimpannya kedalam list
    titles_list = imdb_init['sortedTitle'].tolist()
    return titles_list

def get_genre_data():   # fungsi untuk mengambil data genre dari dataset dan menyimpannya kedalam list
    genres_list = imdb_init['genres'].str.split().explode()
    unique_genres = genres_list.unique()    # menggunakan fungsi unique() karena hanya untuk mengetahui setiap genre yang ada, untuk ditampilkan pada combobox
    unique_genres = list(unique_genres)     
    return unique_genres

def get_type_data():    # fungsi untuk mengambil data tipe film dari dataset dan menyimpannya kedalam list
    types_list = imdb_init['titleType'].str.split().explode()
    unique_types = types_list.unique()      # menggunakan fungsi unique() karena hanya untuk mengetahui setiap genre yang ada, untuk ditampilkan pada combobox
    unique_types = list(unique_types)
    return unique_types

def get_year_data():    # fungsi untuk mengambil data tahun rilis dari dataset dan menyimpannya kedalam list
    years_list = imdb_init['startYear'].tolist()
    unique_years = set(years_list)      # tidak bisa menggunakan unique() karena data numerik
    unique_years = [int(number) for number in sorted(list(unique_years))]   # sorting agar tahun rilis berurutan dan menjadikannya integer
    return unique_years

def get_rating_data():       # fungsi untuk mengambil data rating dari dataset dan menyimpannya kedalam list
    rating_list = imdb_init['averageRating'].tolist()
    unique_rating = set(rating_list)    # menggunakan set() karena data numerik
    unique_rating = sorted(list(unique_rating)) # sorting agar rating berurutan dan menjadikannya integer
    return unique_rating