# A Large-Scale Empirical Study on the Usage Scenario of Learning-Based Vulnerability Detection

## What do we have?

- real world data with label from NVD
- implementation using astminer (token, code2vec, code2seq, astnn) and SVF (Vuldeepecker, SySeVR, μVuldeepecker, VGDetector)
- summarizaiton of existing efforts

## RQs

> Do we need heavy semantic analysis regarding all vul categories?

We attempt to investigate the importance of lexical, syntactic and semantic information when detecting different kinds of vulnerability, and balance the effectiveness and the cost of program analysis. Collect the gaps of (1) effectiveness and (2) pre-processing time cost.

> For semantic analysis, do we need more precise program analysis?

SVF can provide way more precise result (inter-procedural, context-sensitive, alias-aware) than Joern. We aim to find wether more precise program analysis can help boost the effectiveness significantly. Here we can use some of our dataset without considering vulnerability types.

> Can different neural network model enhance the effectiveness?

Compare SVM/RF, TextCNN, RNN, transformers, attention, graph neural network or mixed.

> Can these tools actually help developers fix the bug? Is it the same with regard to all vul types?

The usefulness of facilitating bug fixing for different vul categories. For example, some vulnerabilities need the value flow from and to the key point in order to find what step goes wrong.

**Important:**

- We should build our benchmark based on real-world projects through analyzing CPEs, commit messages and bug reports. (e.g., NVD, https://security-tracker.debian.org/tracker/, https://bugs.chromium.org/p/chromium/issues/list)
- We need to collect enough samples and can analyze big projects, so building all project is not applicable considering that we have limited computing resources.
- We can leverage [ReVeal](https://github.com/VulDetProject/ReVeal), which is based on [Joern](https://joern.io/), whose parser is the same as our token and AST-based method.

## TODO

- Use Joern to re-implement Vuldeepecker, SySeVR, μVuldeepecker, VGDetector and Devign.
- Collect more data and take a deeper look into the pattern of different vulnerabilities.
- Use different model.
- User study.


分类 用少数词概括研究问题，由层次感和针对性，问题不能简单yes or no
能否提高以及程度

对比 递进 ablation