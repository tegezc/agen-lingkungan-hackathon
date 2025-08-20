# File ini digunakan untuk menjalankan agen dari direktori root proyek
# agar semua import modular berfungsi dengan baik.
from services import agent_logic

if __name__ == "__main__":
    agent_logic.run_agent()