#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <cstdlib>
#include <ctime>

// Number of elements in the vector
const int numElements = 10;

// Shared vector
std::vector<int> data(numElements);

// Mutex to protect access to the shared vector
std::mutex dataMutex;

// Function for each thread to read and write to data randomly
void processData(int threadId) {
    srand(static_cast<unsigned int>(time(nullptr)));

    for (int i = 0; i < 5; ++i) {
        // Randomly choose an index
        int index = rand() % numElements;

        // Lock the mutex before accessing the shared vector
        std::lock_guard<std::mutex> lock(dataMutex);

        // Read and write to the shared vector
        int value = data[index];
        data[index] = value + 1;

        // Output the operation
        std::cout << "Thread " << threadId << ": Incremented data[" << index << "] to " << data[index] << std::endl;

        // Unlock the mutex after accessing the shared vector
    }
}

int main() {
    // Initialize data vector
    for (int i = 0; i < numElements; ++i) {
        data[i] = 0;
    }

    // Number of threads
    const int numThreads = 3;

    // Container for thread objects
    std::vector<std::thread> threads;

    // Start the threads
    for (int i = 0; i < numThreads; ++i) {
        threads.emplace_back(processData, i + 1);
    }

    // Join the threads to the main thread
    for (auto& thread : threads) {
        thread.join();
    }

    return 0;
}
