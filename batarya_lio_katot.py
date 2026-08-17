import numpy as np
import time

from qiskit.circuit.library import efficient_su2
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.primitives import BackendEstimatorV2

# Gürültü ve Optimizasyon Kütüphaneleri
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_algorithms.optimizers import SPSA

from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

def run_noisy_lio_simulation():
    print("1. PySCF Sürücüsü Başlatılıyor (Li-O Katot Modeli)...")
    driver = PySCFDriver(
        atom="Li 0 0 0; O 0 0 1.69",
        basis="sto3g",
        charge=0,
        spin=1,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    
    print("2. Active Space İndirgemesi Yapılıyor...")
    transformer = ActiveSpaceTransformer(num_electrons=(4, 3), num_spatial_orbitals=5)
    problem_reduced = transformer.transform(problem)
    constant_energy_shift = sum(problem_reduced.hamiltonian.constants.values())
    
    mapper = ParityMapper(num_particles=problem_reduced.num_particles)
    hamiltonian_qubit = mapper.map(problem_reduced.hamiltonian.second_q_op())
    num_qubits = hamiltonian_qubit.num_qubits
    print(f"   -> İndirgeme Başarılı! Gereken Mantıksal Kubit Sayısı: {num_qubits}")
    
    print("\n3. Kesin Hedef (Exact Eigensolver) Hesaplanıyor...")
    numpy_solver = NumPyMinimumEigensolver()
    calc = GroundStateEigensolver(mapper, numpy_solver)
    exact_res = calc.solve(problem_reduced)
    exact_total_energy = exact_res.total_energies[0]
    print(f"   -> Kesin Temel Durum Enerjisi: {exact_total_energy:.6f} Hartree")
    
    print("\n4. Donanım Gürültü Modeli (Noise Model) İnşa Ediliyor...")
    noise_model = NoiseModel()
    
    # IBM sistemlerinin tipik hata oranları: 
    # Tekli kapılarda ~%0.1 (0.001), Çiftli dolanıklık (CX) kapılarında ~%1 (0.01) hata
    error_1q = depolarizing_error(0.001, 1)
    error_2q = depolarizing_error(0.01, 2)
    
    noise_model.add_all_qubit_quantum_error(error_1q, ['ry', 'rz'])
    noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
    
    noisy_simulator = AerSimulator(noise_model=noise_model)
    
    print("5. Ansatz Devresi Derleniyor ve Gürültülü Estimator Kuruluyor...")
    ansatz_template = efficient_su2(num_qubits, reps=2, entanglement='linear')
    compiled_ansatz = transpile(ansatz_template, backend=noisy_simulator)
    
    # Gerçek kuantum donanımını taklit etmesi için BackendEstimatorV2 kullanıyoruz
    estimator = BackendEstimatorV2(backend=noisy_simulator)
    # Atış sayısını belirliyoruz (Ölçüm gürültüsü - Shot noise)
    estimator.options.default_shots = 2048 
    
    history = {'steps': 0}
    
    def cost_function(params):
        pub = (compiled_ansatz, hamiltonian_qubit, params)
        job = estimator.run([pub])
        electronic_energy = job.result()[0].data.evs
        
        history['steps'] += 1
        if history['steps'] % 25 == 0:
            current_total = electronic_energy + constant_energy_shift
            error_margin = current_total - exact_total_energy
            print(f"   Iterasyon {history['steps']:3d} | Gürültülü Enerji: {current_total:.4f} H | Sapma: +{error_margin:.4f} H")
            
        return electronic_energy

    np.random.seed(42)
    initial_parameters = np.random.rand(compiled_ansatz.num_parameters) * 2 * np.pi
    
    print("6. SPSA Optimizatörü ile VQE Başlıyor (Gürültüye dayanıklı algoritma)...")
    
    spsa = SPSA(maxiter=250)
    result = spsa.minimize(fun=cost_function, x0=initial_parameters)
    
    final_electronic_energy = result.fun
    vqe_total_energy = final_electronic_energy + constant_energy_shift
    
    print("\n" + "="*70)
    print("GÜRÜLTÜLÜ DONANIM: Li-O KATOT BATARYA SİMÜLASYONU")
    print("="*70)
    print(f"Gürültü Modeli        : Depolarizing (1Q: 0.1%, 2Q: 1.0%)")
    print(f"Ölçüm Atışı (Shots)   : 2048")
    print(f"Optimizatör           : SPSA (250 İterasyon)")
    print("-" * 70)
    print(f"Hedeflenen Kesin Enerji: {exact_total_energy:.6f} Hartree")
    print(f"VQE'nin Ulaştığı Enerji: {vqe_total_energy:.6f} Hartree")
    print(f"Donanım Kaynaklı Sapma : +{vqe_total_energy - exact_total_energy:.6f} Hartree")
    print("="*70)

if __name__ == "__main__":
    run_noisy_lio_simulation()
