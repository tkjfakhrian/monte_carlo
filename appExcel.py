import streamlit as st
from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import numpy as np
import pymysql as pm
import math

class MainClass() :
    def __init__(self):
        self.data = Data()
        self.simulasi = Simulasi()

    # Fungsi judul halaman
    def judul_halaman(self):
        nama_app = "Aplikasi Simulasi Penerimaan Mahasiswa"
        st.title(nama_app)
        #st.header(header)
        #st.subheader(subheader)

    # Fungsi menu sidebar
    def sidebar_menu(self):
        with st.sidebar:
            #selected = option_menu('Menu',['Upload Data','Tabel Distribusi','Simulasi'],
            selected = option_menu('Menu',['Upload Data','Simulasi'],
            icons =["easel2", "table", "graph-up", "input-cursor"],
            menu_icon="cast",
            default_index=0)
            
        if (selected == 'Upload Data'):
            self.data.menu_data()

        if (selected == 'Tabel Distribusi'):
            self.preprocessing.menu_preprocessing()

        if (selected == 'Simulasi'):
            self.simulasi.menu_simulasi()

class Data(MainClass) :
    def __init__(self):
        self.state = st.session_state.setdefault('state', {})
        if 'DataPenerimaan' not in self.state:
            self.state['DataPenerimaan'] = pd.DataFrame()

    def upload_DataPenerimaan(self):
        try:
            uploaded_file = st.file_uploader("Upload Data Penerimaan Mahasiswa", type=["xlsx"], key="penerimaan")
            if uploaded_file is not None:
                self.state['DataPenerimaan'] = pd.DataFrame()
                DataPenerimaan = pd.read_excel(uploaded_file)
                #DataPenerimaan = DataPenerimaan['Tahun'].astype(str)

                self.state['DataPenerimaan'] = DataPenerimaan
        except(KeyError, IndexError):
            st.error("Data yang diupload tidak sesuai")

    def tampil_DataPenerimaan(self) :
        if not self.state['DataPenerimaan'].empty:
            Data = self.state['DataPenerimaan']
            Data['Tahun'] = Data['Tahun'].astype(str)
            st.dataframe(Data)

    def menu_data(self):
        self.judul_halaman()
        self.upload_DataPenerimaan()
        self.tampil_DataPenerimaan()

class Simulasi(Data) :
    def __init__(self):
        self.list_tahun = []
        self.list_jml_pendaftar = []
        self.list_jml_lulus = []
        self.list_jml_register = []
        self.maks_jml_pendaftar = 0
        self.maks_jml_lulus = 0
        self.maks_jml_register = 0
        self.min_jml_pendaftar = 0
        self.min_jml_lulus = 0
        self.min_jml_register = 0
        self.banyak_data = 0

        #Inisialisasi Untuk Tabel Distribusi Frekuensi
        self.Nilai_Interval_Kelas = None
        
        
        self.state = st.session_state.setdefault('state', {})
        if 'DataPenerimaan' not in self.state:
            self.state['DataPenerimaan'] = pd.DataFrame()

    def inisialisasi(self) :
        DataPenerimaan = self.state['DataPenerimaan']
        
        #Membuat List Tahun, Pendaftar, Lulus, dan Register
        self.list_tahun = DataPenerimaan['Tahun'].tolist()
        self.list_jml_pendaftar = DataPenerimaan['Jml_Pendaftar'].tolist()
        self.list_jml_lulus = DataPenerimaan['Jml_Lulus'].tolist()
        self.list_jml_register = DataPenerimaan['Jml_Register'].tolist()

        #Nilai Maksimum dan Minimum Pendaftar, Lulus, dan Register
        #Nilai Maksimum
        self.maks_jml_pendaftar = DataPenerimaan['Jml_Pendaftar'].max()
        self.maks_jml_lulus = DataPenerimaan['Jml_Lulus'].max()
        self.maks_jml_register = DataPenerimaan['Jml_Register'].max()

        #Nilai Minimum
        self.min_jml_pendaftar = DataPenerimaan['Jml_Pendaftar'].min()
        self.min_jml_lulus = DataPenerimaan['Jml_Lulus'].min()
        self.min_jml_register = DataPenerimaan['Jml_Register'].min()

        #Banyak Data
        self.banyak_data = DataPenerimaan.shape[0]
    
    #Function Pembuatan Tabel Distribusi
    def Interval_Kelas (self, Nilai_Maksimal, Nilai_Minimal, Panjang_Kelas) :
        return math.ceil((Nilai_Maksimal-Nilai_Minimal) / Panjang_Kelas)


    #Subrutin Tabel Distribusi
    def Tabel_Distribusi (self, Nilai_Maksimal, Nilai_Minimal,Panjang_Kelas) :
        List_Distribusi = []
        data = Nilai_Minimal
        interval = self.Interval_Kelas(Nilai_Maksimal, Nilai_Minimal, Panjang_Kelas)
        for i in range(Panjang_Kelas) :
            List_Range = list(range(data, data+interval))
            List_Distribusi.append(List_Range)
            data += interval
        
        return List_Distribusi

    #Subrutin Menghitung Frekuensi Kemunculan
    def Tabel_Frekuensi (self, Nilai_Maksimal, Nilai_Minimal, Panjang_Kelas, Index) :
        Dict_Frekuensi = {}
        if Index == 'penerimaan' :
            Data_Penerimaan = self.list_jml_pendaftar
        elif Index == 'lulus' :
            Data_Penerimaan = self.list_jml_lulus
        elif Index == 'register' :
            Data_Penerimaan = self.list_jml_register

        List_Distribusi = self.Tabel_Distribusi(Nilai_Maksimal, Nilai_Minimal, Panjang_Kelas)
        for i in range(0,len(List_Distribusi)) :
            for j in range(0,len(List_Distribusi[0])) :
                for data in Data_Penerimaan :
                    if(data == List_Distribusi[i][j]) :
                        if (i in Dict_Frekuensi) :
                            Dict_Frekuensi[i] += 1
                        else :
                            Dict_Frekuensi[i] = 1
        
        return Dict_Frekuensi
    
    ##Mendapatkan Tabel Distribusi Untuk Number Generator
    #Subrutin Mencari N (Banyak Data)
    def Total_Data (self,Nilai_Maksimal, Nilai_Minimal, Panjang_Kelas, Index) :
        Total_Data = 0
        Dict_Frekuensi = self.Tabel_Frekuensi(Nilai_Maksimal,Nilai_Minimal, Panjang_Kelas, Index)
        for i in Dict_Frekuensi :
            Total_Data += Dict_Frekuensi[i]
        
        return Total_Data
    
    #Subrutin Menghitung Probabilitas Kemunculan
    def Probability (self, Nilai_Maksimal, Nilai_Minimal, Panjang_Data, Index) :
        Dict_Probabilitas = {}
        Dict_Frekuensi = self.Tabel_Frekuensi(Nilai_Maksimal,Nilai_Minimal,Panjang_Data,Index)
        Banyak_Data = self.Total_Data(Nilai_Maksimal,Nilai_Minimal,Panjang_Data,Index)

        for i in range(0,len(Dict_Frekuensi)) :
            Dict_Probabilitas[i] = round(Dict_Frekuensi[i] / Banyak_Data,2) #Membulatkan 2 Angka Dibelakang Koma

        return Dict_Probabilitas

    #Subrutin Probabilitas Kumulatif
    def Cumulative_Probability (self, Nilai_Maksimal, Nilai_Minimal, Panjang_Data, Index) :
        Dict_Kumulatif = {}
        Dict_Probabilitas = self.Probability(Nilai_Maksimal, Nilai_Minimal, Panjang_Data, Index)
        Kumulatif = Dict_Probabilitas[0]
        for i in range(0,len(Dict_Probabilitas)) :
            Dict_Kumulatif[i] = Kumulatif
            if (i != len(Dict_Probabilitas)-1) :
                Kumulatif += Dict_Probabilitas[i+1]

        return Dict_Kumulatif

    #Subrutin Tabel Distribusi Number Generator
    def Tabel_Distribusi_Number_Generator (self,Nilai_Maksimal, Nilai_Minimal, Panjang_Data, Index) :
        list_number_generator = [0]
        data = 0
        Kumulatif = self.Cumulative_Probability(Nilai_Maksimal, Nilai_Minimal, Panjang_Data, Index)
        for i in range(len(Kumulatif)) :
            range_ng = int(Kumulatif[i]*100) + 1
            list_ng = list(range(data, range_ng))
            list_number_generator.append(list_ng)
            data = range_ng
        
        return list_number_generator

    #Subrutin Simulasi Monte Carlo
    def Simulasi_Pendaftaran (self, T_Distribusi, T_NG_Distribusi, awal, akhir, Random_Number) :
        list_Simulasi = [] #List Untuk Menampung Simulasi
        for i in range(awal, akhir+1) :
            for x in range(0, len(T_Distribusi)) :
                if T_NG_Distribusi[x] :
                    if Random_Number in T_NG_Distribusi[x] :
                        var_random = np.random.choice(T_Distribusi[x])
            list_Simulasi.append(var_random)
        
        return list_Simulasi

    def Simulasi (self, Simulasi_Sebelumnya,T_Distribusi, T_NG_Distribusi, awal, akhir, Random_Number) :
        list_Simulasi = [] #List Untuk Menampung Simulasi
        for i in range(awal, akhir+1) :
            for x in range(0, len(T_Distribusi)) :
                if T_NG_Distribusi[x] :
                    if Random_Number in T_NG_Distribusi[x] :
                        var_random = np.random.choice(T_Distribusi[x])
                        while(var_random > Simulasi_Sebelumnya[i-1]) :
                            var_random = np.random.choice(T_Distribusi[x])
            list_Simulasi.append(var_random)
        
        return list_Simulasi


    def menu_simulasi(self) :
        self.judul_halaman()
        try :
        
            self.inisialisasi()
            #Menghitung Banyak Kelas / Kelompok Data
            Panjang_Kelas = round(1 + (3.322 * (math.log(self.banyak_data,10))))
            
            #Membangkitkan Tabel Distribusi Mahasiswa Mendaftar
            Jml_Pendaftar = self.Tabel_Distribusi(self.maks_jml_pendaftar,self.min_jml_pendaftar,Panjang_Kelas)
            ng_Jml_Pendaftar = self.Tabel_Distribusi_Number_Generator(self.maks_jml_pendaftar,self.min_jml_pendaftar,Panjang_Kelas,"penerimaan")

            #Membangkitkan Tabel Distribusi Mahasiswa Lulus Seleksi
            Jml_Lulus = self.Tabel_Distribusi(self.maks_jml_lulus,self.min_jml_lulus,Panjang_Kelas)
            ng_Jml_lulus = self.Tabel_Distribusi_Number_Generator(self.maks_jml_lulus,self.min_jml_lulus,Panjang_Kelas,"lulus")

            #Membangkitkan Tabel Distribusi Mahasiswa Registrasi
            Jml_Regis = self.Tabel_Distribusi(self.maks_jml_register,self.min_jml_register,Panjang_Kelas)
            ng_Jml_Regis = self.Tabel_Distribusi_Number_Generator(self.maks_jml_register,self.min_jml_register,Panjang_Kelas,"register")

            #Form Untuk Simulasi
            jml_simulasi = st.number_input('Masukkan Jumlah Simulasi :')

            if st.button('Simulasikan') and jml_simulasi > 0:
                awal = 1
                akhir = round(jml_simulasi)
                #Pembangkit Bilangan Acak
                bilrand = np.random.randint(0,100) #Membangkitkan Bilangan Acak Antara 0-100

                Sim_Pendaftaran = self.Simulasi_Pendaftaran(Jml_Pendaftar,ng_Jml_Pendaftar,awal,akhir,bilrand)
                Sim_Lulus = self.Simulasi (Sim_Pendaftaran,Jml_Lulus,ng_Jml_lulus,awal,akhir,bilrand)
                Sim_Regis = self.Simulasi (Sim_Lulus,Jml_Regis,ng_Jml_Regis,awal,akhir,bilrand)
                

                range_simulasi = []
                for i in range (awal,akhir+1) :
                    range_simulasi.append('sim-'+str(i).zfill(2))

                st.header("Chart Hasil Simulasi")
                #Grafik Simulasi
                chart_simulasi = pd.DataFrame(
                    list(zip(Sim_Pendaftaran,Sim_Lulus,Sim_Regis)),
                    columns=["Pendaftar","Lulus","Registrasi"],
                    #index = list(range(awal, akhir+1))
                    index = range_simulasi
                )
                st.dataframe(chart_simulasi)
                st.line_chart(chart_simulasi)

                st.header("Chart Data Fakta")
                #Grafik Data Fakta
                chart_fakta = pd.DataFrame(
                    list(zip(self.list_jml_pendaftar,self.list_jml_lulus,self.list_jml_register)),
                    columns=["Pendaftar","Lulus","Registrasi"],
                    index = self.list_tahun
                )

                st.line_chart(chart_fakta)

                st.header("Chart Data Fakta + Simulasi")

                #list_tahun.extend(list(range(awal,akhir+1)))
                self.list_tahun.extend(range_simulasi)
                self.list_jml_pendaftar.extend(Sim_Pendaftaran)
                self.list_jml_lulus.extend(Sim_Lulus)
                self.list_jml_register.extend(Sim_Regis)

                #st.write(list_tahun)
                #Grafik Simulasi
                chart_fakta_simulasi = pd.DataFrame(
                    list(zip(self.list_jml_pendaftar,self.list_jml_lulus,self.list_jml_register)),
                    columns=["Pendaftar","Lulus","Registrasi"],
                    index = self.list_tahun
                )
                st.line_chart(chart_fakta_simulasi)
            else :
                st.write('Mohon Masukkan Jumlah Simulasi Terlebih Dahulu')

        except :
            st.write('Upload File Terlebih Dahulu')        

if __name__ == "__main__":
    # Create an instance of the main class
    main = MainClass()
    
main.sidebar_menu()






