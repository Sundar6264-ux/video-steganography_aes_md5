# 🔐 Video Steganography with AES & MD5
> **Project timeline:** Initially built in **May 2024**; this README,Codebase updated **September 2025**.


Hide encrypted text **inside video frames** using **AES‑256‑GCM** and validate integrity with **MD5 checksums**.  
The encoder embeds ciphertext into select frames via **LSB steganography** and rebuilds a playable video (audio preserved).  

The decoder extracts, verifies, and reconstructs the original plaintext.

---

## 📂 Project Structure
```
├───src/
├   ├── aes_utils.py            # AES‑256‑GCM encryption/decryption helpers
├   ├── md5_utils.py            # MD5 checksum generation & verification
├   ├── encode.py               # Encoder: hides encrypted messages inside video frames
├   ├── decode.py               # Decoder: extracts and decrypts hidden messages
├
├── requirements.txt        # Python dependencies
└── README.md
```

[Paper Pdf](https://drive.google.com/file/d/1PMvY5raevR0bQhm9SWLN9nNHKOVoDWsT/view?usp=share_link)

📦 **Media files (not in repo):** download from this Drive folder and place them in the repo root:
- Carrier video: `DustBunnyTrailer.mp4`
- Optional still image for frame indices: `Hiddn.webp`
- (Outputs will be created locally): `video.mov`, `image-enc.png`

[Download media](https://drive.google.com/drive/folders/14fXWpIY3sSY_ugPZB3izdRYuehcSRkWs?usp=share_link)

> **Note:** The filename `Hiddn.webp` is just a placeholder. You can use any still image if you choose the “store indices in image” option.

---

## ⚡ Features

- 🔒 **AES‑256‑GCM** symmetric encryption for confidentiality and authenticity (via GCM tag).
- 🧮 **MD5 checksum** computed over plaintext for an extra integrity snapshot.
- 🧬 **LSB steganography** embeds encrypted chunks into selected video frames.
- 🖼️ Optional: store **frame indices** in a still image.
- 🎵 **Original audio preserved** when rebuilding the stego video.
- ✅ Decoder **verifies checksum** and restores plaintext on success.

---

## 🛠 Requirements

- **Python** 3.8+
- **FFmpeg** available on your system `PATH`
- Python packages (install via `requirements.txt`):
  - `opencv-python`
  - `stegano`
  - `pycryptodome`
  - `pillow`
  - `termcolor`
  - `pyfiglet`

Create and activate a virtual environment (recommended), then install deps:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

A sample `requirements.txt` (if you need one):

```
opencv-python
stegano
pycryptodome
pillow
termcolor
pyfiglet
```

---

## 🚀 Usage

### 1️⃣ Encode a message
Run the encoder and follow prompts:

```bash
python encode.py
```
- Enter the text you want to hide.
- Provide frame indices when asked (e.g. `2 3 4 ... 89`).
- Choose whether to store frame numbers in a still image.
- On success:
  - A new `video.mov` is created with the hidden message.
  - If chosen, frame numbers are saved in `image-enc.png`.

### 2️⃣ Decode a message
Run the decoder and follow prompts:

```bash
python decode.py
```
- Provide the path to the stego video (e.g. `video.mov`).
- Choose how to supply frame indices:
  - manually,
  - from the still image (e.g. `image-enc.png`),
  - or scan all frames.
- The hidden message is revealed after integrity verification.

---

## 🎯 Example (Interactive)

**Encoding**
```
Enter text to hide inside image.
Enter Text : Hello World
```

**Decoding (sample output)**
```
[MD5 verified ✓]
Decoded Message: Hello World
```

---

## 🧩 How It Works (High Level)

1. **Plaintext → Ciphertext**: `aes_utils.py` encrypts input using AES‑256‑GCM (random nonce per run).  
2. **Integrity Snapshot**: `md5_utils.py` computes MD5 over the plaintext for a lightweight check.  
3. **Embedding**: `encode.py` splits ciphertext and embeds bits into specified video frames via LSB.  
4. **Muxing**: frames are reassembled into `video.mov` while preserving original audio (via FFmpeg).  
5. **Extraction**: `decode.py` reads frames, collects embedded bits, and reconstructs ciphertext.  
6. **Decryption + Verify**: decrypt via AES‑GCM, compare plaintext MD5 with stored MD5, print message.

---

## ⚖️ Security Notes (Read Before Use)

- **GCM already provides integrity/authenticity.** MD5 here is an *additional* lightweight check and **not** a substitute for cryptographic authenticity.  
- **MD5 is not collision‑resistant.** Do **not** use MD5 for security decisions in adversarial settings; rely on AES‑GCM’s auth tag.  
- **Operational security matters.** Steganography can be detected with advanced analysis. Treat this as an educational/demo tool.

---

## 🧪 Troubleshooting

- **FFmpeg not found**: Ensure `ffmpeg` is installed and on your `PATH` (e.g., `ffmpeg -version` prints a version).  
- **Codec/format errors**: Convert your carrier video to a standard codec (e.g., H.264 MP4) before encoding.  
- **Out-of-range indices**: Make sure frame indices exist in the chosen video.  
- **Decode fails / MD5 mismatch**: Wrong frame indices, damaged video, or wrong key/nonce can cause failures.

---

## 📜 License

Add your preferred license (e.g., MIT, Apache‑2.0) here.

---

## 🙏 Acknowledgments

- OpenCV for video handling
- Stegano for steganographic primitives
- PyCryptodome for AES‑GCM
- FFmpeg for muxing

---

## 📣 Disclaimer

This repository is for **educational and research** purposes. Ensure you have legal rights to any media you process and comply with local laws and institutional policies.
