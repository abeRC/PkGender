#!/usr/bin/env python3

"""Python script to change gender and name (+other trainer data) in gen IV games (currently only HGSS supported)."""

# sanity check: verify current checksum to make sure all addresses are ok
# when changing name, careful with max size, allowed characters, terminator and trailing characters (fill with 00 after the terminator)

from fastcrc.crc16 import ibm_3740
from collections import namedtuple
from enum import Enum

small_block_1_start = 0x00000
small_block_2_start = 0x40000
footer_offset_HGSS = 0xF618
footer_offset_Pt = 0xCF18
footer_offset_DP = 0xC0EC
footer_offset_dict = { # might work with StrEnum (py 3.11+)?
    "HGSS": footer_offset_HGSS,
    "DP": footer_offset_DP,
    "Pt": footer_offset_Pt
}
class TargetGame(Enum):
    HGSS = "HGSS"
    DP = "DP"
    Pt = "Pt"

def parse_arguments():
    # TODO: implement this
    # use named tuple for to_change
    pass

def read_save (save_path : str) -> bytes:
    with open(save_path, "rb") as f:
        data_all = f.read()
    return data_all

def return_footer_offset (target_game : TargetGame):
    return footer_offset_dict[target_game.value]

def find_small_blocks (data_all, target_game : TargetGame):
    footer_offsset = return_footer_offset(target_game)
    small_block_1 = data_all[small_block_1_start : small_block_1_start+footer_offsset]
    small_block_2 = data_all[small_block_2_start : small_block_2_start+footer_offsset]
    return (small_block_1, small_block_2)

def calculate_checksum (small_block):
    chk = ibm_3740(small_block)
    # convert chk to hexadecimal and invert the bytes (little-endian format)
    chk_bytes = bytes.fromhex(f"{chk:x}")[::-1] 
    return chk_bytes

def determine_target_game (small_blocks) -> TargetGame:
    # TODO: implement this
    # NOTE: this should be a sanity check; check both small blocks
    target_game = TargetGame.HGSS 
    return target_game

def edit_save(small_blocks, to_change, target_game, data_all, save_path):
    # TODO: implement this
    # to_change = [changegender = False]
    # copy save before editing
    # use bytearray to modify offsets and calculate checksums
    # NOTE: remember to little-endian the checksum
    pass

def main ():
    save_path, to_change = parse_arguments()
    data_all = read_save(save_path)
    target_game = determine_target_game(data_all)
    small_blocks = find_small_blocks(data_all, target_game)
    edit_save(small_blocks, to_change, target_game, data_all, save_path)

if __name__ == "__main__":
    main()
