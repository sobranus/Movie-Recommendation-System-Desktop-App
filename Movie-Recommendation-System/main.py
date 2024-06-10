import webbrowser   # 1-7 mengimpor modul-modul yang diperlukan serta file system.py dan HyperlikManager.py
import tkinter
import re
from functools import partial
from tkinter import ttk
import system as ims
from HyperlinkManager import *


def update_values(combox, data_type):   # fungsi untuk update isi dari input-input combo box
    filter_str = combox.get().lower()   # mengubah jika ada perbedaan huruf besar dengan kecil, karena python case sensitive.
    filter_str = ' '.join([word for word in re.split(r'\s+', filter_str) if word != ''])    # memfilter data agar setiap kata hanya dipisah spasi sehingga mengeliminasi whitespace tidak perlu 
    
    if data_type == type_data:  # jika parameter data_type dari type_data yaitu data tipe film, maka
        data_type = list(type_mapping.keys())   # agar kata kunci dari type_mapping yang ditampilkan di combobox, bukan value asli dataset, misal tvMiniSeries menjadi TV Mini Series

    if filter_str == '':
        combox['values'] = data_type    # tampilkan semua data jika combobox kosong
    else:
        filtered_list_1 = []
        filtered_list_2 = []
        for value in data_type:
            if str(value).lower().startswith(filter_str):   # data combobox dicocokkan dengan dataset apakah ada yang sama (dimulai dengan > ava ~ avatar)
                filtered_list_1.append(value)
            elif filter_str in str(value).lower():  # data combobox dicocokkan dengan dataset apakah ada yang sama (mengandung > vat ~ avatar)
                filtered_list_2.append(value)
        combox['values'] = filtered_list_1 + filtered_list_2    # hasil pencarian disortir (dimulai dengan) duahulu, lalu (mengandung) dan dimasukkan kedalam combo box

def get_text(event=None):   # fungsi untuk melakukan proses rekomendasi
    text_widget = Text(root, font='Courier 13 italic', cursor='arrow', bg='white', height=11, width=60)    # membuat widget text untuk menampilkan hasil rekomendasi
    text_widget.tag_configure('tag-center', justify='center')
    hyperlink = HyperlinkManager(text_widget)   # seting untuk teks output rekomendasi dijadikan teks hyperlink > HyperlinkManager.py
    
    if button2.cget("relief") == 'sunken' and button3.cget("relief") == 'raised':   # jika button2 sunken dan button3 relief artinya jika input berupa judul film
        query = combo1.get()    # mengambil data judul film pada combo box combo1 untuk diproses
    elif button2.cget("relief") == 'raised' and button3.cget("relief") == 'sunken': # jika button2 relief dan button3 sunken artinya jika input berupa preferensi
        new_data = {
        'sortedTitle': [f'Preference Index ({combo6.get()})'],      # 38-47 adalah variabel data preferensi sementara karena proses cosine similarity memerlukan index pada dataset
        'primaryTitle': [f'Preference Index'],
        'tconst': [f'ttinvalid'],
        'titleType': [f'{type_mapping.get(combo5.get(), "")}'],
        'averageRating': [f'{combo7.get()}'],
        'genres': [f'{combo2.get()} {combo3.get()} {combo4.get()}'.rstrip()],
        'numVotes': [f'invalid'],
        'startYear': [f'{combo6.get()}'],
        }
        ims.preference_maker(new_data)      # data baru ditambahkan ke dataset
        preference = ims.preference_get()   # mendapatkan index data preferensi yang telah dibuat
        query = preference      # data preferensi yang akan diproses
    
    query = ' '.join([word for word in re.split(r'\s+', query) if word != ''])  # memfilter whitespace data input seperti pada baris 13
    text = ims.get_recommendations(query)   # proses mendapatkan rekomendasi > system.py
    
    if button2.cget("relief") == 'raised' and button3.cget("relief") == 'sunken':   # jika dalam posisi input preferensi
        ims.preference_delete()     # menghapus data preferensi sementara yang dibuat
        
    if text is None:        # 58-63 menampilkan teks jika text pada baris 53 None (proses rekomendasi gagal/item pada input tidak ditemukan)
        text = "Item tidak ditemukan!\n"
        text_widget.insert(1.0, text, 'tag-center')
        text_widget.insert(END, '\n Tips:\n\n 1. Input tidak boleh kosong.\n '
                                '2. Cek kesalahan ketikan.\n '
                                '3. Gunakan bantuan dropdown untuk menemukan.\n ', 'tag-left')
    else:
        text_widget.delete(1.0, END)    # menghapis teks pada widget
        for idx, title, imdb_url in text.itertuples():  # output dari proses baris 53 berupa indeks, judul film dan url film berupa tuple sesuai kolomnya pada dataset
            text_widget.insert(END, title, hyperlink.add(partial(open_link, imdb_url)))     # menampilkan judul pada widget teks beserta menambahkan teksnya hyperlink
            if idx != 19:               # 68-69 Hanya menampilkan 0-19 atau 20 judul film saja pada kotak rekomendasi
                text_widget.insert(END, '\n')
                text_widget.insert(END, '\n')
                
    text_widget.config(highlightcolor='black', highlightbackground="gray", highlightthickness=2)    #71-75 seting posisi, menampilkan widget teks dan menambahkan scrollbar
    text_widget.place(x=center_label(root, text_widget), y=375)
    scroll_y = Scrollbar(text_widget, orient='vertical', command=text_widget.yview)
    scroll_y.place(x=185*3 + 30, relheight=1)
    text_widget.configure(state='disabled', yscrollcommand=scroll_y.set)
    
def toggle_input(input):    # fungsi pembeda jika input berdasarkan judul atau preferensi
    
    title_label.place_forget()  # 79-83 menghilangkan label-label jenis input
    genre_box_label.place_forget()
    type_box_label.place_forget()
    year_box_label.place_forget()
    rating_box_label.place_forget()
    
    if input == 'judul':    # jika tombol input judul ditekan
        button2.config(relief=tkinter.SUNKEN)   # mengubah tampilan tombol untuk menandakan dalam posisi input judul
        button3.config(relief=tkinter.RAISED)
        title_label.place(x=center_label(root, title_label), y=210)    # memunculkan label input judul
        
        combo2.place_forget()   # menghilangkan combobox input preferensi (2-7)
        combo3.place_forget()
        combo4.place_forget()
        combo5.place_forget()
        combo6.place_forget()
        combo7.place_forget()
        combo1.place(x=center_label(root, combo1), y=250)   # memunculkan combobox input judul (1)
    elif input == 'preferensi':    # jika tombol input preferensi ditekan
        button3.config(relief=tkinter.SUNKEN)   # mengubah tampilan tombol untuk menandakan dalam posisi input preferensi
        button2.config(relief=tkinter.RAISED)
        genre_box_label.place(x=center_label(root, title_label)-270, y=210)    # memunculkan label input preferensi
        type_box_label.place(x=center_label(root, title_label)+45, y=210)
        year_box_label.place(x=center_label(root, title_label)+235, y=210)
        rating_box_label.place(x=center_label(root, title_label)+455, y=210) 
        
        combo1.place_forget()   # menghilangkan combobox input judul (1)
        combo2.place(x=center_label(root, combo2)-425, y=250)      # memunculkan combobox input preferensi (2-7)
        combo3.place(x=center_label(root, combo3)-300, y=250)
        combo4.place(x=center_label(root, combo4)-175, y=250)
        combo5.place(x=center_label(root, combo5)+25, y=250)
        combo6.place(x=center_label(root, combo6)+225, y=250)
        combo7.place(x=center_label(root, combo7)+425, y=250)
        
    
def center_label(root, element):  # fungsi untuk menempatkan elemen-elemen GUI di tengah (sumbu x)
    element.place(x=0, y=-1000)   # inisiasi agar bisa diupdate, y=-1000 karena seringkali bug terlihat sekejap jika ditampilkan di jangkauan layar
    root.update_idletasks()     
    window_width = root.winfo_width()   # mendapatkan lebar layar
    label_width = element.winfo_width()   # mendapatkan lebar elemen
    x = (window_width - label_width) // 2   #menghitung dimana sumbu x untuk elemen harus ditempatkan
    return x

def open_link(my_url):  # fungsi untuk membuka web browser dengan link my_url
    webbrowser.open_new(url=my_url)

root = Tk()     # membuat main window dengan variabel root
root.title("Sistem Rekomendasi Film")   # judul untuk window
screen_width = root.winfo_screenwidth()     
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")    # membuat main window menjadi fullscreen
root.resizable(width=False, height=False)   # membuat window tidak bisa diubah ukurannya

frame = Frame(root, height=614, width=1136).place(x=200, y=100)     # membuat frame untuk menempatkan elemen-elemen GUI
bg_image = PhotoImage(file=r'background.png')   # import png untuk background
bg_label = Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)   # membuat label untuk menampilkan gambar background

label1 = Label(frame, font='Helvetica 13', text='Sistem Rekomendasi Film', height=2, width=40,
               bg='white', highlightthickness=2, highlightbackground="gray")    # label tulisan judul sistem
method_label = Label(frame, font='Helvetica 13', text='Pilih input yang akan diberikan:')   # label pemilihan input

title_label = Label(frame, font='Helvetica 13', text='Pilih Judul Film:')   # 141-145 label-label untuk input-input
genre_box_label = Label(frame, font='Helvetica 13', text='Genre:')
type_box_label = Label(frame, font='Helvetica 13', text='Tipe Film:')
year_box_label = Label(frame, font='Helvetica 13', text='Tahun Rilis:')
rating_box_label = Label(frame, font='Helvetica 13', text='Rating:')

movie_data = ims.get_movie_data()   # 147-151 variabel untuk menyimpan data-data dari dataset melalui system.py(ims)
genre_data = ims.get_genre_data()
type_data = ims.get_type_data()
year_data = ims.get_year_data()
rating_data = ims.get_rating_data()
type_mapping = {        # mapping untuk tampilan pada combobox tipe film
    'Movie': 'movie',
    'TV Series': 'tvSeries',
    'TV Movie': 'tvMovie',
    'TV Mini Series': 'tvMiniSeries',
    'TV Special': 'tvSpecial',
    'Video': 'video',
}

combo1 = ttk.Combobox(frame, width=60, font=("Courier", 13), postcommand=lambda: update_values(combo1, movie_data), values=movie_data)  # 161-167 combobox untuk input-input dengan postcommand fungsi update_values()
combo2 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo2, genre_data), values=genre_data)
combo3 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo3, genre_data), values=genre_data)
combo4 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo4, genre_data), values=genre_data)
combo5 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo5, type_data), values=type_data)
combo6 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo6, year_data), values=year_data)
combo7 = ttk.Combobox(frame, width=10, font=("Courier", 13), postcommand=lambda: update_values(combo7, rating_data), values=rating_data)

button1 = Button(frame, text='Dapatkan Rekomendasi', font='Arial 13 bold', bg='white', width=35, command=get_text)  # tombol dapatkan rekomendasi dengan command get_text()
button2 = Button(frame, text='Judul Film', font='Arial 13 bold', bg='white', width=20, command=lambda : toggle_input('judul'))  # tombol input judul
button3 = Button(frame, text='Preferensi', font='Arial 13 bold', bg='white', width=20, command=lambda : toggle_input('preferensi')) #tombol input preferensi

output_text = Text(frame, font='Times 13 ', cursor='arrow', bg='white', height=11, width=60)  # 173-177 membuat kotak teks untuk output
output_text.tag_configure('tag-center', justify='center')
output_text.insert(1.0, 'Output:\n', 'tag-center')
output_text.config(highlightcolor='black', highlightbackground="gray", highlightthickness=2)
output_text.configure(state='disabled')

root.option_add('*TCombobox*Listbox.font', ("Times", 13))   # seting font untuk combo box
root.update_idletasks()     # update perubahan pada main window

output_text.place(x=center_label(root, output_text), y=375)     # 182-187 menentukan posisi elemen-elemen GUI serta menampilkannya
label1.place(x=center_label(root, label1), y=50)
method_label.place(x=center_label(root, method_label), y=120)
button1.place(x=center_label(root, button1), y=300)
button2.place(x=550, y=160)
button3.place(x=778, y=160)

if __name__ == '__main__':     # main loop
    root.mainloop()
