from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

def run_exact_solver():
    print("1. PySCF Sürücüsü Başlatılıyor (LiH Molekülü)...")
    driver = PySCFDriver(
        atom="Li 0 0 0; H 0 0 1.5949",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    
    print("2. NumPyMinimumEigensolver (Kesin Çözücü) Hazırlanıyor...")
    # Klasik bilgisayarının RAM'ini kullanarak matrisin en küçük özdeğerini kesin olarak çözer
    numpy_solver = NumPyMinimumEigensolver()
    mapper = ParityMapper(num_particles=problem.num_particles)
    
    # Eigensolver algoritmasını molekül problemi ile birleştiriyoruz
    calc = GroundStateEigensolver(mapper, numpy_solver)
    
    print("3. Kesin Enerji Hesaplanıyor (Bu işlem çok kısa sürecek)...")
    result = calc.solve(problem)
    
    print("\n" + "="*65)
    print("KESİN ÇÖZÜM (EXACT EIGENSOLVER) RAPORU")
    print("="*65)
    print(f"Molekül Tipi                : Lityum Hidrür (LiH)")
    print(f"Bağ Uzunluğu                : 1.5949 Å")
    print("-" * 65)
    print(f"Sadece Elektronik Enerji    : {result.groundenergy:.6f} Hartree")
    print(f"Nükleer İtme Enerjisi       : {result.nuclear_repulsion_energy:.6f} Hartree")
    print("-" * 65)
    # result.total_energies[0] elektronik enerji ile nükleer itmenin toplamını verir
    print(f"KESİN TEMEL DURUM ENERJİSİ  : {result.total_energies[0]:.6f} Hartree")
    print("="*65)

if __name__ == "__main__":
    run_exact_solver()
