import os
import sys

# Repo nie jest zainstalowanym pakietem -- dorzuc katalog NADRZEDNY
# wobec GSF do sys.path, zeby `import GSF.TIMDR...` dzialalo (kod uzywa
# bezwzglednych importow "GSF.<modul>...", patrz VALIDATOR/validator.py).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_OF_REPO = os.path.dirname(REPO_ROOT)
if PARENT_OF_REPO not in sys.path:
    sys.path.insert(0, PARENT_OF_REPO)
