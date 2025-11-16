from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Helper functions
def get_db():
    conn = sqlite3.connect('spp.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_surat_bebas(nim):
    """Generate surat bebas SPP dalam format text"""
    conn = get_db()
    mahasiswa = conn.execute('SELECT * FROM mahasiswa WHERE nim = ?', (nim,)).fetchone()
    conn.close()
    
    surat = f"""
    SURAT BEBAS ADMINISTRASI SPP
    UNIVERSITAS CONTOH
    
    Dengan ini menerangkan bahwa:
    
    NIM     : {mahasiswa['nim']}
    Nama    : {mahasiswa['nama']}
    
    Telah menyelesaikan pembayaran SPP dan dinyatakan LUNAS.
    Mahasiswa tersebut dapat mengikuti proses administrasi akademik.
    
    Jakarta, {datetime.now().strftime('%d %B %Y')}
    
    Hormat kami,
    Sistem Administrasi Otomatis
    -----------------------------
    Catatan: Surat ini digenerate otomatis oleh sistem
    """
    
    # Simpan file
    if not os.path.exists('static/surat'):
        os.makedirs('static/surat')
    
    filename = f"static/surat/surat_bebas_{nim}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(surat)
    
    return filename

# ROUTES
@app.route('/')
def home():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/mahasiswa')
def status_mahasiswa():
    """Cek status mahasiswa"""
    nim = request.args.get('nim', '')
    status_info = None
    
    if nim:
        conn = get_db()
        mahasiswa = conn.execute('''
            SELECT m.*, p.tanggal_bayar, p.status as status_bayar 
            FROM mahasiswa m 
            LEFT JOIN pembayaran p ON m.nim = p.nim 
            WHERE m.nim = ?
        ''', (nim,)).fetchone()
        conn.close()
        
        if mahasiswa:
            status_info = dict(mahasiswa)
    
    return render_template('status_mahasiswa.html', status_info=status_info, nim=nim)

@app.route('/dashboard-dosen')
def dashboard_dosen():
    """Dashboard untuk dosen"""
    conn = get_db()
    
    # Ambil mahasiswa yang sudah bayar tapi belum diaktivasi
    mahasiswa_pending = conn.execute('''
        SELECT m.nim, m.nama, m.email, p.tanggal_bayar, d.nama as nama_dosen
        FROM mahasiswa m
        JOIN pembayaran p ON m.nim = p.nim
        JOIN dosen d ON m.id_dosen = d.id
        WHERE p.status = 'lunas' AND m.status_administrasi = 'pending'
    ''').fetchall()
    
    # Statistik
    total_mahasiswa = conn.execute('SELECT COUNT(*) FROM mahasiswa').fetchone()[0]
    total_lunas = conn.execute('SELECT COUNT(*) FROM pembayaran WHERE status = "lunas"').fetchone()[0]
    total_active = conn.execute('SELECT COUNT(*) FROM mahasiswa WHERE status_administrasi = "active"').fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard_dosen.html', 
                         mahasiswa_pending=mahasiswa_pending,
                         total_mahasiswa=total_mahasiswa,
                         total_lunas=total_lunas,
                         total_active=total_active)

@app.route('/api/bayar-spp', methods=['POST'])
def bayar_spp():
    """API untuk simulasi pembayaran SPP"""
    data = request.json
    nim = data.get('nim')
    jumlah = data.get('jumlah', 2500000)
    
    conn = get_db()
    
    # Cek apakah mahasiswa ada
    mahasiswa = conn.execute('SELECT * FROM mahasiswa WHERE nim = ?', (nim,)).fetchone()
    if not mahasiswa:
        return jsonify({'status': 'error', 'message': 'NIM tidak ditemukan'})
    
    # Simpan pembayaran
    conn.execute('''
        INSERT INTO pembayaran (nim, tanggal_bayar, jumlah, status)
        VALUES (?, ?, ?, 'lunas')
    ''', (nim, datetime.now().date(), jumlah))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success', 
        'message': f'Pembayaran SPP sebesar Rp {jumlah:,} berhasil!'
    })

@app.route('/api/aktivasi/<nim>', methods=['POST'])
def aktivasi_mahasiswa(nim):
    """API untuk aktivasi administrasi oleh dosen"""
    conn = get_db()
    
    # Update status jadi active
    conn.execute('''
        UPDATE mahasiswa 
        SET status_administrasi = 'active' 
        WHERE nim = ?
    ''', (nim,))
    
    conn.commit()
    conn.close()
    
    # Generate surat bebas SPP
    filename = generate_surat_bebas(nim)
    
    return jsonify({
        'status': 'success', 
        'message': f'Mahasiswa {nim} berhasil diaktivasi!',
        'surat_url': f'/download-surat/{nim}'
    })

@app.route('/download-surat/<nim>')
def download_surat(nim):
    """Download surat bebas SPP"""
    filename = f"static/surat/surat_bebas_{nim}.txt"
    return send_file(filename, as_attachment=True)

@app.route('/api/laporan')
def generate_laporan():
    """Generate laporan sederhana"""
    conn = get_db()
    
    laporan = conn.execute('''
        SELECT m.nim, m.nama, m.status_administrasi, 
               p.tanggal_bayar, p.jumlah, p.status as status_bayar
        FROM mahasiswa m
        LEFT JOIN pembayaran p ON m.nim = p.nim
        ORDER BY m.nim
    ''').fetchall()
    
    conn.close()
    
    # Format laporan
    laporan_data = []
    for row in laporan:
        laporan_data.append(dict(row))
    
    return jsonify(laporan_data)

if __name__ == '__main__':
    # Pastikan database sudah setup
    if not os.path.exists('spp.db'):
        print("⚠️  Database belum ada, jalankan: python database.py")
        exit()
    
    print("🚀 Server berjalan di: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)