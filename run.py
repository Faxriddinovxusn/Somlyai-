import subprocess
import sys
import time
import os

def main():
    print("🚀 Somly AI - Barcha tizimlarni ishga tushirish...")

    # Frontend (Vite) ni ishga tushirish
    # Windows muhitida npm to'g'ri ishlashi uchun shell=True qilingan
    webapp_dir = os.path.join(os.getcwd(), "webapp")
    vite_process = subprocess.Popen(
        "npm run dev",
        cwd=webapp_dir,
        shell=True
    )
    print("✅ Frontend (Vite) jarayoni boshlandi (localhost:3000)...")

    # Backend (Bot va API) ni ishga tushirish
    bot_process = subprocess.Popen(
        [sys.executable, "-m", "src.bot"],
        cwd=os.getcwd()
    )
    print("✅ Backend (Bot va API) jarayoni boshlandi...")

    try:
        # Asosiy jarayonni ushlab turish
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Tizim to'xtatilmoqda...")
        vite_process.terminate()
        bot_process.terminate()
        print("✅ Barcha jarayonlar to'xtatildi.")

if __name__ == "__main__":
    main()
