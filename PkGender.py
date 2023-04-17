#!/usr/bin/env python3

"""Python script to change gender and name (+other trainer data) in gen IV games (currently only HGSS supported)."""

# sanity check: verify current checksum to make sure all addresses are ok
# when changing name, careful with max size, allowed characters, terminator and trailing characters (fill with 00 after the terminator)

from typing import Tuple
import argparse
from fastcrc.crc16 import ibm_3740
from collections import namedtuple
from enum import Enum
import os.path
from shutil import copy2
import uuid
import string
import logging
import sys

PROGRAM_NAME = 'PkGender'
PROGRAM_VERSION = "v0.9 (zoopoide)" # v1 will be zoopinho
small_block_1_start = 0x00000
small_block_2_start = 0x40000
trainer_name_size = 0x10

class TargetGame (Enum):
    HGSS = "HGSS"
    DP = "DP"
    Pt = "Pt"

# footer start offsets
footer_offset_dict = {
    TargetGame.HGSS: 0xF618,
    TargetGame.DP: 0xC0EC,
    TargetGame.Pt: 0xCF18
}
footer_size_dict = {
    TargetGame.HGSS: 0x10,
    TargetGame.DP: 0x14, # TODO: check if this is correct
    TargetGame.Pt: 0x14
}
# start offsets for several trainer properties
prop_offset_dict = {
    "gender": {
        TargetGame.HGSS: 0x7c,
        TargetGame.DP: 0x7c,
        TargetGame.Pt: 0x80
    },
    "name": {
        TargetGame.HGSS: 0x64,
        TargetGame.DP: 0x64,
        TargetGame.Pt: 0x68
    }
}

# create a named tuple type to increase readability of the argument list
ChangeList = namedtuple("ChangeList", ["gender", "name"])

def setup_logging (debug : bool):
    if debug: # debug #read this from an argument
        log_level = logging.DEBUG 
    else:
        log_level = logging.INFO

    log_format = "[{levelname}] - {message}"
    logging.basicConfig(level=log_level, format=log_format, style='{')

def parse_arguments():
    """Parse command-line arguments using the argparse library.
    This also sets up logging."""
    version_string = PROGRAM_NAME + " " + PROGRAM_VERSION + " -- Copyright (c) abeRC"
    parser = argparse.ArgumentParser(
                    description='A Python script to change trainer data (name, gender, etc.)\n'+
                                'in gen IV Pokémon games (Diamond, Pearl, Platinum, HeartGold, SoulSilver).',
                    epilog=version_string,
                    formatter_class=argparse.RawTextHelpFormatter) # print help for name in a prettier way
    parser.add_argument('savefile', help="path to save file") # positional argument
    
    parser.add_argument('--name', help="change trainer's name to specified string\n (limit of 7 characters)") # takes a value
    parser.add_argument('--gender', action='store_true', help="swap trainer's gender") # on/off flag

    parser.add_argument('--verify-only','--dry-run', action='store_true', 
                        help='do not edit save file\n (only verify checksum)') # on/off flag
    parser.add_argument('--debug','-d', action='store_true', help='enable debug messages') # on/off flag
    parser.add_argument('--version','-v', action='version', 
                        version=version_string, help='print version information')

    args = parser.parse_args()
    setup_logging(args.debug)
    logging.debug(f"args: {args}")

    return args

def verify_soundness (save_path : str, to_change : ChangeList):
    """Verify if command-line arguments are appropriate."""

    # check if save file looks ok
    if not os.path.isfile(save_path):
        raise Exception(f"Not a valid file: {save_path}")
    if not save_path.lower().endswith(".sav"):
        logging.warn("Save file does not have the .sav extension.")
    
    # if not None, verify if name is <= 7 characters and alphanumeric
    trainer_name = to_change.name
    if trainer_name:
        if len(trainer_name) >= 8:
            raise ValueError("Trainer name must have 7 or less characters.")
        alpha_num = set(string.digits+string.ascii_letters)
        if set(trainer_name).difference(alpha_num): # if trainer_name has characters not in alpha_num
            raise ValueError("Trainer name may only contain alphanumeric characters currently.")


def read_save (save_path : str) -> bytes:
    with open(save_path, "rb") as f:
        data_all = f.read()
    return data_all

def find_small_blocks (data_all : bytes, target_game : TargetGame):
    footer_offset, _ = footer_offset_dict[target_game], footer_size_dict[target_game]
    small_block_1 = data_all[small_block_1_start : small_block_1_start+footer_offset]
    small_block_2 = data_all[small_block_2_start : small_block_2_start+footer_offset]
    return (small_block_1, small_block_2)

def calculate_checksum (small_block : bytes) -> bytes:
    """Given a small block (excluding footer), calculate its (little-endian) checksum."""
    # NOTE: gen IV games use a CRC-16 checksum with the following configuration:
    # poly: 0x1021, init: 0xffff, xorout: 0x0000, refin: False, refout: False
    # (This is the configuration used by ibm_3740.)
    # Also, the footer is excluded from the calculation.

    chk = ibm_3740(small_block)
    # convert chk to hexadecimal and invert the bytes (little-endian format)
    chk_bytes = bytes.fromhex(f"{chk:04x}")[::-1] 
    return chk_bytes

def determine_target_game (data_all : bytes) -> TargetGame:
    """Attempts to verify small-block-checksums using offsets for all possible target games,
    returning the correct target game on success. 
    This helps ensure everything is in order."""

    for target_game in TargetGame:
        logging.info(f"Checking if target game is <{target_game}> ...")
        
        # calculate checksums from data assuming target game
        small_block_1, small_block_2 = find_small_blocks(data_all, target_game)
        logging.debug("  small block 1 (original, calculated)")
        chk1_calculated = calculate_checksum(small_block_1)
        logging.debug(f"  checksum: {chk1_calculated.hex().upper()}")
        logging.debug("  small block 2 (original, calculated)")
        chk2_calculated = calculate_checksum(small_block_2)
        logging.debug(f"  checksum: {chk2_calculated.hex().upper()}")

        # calculate offsets and read (possibly) checksums from the data
        footer_offset, footer_size = footer_offset_dict[target_game], footer_size_dict[target_game]
        logging.debug("  small block 1 (original, read)")
        chk1_read = data_all[footer_offset + footer_size - 2 : footer_offset + footer_size]
        logging.debug(f"  checksum: {chk1_read.hex().upper()}")
        logging.debug("  small block 2 (original, read)")
        chk2_read = data_all[small_block_2_start + footer_offset + footer_size - 2 : 
                                small_block_2_start + footer_offset + footer_size]
        logging.debug(f"  checksum: {chk2_read.hex().upper()}")

        # sanity check
        comp1 = (chk1_calculated == chk1_read) 
        comp2 = (chk2_calculated == chk2_read)
        if (comp1 and not comp2) or (comp2 and not comp1):
            wrong_comp = "2nd" if (comp1 and not comp2) else "1st"
            # NOTE: not sure if it's possible for one of the checksums to be wrong?
            logging.warn(f"Checksum for the {wrong_comp} small block is incorrect but the other one is fine.")
        elif (comp1 and comp2):
            break
    else:
        raise Exception("Could not determine target game.")
    
    logging.info(f"Target game is {target_game.value} !")
    return target_game

def translate_name (trainer_name : str) -> bytearray:
    """Given a trainer name string, returns the corresponding internal representation used in the game."""
    
    if not trainer_name.isalnum(): # TODO: implement this
        raise NotImplementedError("Only alphanumeric values are accepted at this moment")

    barray = bytearray(trainer_name_size) # 16 bytes filled with zeroes
    for (i,c) in enumerate(trainer_name):
        if c in string.digits:
            chr_distance = ord(c) - ord('0')
            chr_start = 0x21 # '0'
        elif c in string.ascii_uppercase:
            chr_distance = ord(c) - ord('A')
            chr_start = 0x2b # 'A'
        elif c in string.ascii_lowercase:
            chr_distance = ord(c) - ord('a')
            chr_start = 0x45 # 'a'
        new_c = bytes([chr_start + chr_distance, 0x01])
        barray[2*i : 2*i+2] = new_c
    i += 1
    barray[2*i : 2*i+2] = bytes([0xff, 0xff]) # terminator
    beauty = lambda barr: barr.hex().upper().replace("01", "01 ").replace("FFFF", "FFFF ").replace("0000", "0000 ")
    logging.debug(f"Internal representation of name is: {beauty(barray)}")

    return barray

def edit_single_prop (edited_data : bytearray, target_game : TargetGame, prop : str, new_value):
    """Edits property prop in bytearray edited_data according to new_value."""
    
    # calculate property offset and edit data for both blocks
    offset = prop_offset_dict[prop][target_game]
    if prop == "gender":
        edited_data[offset] = 0x01 ^ edited_data[offset] # flip last bit
        edited_data[small_block_2_start + offset] = 0x01 ^ edited_data[small_block_2_start + offset]
    elif prop == "name":
        name_bytes = translate_name(new_value)
        edited_data[offset : offset + trainer_name_size] = name_bytes
        edited_data[small_block_2_start + offset : 
                    small_block_2_start + offset + trainer_name_size] = name_bytes

def edit_save (data_all : bytes, target_game : TargetGame, to_change : ChangeList, save_path : str):
    """Performs the changes specified in to_change to the save file at save_path.
    This assumes the target_game is correct and data_all contains the save file data.
    Note: before editing the save file, a backup (with a unique file name) will be created."""
    
    logging.info(f"Creating a backup of {save_path} ...")

    # get useful absolute paths
    save_path_abs = os.path.abspath(save_path)
    dir_path = os.path.dirname(os.path.abspath(save_path))

    # get extension
    if "." in save_path:
        save_name, ext = save_path.rsplit(".")
    else:
        save_name, ext = save_path, ""

    # create a unique file name
    bunch_of_characters = uuid.uuid4().hex
    save_path_bak_abs_path = os.path.join(dir_path, 
                                    save_name + "__bak_" + bunch_of_characters + "." + ext)
    # actually create a backup
    copy2(save_path_abs, save_path_bak_abs_path)
    logging.info(f"Backup created at {save_path_bak_abs_path}\nPlease revert to this backup if you have any issues.")
    
    # perform the changes requested
    edited_data = bytearray(data_all) # editable bytes
    for (prop, new_value) in to_change._asdict().items():
        # only change something if new_value is truthy
        if new_value:
            logging.info(f"Changing trainer's {prop}" 
                            + (f" to {new_value} ..." if (type(new_value) != bool) else ""))
            edit_single_prop(edited_data, target_game, prop, new_value)

    # calculate the checksums
    small_block_1, small_block_2 = find_small_blocks(bytes(edited_data), target_game)
    logging.debug("  small block 1 (edited)")
    chk1 = calculate_checksum(small_block_1)
    logging.debug(f"  checksum: {chk1.hex().upper()}")
    logging.debug("  small block 2 (edited)")
    chk2 = calculate_checksum(small_block_2)
    logging.debug(f"  checksum: {chk2.hex().upper()}")

    # edit the checksums
    footer_offset, footer_size = footer_offset_dict[target_game], footer_size_dict[target_game]
    edited_data[footer_offset + footer_size - 2 : footer_offset + footer_size] = chk1
    edited_data[small_block_2_start + footer_offset + footer_size - 2 : 
                small_block_2_start + footer_offset + footer_size] = chk2
    
    # write into the save file
    with open(save_path, "wb") as f:
        f.write(edited_data)

def main ():
    # parse arguments
    args = parse_arguments()
    save_path = args.savefile
    to_change = ChangeList(gender=args.gender, name=args.name)
    verify_soundness(save_path, to_change)

    # read save, determine game, edit save file (unless --verify-only is set)
    data_all = read_save(save_path)
    target_game = determine_target_game(data_all)
    if not args.verify_only:
        edit_save(data_all, target_game, to_change, save_path)
    logging.info("Done!")

if __name__ == "__main__":
    main()
