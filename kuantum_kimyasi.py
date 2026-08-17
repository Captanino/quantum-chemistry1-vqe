import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import RealAmplitudes
# Kuantum Kimyası Simülasyonu: PySCF ve Qiskit Nature Entegrasyonu
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import RealAmplitudes
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import EstimatorV2 as Estimator

# Qiskit Nature modülleri
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper

def solve_real_molecule():
    print("1. PySCF Sürücüsü Başlatılıyor ve Moleküler Yapı Çözümleniyor...")
    driver = PySCFDriver(
        atom="H 0 0 0; H 0 0 0.735",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    
    nuclear_repulsion_energy = problem.nuclear_repulsion_energy
    
    print("2. Fermiyonik Hamiltoniyen Kubit (Pauli) Operatörlerine Dönüştürülüyor...")
    hamiltonian_fermionic = problem.hamiltonian.second_q_op()
    
    mapper = JordanWignerMapper()
    hamiltonian_qubit = mapper.map(hamiltonian_fermionic)
    num_qubits = hamiltonian_qubit.num_qubits
    
    print(f"   -> Dönüşüm Tamamlandı. Gereken Mantıksal Kubit Sayısı: {num_qubits}\n")
    
    # 3. Kuantum Devresi (Ansatz) ve Derleme (Transpile) Katmanı
    # Hazır devreyi simülatörün (Aer) anlayacağı temel kapılara dönüştürüyoruz.
    simulator = AerSimulator()
    base_ansatz = RealAmplitudes(num_qubits, reps=2)
    ansatz = transpile(base_ansatz, simulator)
    
    estimator = Estimator()
    history = {'energy': [], 'steps': 0}
    
    def cost_function(params):
        pub = (ansatz, hamiltonian_qubit, params)
        job = estimator.run([pub])
        result = job.result()[0]
        
        electronic_energy = result.data.evs
        history['steps'] += 1
        history['energy'].append(electronic_energy)
        
        if history['steps'] % 50 == 0:
            current_total = electronic_energy + nuclear_repulsion_energy
            print(f"   Iterasyon {history['steps']:3d} | Güncel Toplam Enerji: {current_total:.6f} Hartree")
            
        return electronic_energy

    np.random.seed(42)
    initial_parameters = np.random.rand(ansatz.num_parameters) * 2 * np.pi
    
    print("3. SciPy COBYLA ile VQE Optimizasyonu Başlıyor (Max Iter: 500)...")
    result = minimize(
        cost_function,
        initial_parameters,
        method='COBYLA',
        options={'maxiter': 500, 'tol': 1e-6}
    )
    
    final_electronic_energy = result.fun
    total_ground_state_energy = final_electronic_energy + nuclear_repulsion_energy
    
    print("\n" + "="*65)
    print("GERÇEK KUANTUM KİMYASI SİMÜLASYON RAPORU")
    print("="*65)
    print(f"Molekül Tipi          : Hidrojen (H2)")
    print(f"Bağ Uzunluğu          : 0.735 Å")
    print(f"Kullanılan Çözücüler  : PySCF + Qiskit Nature + AerSimulator")
    print(f"Fermiyonik Dönüşüm    : Jordan-Wigner ({num_qubits} Kubit)")
    print(f"Toplam Iterasyon      : {history['steps']} / 500")
    print("-" * 65)
    print(f"Hesaplanan Elk. Enerji: {final_electronic_energy:.6f} Hartree")
    print(f"Nükleer İtme Enerjisi : {nuclear_repulsion_energy:.6f} Hartree")
    print("="*65)
    print(f"En Düşük Kararlı Moleküler Enerji Değeri: {total_ground_state_energy:.6f} Hartree")
    print("="*65)

if __name__ == "__main__":
    solve_real_molecule()

# Kuantum Kimyası Simülasyonu: PySCF ve Qiskit Nature Entegrasyonu
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import RealAmplitudes
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import EstimatorV2 as Estimator

# Qiskit Nature modülleri
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper

def solve_real_molecule():
    print("1. PySCF Sürücüsü Başlatılıyor ve Moleküler Yapı Çözümleniyor...")
    driver = PySCFDriver(
        atom="H 0 0 0; H 0 0 0.735",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    
    nuclear_repulsion_energy = problem.nuclear_repulsion_energy
    
    print("2. Fermiyonik Hamiltoniyen Kubit (Pauli) Operatörlerine Dönüştürülüyor...")
    hamiltonian_fermionic = problem.hamiltonian.second_q_op()
    
    mapper = JordanWignerMapper()
    hamiltonian_qubit = mapper.map(hamiltonian_fermionic)
    num_qubits = hamiltonian_qubit.num_qubits
    
    print(f"   -> Dönüşüm Tamamlandı. Gereken Mantıksal Kubit Sayısı: {num_qubits}\n")
    
    # 3. Kuantum Devresi (Ansatz) ve Derleme (Transpile) Katmanı
    # Hazır devreyi simülatörün (Aer) anlayacağı temel kapılara dönüştürüyoruz.
    simulator = AerSimulator()
    base_ansatz = RealAmplitudes(num_qubits, reps=2)
    ansatz = transpile(base_ansatz, simulator)
    
    estimator = Estimator()
    history = {'energy': [], 'steps': 0}
    
    def cost_function(params):
        pub = (ansatz, hamiltonian_qubit, params)
        job = estimator.run([pub])
        result = job.result()[0]
        
        electronic_energy = result.data.evs
        history['steps'] += 1
        history['energy'].append(electronic_energy)
        
        if history['steps'] % 50 == 0:
            current_total = electronic_energy + nuclear_repulsion_energy
            print(f"   Iterasyon {history['steps']:3d} | Güncel Toplam Enerji: {current_total:.6f} Hartree")
            
        return electronic_energy

    np.random.seed(42)
    initial_parameters = np.random.rand(ansatz.num_parameters) * 2 * np.pi
    
    print("3. SciPy COBYLA ile VQE Optimizasyonu Başlıyor (Max Iter: 500)...")
    result = minimize(
        cost_function,
        initial_parameters,
        method='COBYLA',
        options={'maxiter': 500, 'tol': 1e-6}
    )
    
    final_electronic_energy = result.fun
    total_ground_state_energy = final_electronic_energy + nuclear_repulsion_energy
    
    print("\n" + "="*65)
    print("GERÇEK KUANTUM KİMYASI SİMÜLASYON RAPORU")
    print("="*65)
    print(f"Molekül Tipi          : Hidrojen (H2)")
    print(f"Bağ Uzunluğu          : 0.735 Å")
    print(f"Kullanılan Çözücüler  : PySCF + Qiskit Nature + AerSimulator")
    print(f"Fermiyonik Dönüşüm    : Jordan-Wigner ({num_qubits} Kubit)")
    print(f"Toplam Iterasyon      : {history['steps']} / 500")
    print("-" * 65)
    print(f"Hesaplanan Elk. Enerji: {final_electronic_energy:.6f} Hartree")
    print(f"Nükleer İtme Enerjisi : {nuclear_repulsion_energy:.6f} Hartree")
    print("="*65)
    print(f"En Düşük Kararlı Moleküler Enerji Değeri: {total_ground_state_energy:.6f} Hartree")
    print("="*65)

if __name__ == "__main__":
    solve_real_molecule()
