import csv
import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox, Treeview

from tkcalendar import DateEntry


# Veritabanı Oluşturma
def create_db():
    conn = sqlite3.connect('hasta_randevu.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hasta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT,
            soyad TEXT,
            dogum_tarihi TEXT,
            telefon TEXT,
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS randevu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hasta_id INTEGER,
            randevu_tarihi TEXT,
            saat TEXT,
            aciklama TEXT,
            durum TEXT DEFAULT 'Bekliyor',
            FOREIGN KEY(hasta_id) REFERENCES hasta(id)
        )
    ''')
    conn.commit()
    conn.close()

# Bugünkü randevuları bildir
def kontrol_yaklasan_randevular():
    conn = sqlite3.connect('hasta_randevu.db')
    cursor = conn.cursor()
    bugun = datetime.date.today().isoformat()
    cursor.execute('''
        SELECT hasta.ad, hasta.soyad, randevu.randevu_tarihi, randevu.saat 
        FROM randevu
        JOIN hasta ON hasta.id = randevu.hasta_id
        WHERE randevu.randevu_tarihi = ?
    ''', (bugun,))
    randevular = cursor.fetchall()
    conn.close()
    if randevular:
        mesaj = "\n".join([f"{r[0]} {r[1]} - {r[2]} {r[3]}" for r in randevular])
        messagebox.showinfo("Bugünkü Randevular", mesaj)

def kontrol_yaklasan_saatlik_randevular():
    conn = sqlite3.connect('hasta_randevu.db')
    cursor = conn.cursor()
    simdi = datetime.datetime.now()
    bir_saat_sonra = simdi + datetime.timedelta(hours=1)

    bugun = simdi.date().isoformat()
    simdi_saat = simdi.time().strftime("%H:%M")
    bir_saat_sonra_saat = bir_saat_sonra.time().strftime("%H:%M")

    cursor.execute('''
        SELECT hasta.ad, hasta.soyad, randevu.randevu_tarihi, randevu.saat 
        FROM randevu
        JOIN hasta ON hasta.id = randevu.hasta_id
        WHERE randevu.randevu_tarihi = ? AND randevu.saat > ? AND randevu.saat <= ?
    ''', (bugun, simdi_saat, bir_saat_sonra_saat))

    randevular = cursor.fetchall()
    conn.close()

    if randevular:
        mesaj = "\n".join([f"{r[0]} {r[1]} - Saat {r[3]}" for r in randevular])
        messagebox.showinfo("Yaklaşan Randevular (1 Saat İçinde)", mesaj)

# Hasta ve Randevu Ekle
def hasta_ve_randevu_ekle(ad, soyad, dogum_tarihi, telefon, randevu_tarihi, saat, aciklama, durum):
    conn = sqlite3.connect('hasta_randevu.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO hasta (ad, soyad, dogum_tarihi, telefon) VALUES (?, ?, ?, ?)',
                   (ad, soyad, dogum_tarihi, telefon,))
    cursor.execute('SELECT LAST_INSERT_ROWID()')
    hasta_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO randevu (hasta_id, randevu_tarihi, saat, aciklama, durum) VALUES (?, ?, ?, ?, ?)',
                   (hasta_id, randevu_tarihi, saat, aciklama, durum))
    conn.commit()
    conn.close()
    messagebox.showinfo("Başarılı", "Hasta ve randevu kaydı başarıyla eklendi!")

# Yeni Hasta ve Randevu Kaydı
def yeni_hasta_randevu_kaydi():
    form = tk.Toplevel()
    form.title("Yeni Hasta ve Randevu Kaydı")
    form.configure(bg="#0d1b2a")  # Arka planı gece mavisi yap

    # Ortak stil seçenekleri
    label_style = {"font": ("Segoe UI", 10), "fg": "white", "bg": "#0d1b2a"}
    entry_style = {"font": ("Segoe UI", 10)}

    tk.Label(form, text="İsim:", **label_style).grid(row=0, column=0)
    isim_entry = tk.Entry(form, **entry_style)
    isim_entry.grid(row=0, column=1)

    tk.Label(form, text="Soyisim:", **label_style).grid(row=1, column=0)
    soyisim_entry = tk.Entry(form, **entry_style)
    soyisim_entry.grid(row=1, column=1)

    tk.Label(form, text="Doğum Tarihi:", **label_style).grid(row=2, column=0)
    dogum_entry = DateEntry(form, date_pattern='yyyy-mm-dd')
    dogum_entry.grid(row=2, column=1)

    tk.Label(form, text="Telefon:", **label_style).grid(row=3, column=0)
    telefon_entry = tk.Entry(form, **entry_style)
    telefon_entry.grid(row=3, column=1)

    tk.Label(form, text="Randevu Tarihi:", **label_style).grid(row=5, column=0)
    randevu_entry = DateEntry(form, date_pattern='yyyy-mm-dd')
    randevu_entry.grid(row=5, column=1)

    tk.Label(form, text="Saat:", **label_style).grid(row=6, column=0)
    saat_cb = Combobox(form, values=[f"{i}:00" for i in range(9, 18)])
    saat_cb.grid(row=6, column=1)

    tk.Label(form, text="Durum:", **label_style).grid(row=7, column=0)
    durum_cb = Combobox(form, values=["Bekliyor", "Tamamlandı", "İptal Edildi"])
    durum_cb.set("Bekliyor")
    durum_cb.grid(row=7, column=1)

    tk.Label(form, text="Açıklama:", **label_style).grid(row=8, column=0)
    aciklama_txt = tk.Text(form, height=3, width=30, font=("Segoe UI", 10))
    aciklama_txt.grid(row=8, column=1)

    def kaydet():
        hasta_ve_randevu_ekle(
            isim_entry.get(), soyisim_entry.get(), dogum_entry.get(),
            telefon_entry.get(), randevu_entry.get(),
            saat_cb.get(), aciklama_txt.get("1.0", "end-1c"), durum_cb.get()
        )
        form.destroy()

    tk.Button(form, text="Kaydet", command=kaydet,
              font=("Segoe UI", 10), bg="#1b263b", fg="white").grid(row=9, column=0, columnspan=2, pady=10)

# Randevuları getir
def get_randevular():
    conn = sqlite3.connect('hasta_randevu.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.ad, h.soyad, h.telefon, r.randevu_tarihi, r.saat, r.aciklama, r.durum
        FROM randevu r
        JOIN hasta h ON h.id = r.hasta_id
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def verileri_csv_disa_aktar():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV Dosyası", "*.csv")],
                                            title="CSV olarak kaydet")
    if filepath:
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Ad", "Soyad", "Telefon", "Tarih", "Saat", "Açıklama", "Durum"])
                for row in get_randevular():
                    writer.writerow(row)
            messagebox.showinfo("Başarılı", f"Veriler CSV olarak kaydedildi:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi:\n{e}")

# Güncelleme penceresi
def randevu_guncelle(randevu):
    form = tk.Toplevel()
    form.title("Randevu Güncelle")

    tk.Label(form, text="Yeni Saat:").grid(row=0, column=0)
    saat_cb = Combobox(form, values=[f"{i}:00" for i in range(9, 18)])
    saat_cb.set(randevu[4])
    saat_cb.grid(row=0, column=1)

    tk.Label(form, text="Yeni Açıklama:").grid(row=1, column=0)
    aciklama_txt = tk.Text(form, height=3, width=30)
    aciklama_txt.insert("1.0", randevu[5])
    aciklama_txt.grid(row=1, column=1)

    tk.Label(form, text="Durum:").grid(row=2, column=0)
    durum_cb = Combobox(form, values=["Bekliyor", "Tamamlandı", "İptal Edildi"])
    durum_cb.set(randevu[6])
    durum_cb.grid(row=2, column=1)

    def kaydet():
        conn = sqlite3.connect('hasta_randevu.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE randevu SET saat=?, aciklama=?, durum=?
            WHERE hasta_id=(SELECT id FROM hasta WHERE ad=? AND soyad=?) AND randevu_tarihi=?
        ''', (saat_cb.get(), aciklama_txt.get("1.0", "end-1c"), durum_cb.get(), randevu[0], randevu[1], randevu[3]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Randevu güncellendi.")
        form.destroy()

    tk.Button(form, text="Güncelle", command=kaydet).grid(row=3, column=0, columnspan=2)

# Randevuları göster
def randevulari_goruntule():
    form = tk.Toplevel()
    form.title("Randevular")
    form.configure(bg="#0d1b2a")  # Arka plan gece mavisi

    style = {"font": ("Segoe UI", 10), "fg": "white", "bg": "#0d1b2a"}

    tree = Treeview(form, columns=("Ad", "Soyad", "Telefon", "Tarih", "Saat", "Açıklama", "Durum"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)

    tree.grid(row=0, column=0, columnspan=3, pady=10)

    for r in get_randevular():
        tree.insert("", "end", values=r)

    def guncelle_sec():
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])["values"]
            randevu_guncelle(values)

    tk.Button(form, text="Randevuyu Güncelle", command=guncelle_sec,
              font=("Segoe UI", 10), bg="#1b263b", fg="white").grid(row=1, column=0, columnspan=3, pady=5)

# Ana pencere
def ana_pencere():

        window = tk.Tk()
        window.title("Diş Hekimi Otomasyonu")
        window.configure(bg="#0d1b2a")  # Gece mavisi arka plan

        tk.Label(window, text="Diş Hekimi Randevu Sistemi", font=("Segoe UI", 16),
             fg="white", bg="#0d1b2a").pack(pady=10)

        kontrol_yaklasan_randevular()

        tk.Button(window, text="Yeni Hasta ve Randevu", width=30, font=("Segoe UI", 10),
              command=yeni_hasta_randevu_kaydi, bg="#1b263b", fg="white").pack(pady=5)

        tk.Button(window, text="Randevuları Görüntüle", width=30, font=("Segoe UI", 10),
              command=randevulari_goruntule, bg="#1b263b", fg="white").pack(pady=5)

        tk.Button(window, text="Çıkış", width=30, font=("Segoe UI", 10),
              command=window.quit, bg="#1b263b", fg="white").pack(pady=5)
        tk.Button(window, text="Randevuları CSV'ye Aktar", width=30, font=("Segoe UI", 10),
              command=verileri_csv_disa_aktar, bg="#1b263b", fg="white").pack(pady=5)

        window.mainloop()


kontrol_yaklasan_saatlik_randevular()
def giris_ekrani():
    login = tk.Tk()
    login.title("Giriş Yap")
    login.geometry("300x200")
    login.configure(bg="#0d1b2a")

    tk.Label(login, text="Kullanıcı Adı:", font=("Segoe UI", 10), fg="white", bg="#0d1b2a").pack(pady=5)
    kullanici_entry = tk.Entry(login, font=("Segoe UI", 10))
    kullanici_entry.pack()

    tk.Label(login, text="Şifre:", font=("Segoe UI", 10), fg="white", bg="#0d1b2a").pack(pady=5)
    sifre_entry = tk.Entry(login, show="*", font=("Segoe UI", 10))
    sifre_entry.pack()

    def kontrol_et():
        kullanici = kullanici_entry.get()
        sifre = sifre_entry.get()
        if kullanici == "admin" and sifre == "1234":
            login.destroy()
            ana_pencere()
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış!")

    tk.Button(login, text="Giriş", command=kontrol_et, font=("Segoe UI", 10),
              bg="#1b263b", fg="white").pack(pady=10)

    login.mainloop()

giris_ekrani()
