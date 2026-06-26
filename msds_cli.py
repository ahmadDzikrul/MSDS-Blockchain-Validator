# msds_cli.py - MSDS Validator CLI untuk Sepolia Testnet
from web3 import Web3
from dotenv import load_dotenv
import os
import hashlib
import argparse
import sys

# ================= KONFIGURASI =================
# Load environment variables dari .env
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
# ⚠️ GANTI DENGAN ALAMAT KONTRAK YANG SUDAH DI-DEPLOY!
CONTRACT_ADDRESS = "0x8E9911D237fdC0FCE73506Bfe9C1dF24eF63de7A"

# RPC Sepolia (publik, stabil)
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

# ABI Minimal untuk interaksi dengan kontrak MSDSValidator
ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_msdsId", "type": "string"},
            {"internalType": "bytes32", "name": "_fileHash", "type": "bytes32"}
        ],
        "name": "registerMSDS",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_msdsId", "type": "string"},
            {"internalType": "bytes32", "name": "_uploadedHash", "type": "bytes32"}
        ],
        "name": "verifyMSDS",
        "outputs": [
            {"internalType": "bool", "name": "isValid", "type": "bool"},
            {"internalType": "string", "name": "status", "type": "string"},
            {"internalType": "address", "name": "issuer", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_msdsId", "type": "string"}
        ],
        "name": "revokeMSDS",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "", "type": "string"}
        ],
        "name": "msdsRecords",
        "outputs": [
            {"internalType": "address", "name": "issuer", "type": "address"},
            {"internalType": "bytes32", "name": "fileHash", "type": "bytes32"},
            {"internalType": "string", "name": "status", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ================= INISIALISASI =================
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    print("❌ Gagal terhubung ke Sepolia! Cek koneksi internet atau RPC URL.")
    sys.exit(1)

print("✅ Terhubung ke Sepolia Testnet")

# Setup akun dari private key
try:
    account = web3.eth.account.from_key(PRIVATE_KEY)
except Exception as e:
    print(f"❌ Private key tidak valid: {e}")
    sys.exit(1)

print(f"👛 Wallet: {account.address}")

# Setup kontrak
contract = web3.eth.contract(
    address=web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)

# ================= FUNGSI BANTUAN =================

def calculate_file_hash(filepath):
    """Hitung SHA-256 hash dari file (untuk integritas dokumen)"""
    if not os.path.exists(filepath):
        print(f"❌ File tidak ditemukan: {filepath}")
        sys.exit(1)
    
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Baca per chunk untuk file besar
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    
    # Kembalikan sebagai bytes32 (format yang diterima Solidity)
    return sha256.digest()

def wait_for_receipt(tx_hash, timeout=120):
    """Tunggu transaksi dikonfirmasi"""
    print("⏳ Menunggu konfirmasi block...")
    try:
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return receipt
    except Exception as e:
        print(f"⚠️ Timeout atau error: {e}")
        print("💡 Cek TX Hash di Etherscan: https://sepolia.etherscan.io/tx/" + tx_hash.hex())
        return None

# ================= FITUR CLI =================

def register_msds(msds_id, filepath):
    """Register MSDS baru ke blockchain"""
    print(f"\n📝 Register MSDS")
    print(f"   ID: {msds_id}")
    print(f"   File: {filepath}")
    
    # Hitung hash file
    file_hash = calculate_file_hash(filepath)
    print(f"   🔐 Hash: {file_hash.hex()}")
    
    # Bangun transaksi
    print("   📤 Membangun transaksi...")
    nonce = web3.eth.get_transaction_count(account.address)
    gas_price = web3.eth.gas_price
    
    tx = contract.functions.registerMSDS(msds_id, file_hash).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': gas_price,
        'chainId': 11155111
    })
    
    # Sign & kirim
    print("   ✍️  Menandatangani transaksi...")
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"   🚀 TX Hash: {tx_hash.hex()}")
    
    # Tunggu konfirmasi
    receipt = wait_for_receipt(tx_hash)
    if receipt and receipt['status'] == 1:
        print(f"\n✅ SUKSES! MSDS terdaftar di blockchain")
        print(f"   🔗 Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
        print(f"   📦 Block: {receipt['blockNumber']}")
    else:
        print("\n❌ Transaksi gagal atau timeout")

def verify_msds(msds_id, filepath):
    """Verifikasi keaslian MSDS"""
    print(f"\n🔍 Verifikasi MSDS")
    print(f"   ID: {msds_id}")
    print(f"   File: {filepath}")
    
    # Hitung hash file lokal
    local_hash = calculate_file_hash(filepath)
    print(f"   🔐 Hash lokal: {local_hash.hex()}")
    
    # Query ke blockchain (view function, tidak butuh gas)
    print("   📡 Query ke blockchain...")
    try:
        is_valid, status, issuer = contract.functions.verifyMSDS(msds_id, local_hash).call()
        
        print("\n" + "="*50)
        if is_valid:
            print("✅ HASIL: AUTENTIK & VALID")
        else:
            print("❌ HASIL: TIDAK VALID")
        
        print(f"   📌 Status on-chain: {status}")
        print(f"   👤 Issuer: {issuer}")
        print(f"   🔗 Contract: {CONTRACT_ADDRESS}")
        print("="*50)
        
        if not is_valid and status == "ACTIVE":
            print("\n⚠️  Kemungkinan:")
            print("   • File telah dimodifikasi (hash tidak cocok)")
            print("   • MSDS ID salah atau tidak terdaftar")
            
    except Exception as e:
        print(f"\n❌ Error saat query: {e}")
        if "not found" in str(e).lower():
            print("💡 MSDS ID mungkin belum terdaftar di blockchain")

def revoke_msds(msds_id):
    """Revoke MSDS (hanya oleh issuer)"""
    print(f"\n🚨 Revoke MSDS")
    print(f"   ID: {msds_id}")
    
    print("   📤 Membangun transaksi...")
    nonce = web3.eth.get_transaction_count(account.address)
    gas_price = web3.eth.gas_price
    
    tx = contract.functions.revokeMSDS(msds_id).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': gas_price,
        'chainId': 11155111
    })
    
    print("   ✍️  Menandatangani...")
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"   🚀 TX Hash: {tx_hash.hex()}")
    
    receipt = wait_for_receipt(tx_hash)
    if receipt and receipt['status'] == 1:
        print(f"\n✅ MSDS berhasil direvoke!")
        print(f"   🔗 Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
    else:
        print("\n❌ Revoke gagal atau timeout")

# ================= ENTRY POINT =================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🧪 MSDS Blockchain Validator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python msds_cli.py register --id MSDS-001 --file docs/acetone.pdf
  python msds_cli.py verify  --id MSDS-001 --file docs/acetone.pdf
  python msds_cli.py revoke  --id MSDS-001
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Perintah tersedia")
    
    # Parser: register
    p_reg = subparsers.add_parser("register", help="Daftar MSDS baru ke blockchain")
    p_reg.add_argument("--id", required=True, help="ID unik MSDS (contoh: MSDS-ACETONE-001)")
    p_reg.add_argument("--file", required=True, help="Path file PDF/TXT MSDS")
    
    # Parser: verify
    p_ver = subparsers.add_parser("verify", help="Verifikasi keaslian MSDS")
    p_ver.add_argument("--id", required=True, help="ID unik MSDS")
    p_ver.add_argument("--file", required=True, help="Path file yang ingin divalidasi")
    
    # Parser: revoke
    p_rev = subparsers.add_parser("revoke", help="Cabut MSDS (hanya issuer)")
    p_rev.add_argument("--id", required=True, help="ID unik MSDS")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
    elif args.command == "register":
        register_msds(args.id, args.file)
    elif args.command == "verify":
        verify_msds(args.id, args.file)
    elif args.command == "revoke":
        revoke_msds(args.id)