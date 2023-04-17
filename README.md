# PkGender.py

A Python script to change trainer data (name, gender, etc.) in gen IV Pokémon games (Diamond, Pearl, Platinum, HeartGold, SoulSilver).

* **USE AT YOUR OWN RISK!**

* Note: NO$GBA prepends .sav files with a header, making them a slightly different format. Please convert to regular .sav files before using this tool.

### Setup

* To use the [provided binaries](https://github.com/abeRC/PkGender/releases/), unzip the archive and run the executable normally according to usage instructions.

* To run this script using the Python interpreter, Python 3.6+ is required.
  
  * It is recommended to run this script inside a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) with the [fastcrc module](https://fastcrc.readthedocs.io/en/latest/) installed (through pip).
  
  * You could also install fastcrc through your system pip (pip3 on Linux).

### Usage

* Linux (from a terminal prompt)
  
  ```
  ./PkGender [--name NAME] [--gender] [--verify-only] [--help] [--debug] [--version] savefile
  ```

* Windows (from a powershell or cmd prompt)
  
  NOTE: This may or may not work since it was compiled in a weird way (i.e., using wine instead of a Windows system). On my tests, it did work, though, so it should be ok.  :)
  
  ```
  .\PkGender [--name NAME] [--gender] [--verify-only] [--help] [--debug] [--version] savefile
  ```

* Python interpreter (see Setup for dependencies)
  
  ```
  python PkGender.py [--name NAME] [--gender] [--verify-only] [--help] [--debug] [--version] savefile
  ```

* Positional arguments:
  
  | Argument | Description       |
  | -------- |:-----------------:|
  | savefile | Path to save file |

* Optional arguments:
  
  | Argument                 | Description                                           |
  | ------------------------ |:-----------------------------------------------------:|
  | -h, --help               | Show the help message and exit                        |
  | --name NAME              | Change trainer's name to NAME (limit of 7 characters) |
  | --gender                 | Swap trainer's gender                                 |
  | --verify-only, --dry-run | Do not edit save file (only verify checksum)          |
  | -d, --debug              | Enable debug messages                                 |
  | -v, --version            | Print version information                             |

### Planned features

* Support for additional symbols in trainer name

* Support to change trainer id, secret id, money, badges, country of origin / language

* Support for additional generations of Pokémon games

* Visual interface
