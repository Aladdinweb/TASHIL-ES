# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'utils'))
from app.utils.database import initialize_database

def main():
    initialize_database()
    print("EPSP ES-SENIA — Application démarrée. GUI à venir.")

if __name__ == "__main__":
    main()
