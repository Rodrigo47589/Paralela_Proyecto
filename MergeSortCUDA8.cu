#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <cuda_runtime.h>

// Ajusta cuántos hilos tendrá cada bloque CUDA
#define BLOCK_SIZE 1024

// Función para obtener la cantidad de núcleos CUDA de la GPU activa
int getCudaCores() {
    int device;
    cudaGetDevice(&device);
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, device);

    // Cada arquitectura NVIDIA tiene diferente número de núcleos por multiprocesador
    int cores_per_sm = 0;
    switch (prop.major) {
    case 7: // Turing (GTX 1650)
        cores_per_sm = 64;
        break;
    }
    return prop.multiProcessorCount * cores_per_sm;
}

// Kernel CUDA: cada hilo fusiona un segmento ("run") del arreglo
__global__
void merge_kernel(const float* A, const int* idx_A, float* B, int* idx_B,
    int N, int width) {
    // Cada hilo calcula el inicio de su segmento
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int segSize = 2 * width;
    int segStart = tid * segSize;
    if (segStart >= N) return; // Si se pasa del tamaño, no hace nada

    // Definir los límites de los dos subarreglos a fusionar
    int mid = min(segStart + width, N);
    int end = min(segStart + segSize, N);

    // Fusión ordenada (descendente)
    int i = segStart, j = mid, k = segStart;
    while (i < mid && j < end) {
        if (A[i] >= A[j]) {
            B[k] = A[i];
            idx_B[k] = idx_A[i];
            i++;
        }
        else {
            B[k] = A[j];
            idx_B[k] = idx_A[j];
            j++;
        }
        k++;
    }
    // Copia remanente si queda
    while (i < mid) {
        B[k] = A[i];
        idx_B[k] = idx_A[i];
        i++; k++;
    }
    while (j < end) {
        B[k] = A[j];
        idx_B[k] = idx_A[j];
        j++; k++;
    }
}

// Función que controla el merge sort en GPU y muestra info de cada pasada
void merge_sort_gpu(float* d_in, int* d_idx, float* d_out, int* d_out_idx, int N, int cuda_cores) {
    int* d_temp_idx;
    float* d_temp;
    cudaMalloc(&d_temp, N * sizeof(float));
    cudaMalloc(&d_temp_idx, N * sizeof(int));
    cudaMemcpy(d_temp, d_in, N * sizeof(float), cudaMemcpyDeviceToDevice);
    cudaMemcpy(d_temp_idx, d_idx, N * sizeof(int), cudaMemcpyDeviceToDevice);

    bool flip = false;
    // La variable width define el tamaño de run a fusionar (1, 2, 4, 8, ...)
    for (int width = 1; width < N; width *= 2) {
        int numSegs = (N + 2 * width - 1) / (2 * width); // Cuántos segmentos en esta pasada
        int numBlocks = (numSegs + BLOCK_SIZE - 1) / BLOCK_SIZE;
        int totalHilos = numBlocks * BLOCK_SIZE;

        // Imprimir cómo se distribuye el trabajo en GPU en cada pasada
        std::cout << "[PASADA width=" << width
            << "] segmentos=" << numSegs
            << ", bloques=" << numBlocks
            << ", hilosPorBloque=" << BLOCK_SIZE
            << ", totalHilosLanzados=" << totalHilos
            << ", CUDA_cores=" << cuda_cores
            << std::endl;

        if (!flip) {
            merge_kernel << <numBlocks, BLOCK_SIZE >> >
                (d_temp, d_temp_idx, d_out, d_out_idx, N, width);
        }
        else {
            merge_kernel << <numBlocks, BLOCK_SIZE >> >
                (d_out, d_out_idx, d_temp, d_temp_idx, N, width);
        }
        cudaDeviceSynchronize();
        flip = !flip;
    }
    // Copiar al buffer final si quedó en el temporal
    if (!flip) {
        cudaMemcpy(d_out, d_temp, N * sizeof(float), cudaMemcpyDeviceToDevice);
        cudaMemcpy(d_out_idx, d_temp_idx, N * sizeof(int), cudaMemcpyDeviceToDevice);
    }
    cudaFree(d_temp);
    cudaFree(d_temp_idx);
}

// Lee el CSV, omitiendo cabecera, y llena dos vectores: nombres y scores
void leerCSV(const std::string& filename, std::vector<std::string>& nombres, std::vector<float>& scores) {
    std::ifstream in(filename);
    std::string line;
    bool primera = true;
    while (std::getline(in, line)) {
        if (primera) { primera = false; continue; } // Salta cabecera
        std::stringstream ss(line);
        std::string nombre, scoreStr;
        if (!std::getline(ss, nombre, ',')) continue;
        if (!std::getline(ss, scoreStr)) continue;
        if (nombre.empty() || scoreStr.empty()) continue;
        try {
            scores.push_back(std::stof(scoreStr));
            nombres.push_back(nombre);
        }
        catch (...) {
            std::cerr << "Línea con formato incorrecto: " << line << std::endl;
        }
    }
}

// Escribe los resultados ordenados en un archivo CSV
void escribirCSV(const std::string& filename, const std::vector<std::string>& nombres, const std::vector<float>& scores) {
    std::ofstream out(filename);
    for (size_t i = 0; i < nombres.size(); ++i) {
        out << nombres[i] << "," << scores[i] << "\n";
    }
}

int main(int argc, char* argv[]) {
    std::string archivo_in = argc > 1 ? argv[1] : "usuarios.csv";
    std::string archivo_out = argc > 2 ? argv[2] : "usuarios_ordenados_merge.csv";
    std::vector<std::string> nombres;
    std::vector<float> scores;
    leerCSV(archivo_in, nombres, scores);
    int N = scores.size();
    std::vector<int> idx(N);
    for (int i = 0; i < N; ++i) idx[i] = i;

    float* d_in;     int* d_idx;
    float* d_out;    int* d_out_idx;
    cudaMalloc(&d_in, N * sizeof(float));
    cudaMalloc(&d_idx, N * sizeof(int));
    cudaMalloc(&d_out, N * sizeof(float));
    cudaMalloc(&d_out_idx, N * sizeof(int));
    cudaMemcpy(d_in, scores.data(), N * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_idx, idx.data(), N * sizeof(int), cudaMemcpyHostToDevice);

    // Obtiene y muestra el número de CUDA cores físicos de la GPU
    int cuda_cores = getCudaCores();

    // Toma el tiempo de ejecución en GPU
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start);

    merge_sort_gpu(d_in, d_idx, d_out, d_out_idx, N, cuda_cores);

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float ms;
    cudaEventElapsedTime(&ms, start, stop);
    printf("Tiempo GPU Merge Sort: %.4f ms\n", ms);

    // Copia los resultados a memoria del host
    std::vector<float> scores_sorted(N);
    std::vector<int> idx_sorted(N);
    cudaMemcpy(scores_sorted.data(), d_out, N * sizeof(float), cudaMemcpyDeviceToHost);
    cudaMemcpy(idx_sorted.data(), d_out_idx, N * sizeof(int), cudaMemcpyDeviceToHost);

    // Muestra el top 10 en pantalla
    std::vector<std::string> nombres_sorted(N);
    for (int i = 0; i < N; ++i)
        nombres_sorted[i] = nombres[idx_sorted[i]];

    std::cout << "\n=== TOP 10 USUARIOS ===" << std::endl;
    for (int i = 0; i < std::min(N, 10); ++i) {
        std::cout << (i + 1) << ". " << nombres_sorted[i] << " - " << scores_sorted[i] << std::endl;
    }
    std::cout << "=======================\n" << std::endl;

    escribirCSV(archivo_out, nombres_sorted, scores_sorted);
    printf("Archivo ordenado guardado en: %s\n", archivo_out.c_str());

    cudaFree(d_in); cudaFree(d_idx); cudaFree(d_out); cudaFree(d_out_idx);
    return 0;
}
