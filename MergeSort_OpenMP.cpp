#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <omp.h>
#include <iomanip>
#include <cstring>
#include <algorithm>

const int MAX_DEPTH = 2;     // Mayor profundidad de tareas paralelas
const int THRESHOLD = 10000; // Solo paralelizar si hay suficientes datos

void merge(std::vector<int>& arr, std::vector<int>& indices, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    std::vector<int> left_arr(n1), right_arr(n2);
    std::vector<int> left_indices(n1), right_indices(n2);

    for (int i = 0; i < n1; i++) {
        left_arr[i] = arr[left + i];
        left_indices[i] = indices[left + i];
    }
    for (int i = 0; i < n2; i++) {
        right_arr[i] = arr[mid + 1 + i];
        right_indices[i] = indices[mid + 1 + i];
    }

    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (left_arr[i] >= right_arr[j]) { // Orden descendente
            arr[k] = left_arr[i];
            indices[k] = left_indices[i];
            i++;
        }
        else {
            arr[k] = right_arr[j];
            indices[k] = right_indices[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = left_arr[i];
        indices[k] = left_indices[i];
        i++; k++;
    }

    while (j < n2) {
        arr[k] = right_arr[j];
        indices[k] = right_indices[j];
        j++; k++;
    }
}

void parallelMergeSort(std::vector<int>& arr, std::vector<int>& indices, int left, int right, int depth) {
    if (left < right) {
        int mid = (left + right) / 2;
        if (depth < MAX_DEPTH && (right - left) > THRESHOLD) {
#pragma omp task shared(arr, indices)
            parallelMergeSort(arr, indices, left, mid, depth + 1);
#pragma omp task shared(arr, indices)
            parallelMergeSort(arr, indices, mid + 1, right, depth + 1);
#pragma omp taskwait
        }
        else {
            parallelMergeSort(arr, indices, left, mid, depth + 1);
            parallelMergeSort(arr, indices, mid + 1, right, depth + 1);
        }
        merge(arr, indices, left, mid, right);
    }
}

void sortParallel(std::vector<int>& arr, std::vector<int>& indices) {
#pragma omp parallel
    {
#pragma omp single
        parallelMergeSort(arr, indices, 0, arr.size() - 1, 0);
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

    for (int i = 0; i < N; i++) {
        sortable[i] = static_cast<int>(puntajes[i] * 1000);
        indices[i] = i;
    }

    double t0 = omp_get_wtime();
    sortParallel(sortable, indices);
    double t1 = omp_get_wtime();
    double elapsed_time = (t1 - t0) * 1000.0;

    std::cout << "MergeSort  + OpenMP : " << std::fixed << std::setprecision(5) << elapsed_time << " milisegundos\n";
    std::cout << "Maximo numero de hilos disponibles: " << omp_get_max_threads() << "\n";

    std::cout << "\nTop 10 puntajes:\n";
    for (int i = 0; i < 10 && i < N; i++) {
        int idx = indices[i];
        std::cout << nombres[idx] << " - " << puntajes[idx] << "\n";
    }

    std::ofstream output_file("usuarios_ordenados.csv");
    output_file << "nombre,puntaje\n";
    for (int i = 0; i < N; i++) {
        int idx = indices[i];
        output_file << nombres[idx] << "," << puntajes[idx] << "\n";
    }
    output_file.close();

    std::cout << "Archivo CSV ordenado guardado como 'usuarios_ordenados.csv'.\n";

    return 0;
}











