// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MSDSValidator {
    struct MSDSInfo {
        address issuer;       // Siapa yang upload (Produsen)
        bytes32 fileHash;     // Hash SHA-256 dari PDF MSDS
        string status;        // "ACTIVE" atau "REVOKED"
        uint256 timestamp;    // Waktu registrasi
        bool exists;          // Penanda keberadaan
    }

    mapping(string => MSDSInfo) public msdsRecords;
    string[] public msdsIdList; // List semua ID yang terdaftar

    // Event untuk notifikasi
    event MSDSRegistered(string msdsId, address issuer, bytes32 fileHash);
    event MSDSVerified(string msdsId, bool isValid);
    event MSDSRevoked(string msdsId, address revoker);

    // 1. Register MSDS Baru
    function registerMSDS(string memory _msdsId, bytes32 _fileHash) public {
        require(!msdsRecords[_msdsId].exists, "MSDS ID sudah ada!");
        
        msdsRecords[_msdsId] = MSDSInfo({
            issuer: msg.sender,
            fileHash: _fileHash,
            status: "ACTIVE",
            timestamp: block.timestamp,
            exists: true
        });
        
        msdsIdList.push(_msdsId);
        emit MSDSRegistered(_msdsId, msg.sender, _fileHash);
    }

     // 2. Verifikasi MSDS (Read Only)
    function verifyMSDS(string memory _msdsId, bytes32 _uploadedHash) public view returns (bool isValid, string memory status, address issuer) {
        MSDSInfo memory doc = msdsRecords[_msdsId];
        require(doc.exists, "MSDS ID tidak ditemukan!");
        
        // ✅ FIX: Bandingkan hash string, bukan string langsung
        bool isActive = keccak256(abi.encodePacked(doc.status)) == keccak256(abi.encodePacked("ACTIVE"));
        isValid = (doc.fileHash == _uploadedHash) && isActive;
        
        return (isValid, doc.status, doc.issuer);
    }

    // 3. Revoke MSDS (Cabut jika ada bahaya)
    function revokeMSDS(string memory _msdsId) public {
        MSDSInfo storage doc = msdsRecords[_msdsId];
        require(doc.exists, "MSDS ID tidak ditemukan!");
        require(doc.issuer == msg.sender, "Hanya pemilik yang bisa mencabut!");
        
        doc.status = "REVOKED";
        emit MSDSRevoked(_msdsId, msg.sender);
    }
}