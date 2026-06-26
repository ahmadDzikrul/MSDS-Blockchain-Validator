import hashlib
import ecdsa
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

def blockchain_signature_simulation():
    print("="*60)
    print("SIMULASI DIGITAL SIGNATURE (Langkah 3 & 7)")
    print("="*60)

    # 📝 Data Transaksi Awal
    tx_data = "Alice->Bob:10ETH"
    
    # ==========================================
    # LANGKAH 2: HASHING (Persiapan)
    # ==========================================
    tx_hash = hashlib.sha256(tx_data.encode('utf-8')).digest()
    print(f"\n🔹 1. Hash Transaksi (SHA-256)       : {tx_hash.hex()}")

    # ==========================================
    # LANGKAH 3: SIGNING (Pembuatan Signature)
    # ==========================================
    # Generate pasangan kunci untuk Alice (secp256k1 = standar Bitcoin/Ethereum)
    alice_priv_key = SigningKey.generate(curve=SECP256k1)
    alice_pub_key  = alice_priv_key.get_verifying_key()
    
    # Tanda tangani HASH transaksi menggunakan Private Key
    # sign_digest() digunakan karena kita sudah melakukan hashing manual
    signature = alice_priv_key.sign_digest(tx_hash)
    print(f"🔹 2. Digital Signature (σ)          : {signature.hex()}")
    print(f"   🔑 Public Key Alice (dibroadcast) : {alice_pub_key.to_string().hex()[:32]}...")

    # ==========================================
    # LANGKAH 6: RE-HASHING DI NODE
    # ==========================================
    # Node menerima tx_data mentah dan menghitung hash secara independen
    node_hash = hashlib.sha256(tx_data.encode('utf-8')).digest()

    # ==========================================
    # LANGKAH 7: VERIFICATION (Validasi oleh Node)
    # ==========================================
    print("\n" + "-"*60)
    print("🛡️ PROSES VALIDASI OLEH NODE")
    print("-"*60)
    
    # ✅ Skenario 1: Data TIDAK diubah (Valid)
    try:
        is_valid = alice_pub_key.verify_digest(signature, node_hash)
        print(f"✅ Verifikasi (Data Asli)          : {is_valid} → Transaksi DITERIMA")
    except BadSignatureError:
        print(f"❌ Verifikasi (Data Asli)          : False → Transaksi DITOLAK")

    # ❌ Skenario 2: Data DIUBAH oleh peretas di transit
    tampered_tx = "Alice->Bob:100ETH"  # Peretas menambah jumlah
    tampered_hash = hashlib.sha256(tampered_tx.encode('utf-8')).digest()
    
    try:
        is_valid_tampered = alice_pub_key.verify_digest(signature, tampered_hash)
        print(f"✅ Verifikasi (Data Dimodifikasi)  : {is_valid_tampered}")
    except BadSignatureError:
        print(f"❌ Verifikasi (Data Dimodifikasi)  : False → Transaksi DITOLAK")
        
    print("\n📌 Kesimpulan: Signature hanya valid jika Hash yang dihitung Node \n   MATCH persis dengan Hash yang ditandatangani oleh Pengirim.")

if __name__ == "__main__":
    blockchain_signature_simulation()