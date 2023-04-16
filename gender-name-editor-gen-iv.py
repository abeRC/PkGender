#!/usr/bin/env python3

"""Python script to change gender and name (+other trainer data) in gen IV games (currently only HGSS supported)."""

# sanity check: verify current checksum to make sure all addresses are ok
# when changing name, careful with max size, allowed characters, terminator and trailing characters (fill with 00 after the terminator)

from fastcrc.crc16 import ibm_3740
from collections import namedtuple
from enum import Enum
import logging

small_block_1_start = 0x00000
small_block_2_start = 0x40000
# footer start offsets
footer_offset_dict = { # might work with StrEnum (py 3.11+)?
    "HGSS": 0xF618,
    "DP": 0xC0EC,
    "Pt": 0xCF18
}
footer_size_dict = {
    "HGSS": 0x10,
    "DP": 0x14,
    "Pt": 0x14
}

class TargetGame (Enum):
    HGSS = "HGSS"
    DP = "DP"
    Pt = "Pt"


def parse_arguments():
    # TODO: implement this

    # create a named tuple type to increase readability of the argument list
    ChangeList = namedtuple("ChangeList", ["gender", "name"])

    #save_path = "POKEMON SS_IPGE01_00.sav"
    save_path = "Pokemon - Pearl Version.SAV"
    to_change = ChangeList(gender=False, name="Zoop")
    return save_path, to_change

def read_save (save_path : str) -> bytes:
    with open(save_path, "rb") as f:
        data_all = f.read()
    return data_all

def get_footer_offset_and_size (target_game : TargetGame):
    return (footer_offset_dict[target_game.value],
            footer_size_dict[target_game.value])

def find_small_blocks (data_all : bytes, target_game : TargetGame):
    footer_offset, _ = get_footer_offset_and_size(target_game)
    small_block_1 = data_all[small_block_1_start : small_block_1_start+footer_offset]
    small_block_2 = data_all[small_block_2_start : small_block_2_start+footer_offset]
    return (small_block_1, small_block_2)

def calculate_checksum (small_block : bytes):
    # NOTE: gen IV games use a CRC-16 checksum with the following configuration:
    # poly: 0x1021, init: 0xffff, xorout: 0x0000, refin: False, refout: False
    # (This is the configuration used by ibm_3740.)
    # Also, the footer is excluded from the calculation.

    chk = ibm_3740(small_block)
    # convert chk to hexadecimal and invert the bytes (little-endian format)
    chk_bytes = bytes.fromhex(f"{chk:04x}")[::-1] 
    return chk_bytes

def determine_target_game (data_all) -> TargetGame:
    """Attempts to verify small-block-checksums using offsets for all possible target games,
    returning the correct target game on success. 
    This helps ensure everything is in order."""

    for target_game in TargetGame:
        logging.info(f"Checking if target game is <{target_game}> ...")
        
        # calculate checksums from data assuming target game
        small_block_1, small_block_2 = find_small_blocks(data_all, target_game)
        logging.info("  small block 1 (original, calculated)")
        chk1_calculated = calculate_checksum(small_block_1)
        logging.info(f"  checksum: {chk1_calculated.hex().upper()}")
        logging.info("  small block 2 (original, calculated)")
        chk2_calculated = calculate_checksum(small_block_2)
        logging.info(f"  checksum: {chk2_calculated.hex().upper()}")

        # calculate offsets and read (possibly) checksums from the data
        footer_offset, footer_size = get_footer_offset_and_size(target_game)
        logging.info("  small block 1 (original, read)")
        chk1_read = data_all[footer_offset + footer_size - 2 : footer_offset + footer_size]
        logging.info(f"  checksum: {chk1_read.hex().upper()}")
        logging.info("  small block 2 (original, read)")
        chk2_read = data_all[small_block_2_start + footer_offset + footer_size - 2 : small_block_2_start + footer_offset + footer_size]
        logging.info(f"  checksum: {chk2_read.hex().upper()}")

        # sanity check
        comp1 = (chk1_calculated == chk1_read) 
        comp2 = (chk2_calculated == chk2_read)
        if (comp1 and not comp2) or (comp2 and not comp1):
            wrong_comp = "2nd" if (comp1 and not comp2) else "1st"
            # NOTE: not sure if it's possible for the checksum to be wrong?
            logging.warn(f"Checksum for the {wrong_comp} small block is incorrect but the other one is fine.")
        elif (comp1 and comp2):
            break
    else:
        raise Exception("Could not determine target game.")
    
    logging.info(f"Target game is {target_game.value} !")
    return target_game

def edit_save(data_all, target_game, to_change, save_path):
    # TODO: implement this
    # NOTE: copy save before editing
    # use bytearray to modify offsets and calculate checksums
    edited_data = bytearray(data_all)
    # NOTE: remember to little-endian the checksum
    pass

def main ():
    # setup logging
    if True: # debug #read this from an argument
        log_level = logging.DEBUG 
    else:
        log_level = logging.WARNING

    log_format = "[{levelname}] - {message}"
    logging.basicConfig(level=log_level, format=log_format, style='{')

    # parse arguments
    save_path, to_change = parse_arguments()
    if not save_path.lower().endswith(".sav"):
        logging.warn("Save file does not have the .sav extension.")

    data_all = read_save(save_path)
    target_game = determine_target_game(data_all)
    #edit_save(data_all, target_game, to_change, save_path)



if __name__ == "__main__":
    main()
