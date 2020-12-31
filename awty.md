# Code Embedding for Statically Detecting Software Vulnerabilities: Are We There Yet

This work aims to evaluate and compare recent proposed state-of-the-art Code Embedding approaches for vulnerability detection task in terms of serveral criteria, and reveal the advantages and disadvantages of those tools, thereby giving a road-map for future directions of statically detecting software vulnerabilities via learning method.

## Comparing criteria

- Ease of use: how much effort it took us to install and use it?
- Effectiveness: the effectiveness on a unified dataset by using three metrics: recall, precision, and F1-Score.
- Efficiency/Scalability: prediction rate (samples/sec) and performance on large dataset.
- Code coverage achieved.
- Supporting language.
- Feedback for developers: the usefulness of the code representation on helping software developers locate and fix the bugs (granularity).

## Approaches

### Token-based

#### [Automated Vulnerability Detection in Source Code Using Deep Representation Learning](resources/pdf/tokendl.pdf)

- Task: vul detect using token embedding
- Language: c/c++
- Toolchains: python
- Implementation: None. This approach leverages a simple CNN/RNN to embed function bodies into a latent space and feed the vector representation to a random forest classifier.
- Dataset: https://osf.io/6fexn/ (real-world, function-level)
- Note: we need to re-implement this approach.

### AST-based

#### [Code2vec](resources/pdf/code2vec.pdf)/[Code2seq](resources/pdf/code2seq.pdf)

- Task: Code embedding for function name prediction and code summarization
- Language: Java/C/C++/C#
- Toolchains: java, python
- Implementation:
  - code2vec: https://github.com/tech-srl/code2vec
  - code2seq: https://github.com/tech-srl/code2seq
- Note: We can leverage the code embedding technique proposed by the author to achieving the task of vulnerability detection, but a C/C++ vulnerability database should be built first.

#### [ASTNN](resources/pdf/astnn_icse2019.pdf)

- Tasks: Code embedding for code classification and code clone.
- Language: C/C++/Java
- Toolchains: python
- Implementation: https://github.com/zhangj111/astnn
- Note: change code classification to bug detection.

### Control- or/and data-flow-based

#### [Vuldeepecker](resources/pdf/vuldeepecker.pdf)

- Task: vul detect CWE119, CWE399
- Language: c/c++
- Toolchains: checkmarx, python
- Implementation: None
- Dataset: https://github.com/CGCL-codes/VulDeePecker
- Note: we need to re-implement this approach.

#### [muVulDeePecker](resources/pdf/muVulDeePecker.pdf)

- Task: Multiclass Vulnerability Detection
- Language: C/C++
- Toolchains: [Joern](https://github.com/ShiftLeftSecurity/joern), checkmarx, python
- Implementation: None

#### [SySeVR](resources/pdf/SySeVR.pdf)

- Task: Multiclass Vulnerability Detection
- Language: C/C++
- Toolchains: [Joern](https://github.com/ShiftLeftSecurity/joern), checkmarx, python
- implementation: None

#### VGDetector

- Task: Multiclass Vulnerability Detection
- Language: C/C++
- Toolchains: SVF

### Others

#### [Func2vec](resources/pdf/func2vec.pdf)

- Task: code embedding for Function synonyms identification
- Language: C/C++
- Toolchains: cpp, python
- Implementation: https://github.com/defreez-ucd/func2vec-fse2018-artifact
- Note: We need to investigate how to produce vectors representing the functions.

#### [Code Vectors](resources/pdf/codevectors.pdf)

- Task: code embedding for three different tasks
- Language: C/C++
- Toolchains: python
- Implementation: https://github.com/jjhenkel/code-vectors-artifact
- Note: It uses symbolic traces of a program. We need to investigate how to produce vectors from the source code.

## Difficulties

- We need to build up an unified dataset from real-world open-source projects.
- Some of the tools are not publicly.
- The programming language of vulnerabilities they can detect varies, so we may need to re-implement some of the tools.

## Results

Due to different tool kits (antlr, svf) with different versions, different model framework (pytorch-lightning) with different settings and parameters' initializing randomness, the result can be different from previous papers (better or worse).

## Deprecated

### [Improving Bug Detection via Context-Based Code Representation Learning and Attention-Based Neural Networks](resources/pdf/3360588.pdf)

- Task: 0/1 Vulnerability Detection
- Language: Java
- Toolchains: java, python
- Implementation: https://github.com/OOPSLA-2019-BugDetection/OOPSLA-2019-BugDetection
- Note: We need to re-implement a c/c++ version, which is extremely challenging because its framework is very complicated. Also, the config of the neural network is not publicly currently.

### [DeepBugs](resources/pdf/deepbugs.pdf)

- Task: 0/1 name-based bug detection
- Language: JavaScript
- Toolchains: python
- Implementation: https://github.com/michaelpradel/DeepBugs
- Dataset: https://github.com/michaelpradel/DeepBugs/tree/master/data/js
- Note: we need to re-implement a c/c++ version. The implementation seems complicated and takes time to re-implement. We need to find a robust c/cpp parser to generate the AST and implement the algorithm by strictly following the paper.

### [Nice2Predict](resources/pdf/alon2018.pdf)

- Task: code embedding for predicting numerous program properties
- Language: JS
- Toolchains: java, python
- Implementation:
  - Path extraction: [PigeonJS](https://github.com/tech-srl/PigeonJS)
  - model: [Nice2Predict](https://github.com/eth-sri/Nice2Predict)
- Note: We need to re-implement a C/C++ version of the path extraction component.


### [CodeNN](resources/pdf/codenn.pdf)

- Task: code embedding for code summarization
- Language: C#/sql/python
- Toolchains: lua, python
- Implementation: https://github.com/sriniiyer/codenn
- Note: We need to re-implement a C/C++ version of the pre-processing component.

### [DeepSim](resources/pdf/deepsim.pdf)

- Task: code embedding for code clone detection
- Language: Java
- Toolchains: python
- Implementation: https://github.com/parasol-aser/deepsim
- Note: We need to re-implement a C/C++ version.

### [LEARNING TO REPRESENT PROGRAMS WITH GRAPHS](resources/pdf/1711.00740.pdf)

- Task: VARNAMING and VARMISUSE
- Language: C#
- Toolchains: python
- Implementation: https://github.com/microsoft/tf-gnn-samples
- Note: We need to re-implement a C/C++ version.


https://lilicoding.github.io/papers/zhan2020automated.pdf