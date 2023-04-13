#!/usr/bin/env python3

"""Python script to change gender and name (+other trainer data) in gen IV games (currently only HGSS supported)."""

# sanity check: verify current checksum to make sure all addresses are ok
# when changing name, careful with max size, allowed characters, terminator and trailing characters (fill with 00 after the terminator)
