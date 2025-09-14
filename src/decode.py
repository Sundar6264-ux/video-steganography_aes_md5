"""
Decode.py — Interactive decoder for the Video Steganography pipeline.

Mirrors your encoder exactly:
- Ciphertext chunks inside frames are Base64 strings produced by AES_Utils.encrypt_AES_256(bytes).
- Frame indices optionally stored in a still image are also Base64 strings (encrypted the same way).
- After decryption, the plaintext starts with a 32-hex MD5 of the original message, followed by the message itself.

This script:
1) Prompts for the stego video path.
2) Lets you choose how to get frame indices:
   - Reveal encrypted frame list from a still image (and decrypt via AES_Utils),
   - Manually enter frame numbers/ranges,
   - Or scan all frames.
3) Extracts those frames, reveals Base64 chunks, concatenates them.
4) Decrypts using AES_Utils.decrypt_AES_256 (same key/iv as encoder).
5) Verifies the 32-char MD5 prefix with MD5_Utils.md5_checksum(body); if OK, strips it.
6) Prints the result and can save it to a file.
"""

import os
import tempfile
import base64
import ast
from typing import List, Optional, Tuple

import cv2
from stegano import lsb
from PIL import Image

import aes_utils        # use same helpers as the encoder
import md5_utils        # same checksum function as the encoder


# ------------------------------ Helper funcs --------------------------------

def parse_frames_spec(spec: str) -> List[int]:
    """
    Parse frames like '1,4,6-9,12' into a sorted unique list of ints.
    Also accepts a single range like '1-48'.
    """
    spec = spec.strip()
    frames = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a), int(b)
            if a <= b:
                frames.update(range(a, b + 1))
            else:
                frames.update(range(b, a + 1))
        else:
            frames.add(int(part))
    return sorted(frames)


def extract_frames(video_path: str, frame_indices: Optional[List[int]] = None) -> List[Tuple[int, str]]:
    """
    Extract frames to temp PNG files, return list of (index, path).
    If frame_indices is None, extract all frames (can be slow).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    chosen = set(frame_indices) if frame_indices else set(range(total))

    tmpdir = tempfile.mkdtemp(prefix="frames_")
    out = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx in chosen:
            p = os.path.join(tmpdir, f"frame_{idx:06d}.png")
            cv2.imwrite(p, frame)
            out.append((idx, p))
        idx += 1
    cap.release()

    if not out:
        raise RuntimeError("No frames extracted. Check your frame indices or video path.")
    return out


def reveal_from_image(img_path: str) -> Optional[str]:
    """Reveal hidden text from an image using stegano.lsb (tries path then PIL Image)."""
    try:
        return lsb.reveal(img_path)
    except Exception:
        try:
            im = Image.open(img_path)
            return lsb.reveal(im)
        except Exception:
            return None


def reveal_chunks_from_frames(video_path: str, frames: Optional[List[int]]) -> str:
    """
    Extract images for the specified frames and reveal text chunks.
    Returns the concatenated string (intended to be a single Base64 ciphertext).
    """
    pairs = extract_frames(video_path, frames)
    chunks = []
    for idx, p in pairs:
        msg = reveal_from_image(p)
        if msg:
            chunks.append(msg)
    return "".join(chunks)


def _decrypt_with_aes_utils_flex(cipher_b64_or_bytes):
    """
    Be compatible with BOTH versions of AES_Utils.decrypt_AES_256:
    - Some implementations expect a base64 *string*.
    - Others expect raw *bytes* (and will error if given str).
    This tries both paths safely and always returns *bytes*.
    """
    # Try passing through directly first
    try:
        out = AES_Utils.decrypt_AES_256(cipher_b64_or_bytes)
        if isinstance(out, str):
            return out.encode("utf-8", errors="replace")
        return out  # assume bytes
    except TypeError:
        # If the AES layer rejected str, try base64-decode to bytes and pass bytes in
        try:
            if isinstance(cipher_b64_or_bytes, str):
                cipher_bytes = base64.b64decode(cipher_b64_or_bytes)
            else:
                cipher_bytes = cipher_b64_or_bytes
            out = AES_Utils.decrypt_AES_256(cipher_bytes)
            if isinstance(out, str):
                return out.encode("utf-8", errors="replace")
            return out
        except Exception as e:
            raise RuntimeError(f"Decryption failed (bytes path): {e}")
    except Exception as e:
        # If the direct path failed for another reason, try the bytes path once
        try:
            if isinstance(cipher_b64_or_bytes, str):
                cipher_bytes = base64.b64decode(cipher_b64_or_bytes)
            else:
                cipher_bytes = cipher_b64_or_bytes
            out = AES_Utils.decrypt_AES_256(cipher_bytes)
            if isinstance(out, str):
                return out.encode("utf-8", errors="replace")
            return out
        except Exception as e2:
            raise RuntimeError(f"Decryption failed: {e2}")


def derive_frames_from_still_image(still_image_path: str) -> List[int]:
    """
    Reveal encrypted frame indices from a still image, then decrypt via AES_Utils
    (robust to either string-or-bytes decrypt implementations).
    Encoder stored: str(FRAMES).encode('utf-8') -> AES_Utils.encrypt_AES_256 -> (Base64) -> lsb in image.
    """
    hidden = reveal_from_image(still_image_path)
    if not hidden:
        raise RuntimeError("No hidden data found in still image.")

    try:
        decrypted_bytes = _decrypt_with_aes_utils_flex(hidden)
        recovered = decrypted_bytes.decode("utf-8", errors="replace").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to decrypt frame indices from still image: {e}")

    # Expect something like "[1, 4, 6, 7, 8]". Try literal_eval first; fallback to spec parse.
    try:
        val = ast.literal_eval(recovered)
        if isinstance(val, list) and all(isinstance(x, int) for x in val):
            return val
    except Exception:
        pass

    # Fallback: allow "1-48" style specs
    try:
        return parse_frames_spec(recovered)
    except Exception:
        raise RuntimeError(f"Could not parse frame indices from decrypted text: {recovered!r}")


def verify_md5_from_payload(payload: str) -> Tuple[bool, str]:
    """
    Verify MD5 checksum prefix (first 32 chars) against the message body,
    using the exact same MD5_Utils.md5_checksum as the encoder.

    Returns:
        (ok: bool, body: str)
        ok=True if checksum matches, body=original message without checksum
    """
    if len(payload) < 32:
        return False, payload

    checksum = payload[:32]
    body = payload[32:]

    recomputed = MD5_Utils.md5_checksum(body)
    if recomputed == checksum:
        return True, body
    else:
        return False, body


# ----------------------------------- Main -----------------------------------

def main():
    print("\n=== Video Steganography — Interactive Decoder ===\n")

    # 1) Stego video path
    video_path = input("Enter path to stego video (e.g., video.mov): ").strip()
    if not os.path.exists(video_path):
        print("Error: video file not found.")
        return

    # 2) How to get frame indices
    print("\nHow do you want to get frame indices?")
    print("  1) Reveal from a still image (encrypted frame numbers)")
    print("  2) Enter frame numbers manually (e.g., 1-48 or 1,2,3,...)")
    print("  3) Scan ALL frames (slow)")
    choice = input("Choose 1/2/3: ").strip()

    frames: Optional[List[int]] = None
    if choice == "1":
        still_path = input("Enter path to the still image (e.g., image-enc.png): ").strip()
        if not os.path.exists(still_path):
            print("Error: still image not found.")
            return
        try:
            frames = derive_frames_from_still_image(still_path)
            print(f"Recovered frame indices: {frames}")
        except Exception as e:
            print(f"Failed to derive frames from still image: {e}")
            return

    elif choice == "2":
        spec = input("Enter frames (e.g., 1-48 or 1,2,3,...): ").strip()
        try:
            frames = parse_frames_spec(spec)
        except Exception as e:
            print(f"Invalid frame spec: {e}")
            return

    elif choice == "3":
        frames = None  # scan all
        print("Scanning all frames... (this can be slow)")
    else:
        print("Invalid choice.")
        return

    # 3) Reveal ciphertext chunks from frames (Base64 string)
    try:
        raw_joined = reveal_chunks_from_frames(video_path, frames)
    except Exception as e:
        print(f"Failed to reveal data from frames: {e}")
        return

    if not raw_joined:
        print("No hidden data found in the selected frames.")
        return

    # 4) Decrypt with AES_Utils (robust to either str-or-bytes decrypt implementations)
    try:
        plaintext_bytes = _decrypt_with_aes_utils_flex(raw_joined)  # returns bytes
        plaintext = plaintext_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Decryption failed: {e}")
        return

    # 5) MD5 header verification (exactly symmetric to encoder)
    verified, body = verify_md5_from_payload(plaintext)
    if verified:
        print("[MD5 verified ✓]")
    else:
        print("[MD5 missing or mismatch]")

    # 6) Output
    print("\n--- Decoded Message ---\n")
    print(body)
    print("\n-----------------------\n")

    save = input("Save decoded message to a file? (y/N): ").strip().lower()
    if save == "y":
        out_path = input("Enter output path (e.g., decoded.txt): ").strip()
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(body)
            print(f"Saved to: {out_path}")
        except Exception as e:
            print(f"Failed to save file: {e}")


if __name__ == "__main__":
    main()
