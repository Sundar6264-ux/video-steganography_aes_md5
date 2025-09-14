from stegano import lsb
import cv2
import math
import os
import shutil
from subprocess import call,STDOUT
import aes_utils
import sys
from termcolor import cprint
from pyfiglet import figlet_format
import base64
import PIL.Image as PILImage
import hashlib
import md5_utils


# Used to split string into parts.
def split_string(s_str,count=100):
    per_c=math.ceil(len(s_str)/count)
    c_cout=0
    out_str=''
    split_list=[]
    for s in s_str:
        out_str+=s
        c_cout+=1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str=''
            c_cout=0
    if c_cout!=0:
        split_list.append(out_str)
    return split_list

# Used to count frames in Video
def countFrames():
    f_name = '/Users/somasundar/PycharmProjects/Python_Enc_Dec/venv/DustBunnyTrailer.mp4'
    cap = cv2.VideoCapture(f_name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cprint(f"Total frame in video are : {length-1}",'blue')
    return length

# Extract the frames
def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder="./tmp"
    cprint("[INFO] tmp directory is created",'green')
    vidcap = cv2.VideoCapture(video)
    count = 0
    cprint("[INFO] Extracting frames from video \n Please be patient",'blue')
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1
    cprint("[INFO] All frames are extracted from video",'green')

# Encrypt and encode text into frames
def encode_string(input_string, root="./tmp/"):
    #input_string = base64.b64encode(input_string.encode('utf-8'))
    input_string = input_string.encode('utf-8')

    cprint(
        "256 Bit AES Encrypted {Asymmetric Encryption} ",'blue')
    res = input_string
    input_string = AES_Utils.encrypt_AES_256(res)

    print(f"\n AES Encypted message: {input_string}")
    split_string_list = split_string(input_string)
    print(split_string_list)
    split_string_length = len(split_string_list)

    FRAMES = list(map(int, input(f"Enter {split_string_length} FRAME NUMBERS seperated by space : ").split()))

    frame_choice = int(input("1) Do you want to store frame numbers in an image /n 2) No! Don't store : "))
    if frame_choice == 1:
        ENCODE_IMAGE = input("Enter image name with extension : ")
        res = str(FRAMES)
        res = res.encode('utf-8')
        FRAMES_ENCODED = AES_Utils.encrypt_AES_256(res)
        secret = lsb.hide(ENCODE_IMAGE, str(FRAMES_ENCODED))
        print(str(FRAMES_ENCODED))
        secret.save("image-enc.png")
        cprint("[Info] Frames numbers are hidden inside the image with filename image-enc.png", 'red')
    else:
        cprint("[Info] Frame numbers are not stored anywhere. Please remember them.", 'red')

    for i in range(0, len(FRAMES)):
        f_name = "{}{}.png".format(root, FRAMES[i])
        secret_enc = lsb.hide(f_name, split_string_list[i])
        secret_enc.save(f_name)
        cprint("[INFO] Frame {} holds {}".format(FRAMES[i], split_string_list[i]), 'blue')

# delete temporary files
def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")

def main():
    f_name = '/Users/somasundar/Desktop/marvelteaser.mp4'
    TEXT_TO_ENCODE1 = input("Enter text to hide inside image. \n Enter Text : ")
    Original_Checksum = MD5_Utils.md5_checksum(TEXT_TO_ENCODE1)
    TEXT_TO_ENCODE = Original_Checksum + TEXT_TO_ENCODE1
    #print(len(TEXT_TO_ENCODE))
    #print(len(TEXT_TO_ENCODE1))
    #print(TEXT_TO_ENCODE)
    #print(TEXT_TO_ENCODE1)
    print(Original_Checksum)
    countFrames()
    frame_extraction(f_name)
    encode_string(TEXT_TO_ENCODE)
    # Mix images into video and add audio.
    call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    cprint("Video is succesfully encoded with encrypted text.",'green')
    clean_tmp()


if __name__ == "__main__":
    if 'TERM' not in os.environ:
        #print("sjf")
        # Set TERM to a default value, such as 'xterm'
        os.environ['TERM'] = 'xterm'
    os.system('cls' if os.name == 'nt' else 'clear')
    cprint(figlet_format('SOMA', font='slant'),'yellow', attrs=['bold'])
    cprint(figlet_format('AES & RSA encrypted Video Steganography Encoder', font='digital'),'green', attrs=['bold'])
    main()