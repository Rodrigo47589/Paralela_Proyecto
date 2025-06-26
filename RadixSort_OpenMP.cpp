#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <omp.h>
#include <iomanip>
#include <cstring>
#include <algorithm>

#define BASE 256  // base para counting sort (bytes)
#define BYTES sizeof(int)  // 4 bytes para float reinterpretado

// Reinterpreta float como int conservando el orden
inline int floatToSortableInt(float f) {
    int i = *reinterpret_cast<int*>(&f);
    return (i >= 0) ? (i ^ 0x80000000) : (~i);
}

inline float sortableIntToFloat(int i) {
    i = (i >= 0x80000000) ? (i ^ 0x80000000) : (~i);
    return *reinterpret_cast<float*>(&i);
}

// Radix Sort paralelizado con OpenMP y control de carga
void radixSort(std::vector<int>& arr, std::vector<int>& indices, int num_threads) {
    int N = arr.size();
    std::vector<int> output(N);
    std::vector<int> output_idx(N);
    int count[BASE];

    // Establecer el número de hilos a usar
    omp_set_num_threads(num_threads);

    for (int byte = 0; byte < BYTES; byte++) {
        std::fill(count, count + BASE, 0);

        // Conteo de ocurrencias por byte (paralelizado)
#pragma omp parallel
        {
            int local_count[BASE] = { 0 };

#pragma omp for
            for (int i = 0; i < N; i++) {
                int b = (arr[i] >> (byte * 8)) & 0xFF;
                local_count[b]++;
            }

#pragma omp critical
            for (int i = 0; i < BASE; i++)
                count[i] += local_count[i];
        }

        // Acumulado
        for (int i = 1; i < BASE; i++)
            count[i] += count[i - 1];

        // Construir arreglo ordenado por byte actual (no paralelizado por dependencia)
        for (int i = N - 1; i >= 0; i--) {
            int b = (arr[i] >> (byte * 8)) & 0xFF;
            output[--count[b]] = arr[i];
            output_idx[count[b]] = indices[i];
        }

        // Copiar para siguiente iteración
        std::copy(output.begin(), output.end(), arr.begin());
        std::copy(output_idx.begin(), output_idx.end(), indices.begin());
    }
}

int main() {
    std::vector<std::string> nombres;
    std::vector<float> puntajes;

    std::ifstream archivo("usuarios.csv");
    std::string linea;
    std::getline(archivo, linea); // cabecera

    while (std::getline(archivo, linea)) {
        size_t coma = linea.find(',');
        if (coma != std::string::npos) {
            nombres.push_back(linea.substr(0, coma));
            puntajes.push_back(std::stof(linea.substr(coma + 1)));
        }
    }

    int N = puntajes.size();
    std::vector<int> sortable(N);
    std::vector<int> indices(N);

    // Convertir floats a enteros ordenables
    for (int i = 0; i < N; i++) {
        sortable[i] = floatToSortableInt(puntajes[i]);
        indices[i] = i;
    }

    int num_threads = 8;  // Controlar el número de hilos

    double t0 = omp_get_wtime();  // Tiempo inicial en segundos
    radixSort(sortable, indices, num_threads);
    double t1 = omp_get_wtime();  // Tiempo final en segundos

    // Convertir el tiempo de ejecución a milisegundos
    double elapsed_time_ms = (t1 - t0) * 1000.0;

    std::cout << "RadixSort + OpenMP en " << std::fixed << std::setprecision(5) << elapsed_time_ms << " milisegundos.\n";

    // Mostrar el máximo número de hilos disponibles
    std::cout << "Maximo numero de hilos disponibles: " << omp_get_max_threads() << "\n";

    std::cout << "\nTop 10 puntajes:\n";
    for (int i = N - 1; i >= N - 10; i--) {
        int idx = indices[i];
        std::cout << nombres[idx] << " - " << puntajes[idx] << "\n";
    }

    // Guardar el CSV ordenado
    std::ofstream output_file("usuarios_ordenados.csv");
    output_file << "nombre,puntaje\n";  // Cabecera

    for (int i = N - 1; i >= 0; i--) {
        int idx = indices[i];
        output_file << nombres[idx] << "," << puntajes[idx] << "\n";
    }

    output_file.close();

    std::cout << "Archivo CSV ordenado guardado como 'usuarios_ordenados.csv'.\n";

    return 0;
}
