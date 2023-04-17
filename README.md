# PkGender.py

A Python script to change trainer data (name, gender, etc.) in gen IV Pokémon games (Diamond, Pearl, Platinum, HeartGold, SoulSilver).

* **USE AT YOUR OWN RISK!**

* Python 3.6+ required

* It is recommended to run this script inside a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) with the [fastcrc module](https://fastcrc.readthedocs.io/en/latest/) installed (through pip).
  
  * You could also install fastcrc through your system pip (pip3 on Linux).

* Note: NO$GBA prepends .sav files with a header, making them a slightly different format. Please convert to regular .sav files before using this tool.

### Usage

```
PkGender.py [--name NAME] [--gender] [--verify-only] [--help] [--debug] [--version] savepath
```

* Positional arguments:
  
  | Argument | Description       |
  | -------- |:-----------------:|
  | savepath | path to save file |

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

* Executable binaries

* Support for additional generations of Pokémon games

* Visual interface
