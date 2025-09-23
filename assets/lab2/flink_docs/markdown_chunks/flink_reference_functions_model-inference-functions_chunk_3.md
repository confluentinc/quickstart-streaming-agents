---
document_id: flink_reference_functions_model-inference-functions_chunk_3
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 8
---

ROW) AS anomalies FROM test_table;

## ML_EVALUATE¶

Aggregate a table and return model evaluation metrics.

Syntax

    ML_EVALUATE(`model_name`, label, col1, col2, ...) FROM 'eval_data_table';

### Description¶

The ML_EVALUATE function is a table aggregation function that takes an entire table and returns a single row of model evaluation metrics. If run on all versions of a model, the function returns one row for each model version. After comparing the metrics for different versions, you can update the default version for deployment with the model that has the best evaluation metrics.

Internally, the ML_EVALUATE function runs ML_PREDICT and processes the results.

Before using ML_EVALUATE, you must register the model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement.

The first argument to the ML_EVALUATE table function is the model name. The second argument is the true label that the output of the model should be evaluated against. Its type depends on the model OUTPUT type and the model task. The other arguments are the columns used for prediction. They are defined in the model resource INPUT for AI models and may vary in length or type.

The return type of the ML_EVALUATE function is `Map<String, Double>` for all types of tasks. Each task type has different metrics keys in the map, depending on the task type.

### Metrics¶

The metric columns returned by ML_EVALUATE depend on the [task type](../statements/create-model.html#flink-sql-create-model-task-types) of the specified model.

#### Classification¶

Classification models choose a group to place their inputs in and return one of N possible values. A classification model that returns only 2 possible values is called a _binary classifier_. If it returns more than 2 values, it is referred to as _multi-class_.

Classification models return these metrics:

* [Accuracy](https://en.wikipedia.org/wiki/Accuracy_and_precision): Total Fraction of correct predictions across all classes.
* [F1 Score](https://en.wikipedia.org/wiki/F1_score): Harmonic mean of precision and recall.
* [Precision](https://en.wikipedia.org/wiki/Precision_and_recall): (Class X Correctly Predicted) / (# of Class X Predicted)
* [Recall](https://en.wikipedia.org/wiki/Precision_and_recall): (Class X Correctly Predicted) / (# of actual Class X)

#### Clustering¶

Clustering models group the model examples into K groups. Metrics are a measure of how compact the clusters are.

Clustering models return these metrics:

* [Davies Bouldin Index](https://en.wikipedia.org/wiki/Davies%E2%80%93Bouldin_index): A measure of how separated clusters are and how compact they are.
* Intra-Cluster Variance (Mean Squared Distance): Average Squared distance of each training point to the centroid of the cluster it was assigned to.
* [Silhouette Score](https://en.wikipedia.org/wiki/Silhouette_\(clustering\)): Compares how similar each point is to its own cluster with how dissimilar it is to other clusters.

#### Embedding¶

Embedding models return these metrics:

* [Mean Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity): A measure of how similar two vectors are.
* [Mean Jaccard Similarity](https://en.wikipedia.org/wiki/Jaccard_index): A measure of how similar two sets are.
* [Mean Euclidean Distance](https://en.wikipedia.org/wiki/Euclidean_distance): A measure of how similar two vectors are.

#### Regression¶

Regression models predict a continuous output variable based on one or more input features.

Regression models return these metrics:

* [Mean Absolute Error](https://en.wikipedia.org/wiki/Mean_absolute_error): The average of the absolute differences between the predicted and actual values.
* [Mean Squared Error](https://en.wikipedia.org/wiki/Mean_squared_error): The average of the squared differences between the predicted and actual values.

#### Text generation¶

Text generation models generate text based on a prompt. Text generation models return these metrics:

* [Mean BLEU](https://en.wikipedia.org/wiki/BLEU): A measure of how similar two texts are.
* [Mean ROUGE](https://en.wikipedia.org/wiki/ROUGE_\(metric\)): A measure of how similar two texts are.
* [Mean Semantic Similarity](https://en.wikipedia.org/wiki/Semantic_similarity): A measure of how similar two texts are.

#### Example metrics¶

The following table shows example metrics for different task types.

Task type | Example metrics
---|---
Classification | {Accuracy=0.9999991465990892, Precision=0.9996998081063332, Recall=0.0013025368892873059, F1=0.0013025368892873059}
Clustering | {Mean Davies-Bouldin Index=0.9999991465990892}
Embedding | {Mean Cosine Similarity=0.9999991465990892, Mean Jaccard Similarity=0.9996998081063332, Mean Euclidean Distance=0.0013025368892873059}
Regression | {MAE=0.9999991465990892, MSE=0.9996998081063332, RMSE=0.0013025368892873059, MAPE=0.0013025368892873059, R²=0.0043025368892873059}
Text generation | {Mean BLEU=0.9999991465990892, Mean ROUGE=0.9996998081063332, Mean Semantic Similarity=0.0013025368892873059}

### Example¶
