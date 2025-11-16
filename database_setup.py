import sqlite3

def setup_database():
    conn = sqlite3.connect('spp_system.db')
    c = conn.cursor()
    
    # Tabel Mahasiswa
    c.execute('''CREATE TABLE IF NOT EXISTS mahasiswa
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nim TEXT UNIQUE,
                  nama TEXT,
                  email TEXT,
                  id_dosen INTEGER,
                  status_administrasi TEXT DEFAULT 'pending')''')
    
    # Tabel Pembayaran
    c.execute('''CREATE TABLE IF NOT EXISTS pembayaran
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nim TEXT,
                  tanggal_bayar DATE,
                  jumlah INTEGER,
                  status TEXT DEFAULT 'pending',
                  bukti_bayar TEXT)''')
    
    # Tabel Dosen
    c.execute('''CREATE TABLE IF NOT EXISTS dosen
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  kode_dosen TEXT UNIQUE,
                  nama TEXT,
                  email TEXT)''')
    
    # Data sample
    c.execute("INSERT OR IGNORE INTO dosen VALUES (1, 'DOS001', 'Dr. Ahmad', 'ahmad@univ.ac.id')")
    c.execute("INSERT OR IGNORE INTO mahasiswa VALUES (1, '202401001', 'Budi Santoso', 'budi@student.univ.ac.id', 1, 'pending')")
    
    conn.commit()
    conn.close()
    print("Database setup completed!")

if __name__ == "__main__":
    setup_database()
