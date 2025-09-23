---
source_url: https://docs.confluent.io/platform/current/flink/clients-api/rest.html
title: REST APIs for Confluent Manager for Apache Flink
hierarchy: ['platform', 'clients-api', 'rest.html']
scraped_date: 2025-09-05T13:51:47.846988
---

# REST APIs for Confluent Manager for Apache Flink¶

You can use the Confluent REST API to manage these resources for Confluent Manager for Apache Flink® (CMF):

  * Environments
  * Applications

In addition to the REST API, you can manage the above resources by using these Confluent tools:

  * [Confluent CLI](/confluent-cli/current/command-reference/flink/index.html)
  * [Confluent for Kubernetes](https://docs.confluent.io/operator/current/co-manage-flink.html)

## Prerequisites¶

The REST API requires networked access to CMF.

As part of the installation process, a Kubernetes service is created that exposes CMF behind an outward-facing endpoint. By default, the service exposes CMF on port 8080.

If you have configured authentication and/or authorization, each API request must be authenticated and you need permissions on the respective resource.

For more information, see:

  * [Installation with Helm](../installation/helm.html#install-cmf-helm)
  * [Access Control](../configure/access-control.html#cmf-access-control)

## Endpoints (v1)¶

All endpoints are served under `/cmf/api/v1`.

## Identifiers¶

All resources are identified by name. Each name must be unique in its scope and follow the following restrictions:

  * Minimum length: 4
  * Maximum length: 253
  * Pattern: ^[a-z0-9]([-a-z0-9]*[a-z0-9])?(.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$

## Timestamps¶

All timestamps in fields named `metadata.creationTimestamp` and `metadata.updateTimestamp` and the `created_time` and `updated_time` fields in the Environment are RFC 3339 formatted strings, compatible with Java’s [Instant](https://docs.oracle.com/javase/8/docs/api/java/time/Instant.html) type.

The timestamp is in UTC, and does not contain any timezone information.name

This is an example: `2025-03-31T11:34:01.503Z`.

## Example usage with curl¶

The following example shows how to create a Flink Application in an environment called “test” using curl:

Contents of the file `flink-application.yaml`:

    apiVersion: cmf.confluent.io/v1
    kind: FlinkApplication
    metadata:
      name: curl-example
    spec:
      image: confluentinc/cp-flink:1.19.1-cp2
      flinkVersion: v1_19
      flinkConfiguration:
        taskmanager.numberOfTaskSlots: "1"
      serviceAccount: flink
      jobManager:
        resource:
          memory: 1024m
          cpu: 1
      taskManager:
        resource:
          memory: 1024m
          cpu: 1
      job:
        jarURI: local:///opt/flink/examples/streaming/StateMachineExample.jar
        state: running
        parallelism: 3
        upgradeMode: stateless

Submission using `curl`, assuming CMF is running on `localhost:8080`:

    curl -H "Content-type: application/yaml" --data-binary "@flink-application.yaml" localhost:8080/cmf/api/v1/environments/test/applications

## API reference¶

This section contains the REST API reference for Confluent Manager for Apache Flink® and the API spec.

### View the API spec¶

If you want to see the entire API spec, you can view the YAML file in the expanding section below.

View the entire YAML specification file

    # Naming conventions:
    # - Post*: Schemas for POST requests
    # - Get*: Schemas for GET requests
    # Good resources:
    # - Spring Petclinic: https://github.com/spring-petclinic/spring-petclinic-rest/blob/master/src/main/resources/openapi.yml
    openapi: 3.0.1
    info:
      title: Confluent Manager for Apache Flink / CMF
      description: Apache Flink job lifecycle management component for Confluent Platform.
      version: '1.0'
    servers:
      - url: http://localhost:8080
    paths:
      ## ---------------------------- Environments API ---------------------------- ##

      /cmf/api/v1/environments:
        post:
          operationId: createOrUpdateEnvironment
          summary: Create or update an Environment
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/PostEnvironment'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/PostEnvironment'
            required: true
          responses:
            201:
              description: The Environment was successfully created or updated.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Environment'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Environment'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getEnvironments
          summary: Retrieve a paginated list of all environments.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
          responses:
            200:
              description: List of environments found. If no environments are found, an empty list is returned. Note the information about secret is not included in the list call yet. In order to get the information about secret, make a getSecret call.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EnvironmentsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EnvironmentsPage'
            304:
              description: Not modified.
              headers:
                ETag:
                  description: An ID for this version of the response.
                  schema:
                    type: string
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}:
        get:
          operationId: getEnvironment
          summary: Get/Describe an environment with the given name.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment to be retrieved.
              required: true
              schema:
                type: string
          responses:
            200:
              description: Environment found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Environment'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Environment'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteEnvironment
          parameters:
            - name: envName
              in: path
              description: Name of the Environment to be deleted.
              required: true
              schema:
                type: string
          responses:
            200:
              description: Environment found and deleted.
            304:
              description: Not modified.
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Applications API ---------------------------- ##
      /cmf/api/v1/environments/{envName}/applications:
        post:
          operationId: createOrUpdateApplication
          summary: Creates a new Flink Application or updates an existing one in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/FlinkApplication'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/FlinkApplication'
            required: true
          responses:
            201:
              description: The Application was successfully created or updated.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getApplications
          summary: Retrieve a paginated list of all applications in the given Environment.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          responses:
            200:
              description: Application found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ApplicationsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/ApplicationsPage'
            304:
              description: Not modified.
              headers:
                ETag:
                  description: An ID for this version of the response.
                  schema:
                    type: string
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/applications/{appName}:
        get:
          operationId: getApplication
          summary: Retrieve an Application of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Application found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
            304:
              description: Not modified.
              headers:
                ETag:
                  description: An ID for this version of the response.
                  schema:
                    type: string
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Application not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteApplication
          summary: Deletes an Application of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Application found and deleted.
            304:
              description: Not modified.
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1alpha1/environments/{envName}/applications/{appName}/events:
        get:
          operationId: getApplicationEvents
          summary: Get a paginated list of events of the given Application
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Events found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EventsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EventsPage'
            404:
              description: Environment or Application not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/applications/{appName}/start:
        post:
          operationId: startApplication
          summary: Starts an earlier submitted Flink Application
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Application started
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
            304:
              description: Not modified.
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/applications/{appName}/suspend:
        post:
          operationId: suspendApplication
          summary: Suspends an earlier started Flink Application
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Application suspended
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/FlinkApplication'
            304:
              description: Not modified.
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/applications/{appName}/instances:
        get:
          operationId: getApplicationInstances
          summary: Get a paginated list of instances of the given Application
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
          responses:
            200:
              description: Instances found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ApplicationInstancesPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/ApplicationInstancesPage'
            404:
              description: Environment or Application not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/applications/{appName}/instances/{instName}:
        get:
          operationId: getApplicationInstance
          summary: Retrieve an Instance of an Application
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: appName
              in: path
              description: Name of the Application
              required: true
              schema:
                type: string
            - name: instName
              in: path
              description: Name of the ApplicationInstance
              required: true
              schema:
                type: string
          responses:
            200:
              description: ApplicationInstance found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/FlinkApplicationInstance'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/FlinkApplicationInstance'
            404:
              description: FlinkApplicationInstance or environment or application not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Environment Secret Mapping API ---------------------------- ##

      /cmf/api/v1/environments/{envName}/secret-mappings/{name}:
        delete:
          operationId: deleteEnvironmentSecretMapping
          summary: Deletes the Environment Secret Mapping for the given Environment and Secret.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment in which the mapping has to be deleted.
              required: true
              schema:
                type: string
            - name: name
              in: path
              description: Name of the environment secret mapping to be deleted in the given environment.
              required: true
              schema:
                type: string
          responses:
            204:
              description: The Environment Secret Mapping was successfully deleted.
            404:
              description: Environment or Secret not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getEnvironmentSecretMapping
          summary: Retrieve the Environment Secret Mapping for the given name in the given environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: name
              in: path
              description: Name of the environment secret mapping to be retrieved.
              required: true
              schema:
                type: string
          responses:
            200:
              description: Environment Secret Mapping found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
            404:
              description: Environment or Secret not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        put:
          operationId: updateEnvironmentSecretMapping
          summary:
            Updates the Environment Secret Mapping for the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: name
              in: path
              description: Name of the environment secret mapping to be updated
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/EnvironmentSecretMapping'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/EnvironmentSecretMapping'
            required: true
          responses:
            200:
              description: The Environment Secret Mapping was successfully updated.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Environment or Secret not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/secret-mappings:
        post:
          operationId: createEnvironmentSecretMapping
          summary: Creates the Environment Secret Mapping for the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/EnvironmentSecretMapping'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/EnvironmentSecretMapping'
            required: true
          responses:
            200:
              description: The Environment Secret Mapping was successfully created.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: Environment Secret Mapping already exists.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getEnvironmentSecretMappings
          summary: Retrieve a paginated list of all Environment Secret Mappings.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          responses:
            200:
              description: Environment Secret Mappings found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMappingsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/EnvironmentSecretMappingsPage'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Statement API ---------------------------- ##

      /cmf/api/v1/environments/{envName}/statements:
        post:
          operationId: createStatement
          summary: Creates a new Flink SQL Statement in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Statement'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/Statement'
            required: true
          responses:
            200:
              description: The Statement was successfully created.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Statement'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Statement'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: Statement already exists.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getStatements
          summary: Retrieve a paginated list of Statements in the given Environment.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - $ref: '#/components/parameters/computePoolParam'
            - $ref: '#/components/parameters/phaseParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          responses:
            200:
              description: Statements found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/StatementsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/StatementsPage'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/statements/{stmtName}:
        get:
          operationId: getStatement
          summary: Retrieve the Statement of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: stmtName
              in: path
              description: Name of the Statement
              required: true
              schema:
                type: string
          responses:
            200:
              description: Statement found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Statement'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Statement'
            404:
              description: Statement not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteStatement
          summary: Deletes the Statement of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: stmtName
              in: path
              description: Name of the Statement
              required: true
              schema:
                type: string
          responses:
            204:
              description: Statement was found and deleted.
            202:
              description: Statement was found and deletion request received.
            404:
              description: Statement not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        put:
          operationId: updateStatement
          summary: Updates a Statement of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: stmtName
              in: path
              description: Name of the Statement
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Statement'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/Statement'
            required: true
          responses:
            200:
              description: Statement was found and updated.
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Statement not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/statements/{stmtName}/results:
        get:
          operationId: getStatementResult
          summary: Retrieve the result of the interactive Statement with the given name in the given Environment.
          parameters:
            - $ref: '#/components/parameters/pageTokenParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: stmtName
              in: path
              description: Name of the Statement
              required: true
              schema:
                type: string
          responses:
            200:
              description: StatementResults found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/StatementResult'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/StatementResult'
            400:
              description: Statement does not return results.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Statement not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            410:
              description: Results are gone.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/statements/{stmtName}/exceptions:
        get:
          operationId: getStatementExceptions
          summary: Retrieves the last 10 exceptions of the Statement with the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: stmtName
              in: path
              description: Name of the Statement
              required: true
              schema:
                type: string
          responses:
            200:
              description: StatementExceptions found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/StatementExceptionList'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/StatementExceptionList'
            404:
              description: Statement not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Compute Pool API ---------------------------- ##
      /cmf/api/v1/environments/{envName}/compute-pools:
        post:
          operationId: createComputePool
          summary: Creates a new Flink Compute Pool in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/ComputePool'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/ComputePool'
            required: true
          responses:
            200:
              description: The Compute Pool was successfully created.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ComputePool'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/ComputePool'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: Compute Pool already exists.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getComputePools
          summary: Retrieve a paginated list of Compute Pools in the given Environment.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
          responses:
            200:
              description: Compute Pools found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ComputePoolsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/ComputePoolsPage'
            404:
              description: Environment not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/environments/{envName}/compute-pools/{computePoolName}:
        get:
          operationId: getComputePool
          summary: Retrieve the Compute Pool of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: computePoolName
              in: path
              description: Name of the Compute Pool
              required: true
              schema:
                type: string
          responses:
            200:
              description: Compute Pool found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ComputePool'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/ComputePool'
            404:
              description: Compute Pool not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteComputePool
          summary: Deletes the ComputePool of the given name in the given Environment.
          parameters:
            - name: envName
              in: path
              description: Name of the Environment
              required: true
              schema:
                type: string
            - name: computePoolName
              in: path
              description: Name of the ComputePool
              required: true
              schema:
                type: string
          responses:
            204:
              description: Compute Pool was found and deleted.
            404:
              description: Compute Pool not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: Compute Pool is in use and cannot be deleted.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Secrets API ---------------------------- ##

      /cmf/api/v1/secrets:
        post:
          operationId: createSecret
          summary: Create a Secret.
          description: Create a Secret. This secrets can be then used to specify sensitive information in the Flink SQL statements. Right now these secrets are only used for Kafka and Schema Registry credentials.
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Secret'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/Secret'
            required: true
          responses:
            200:
              description: The Secret was successfully created. Note that for security reasons, you can never view the contents of the secret itself once created.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Secret'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Secret'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: The Secret already exists.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getSecrets
          summary: Retrieve a paginated list of all secrets. Note that the actual secret data is masked for security reasons.
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
          responses:
            200:
              description: List of secrets found. If no secrets are found, an empty list is returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/SecretsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/SecretsPage'
            304:
              description: The list of secrets has not changed.
              headers:
                ETag:
                  description: An ID for this version of the response.
                  schema:
                    type: string
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/secrets/{secretName}:
        get:
          operationId: getSecret
          summary: Retrieve the Secret of the given name. Note that the secret data is not returned for security reasons.
          parameters:
            - name: secretName
              in: path
              description: Name of the Secret
              required: true
              schema:
                type: string
          responses:
            200:
              description: Secret found and returned, with security data masked.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Secret'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Secret'
            404:
              description: Secret not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        put:
          operationId: updateSecret
          summary: Update the secret.
          parameters:
            - name: secretName
              in: path
              description: Name of the Secret
              required: true
              schema:
                type: string
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Secret'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/Secret'
          responses:
            200:
              description: Returns the updated Secret
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/Secret'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/Secret'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            404:
              description: Secret with the given name not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteSecret
          summary: Delete the secret with the given name.
          parameters:
            - name: secretName
              in: path
              description: Name of the Secret
              required: true
              schema:
                type: string
          responses:
            204:
              description: Secret was successfully deleted.
            404:
              description: Secret not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

      ## ---------------------------- Catalog API ---------------------------- ##

      /cmf/api/v1/catalogs/kafka:
        post:
          operationId: createKafkaCatalog
          summary: Creates a new Kafka Catalog that can be referenced by Flink Statements
          requestBody:
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/KafkaCatalog'
              application/yaml:
                schema:
                  $ref: '#/components/schemas/KafkaCatalog'
            required: true
          responses:
            200:
              description: The Kafka Catalog was successfully created.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalog'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalog'
            400:
              description: Bad request.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            409:
              description: Kafka Catalog already exists.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            422:
              description: Request valid but invalid content.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        get:
          operationId: getKafkaCatalogs
          summary: Retrieve a paginated list of Kafka Catalogs
          x-spring-paginated: true
          parameters:
            - $ref: '#/components/parameters/pageParam'
            - $ref: '#/components/parameters/sizeParam'
            - $ref: '#/components/parameters/sortParam'
          responses:
            200:
              description: Kafka Catalogs found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalogsPage'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalogsPage'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
      /cmf/api/v1/catalogs/kafka/{catName}:
        get:
          operationId: getKafkaCatalog
          summary: Retrieve the Kafka Catalog of the given name.
          parameters:
            - name: catName
              in: path
              description: Name of the Kafka Catalog
              required: true
              schema:
                type: string
          responses:
            200:
              description: Kafka Catalog found and returned.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalog'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/KafkaCatalog'
            404:
              description: Kafka Catalog not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
        delete:
          operationId: deleteKafkaCatalog
          summary: Deletes the Kafka Catalog of the given name.
          parameters:
            - name: catName
              in: path
              description: Name of the Kafka Catalog
              required: true
              schema:
                type: string
          responses:
            204:
              description: Kafka Catalog was found and deleted.
            404:
              description: Kafka Catalog not found.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'
            500:
              description: Server error.
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/RestError'
                application/yaml:
                  schema:
                    $ref: '#/components/schemas/RestError'

    components:
      # https://github.com/daniel-shuy/swaggerhub-spring-pagination / Copyright (c) 2023 Daniel Shuy
      parameters:
        pageParam:
          in: query
          name: page
          schema:
            type: integer
          description: Zero-based page index (0..N)
        sizeParam:
          in: query
          name: size
          schema:
            type: integer
          description: The size of the page to be returned
        sortParam:
          in: query
          name: sort
          schema:
            type: array
            items:
              type: string
          description: >-
            Sorting criteria in the format: property,(asc|desc). Default sort order is ascending.
            Multiple sort criteria are supported.
        pageTokenParam:
          in: query
          name: page-token
          schema:
            type: string
          description: Token for the next page of results
        computePoolParam:
          in: query
          name: compute-pool
          schema:
            type: string
          description: Name of the ComputePool to filter on
        phaseParam:
          in: query
          name: phase
          schema:
            type: string
            enum: [pending, running, completed, deleting, failing, failed, stopped]
          description: Phase to filter on
      schemas:
        ## ---------------------------- Shared Utilities ---------------------------- ##
        RestError:
          title: REST Error
          description: The schema for all error responses.
          type: object
          properties:
            errors:
              title: errors
              description: List of all errors
              type: array
              items:
                title: error
                type: object
                description: An error
                properties:
                  message:
                    type: string
                    description: An error message
        PaginationResponse:
          type: object
          properties:
            pageable:
              $ref: '#/components/schemas/Pageable'
        Sort:
          type: object
          format: sort
          properties:
            sorted:
              type: boolean
              description: Whether the results are sorted.
              example: true
            unsorted:
              type: boolean
              description: Whether the results are unsorted.
              example: false
            empty:
              type: boolean
        Pageable:
          type: object
          format: pageable
          properties:
            page:
              type: integer
              minimum: 0
            size:
              type: integer
              description: The number of items in a page.
              minimum: 1
            sort:
              $ref: '#/components/schemas/Sort'

        ## ---------------------------- Shared Bases ---------------------------- ##
        ResourceBaseV2:
          type: object
          properties:
            apiVersion:
              description: API version for spec
              type: string
            kind:
              description: Kind of resource - set to resource type
              type: string
          required:
            - apiVersion
            - kind

        PostResourceBase:
          type: object
          properties:
            name:
              title: Name
              description: A unique name for the resource.
              type: string
              # Validate for DNS subdomain name
              minLength: 4
              maxLength: 253
              pattern: '^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'
        GetResourceBase:
          type: object
          properties:
            created_time:
              title: Time when the resource has been created
              type: string
              format: date-time
            updated_time:
              title: Time when the resource has been last updated
              type: string
              format: date-time
        # defines kubernetesNamespace
        KubernetesNamespace:
          type: object
          properties:
            kubernetesNamespace:
              type: string
              title: Kubernetes namespace name where resources referencing this environment are created in.
              minLength: 1
              maxLength: 253
              pattern: '^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'
        # defines properties of fields with flinkApplicationDefaults
        ResourceWithFlinkApplicationDefaults:
          type: object
          properties:
            flinkApplicationDefaults:
              title: the defaults as YAML or JSON for FlinkApplications
              type: object
              format: yamlorjson
        # defines computePool defaults
        ComputePoolDefaults:
          type: object
          properties:
            computePoolDefaults:
              title: ComputePoolDefaults
              description: the defaults as YAML or JSON for ComputePools
              type: object
              format: yamlorjson
        # defines statement defaults
        StatementDefaults:
          type: object
          properties:
            flinkConfiguration:
              description: default Flink configuration for Statements
              type: object
              additionalProperties:
                type: string
        # defines defaults for detached and interactive statements
        AllStatementDefaults:
          type: object
          properties:
            statementDefaults:
              title: AllStatementDefaults
              description: the defaults for detached and interactive Statements
              type: object
              properties:
                detached:
                  description: defaults for detached statements
                  $ref: '#/components/schemas/StatementDefaults'
                interactive:
                  description: defaults for interactive statements
                  $ref: '#/components/schemas/StatementDefaults'

        ## ---------------------------- Request Schemas ---------------------------- ##
        PostEnvironment:
          title: Environment
          description: Environment
          type: object
          required:
            - name
          allOf:
            - $ref: '#/components/schemas/PostResourceBase'
            - $ref: '#/components/schemas/ResourceWithFlinkApplicationDefaults'
            - $ref: '#/components/schemas/KubernetesNamespace'
            - $ref: '#/components/schemas/ComputePoolDefaults'
            - $ref: '#/components/schemas/AllStatementDefaults'

        ## ---------------------------- Response Schemas ---------------------------- ##
        Environment:
          title: Environment
          description: Environment
          type: object
          allOf:
            - $ref: '#/components/schemas/PostResourceBase'
            - $ref: '#/components/schemas/GetResourceBase'
            - $ref: '#/components/schemas/ResourceWithFlinkApplicationDefaults'
            - $ref: '#/components/schemas/KubernetesNamespace'
            - $ref: '#/components/schemas/ComputePoolDefaults'
            - $ref: '#/components/schemas/AllStatementDefaults'
          properties:
            secrets:
              title: Secrets
              description: The secrets mapping for the environment. This is a mapping between connection_secret_id and the secret name.
              type: object
              additionalProperties:
                type: string
              default: { }
          required:
            - name
            - kubernetesNamespace

        EnvironmentSecretMapping:
          title: EnvironmentSecretMapping
          description: The secrets mapping for the environment. The name shows the name of the Connection Secret ID to be mapped.
          type: object
          properties:
            apiVersion:
              title: API version for EnvironmentSecretMapping spec
              type: string
            kind:
              title: Kind of resource - set to EnvironmentSecretMapping
              type: string
            metadata:
              title: EnvironmentSecretMappingMetadata
              description: Metadata about the environment secret mapping
              type: object
              properties:
                name:
                  description: Name of the Connection Secret ID
                  type: string
                uid:
                  description: Unique identifier of the EnvironmentSecretMapping
                  type: string
                creationTimestamp:
                  description: Timestamp when the EnvironmentSecretMapping was created
                  type: string
                updateTimestamp:
                  description: Timestamp when the EnvironmentSecretMapping was last updated
                  type: string
                labels:
                  description: Labels of the EnvironmentSecretMapping
                  type: object
                  additionalProperties:
                    type: string
                annotations:
                  description: Annotations of the EnvironmentSecretMapping
                  type: object
                  additionalProperties:
                    type: string
            spec:
              title: EnvironmentSecretMappingSpec
              description: Spec for environment secret mapping
              type: object
              writeOnly: true
              properties:
                secretName:
                  description: Name of the secret to be mapped to the connection secret id of this mapping.
                  type: string
              required:
                - secretName
          required:
            - apiVersion
            - kind

        EnvironmentSecretMappingsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: EnvironmentSecretMappingsPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/EnvironmentSecretMapping'
                  default: [ ]

        Secret:
          title: Secret
          description: Represents a Secret that can be used to specify sensitive information in the Flink SQL statements.
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: SecretMetadata
                  description: Metadata about the secret
                  type: object
                  properties:
                    name:
                      type: string
                      description: Name of the Secret
                    creationTimestamp:
                      description: Timestamp when the Secret was created
                      type: string
                      readOnly: true
                    updateTimestamp:
                      description: Timestamp when the Secret was last updated
                      type: string
                      readOnly: true
                    uid:
                      description: Unique identifier of the Secret
                      type: string
                      readOnly: true
                    labels:
                      description: Labels of the Secret
                      type: object
                      additionalProperties:
                        type: string
                    annotations:
                      description: Annotations of the Secret
                      type: object
                      additionalProperties:
                        type: string
                  required:
                    - name
                spec:
                  title: SecretSpec
                  description: Spec for secret
                  type: object
                  writeOnly: true
                  properties:
                    data:
                      title: SecretData
                      description: Data of the secret
                      type: object
                      additionalProperties:
                        type: string
                status:
                  title: SecretStatus
                  description: Status for the secret
                  type: object
                  readOnly: true
                  properties:
                    version:
                      title: SecretVersion
                      description: The version of the secret
                      type: string
                    environments:
                      title: Environments
                      description: The environments to which the secret is attached to.
                      type: array
                      items:
                        type: string
              required:
                - metadata
                - spec

        SecretsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: SecretsPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Secret'
                  default: [ ]

        EnvironmentsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: EnvironmentsPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  title: "Env"
                  items:
                    $ref: '#/components/schemas/Environment'
                  default: [ ]

        FlinkApplication:
          title: FlinkApplication
          description: Represents a Flink Application submitted by the user
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: Metadata about the application
                  type: object
                  format: yamlorjson
                spec:
                  title: Spec for Flink Application
                  type: object
                  format: yamlorjson
                status:
                  title: Status for Flink Application
                  type: object
                  format: yamlorjson
              required: # status is optional for application spec
                - metadata
                - spec

        ApplicationsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: ApplicationPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/FlinkApplication'
                  default: [ ]

        FlinkApplicationEvent:
          title: FlinkApplicationEvent
          description: Events from the deployment of Flink clusters
          # TODO(CF-1159): Using the ResourceBaseV2 here leads to incorrectly generated EventType where the generated interface doesn't match the file name causing compilation errors.
          type: object
          properties:
            apiVersion:
              title: API version for Event spec - set to v1alpha1
              type: string
            kind:
              title: Kind of resource - set to FlinkApplicationEvent
              type: string
            metadata:
              title: EventMetadata
              description: Metadata about the event
              type: object
              properties:
                name:
                  description: Name of the Event
                  type: string
                uid:
                  description: Unique identifier of the Event. Identical to name.
                  type: string
                creationTimestamp:
                  description: Timestamp when the Event was created
                  type: string
                flinkApplicationInstance:
                  description: Name of the FlinkApplicationInstance which this event is related to
                  type: string
                labels:
                  description: Labels of the Event
                  type: object
                  additionalProperties:
                    type: string
                annotations:
                  description: Annotations of the Event
                  type: object
                  additionalProperties:
                    type: string
            status:
              type: object
              title: EventStatus
              properties:
                message:
                  description: Human readable status message.
                  type: string
                type:
                  title: EventType
                  description: Type of the event
                  type: string
                data:
                  $ref: '#/components/schemas/EventData'
          required:
            - kind
            - apiVersion
            - metadata
            - status

        EventDataNewStatus:
          type: object
          properties:
            newStatus:
              description: "The new status"
              type: string

        EventDataJobException:
          type: object
          properties:
            exceptionString:
              description: "The full exception string from the Flink job"
              type: string
        EventData:
          oneOf:
            - $ref: '#/components/schemas/EventDataNewStatus'
            - $ref: '#/components/schemas/EventDataJobException'

        EventsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: EventsPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/FlinkApplicationEvent'
                  default: [ ]

        FlinkApplicationInstance:
          title: ApplicationInstance
          description: An instance of a Flink Application
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: ApplicationInstanceMetadata
                  description: Metadata about the instance
                  type: object
                  properties:
                    name:
                      description: Name of the Instance - a uuid.
                      type: string
                    uid:
                      description: Unique identifier of the instance. Identical to name.
                      type: string
                    creationTimestamp:
                      description: Timestamp when the Instance was created
                      type: string
                    updateTimestamp:
                      description: Timestamp when the Instance status was last updated
                      type: string
                    labels:
                      description: Labels of the instance
                      type: object
                      additionalProperties:
                        type: string
                    annotations:
                      description: Annotations of the instance
                      type: object
                      additionalProperties:
                        type: string
                status:
                  type: object
                  title: ApplicationInstanceStatus
                  properties:
                    spec:
                      description: The environment defaults merged with the FlinkApplication spec at instance creation time
                      type: object
                      format: yamlorjson
                    jobStatus:
                      type: object
                      properties:
                        jobId:
                          description: Flink job id inside the Flink cluster
                          type: string
                        state:
                          description: Tracks the final Flink JobStatus of the instance
                          type: string
        ApplicationInstancesPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: ApplicationInstancesPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/FlinkApplicationInstance'
                  default: [ ]

        Statement:
          title: Statement
          description: Represents a SQL Statement submitted by the user
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: StatementMetadata
                  description: Metadata about the statement
                  type: object
                  properties:
                    name:
                      description: Name of the Statement
                      type: string
                    creationTimestamp:
                      description: Timestamp when the Statement was created
                      type: string
                    updateTimestamp:
                      description: Timestamp when the Statement was updated last
                      type: string
                    uid:
                      description: Unique identifier of the Statement
                      type: string
                    labels:
                      description: Labels of the Statement
                      type: object
                      additionalProperties:
                        type: string
                    annotations:
                      description: Annotations of the Statement
                      type: object
                      additionalProperties:
                        type: string
                  required:
                    - name
                spec:
                  title: StatementSpec
                  description: Spec for statement
                  type: object
                  properties:
                    statement:
                      description: SQL statement
                      type: string
                    properties:
                      title: SessionProperties
                      description: Properties of the client session
                      type: object
                      additionalProperties:
                        type: string
                    flinkConfiguration:
                      title: StatementFlinkConfiguration
                      description: Flink configuration for the statement
                      type: object
                      additionalProperties:
                        type: string
                    computePoolName:
                      description: Name of the ComputePool
                      type: string
                    parallelism:
                      description: Parallelism of the statement
                      type: integer
                      format: int32
                    stopped:
                      description: Whether the statement is stopped
                      type: boolean
                  required:
                    - statement
                    - computePoolName
                status:
                  title: StatementStatus
                  description: Status for statement
                  type: object
                  properties:
                    phase:
                      description: The lifecycle phase of the statement
                      type: string
                    detail:
                      description: Details about the execution status of the statement
                      type: string
                    traits:
                      title: StatementTraits
                      description: Detailed information about the properties of the statement
                      type: object
                      properties:
                        sqlKind:
                          description: The kind of SQL statement
                          type: string
                        isBounded:
                          description: Whether the result of the statement is bounded
                          type: boolean
                        isAppendOnly:
                          description: Whether the result of the statement is append only
                          type: boolean
                        upsertColumns:
                          description: The column indexes that are updated by the statement
                          type: array
                          items:
                            type: integer
                            format: int32
                        schema:
                          title: StatementResultSchema
                          description: The schema of the statement result
                          $ref: '#/components/schemas/ResultSchema'
                  required:
                    - phase
                result:
                  title: StatementResult
                  description: Result of the statement
                  $ref: '#/components/schemas/StatementResult'
              required: # status and result are optional for Statement spec
                - metadata
                - spec

        StatementsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: StatementPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Statement'
                  default: [ ]

        StatementResult:
          title: StatementResult
          description: Represents the result of a SQL Statement
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: StatementResultMetadata
                  description: Metadata about the StatementResult
                  type: object
                  properties:
                    creationTimestamp:
                      description: Timestamp when the StatementResult was created
                      type: string
                    annotations:
                      description: Annotations of the StatementResult
                      type: object
                      additionalProperties:
                        type: string
                results:
                  title: StatementResults
                  description: Results of the Statement
                  type: object
                  properties:
                    data:
                      title: Data
                      type: array
                      items:
                        description: A result row
                        type: object
                        format: yamlorjson
              required:
                - metadata
                - results

        StatementException:
          title: StatementException
          description: Represents an exception that occurred while executing a SQL Statement
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                name:
                  description: Name of the StatementException
                  type: string
                message:
                  description: Message of the StatementException
                  type: string
                timestamp:
                  description: Timestamp when the StatementException was created
                  type: string
              required:
                - name
                - message
                - timestamp

        StatementExceptionList:
          title: StatementExceptionList
          description: Represents a list of exceptions that occurred while executing a SQL Statement
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                data:
                  title: Exceptions
                  description: List of exceptions
                  type: array
                  maxItems: 10
                  items:
                    $ref: '#/components/schemas/StatementException'
                    default: [ ]
              required:
                - data

        DataType:
          title: DataType
          description: Represents a SQL data type
          type: object
          properties:
            type:
              description: Name of the data type of the column
              type: string
            nullable:
              description: Whether the data type is nullable
              type: boolean
            length:
              description: Length of the data type
              type: integer
              format: int32
            precision:
              description: Precision of the data type
              type: integer
              format: int32
            scale:
              description: Scale of the data type
              type: integer
              format: int32
            keyType:
              description: Type of the key in the data type (if applicable)
              $ref: '#/components/schemas/DataType'
              x-go-pointer: true
            valueType:
              description: Type of the value in the data type (if applicable)
              $ref: '#/components/schemas/DataType'
              x-go-pointer: true
            elementType:
              description: Type of the elements in the data type (if applicable)
              $ref: '#/components/schemas/DataType'
              x-go-pointer: true
            fields:
              description: Fields of the data type (if applicable)
              type: array
              items:
                type: object
                title: DataTypeField
                description: Field of the data type
                properties:
                  name:
                    description: Name of the field
                    type: string
                  fieldType:
                    description: Type of the field
                    $ref: '#/components/schemas/DataType'
                    x-go-pointer: true
                  description:
                    description: Description of the field
                    type: string
                required:
                  - name
                  - fieldType
            resolution:
              description: Resolution of the data type (if applicable)
              type: string
            fractionalPrecision:
              description: Fractional precision of the data type (if applicable)
              type: integer
              format: int32
          required:
            - type
            - nullable

        ResultSchema:
          title: ResultSchema
          description: Represents the schema of the result of a SQL Statement
          type: object
          properties:
            columns:
              description: Properites of all columns in the schema
              type: array
              items:
                title: ResultSchemaColumn
                type: object
                properties:
                  name:
                    description: Name of the column
                    type: string
                  type:
                    description: Type of the column
                    $ref: '#/components/schemas/DataType'
                required:
                  - name
                  - type
          required:
            - columns

        ComputePool:
          title: ComputePool
          description: Represents the configuration of a Flink cluster
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  title: ComputePoolMetadata
                  description: Metadata about the ComputePool
                  type: object
                  properties:
                    name:
                      description: Name of the ComputePool
                      type: string
                    creationTimestamp:
                      description: Timestamp when the ComputePool was created
                      type: string
                    uid:
                      description: Unique identifier of the ComputePool
                      type: string
                    labels:
                      description: Labels of the ComputePool
                      type: object
                      additionalProperties:
                        type: string
                    annotations:
                      description: Annotations of the ComputePool
                      type: object
                      additionalProperties:
                        type: string
                  required:
                    - name
                spec:
                  title: ComputePoolSpec
                  description: Spec for ComputePool
                  type: object
                  properties:
                    type:
                      description: Type of the ComputePool
                      type: string
                    clusterSpec:
                      description: Cluster Spec
                      type: object
                      format: yamlorjson
                  required:
                    - type
                    - clusterSpec
                status:
                  title: ComputePoolStatus
                  description: Status for ComputePool
                  type: object
                  properties:
                    phase:
                      description: Phase of the ComputePool
                      type: string
                  required:
                    - phase
              required: # status is optional for ComputePool spec
                - metadata
                - spec

        ComputePoolsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: ComputePoolPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/ComputePool'
                  default: [ ]

        CatalogMetadata:
          title: CatalogMetadata
          description: Metadata about the Catalog
          type: object
          properties:
            name:
              description: Name of the Catalog
              type: string
            creationTimestamp:
              description: Timestamp when the Catalog was created
              type: string
            uid:
              description: Unique identifier of the Catalog
              type: string
            labels:
              description: Labels of the Statement
              type: object
              additionalProperties:
                type: string
            annotations:
              description: Annotations of the Statement
              type: object
              additionalProperties:
                type: string
          required:
            - name

        KafkaCatalog:
          title: KafkaCatalog
          description: Represents a the configuration of a Kafka Catalog
          type: object
          allOf:
            - $ref: '#/components/schemas/ResourceBaseV2'
            - type: object
              properties:
                metadata:
                  $ref: '#/components/schemas/CatalogMetadata'
                spec:
                  title: KafkaCatalogSpec
                  description: Spec of a Kafka Catalog
                  type: object
                  properties:
                    srInstance:
                      description: Details about the SchemaRegistry instance of the Catalog
                      type: object
                      properties:
                        connectionConfig:
                          description: connection options for the SR client
                          type: object
                          additionalProperties:
                            type: string
                        connectionSecretId:
                          description: an identifier to look up a Kubernetes secret that contains the connection credentials
                          type: string
                      required:
                        - connectionConfig
                    kafkaClusters:
                      type: array
                      items:
                        type: object
                        properties:
                          databaseName:
                            description: the database name under which the Kafka cluster is listed in the Catalog
                            type: string
                          connectionConfig:
                            description: connection options for the Kafka client
                            type: object
                            additionalProperties:
                              type: string
                          connectionSecretId:
                            description: an identifier to look up a Kubernetes secret that contains the connection credentials
                            type: string
                        required:
                          - databaseName
                          - connectionConfig
                  required:
                    - srInstance
                    - kafkaClusters
              required:
                - metadata
                - spec

        KafkaCatalogsPage:
          type: object
          allOf:
            - $ref: '#/components/schemas/PaginationResponse'
            - type: object
              properties:
                metadata:
                  type: object
                  title: CatalogPageMetadata
                  properties:
                    size:
                      type: integer
                      format: int64
                      default: 0
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/KafkaCatalog'
                  default: [ ]

### Reference details¶

`POST ``/cmf/api/v1/environments`¶

**Create or update an Environment**

**Example request:**

    POST /cmf/api/v1/environments HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "name": "string",
        "flinkApplicationDefaults": {},
        "kubernetesNamespace": "string",
        "computePoolDefaults": {},
        "statementDefaults": {
            "detached": {
                "flinkConfiguration": {}
            },
            "interactive": {
                "flinkConfiguration": {}
            }
        }
    }

Status Codes:|

  * [201 Created](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.2) – The Environment was successfully created or updated. **Example response:**

        HTTP/1.1 201 Created
        Content-Type: application/json

        {
            "name": "string",
            "created_time": "2025-09-05T18:51:30.429387",
            "updated_time": "2025-09-05T18:51:30.429387",
            "flinkApplicationDefaults": {},
            "kubernetesNamespace": "string",
            "computePoolDefaults": {},
            "statementDefaults": {
                "detached": {
                    "flinkConfiguration": {}
                },
                "interactive": {
                    "flinkConfiguration": {}
                }
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments`¶

**Retrieve a paginated list of all environments.**

Query Parameters:
---
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/environments HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – List of environments found. If no environments are found, an empty list is returned. Note the information about secret is not included in the list call yet. In order to get the information about secret, make a getSecret call. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "name": "string",
                    "created_time": "2025-09-05T18:51:30.429387",
                    "updated_time": "2025-09-05T18:51:30.429387",
                    "flinkApplicationDefaults": {},
                    "kubernetesNamespace": "string",
                    "computePoolDefaults": {},
                    "statementDefaults": {
                        "detached": {
                            "flinkConfiguration": {}
                        },
                        "interactive": {
                            "flinkConfiguration": {}
                        }
                    }
                }
            ]
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---
Response Headers:
|

  * **ETag** – An ID for this version of the response.

`GET ``/cmf/api/v1/environments/{envName}`¶

**Get/Describe an environment with the given name.**

Parameters:|

  * **envName** (_string_) – Name of the Environment to be retrieved.

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Environment found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "name": "string",
            "created_time": "2025-09-05T18:51:30.429387",
            "updated_time": "2025-09-05T18:51:30.429387",
            "flinkApplicationDefaults": {},
            "kubernetesNamespace": "string",
            "computePoolDefaults": {},
            "statementDefaults": {
                "detached": {
                    "flinkConfiguration": {}
                },
                "interactive": {
                    "flinkConfiguration": {}
                }
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/environments/{envName}`¶
     Parameters:|

  * **envName** (_string_) – Name of the Environment to be deleted.

---|---
Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Environment found and deleted.
  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`POST ``/cmf/api/v1/environments/{envName}/applications`¶

**Creates a new Flink Application or updates an existing one in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---

**Example request:**

    POST /cmf/api/v1/environments/{envName}/applications HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {},
        "spec": {},
        "status": {}
    }

Status Codes:|

  * [201 Created](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.2) – The Application was successfully created or updated. **Example response:**

        HTTP/1.1 201 Created
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {},
            "spec": {},
            "status": {}
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/applications`¶

**Retrieve a paginated list of all applications in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/environments/{envName}/applications HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Application found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {},
                    "spec": {},
                    "status": {}
                }
            ]
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---
Response Headers:
|

  * **ETag** – An ID for this version of the response.

`GET ``/cmf/api/v1/environments/{envName}/applications/{appName}`¶

**Retrieve an Application of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/applications/{appName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Application found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {},
            "spec": {},
            "status": {}
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Application not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---
Response Headers:
|

  * **ETag** – An ID for this version of the response.

`DELETE ``/cmf/api/v1/environments/{envName}/applications/{appName}`¶

**Deletes an Application of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---
Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Application found and deleted.
  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`GET ``/cmf/api/v1alpha1/environments/{envName}/applications/{appName}/events`¶

**Get a paginated list of events of the given Application**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1alpha1/environments/{envName}/applications/{appName}/events HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Events found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "uid": "string",
                        "creationTimestamp": "string",
                        "flinkApplicationInstance": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "status": {
                        "message": "string",
                        "type": "string",
                        "data": {
                            "newStatus": "string"
                        }
                    }
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment or Application not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`POST ``/cmf/api/v1/environments/{envName}/applications/{appName}/start`¶

**Starts an earlier submitted Flink Application**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---
Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Application started **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {},
            "spec": {},
            "status": {}
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`POST ``/cmf/api/v1/environments/{envName}/applications/{appName}/suspend`¶

**Suspends an earlier started Flink Application**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---
Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Application suspended **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {},
            "spec": {},
            "status": {}
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – Not modified.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`GET ``/cmf/api/v1/environments/{envName}/applications/{appName}/instances`¶

**Get a paginated list of instances of the given Application**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/environments/{envName}/applications/{appName}/instances HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Instances found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "uid": "string",
                        "creationTimestamp": "string",
                        "updateTimestamp": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "status": {
                        "spec": {},
                        "jobStatus": {
                            "jobId": "string",
                            "state": "string"
                        }
                    }
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment or Application not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/applications/{appName}/instances/{instName}`¶

**Retrieve an Instance of an Application**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **appName** (_string_) – Name of the Application
  * **instName** (_string_) – Name of the ApplicationInstance

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/applications/{appName}/instances/{instName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – ApplicationInstance found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "uid": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "labels": {},
                "annotations": {}
            },
            "status": {
                "spec": {},
                "jobStatus": {
                    "jobId": "string",
                    "state": "string"
                }
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – FlinkApplicationInstance or environment or application not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/environments/{envName}/secret-mappings/{name}`¶

**Deletes the Environment Secret Mapping for the given Environment and Secret.**

Parameters:|

  * **envName** (_string_) – Name of the Environment in which the mapping has to be deleted.
  * **name** (_string_) – Name of the environment secret mapping to be deleted in the given environment.

---|---
Status Codes:|

  * [204 No Content](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.5) – The Environment Secret Mapping was successfully deleted.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment or Secret not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`GET ``/cmf/api/v1/environments/{envName}/secret-mappings/{name}`¶

**Retrieve the Environment Secret Mapping for the given name in the given environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **name** (_string_) – Name of the environment secret mapping to be retrieved.

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/secret-mappings/{name} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Environment Secret Mapping found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "uid": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "secretName": "string"
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment or Secret not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`PUT ``/cmf/api/v1/environments/{envName}/secret-mappings/{name}`¶

**Updates the Environment Secret Mapping for the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **name** (_string_) – Name of the environment secret mapping to be updated

---|---

**Example request:**

    PUT /cmf/api/v1/environments/{envName}/secret-mappings/{name} HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "uid": "string",
            "creationTimestamp": "string",
            "updateTimestamp": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "secretName": "string"
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Environment Secret Mapping was successfully updated. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "uid": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "secretName": "string"
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment or Secret not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`POST ``/cmf/api/v1/environments/{envName}/secret-mappings`¶

**Creates the Environment Secret Mapping for the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---

**Example request:**

    POST /cmf/api/v1/environments/{envName}/secret-mappings HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "uid": "string",
            "creationTimestamp": "string",
            "updateTimestamp": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "secretName": "string"
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Environment Secret Mapping was successfully created. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "uid": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "secretName": "string"
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – Environment Secret Mapping already exists. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/secret-mappings`¶

**Retrieve a paginated list of all Environment Secret Mappings.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/environments/{envName}/secret-mappings HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Environment Secret Mappings found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "uid": "string",
                        "creationTimestamp": "string",
                        "updateTimestamp": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "secretName": "string"
                    }
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`POST ``/cmf/api/v1/environments/{envName}/statements`¶

**Creates a new Flink SQL Statement in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---

**Example request:**

    POST /cmf/api/v1/environments/{envName}/statements HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "creationTimestamp": "string",
            "updateTimestamp": "string",
            "uid": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "statement": "string",
            "properties": {},
            "flinkConfiguration": {},
            "computePoolName": "string",
            "parallelism": 1,
            "stopped": true
        },
        "status": {
            "phase": "string",
            "detail": "string",
            "traits": {
                "sqlKind": "string",
                "isBounded": true,
                "isAppendOnly": true,
                "upsertColumns": [
                    1
                ],
                "schema": {
                    "columns": [
                        {
                            "name": "string",
                            "type": {
                                "type": "string",
                                "nullable": true,
                                "length": 1,
                                "precision": 1,
                                "scale": 1,
                                "keyType": {},
                                "valueType": {},
                                "elementType": {},
                                "fields": [
                                    {
                                        "name": "string",
                                        "fieldType": {},
                                        "description": "string"
                                    }
                                ],
                                "resolution": "string",
                                "fractionalPrecision": 1
                            }
                        }
                    ]
                }
            }
        },
        "result": {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "creationTimestamp": "string",
                "annotations": {}
            },
            "results": {
                "data": [
                    {}
                ]
            }
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Statement was successfully created. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "statement": "string",
                "properties": {},
                "flinkConfiguration": {},
                "computePoolName": "string",
                "parallelism": 1,
                "stopped": true
            },
            "status": {
                "phase": "string",
                "detail": "string",
                "traits": {
                    "sqlKind": "string",
                    "isBounded": true,
                    "isAppendOnly": true,
                    "upsertColumns": [
                        1
                    ],
                    "schema": {
                        "columns": [
                            {
                                "name": "string",
                                "type": {
                                    "type": "string",
                                    "nullable": true,
                                    "length": 1,
                                    "precision": 1,
                                    "scale": 1,
                                    "keyType": {},
                                    "valueType": {},
                                    "elementType": {},
                                    "fields": [
                                        {
                                            "name": "string",
                                            "fieldType": {},
                                            "description": "string"
                                        }
                                    ],
                                    "resolution": "string",
                                    "fractionalPrecision": 1
                                }
                            }
                        ]
                    }
                }
            },
            "result": {
                "apiVersion": "string",
                "kind": "string",
                "metadata": {
                    "creationTimestamp": "string",
                    "annotations": {}
                },
                "results": {
                    "data": [
                        {}
                    ]
                }
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – Statement already exists. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/statements`¶

**Retrieve a paginated list of Statements in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.
  * **compute-pool** (_string_) – Name of the ComputePool to filter on
  * **phase** (_string_) – Phase to filter on

**Example request:**

    GET /cmf/api/v1/environments/{envName}/statements HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Statements found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "creationTimestamp": "string",
                        "updateTimestamp": "string",
                        "uid": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "statement": "string",
                        "properties": {},
                        "flinkConfiguration": {},
                        "computePoolName": "string",
                        "parallelism": 1,
                        "stopped": true
                    },
                    "status": {
                        "phase": "string",
                        "detail": "string",
                        "traits": {
                            "sqlKind": "string",
                            "isBounded": true,
                            "isAppendOnly": true,
                            "upsertColumns": [
                                1
                            ],
                            "schema": {
                                "columns": [
                                    {
                                        "name": "string",
                                        "type": {
                                            "type": "string",
                                            "nullable": true,
                                            "length": 1,
                                            "precision": 1,
                                            "scale": 1,
                                            "keyType": {},
                                            "valueType": {},
                                            "elementType": {},
                                            "fields": [
                                                {
                                                    "name": "string",
                                                    "fieldType": {},
                                                    "description": "string"
                                                }
                                            ],
                                            "resolution": "string",
                                            "fractionalPrecision": 1
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "result": {
                        "apiVersion": "string",
                        "kind": "string",
                        "metadata": {
                            "creationTimestamp": "string",
                            "annotations": {}
                        },
                        "results": {
                            "data": [
                                {}
                            ]
                        }
                    }
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/statements/{stmtName}`¶

**Retrieve the Statement of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **stmtName** (_string_) – Name of the Statement

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/statements/{stmtName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Statement found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "statement": "string",
                "properties": {},
                "flinkConfiguration": {},
                "computePoolName": "string",
                "parallelism": 1,
                "stopped": true
            },
            "status": {
                "phase": "string",
                "detail": "string",
                "traits": {
                    "sqlKind": "string",
                    "isBounded": true,
                    "isAppendOnly": true,
                    "upsertColumns": [
                        1
                    ],
                    "schema": {
                        "columns": [
                            {
                                "name": "string",
                                "type": {
                                    "type": "string",
                                    "nullable": true,
                                    "length": 1,
                                    "precision": 1,
                                    "scale": 1,
                                    "keyType": {},
                                    "valueType": {},
                                    "elementType": {},
                                    "fields": [
                                        {
                                            "name": "string",
                                            "fieldType": {},
                                            "description": "string"
                                        }
                                    ],
                                    "resolution": "string",
                                    "fractionalPrecision": 1
                                }
                            }
                        ]
                    }
                }
            },
            "result": {
                "apiVersion": "string",
                "kind": "string",
                "metadata": {
                    "creationTimestamp": "string",
                    "annotations": {}
                },
                "results": {
                    "data": [
                        {}
                    ]
                }
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Statement not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/environments/{envName}/statements/{stmtName}`¶

**Deletes the Statement of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **stmtName** (_string_) – Name of the Statement

---|---
Status Codes:|

  * [204 No Content](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.5) – Statement was found and deleted.
  * [202 Accepted](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.3) – Statement was found and deletion request received.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Statement not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`PUT ``/cmf/api/v1/environments/{envName}/statements/{stmtName}`¶

**Updates a Statement of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **stmtName** (_string_) – Name of the Statement

---|---

**Example request:**

    PUT /cmf/api/v1/environments/{envName}/statements/{stmtName} HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "creationTimestamp": "string",
            "updateTimestamp": "string",
            "uid": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "statement": "string",
            "properties": {},
            "flinkConfiguration": {},
            "computePoolName": "string",
            "parallelism": 1,
            "stopped": true
        },
        "status": {
            "phase": "string",
            "detail": "string",
            "traits": {
                "sqlKind": "string",
                "isBounded": true,
                "isAppendOnly": true,
                "upsertColumns": [
                    1
                ],
                "schema": {
                    "columns": [
                        {
                            "name": "string",
                            "type": {
                                "type": "string",
                                "nullable": true,
                                "length": 1,
                                "precision": 1,
                                "scale": 1,
                                "keyType": {},
                                "valueType": {},
                                "elementType": {},
                                "fields": [
                                    {
                                        "name": "string",
                                        "fieldType": {},
                                        "description": "string"
                                    }
                                ],
                                "resolution": "string",
                                "fractionalPrecision": 1
                            }
                        }
                    ]
                }
            }
        },
        "result": {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "creationTimestamp": "string",
                "annotations": {}
            },
            "results": {
                "data": [
                    {}
                ]
            }
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Statement was found and updated.
  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Statement not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/statements/{stmtName}/results`¶

**Retrieve the result of the interactive Statement with the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **stmtName** (_string_) – Name of the Statement

---|---
Query Parameters:
|

  * **page-token** (_string_) – Token for the next page of results

**Example request:**

    GET /cmf/api/v1/environments/{envName}/statements/{stmtName}/results HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – StatementResults found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "creationTimestamp": "string",
                "annotations": {}
            },
            "results": {
                "data": [
                    {}
                ]
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Statement does not return results. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Statement not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [410 Gone](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.11) – Results are gone. **Example response:**

        HTTP/1.1 410 Gone
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/statements/{stmtName}/exceptions`¶

**Retrieves the last 10 exceptions of the Statement with the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **stmtName** (_string_) – Name of the Statement

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/statements/{stmtName}/exceptions HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – StatementExceptions found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "data": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "name": "string",
                    "message": "string",
                    "timestamp": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Statement not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`POST ``/cmf/api/v1/environments/{envName}/compute-pools`¶

**Creates a new Flink Compute Pool in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---

**Example request:**

    POST /cmf/api/v1/environments/{envName}/compute-pools HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "creationTimestamp": "string",
            "uid": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "type": "string",
            "clusterSpec": {}
        },
        "status": {
            "phase": "string"
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Compute Pool was successfully created. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "type": "string",
                "clusterSpec": {}
            },
            "status": {
                "phase": "string"
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – Compute Pool already exists. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/compute-pools`¶

**Retrieve a paginated list of Compute Pools in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment

---|---
Query Parameters:
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/environments/{envName}/compute-pools HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Compute Pools found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "creationTimestamp": "string",
                        "uid": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "type": "string",
                        "clusterSpec": {}
                    },
                    "status": {
                        "phase": "string"
                    }
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Environment not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/environments/{envName}/compute-pools/{computePoolName}`¶

**Retrieve the Compute Pool of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **computePoolName** (_string_) – Name of the Compute Pool

---|---

**Example request:**

    GET /cmf/api/v1/environments/{envName}/compute-pools/{computePoolName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Compute Pool found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "type": "string",
                "clusterSpec": {}
            },
            "status": {
                "phase": "string"
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Compute Pool not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/environments/{envName}/compute-pools/{computePoolName}`¶

**Deletes the ComputePool of the given name in the given Environment.**

Parameters:|

  * **envName** (_string_) – Name of the Environment
  * **computePoolName** (_string_) – Name of the ComputePool

---|---
Status Codes:|

  * [204 No Content](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.5) – Compute Pool was found and deleted.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Compute Pool not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – Compute Pool is in use and cannot be deleted. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`POST ``/cmf/api/v1/secrets`¶

**Create a Secret.**

Create a Secret. This secrets can be then used to specify sensitive information in the Flink SQL statements. Right now these secrets are only used for Kafka and Schema Registry credentials.

**Example request:**

    POST /cmf/api/v1/secrets HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "data": {}
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Secret was successfully created. Note that for security reasons, you can never view the contents of the secret itself once created. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "data": {}
            },
            "status": {
                "version": "string",
                "environments": [
                    "string"
                ]
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – The Secret already exists. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/secrets`¶

**Retrieve a paginated list of all secrets. Note that the actual secret data is masked for security reasons.**

Query Parameters:
---
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/secrets HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – List of secrets found. If no secrets are found, an empty list is returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "creationTimestamp": "string",
                        "updateTimestamp": "string",
                        "uid": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "data": {}
                    },
                    "status": {
                        "version": "string",
                        "environments": [
                            "string"
                        ]
                    }
                }
            ]
        }

  * [304 Not Modified](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5) – The list of secrets has not changed.
  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---
Response Headers:
|

  * **ETag** – An ID for this version of the response.

`GET ``/cmf/api/v1/secrets/{secretName}`¶

**Retrieve the Secret of the given name. Note that the secret data is not returned for security reasons.**

Parameters:|

  * **secretName** (_string_) – Name of the Secret

---|---

**Example request:**

    GET /cmf/api/v1/secrets/{secretName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Secret found and returned, with security data masked. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "data": {}
            },
            "status": {
                "version": "string",
                "environments": [
                    "string"
                ]
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Secret not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`PUT ``/cmf/api/v1/secrets/{secretName}`¶

**Update the secret.**

Parameters:|

  * **secretName** (_string_) – Name of the Secret

---|---

**Example request:**

    PUT /cmf/api/v1/secrets/{secretName} HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "data": {}
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Returns the updated Secret **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "updateTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "data": {}
            },
            "status": {
                "version": "string",
                "environments": [
                    "string"
                ]
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Secret with the given name not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/secrets/{secretName}`¶

**Delete the secret with the given name.**

Parameters:|

  * **secretName** (_string_) – Name of the Secret

---|---
Status Codes:|

  * [204 No Content](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.5) – Secret was successfully deleted.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Secret not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

`POST ``/cmf/api/v1/catalogs/kafka`¶

**Creates a new Kafka Catalog that can be referenced by Flink Statements**

**Example request:**

    POST /cmf/api/v1/catalogs/kafka HTTP/1.1
    Host: example.com
    Content-Type: application/json

    {
        "apiVersion": "string",
        "kind": "string",
        "metadata": {
            "name": "string",
            "creationTimestamp": "string",
            "uid": "string",
            "labels": {},
            "annotations": {}
        },
        "spec": {
            "srInstance": {
                "connectionConfig": {},
                "connectionSecretId": "string"
            },
            "kafkaClusters": [
                {
                    "databaseName": "string",
                    "connectionConfig": {},
                    "connectionSecretId": "string"
                }
            ]
        }
    }

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – The Kafka Catalog was successfully created. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "srInstance": {
                    "connectionConfig": {},
                    "connectionSecretId": "string"
                },
                "kafkaClusters": [
                    {
                        "databaseName": "string",
                        "connectionConfig": {},
                        "connectionSecretId": "string"
                    }
                ]
            }
        }

  * [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) – Bad request. **Example response:**

        HTTP/1.1 400 Bad Request
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [409 Conflict](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.10) – Kafka Catalog already exists. **Example response:**

        HTTP/1.1 409 Conflict
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [422 Unprocessable Entity](https://www.rfc-editor.org/rfc/rfc4918#section-11.2) – Request valid but invalid content. **Example response:**

        HTTP/1.1 422 Unprocessable Entity
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/catalogs/kafka`¶

**Retrieve a paginated list of Kafka Catalogs**

Query Parameters:
---
|

  * **page** (_integer_) – Zero-based page index (0..N)
  * **size** (_integer_) – The size of the page to be returned
  * **sort** (_array_) – Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.

**Example request:**

    GET /cmf/api/v1/catalogs/kafka HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Kafka Catalogs found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "pageable": {
                "page": 1,
                "size": 1,
                "sort": {
                    "sorted": true,
                    "unsorted": true,
                    "empty": true
                }
            },
            "metadata": {
                "size": 1
            },
            "items": [
                {
                    "apiVersion": "string",
                    "kind": "string",
                    "metadata": {
                        "name": "string",
                        "creationTimestamp": "string",
                        "uid": "string",
                        "labels": {},
                        "annotations": {}
                    },
                    "spec": {
                        "srInstance": {
                            "connectionConfig": {},
                            "connectionSecretId": "string"
                        },
                        "kafkaClusters": [
                            {
                                "databaseName": "string",
                                "connectionConfig": {},
                                "connectionSecretId": "string"
                            }
                        ]
                    }
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`GET ``/cmf/api/v1/catalogs/kafka/{catName}`¶

**Retrieve the Kafka Catalog of the given name.**

Parameters:|

  * **catName** (_string_) – Name of the Kafka Catalog

---|---

**Example request:**

    GET /cmf/api/v1/catalogs/kafka/{catName} HTTP/1.1
    Host: example.com

Status Codes:|

  * [200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) – Kafka Catalog found and returned. **Example response:**

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "apiVersion": "string",
            "kind": "string",
            "metadata": {
                "name": "string",
                "creationTimestamp": "string",
                "uid": "string",
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "srInstance": {
                    "connectionConfig": {},
                    "connectionSecretId": "string"
                },
                "kafkaClusters": [
                    {
                        "databaseName": "string",
                        "connectionConfig": {},
                        "connectionSecretId": "string"
                    }
                ]
            }
        }

  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Kafka Catalog not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

---|---

`DELETE ``/cmf/api/v1/catalogs/kafka/{catName}`¶

**Deletes the Kafka Catalog of the given name.**

Parameters:|

  * **catName** (_string_) – Name of the Kafka Catalog

---|---
Status Codes:|

  * [204 No Content](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.5) – Kafka Catalog was found and deleted.
  * [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) – Kafka Catalog not found. **Example response:**

        HTTP/1.1 404 Not Found
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

  * [500 Internal Server Error](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1) – Server error. **Example response:**

        HTTP/1.1 500 Internal Server Error
        Content-Type: application/json

        {
            "errors": [
                {
                    "message": "string"
                }
            ]
        }

## Troubleshooting¶

  * **Resource not found** : If you encounter the error _Resource not found…_ when making a GET call, it may be due to the wrong URL. Specifically, the requested REST resource might not exist.

For example:

    * When making the GET call:

          GET http://localhost:8080/hello

You will receive the error:

          Resource not found: [hello]

    * Similarly, if you make the GET call:

          GET http://localhost:8080/ or GET http://localhost:8080

You will receive the error:

          Resource not found: []

This occurs because you are requesting an empty resource.
