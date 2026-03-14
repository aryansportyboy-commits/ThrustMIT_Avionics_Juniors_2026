#include <iostream>
#include <queue>
#include <vector>

// -----------------------------------------
// 1. Moving Average Filter
// -----------------------------------------
class MovingAverageFilter {
private:
    int windowSize;
    std::queue<double> window;
    double sum;

public:
    MovingAverageFilter(int size) : windowSize(size), sum(0.0) {}

    double process(double input) {
        sum += input;
        window.push(input);

        if (window.size() > windowSize) {
            sum -= window.front();
            window.pop();
        }

        return sum / window.size();
    }
};

// -----------------------------------------
// 2. Low-Pass Filter (Exponential)
// -----------------------------------------
class LowPassFilter {
private:
    double alpha; // Smoothing factor (0 < alpha < 1)
    double prevOutput;
    bool isFirstRun;

public:
    // alpha closer to 0 = heavier filtering/smoother. 
    // alpha closer to 1 = less filtering/tracks input closely.
    LowPassFilter(double alpha_val) : alpha(alpha_val), prevOutput(0.0), isFirstRun(true) {}

    double process(double input) {
        if (isFirstRun) {
            prevOutput = input;
            isFirstRun = false;
            return input;
        }
        
        // y[n] = alpha * x[n] + (1 - alpha) * y[n-1]
        double output = alpha * input + (1.0 - alpha) * prevOutput;
        prevOutput = output;
        return output;
    }
};

// -----------------------------------------
// 3. High-Pass Filter
// -----------------------------------------
class HighPassFilter {
private:
    double alpha;
    double prevInput;
    double prevOutput;
    bool isFirstRun;

public:
    HighPassFilter(double alpha_val) : alpha(alpha_val), prevInput(0.0), prevOutput(0.0), isFirstRun(true) {}

    double process(double input) {
        if (isFirstRun) {
            prevInput = input;
            prevOutput = input; // Or 0, depending on initialization preference
            isFirstRun = false;
            return prevOutput;
        }

        // y[n] = alpha * (y[n-1] + x[n] - x[n-1])
        double output = alpha * (prevOutput + input - prevInput);
        prevInput = input;
        prevOutput = output;
        return output;
    }
};

// -----------------------------------------
// Main Function to Test
// -----------------------------------------
int main() {
    // Test Data
    std::vector<double> signal = {10, 12, 11, 15, 20, 25, 22, 18, 15, 10};

    MovingAverageFilter maFilter(3);      // Window size of 3
    LowPassFilter lpFilter(0.3);          // Alpha = 0.3
    HighPassFilter hpFilter(0.7);         // Alpha = 0.7

    std::cout << "Input | Moving Avg | Low Pass | High Pass\n";
    std::cout << "-------------------------------------------\n";

    for (double val : signal) {
        double ma = maFilter.process(val);
        double lp = lpFilter.process(val);
        double hp = hpFilter.process(val);

        std::cout << val << "    | " 
                  << ma << "       | " 
                  << lp << "   | " 
                  << hp << "\n";
    }

    return 0;
}