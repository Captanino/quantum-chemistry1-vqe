import numpy as np
import matplotlib.pyplot as plt
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

def run_dissociation_curve():
    print("1. Batarya Şarj/Deşarj Simülasyonu Başlatılıyor...")
    
    # 0.5 Å'dan 3.5 Å'a kadar 0.1 adımlarla mesafeleri belirliyoruz
    distances = np.arange(0.5, 3.5, 0.1)
    exact_energies = []
    
    numpy_solver = NumPyMinimumEigensolver()
    
    print("2. Moleküler Ayrışma Noktaları Hesaplanıyor (Lütfen bekleyin)...\n")
    
    for dist in distances:
        # Her bir mesafe için molekülü yeniden tanımlıyoruz
        driver = PySCFDriver(
            atom=f"Li 0 0 0; H 0 0 {dist:.3f}",
            basis="sto3g",
            charge=0,
            spin=0,
            unit=DistanceUnit.ANGSTROM,
        )
        problem = driver.run()
        mapper = ParityMapper(num_particles=problem.num_particles)
        calc = GroundStateEigensolver(mapper, numpy_solver)
        
        # Kesin enerjiyi hesapla ve listeye ekle
        res = calc.solve(problem)
        energy = res.total_energies[0]
        exact_energies.append(energy)
        
        print(f"   Mesafe: {dist:.1f} Å | Temel Durum Enerjisi: {energy:.6f} Hartree")
    
    print("\n3. Veriler İşlendi. Grafik Çiziliyor...")
    
    # Kuantum analizini görselleştirme
    plt.figure(figsize=(10, 6))
    plt.plot(distances, exact_energies, marker='o', linestyle='-', color='b', label='Kesin Çözüm (Exact)')
    plt.title('LiH Batarya Modeli: Ayrışma Eğrisi (Dissociation Curve)')
    plt.xlabel('Atomlar Arası Mesafe (Angstrom)')
    plt.ylabel('Temel Durum Enerjisi (Hartree)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Grafiği WSL içinde açamayacağımız için masaüstüne/bulunduğumuz dizine kaydediyoruz
    output_filename = "ayrisma_egrisi.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    print(f"\nİşlem Tamamlandı! Grafik '{output_filename}' adıyla kaydedildi.")
    print("Windows Dosya Gezgini'ni açıp Linux dosya sisteminden (\\\\wsl.localhost\\Ubuntu\\home\\fatih) bu PNG dosyasını görüntüleyebilirsin.")

if __name__ == "__main__":
    run_dissociation_curve()
