---
document_id: flink_reference_statements_create-model_chunk_7
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 7
---

### Other formats¶

The following formats are intended for predictive models running on providers like Sagemaker, Vertex AI, and Azure ML. Usually, these models are used for tasks like classification, regression, and clustering.

Currently, none of these formats support PARAMS.

Unless specified, each input format defaults to the associated output format with the same name.

#### AZUREML-PANDAS-DATAFRAME¶

[Azure ML’s version](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models#payload-example-for-a-json-serialized-pandas-dataframe-in-the-split-orientation) of the Pandas Dataframe Split format. The only difference is that this version has “input_data” as the top-level field, instead of “dataframe_split”.

This is the default format for Azure ML models.

The output format defaults to JSON-ARRAY.

#### AZUREML-TENSOR¶

[Azure ML’s version](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models#payload-example-for-a-named-tensor-input) of named input tensors. Equivalent to the “JSON:input_data” input format. the output format defaults to “JSON:outputs”.

#### BINARY¶

Raw binary inputs, serialized in little-endian byte order. This input format accepts multiple input columns, which are packed in order.

#### CSV¶

Comma separated text. This is the default format for Sagemaker models, but Sagemaker models vary widely, and most models must choose a different format.

#### JSON¶

The inputs are formatted as a JSON object, with field names equal to the column names of the model input schema.

The JSON format supports user-defined parameters. If you specify `'{provider}.params.some_key'='value'` in the WITH options, the key and value are used in the JSON input as `{"some_key": "value"}`.

Example:

    {
      "column1": "String Data",
      "column2": [1,2,3,4]
    }

#### JSON-ARRAY¶

The inputs are formatted as a JSON array, including [] brackets, but without the {} braces of a top-level JSON object. Column names are not included in the format.

If the model takes a single input array column, it will be output as the top-level array. Models with multiple inputs have their arrays nested in JSON fashion.

This format is usually appropriate for models that expect Numpy arrays.

Example:

    [1,2,3,"String Data"]

#### JSON:wrapper¶

Similar to the default JSON behavior, but all fields are wrapped in a named top-level object. The wrapper may be any valid JSON string.

Example:

    {
      "wrapper": {
        "column1": "String Data",
        "column2: [1,2,3,4]
      }
    }

#### KSERVE-V1¶

Same as the TF-SERVING format.

#### KSERVE-V2¶

Same as the TRITON format.

#### MLFLOW-TENSOR¶

The format used by some MLFlow models. It is the same format as TF-SERVING-COLUMN.

#### PANDAS-DATAFRAME¶

The [Pandas Dataframe Split](https://mlflow.org/docs/latest/deployment/deploy-model-locally.html#json-input) format used by most MLFlow models.

The output format defaults to JSON-ARRAY.

#### TEXT¶

Model input values formatted as raw text. Use newlines to separate multiple inputs.

#### TF-SERVING¶

The [Tensorflow Serving Row](https://www.tensorflow.org/tfx/serving/api_rest#request_format_2) format. This is the default format for Vertex AI models. It is generally the correct format to use for most predictive models trained in Vertex AI.

#### TF-SERVING-COLUMN¶

The [TensorFlow Serving Column](https://www.tensorflow.org/tfx/serving/api_rest#specifying_input_tensors_in_column_format) format. It is exactly equivalent to “JSON:inputs”. The output format defaults to “JSON:outputs”.

#### TRITON¶

The [Triton/KServeV2](https://github.com/kserve/kserve/blob/master/docs/predict-api/v2/required_api.md) format used by NVidia Triton Inference Servers.

When possible, this format serializes data in the protocol’s mixed json+binary format. Note that some Tensor datatypes, like 16-bit floats, do not have an exact equivalent in Flink SQL, but they are converted, when possible.

#### VERTEXAI-PYTORCH¶

[Vertex AI’s format for PyTorch models](https://cloud.google.com/vertex-ai/docs/predictions/get-online-predictions#request-body-details). This format is the TF-SERVING format with an extra wrapper around the data.

The output format defaults to TF-SERVING.
