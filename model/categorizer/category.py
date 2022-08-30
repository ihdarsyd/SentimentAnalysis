import numpy as np

class Category:
  def __init__(self):
    self.keys = ["gawat","darurat",
      "obat","generik","resep","apotek",
      "transportasi","ambulan", 
      "salin","bayi",
      "kontrol","klinik","puskesmas","operasi","rawat","inap","faskes",
      "kk","anggota","aktif","kartu",
      "bayar","autodebet","manual","tagih","tunggak","aplikasi","debit",
      "rujuk","administrasi","kondisi","sosialisasi","atur","peraturan","pasien","layan",
      "respon","pegawai","tugas","komunikasi",
      "iur","naik","tarif","premi",
      "opname", "biaya","nonaktif","puas","ramah","dinaikin","rata",
      "nunggak","birokrasi","publikasi","daftar","operator","debet","bank","kis",
      "alur","klaim"]
      
    self.dict_c = {
      'Pelayanan Kegawat Darurat': [0,1],
      'Pelayanan Ambulan': [6,7],
      'Pelayanan Persalinan': [8,9],
      'Fasilitas Kesehatan': [10,11,12,13,14,15,16,44,50],
      'Kepesertaan': [17,18,19,20,46,54,58,26],
      'Pelayanan Petugas':[36,37,38,39,47,48,55],
      'Sistem pembayaran': [21,22,23,24,25,26,27,45,56,57,51],
      'Iuran':[21,24,25,40,41,42,43,45,49,51],
      'Prosedur pelayanan': [28,29,30,31,32,33,34,35,52,53,16,59,60],
      'Pelayanan obat dan bahan medis': [2,3,4,5]
    }

    self.label = ["Pelayanan Kegawat Darurat", "Pelayanan obat dan bahan medis",
    "Pelayanan Ambulan", "Pelayanan Persalinan", "Fasilitas Kesehatan",
    "Kepesertaan", "Sistem pembayaran", "Iuran", "Prosedur pelayanan", "Pelayanan Petugas"]

  def generateCategorySpace(self):
    spaces = np.full([len(self.dict_c),len(self.keys)+1], 0)
    
    for key,value in enumerate(self.dict_c):
        for item in self.dict_c[value]:
            spaces[key][item] += 1
    return np.array(spaces)
  
  def generateKeySpace(self, keylist):
    subspace = np.full([len(self.keys)+1], 0)
    for key in keylist:
        subspace[self.keys.index(key)] += 1
    return np.array(subspace)
  
