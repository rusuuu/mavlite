import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# referinta = 11 octeti (LPP standard), delta = 8 octeti
for n in [1, 5, 10, 20, 50, 100]:
    mediu = (11 + (n-1)*8) / n
    print(f"keyframe la fiecare {n:>3} pachete: {mediu:.2f} octeti/pachet")
