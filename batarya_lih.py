import numpy as np
from scipy.optimize import minimize

from qiskit.circuit.library import efficient_su2
from qiskit import transpile
from qiskit_aer.primitives import EstimatorV2 as Estimator
from qiskit_aer import AerSimulator

from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper

def run_full_lih_slsqp_simulation():
    print("1. PySCF Sürücüsü Başlatılıyor (Tam LiH Molekülü)...")
    driver = PySCFDriver(
        atom="Li 0 0 0; H 0 0 1.5949",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    nuclear_repulsion_energy = problem.nuclear_repulsion_energy
    
    print("2. Fermiyonik Operatörler Çıkarılıyor (Active Space İPTAL EDİLDİ)...")
    hamiltonian_fermionic = problem.hamiltonian.second_q_op()
    
    # ParityMapper ile Z2 simetrisinden faydalanıp 2 kubit tasarruf ediyoruz (12 -> 10 Kubit)
    mapper = ParityMapper(num_particles=problem.num_particles)
    hamiltonian_qubit = mapper.map(hamiltonian_fermionic)
    num_qubits = hamiltonian_qubit.num_qubits
    
    print(f"   -> Dönüşüm Tamamlandı. Gereken Mantıksal Kubit Sayısı: {num_qubits}\n")
    
    print("3. Ansatz Devresi Derleniyor (reps=2, Tam Uzay)...")
    # reps=2: 10 kubit için RAM'i kitlemeden yeterli kuantum dolanıklığı (entanglement) sağlar
    ansatz_template = efficient_su2(num_qubits, reps=2, entanglement='linear')
    
    simulator = AerSimulator()
    compiled_ansatz = transpile(ansatz_template, backend=simulator)
    
    estimator = Estimator()
    history = {'steps': 0}
    
    def cost_function(params):
        pub = (compiled_ansatz, hamiltonian_qubit, params)
        job = estimator.run([pub])
        electronic_energy = job.result()[0].data.evs
        
        history['steps'] += 1
        # Süreci izleyebilmek için her 50 iterasyonda bir ekrana log basıyoruz
        if history['steps'] % 50 == 0:
            current_total = electronic_energy + nuclear_repulsion_energy
            print(f"   Iterasyon {history['steps']:3d} | Güncel Toplam Enerji: {current_total:.6f} Hartree")
            
        return electronic_energy

    np.random.seed(42)
    initial_parameters = np.random.rand(compiled_ansatz.num_parameters) * 2 * np.pi
    
    print("4. SciPy SLSQP ile Tam Uzay VQE Optimizasyonu Başlıyor (İşlemci yükü artacaktır)...")
    result = minimize(
        cost_function,
        initial_parameters,
        method='SLSQP',
        options={'maxiter': 2000, 'ftol': 1e-6}
    )
    
    final_electronic_energy = result.fun
    total_ground_state_energy = final_electronic_energy + nuclear_repulsion_energy
    
    print("\n" + "="*65)
    print("TAM UZAY (10 KUBİT) LİTYUM HİDRÜR (LiH) SİMÜLASYONU")
    print("="*65)
    print(f"Molekül Tipi          : Lityum Hidrür (LiH)")
    print(f"Kullanılan Kubit      : {num_qubits} (Sadece Parity İndirgemesi)")
    print(f"Optimizatör           : SLSQP")
    print(f"Toplam Iterasyon      : {history['steps']}")
    print("-" * 65)
    print(f"Nükleer İtme Enerjisi : {nuclear_repulsion_energy:.6f} Hartree")
    print(f"En Düşük Kararlı Enerji: {total_ground_state_energy:.6f} Hartree")
    print("="*65)

if __name__ == "__main__":
    run_full_lih_slsqp_simulation()
