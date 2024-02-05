# Coherence Prediction in Distributed Memory Parallel Machines
## Overview

This project explores the feasibility of coherence prediction in distributed memory parallel machines, specifically focusing on consumer prediction at the home site. Despite challenges identified through statistical analysis, two consumer predictors—LRU and Override—have been proposed and demonstrate promising accuracy in shared memory workloads.
## Motivation

In shared memory parallel workloads within servers and data centers, the use of distributed shared memory (DSM) systems is common. This project aims to address coherence challenges by investigating consumer prediction as a potential mechanism to enhance performance.
## Methodology

The PARSEC 3.0 benchmark suite is utilized to analyze memory traces on a distributed memory parallel machine. The study includes a comprehensive test setup, benchmarks selection, and speculative invalidation setup. Various accuracy metrics are employed to evaluate the effectiveness of the proposed predictors.
## Results

Statistical analysis of benchmark memory traces reveals insights into the opportunities and challenges of coherence prediction. Despite limited benefits in the tested workloads, the LRU and Override consumer predictors exhibit noteworthy accuracy. Bit sensitivity and MHR depth sensitivity analyses further refine our understanding of predictor performance.
## Conclusion

Despite the challenges identified in coherence prediction for distributed memory parallel machines, this project introduces effective consumer predictors. The Override predictor, in particular, showcases robust performance, offering potential benefits in scenarios with shared memory workloads.
## Future Work

Future plans for the project include addressing benchmark issues, extending the study to diverse workloads, and exploring additional aspects such as PHT sensitivity and memory footprint. The evaluation of speedup potential in a cycle-accurate simulator and the application of branch prediction methods to home site message prediction remain open areas for investigation.
