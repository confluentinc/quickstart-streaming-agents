"""
Re-embed the shared Lab 2/3/4 vector corpora with the CSP Hosted embedding model.

AWS (default): for each shared AWS Atlas cluster it reads vector_search.documents
(the 1536-dim Bedrock Titan v1 corpus), embeds every `chunk` with
`system.amazon.titan-embed-text-v2` (1024 dims) through the Flink SQL REST API,
upserts the copies (same _id and metadata, new `embedding`) into
vector_search.documents_csp, and creates the `vector_index_csp` vector index.

Azure (--azure): same for the Azure Atlas clusters (Lab 2 xhgx1kr, Lab 3 iir6woe)
with `system.openai.text-embedding-3-small` (1536 dims), plus the Lab 4 CosmosDB
corpus (fema-iappg, database vector_search): container `documents` is copied into
a new container `documents_csp` whose partition key, indexing policy and vector
embedding policy mirror `documents`.

The original `documents` collection/container and `vector_index` are never touched.

Env vars:
  FLINK_API_KEY / FLINK_API_SECRET   Flink API key for FLINK_ENV_ID (in us-east-1 on
                                     AWS, eastus2 on Azure)
  CONFLUENT_ORG_ID, FLINK_ENV_ID, FLINK_COMPUTE_POOL_ID
  FLINK_CATALOG, FLINK_DATABASE      env / cluster display names for the statements
  FLINK_ENDPOINT                     optional override of the Flink REST endpoint
  ATLAS_WRITE_USERNAME / ATLAS_WRITE_PASSWORD
                                     optional Atlas login with readWrite on
                                     vector_search (and Atlas Search index admin).
                                     Used for both reading `documents` and writing
                                     `documents_csp`. Run with --only for one cluster
                                     at a time when you set these.
  COSMOS_WRITE_KEY                   (--azure, Lab 4) CosmosDB primary (read-write)
                                     key for fema-iappg — required unless --dry-run
                                     or --inspect
  COSMOS_READ_KEY                    (--azure, Lab 4) optional read-only key used for
                                     --dry-run / --inspect when COSMOS_WRITE_KEY isn't
                                     set (the one in terraform/lab4 locals)

When ATLAS_WRITE_* aren't set, the Atlas login falls back to CLUSTER_<ID>_USERNAME /
_PASSWORD from .scratch/credentials-keepalive.env (or the environment) — the shared
read-only workshop users, which can't write, so this only works with --dry-run /
--inspect. Do NOT grant those users write access: their passwords are public in the
lab terraform.

Usage (from the repo root):
  uv run --no-project --with pymongo --with dnspython --with requests \
      --with python-dotenv --with azure-cosmos \
      python scripts/common/reembed_csp.py [--azure] [--inspect | --dry-run] [--only <key>]

  --inspect   read-only: report source doc counts / embedding dims / Cosmos container
              policy. No Flink, no writes.
  --dry-run   also embeds through Flink and checks dims, but writes nothing.
"""

import argparse
import copy
import os
import sys
import time
import uuid
from pathlib import Path

import requests
from dotenv import dotenv_values

DATABASE = "vector_search"
SOURCE_COLLECTION = "documents"
TARGET_COLLECTION = "documents_csp"
TARGET_INDEX = "vector_index_csp"
BATCH = 15

COSMOS_ENDPOINT = "https://fema-iappg.documents.azure.com:443/"
COSMOS_SYSTEM_FIELDS = ("_rid", "_self", "_etag", "_attachments", "_ts")

PROFILES = {
    "aws": {
        "model": "system.amazon.titan-embed-text-v2",
        "dims": 1024,
        "flink_endpoint": "https://flink.us-east-1.aws.confluent.cloud",
        "clusters": {
            "c79vrkg": ("Lab 2", "mongodb+srv://cluster0.c79vrkg.mongodb.net"),
            "w9n3o45": ("Lab 3", "mongodb+srv://cluster0.w9n3o45.mongodb.net"),
            "rgtlalv": ("Lab 4", "mongodb+srv://cluster0.rgtlalv.mongodb.net"),
        },
    },
    "azure": {
        "model": "system.openai.text-embedding-3-small",
        "dims": 1536,
        "flink_endpoint": "https://flink.eastus2.azure.confluent.cloud",
        "clusters": {
            "xhgx1kr": ("Lab 2", "mongodb+srv://cluster0.xhgx1kr.mongodb.net"),
            "iir6woe": ("Lab 3", "mongodb+srv://cluster0.iir6woe.mongodb.net"),
            "cosmos": ("Lab 4", COSMOS_ENDPOINT),
        },
    },
}


def sql_literal(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


class Flink:
    def __init__(self, model, endpoint):
        e = os.environ
        self.model = model
        self.auth = (e["FLINK_API_KEY"], e["FLINK_API_SECRET"])
        endpoint = e.get("FLINK_ENDPOINT") or endpoint
        self.base = f"{endpoint}/sql/v1/organizations/{e['CONFLUENT_ORG_ID']}/environments/{e['FLINK_ENV_ID']}/statements"
        self.pool = e["FLINK_COMPUTE_POOL_ID"]
        self.props = {
            "sql.current-catalog": e["FLINK_CATALOG"],
            "sql.current-database": e["FLINK_DATABASE"],
        }

    def embed(self, items):
        """items: [(id, text)] -> {id: [float]}"""
        rows = ", ".join(
            f"(CAST({sql_literal(i)} AS STRING), CAST({sql_literal(t)} AS STRING))"
            for i, t in items
        )
        sql = (
            f"SELECT t.id, e.embedding FROM (VALUES {rows}) AS t(id, txt), "
            f"LATERAL TABLE(AI_EMBEDDING(`{self.model}`, t.txt)) AS e;"
        )
        name = f"reembed-csp-{uuid.uuid4().hex[:12]}"
        r = requests.post(
            self.base,
            auth=self.auth,
            json={
                "name": name,
                "spec": {"statement": sql, "compute_pool_id": self.pool, "properties": self.props},
            },
            timeout=60,
        )
        r.raise_for_status()
        try:
            for _ in range(120):
                s = requests.get(f"{self.base}/{name}", auth=self.auth, timeout=30).json()
                phase = s["status"]["phase"]
                if phase in ("COMPLETED", "RUNNING"):
                    break
                if phase == "FAILED":
                    raise RuntimeError(s["status"].get("detail"))
                time.sleep(2)
            out, url = {}, f"{self.base}/{name}/results"
            while url and len(out) < len(items):
                page = requests.get(url, auth=self.auth, timeout=60).json()
                for row in page.get("results", {}).get("data", []):
                    if row.get("op", 0) == 0:
                        rid, vec = row["row"]
                        out[rid] = [float(x) for x in vec]
                url = page.get("metadata", {}).get("next") or (url if len(out) < len(items) else None)
                if url and not page.get("results", {}).get("data"):
                    time.sleep(1)
            return out
        finally:
            requests.delete(f"{self.base}/{name}", auth=self.auth, timeout=30)


def embed_all(flink, docs, id_field, dims):
    """{id: vector} for every doc's `chunk`, checking dims."""
    vecs = {}
    for start in range(0, len(docs), BATCH):
        batch = docs[start : start + BATCH]
        got = flink.embed([(str(d[id_field]), d["chunk"]) for d in batch])
        for d in batch:
            vec = got.get(str(d[id_field]))
            if not vec or len(vec) != dims:
                sys.exit(f"  ✗ {d[id_field]}: got {len(vec) if vec else 0} dims, expected {dims}")
            vecs[str(d[id_field])] = vec
        print(f"  embedded {min(start + BATCH, len(docs))}/{len(docs)}")
    return vecs


# ---------------------------------------------------------------------------
# MongoDB Atlas
# ---------------------------------------------------------------------------


def atlas_login(key, creds):
    """ATLAS_WRITE_* when set, else the cluster's (read-only) CLUSTER_<ID>_* login."""
    user = os.environ.get("ATLAS_WRITE_USERNAME")
    pw = os.environ.get("ATLAS_WRITE_PASSWORD")
    if user and pw:
        return user, pw, "ATLAS_WRITE_USERNAME"
    user = creds.get(f"CLUSTER_{key.upper()}_USERNAME")
    pw = creds.get(f"CLUSTER_{key.upper()}_PASSWORD")
    if not (user and pw):
        sys.exit(
            f"Set ATLAS_WRITE_USERNAME/_PASSWORD, or CLUSTER_{key.upper()}_USERNAME/_PASSWORD "
            "in .scratch/credentials-keepalive.env"
        )
    return user, pw, f"CLUSTER_{key.upper()}_USERNAME"


def reembed_atlas(key, profile, flink, creds, mode):
    from pymongo import MongoClient, ReplaceOne
    from pymongo.operations import SearchIndexModel

    lab, uri = profile["clusters"][key]
    dims = profile["dims"]
    user, pw, source = atlas_login(key, creds)
    db = MongoClient(uri, username=user, password=pw, serverSelectionTimeoutMS=20000)[DATABASE]
    docs = list(db[SOURCE_COLLECTION].find())
    print(f"\n{lab} ({key}): {len(docs)} docs in {SOURCE_COLLECTION} (login from {source})")

    if mode == "inspect":
        src_dims = {len(d.get("embedding") or []) for d in docs}
        print(f"  source embedding dims: {sorted(src_dims)}")
        names = set(db.list_collection_names())
        print(f"  {TARGET_COLLECTION} exists: {TARGET_COLLECTION in names}")
        return

    vecs = embed_all(flink, docs, "_id", dims)
    ops = [ReplaceOne({"_id": d["_id"]}, {**d, "embedding": vecs[str(d["_id"])]}, upsert=True) for d in docs]

    if mode == "dry-run":
        print(f"  dry run: would upsert {len(ops)} docs into {TARGET_COLLECTION}")
        return
    db[TARGET_COLLECTION].bulk_write(ops)
    print(f"  ✓ upserted {len(ops)} docs into {TARGET_COLLECTION}")

    if not any(i["name"] == TARGET_INDEX for i in db[TARGET_COLLECTION].list_search_indexes()):
        db[TARGET_COLLECTION].create_search_index(
            SearchIndexModel(
                definition={"fields": [{"type": "vector", "path": "embedding", "numDimensions": dims, "similarity": "cosine"}]},
                name=TARGET_INDEX,
                type="vectorSearch",
            )
        )
        print(f"  ✓ created {TARGET_INDEX}")
    for _ in range(60):
        idx = next(i for i in db[TARGET_COLLECTION].list_search_indexes() if i["name"] == TARGET_INDEX)
        if idx.get("queryable"):
            break
        time.sleep(5)
    probe = docs[0]
    hit = next(
        db[TARGET_COLLECTION].aggregate(
            [{"$vectorSearch": {"index": TARGET_INDEX, "path": "embedding", "queryVector": vecs[str(probe["_id"])], "numCandidates": 50, "limit": 1}}]
        ),
        None,
    )
    ok = hit is not None and hit["_id"] == probe["_id"]
    print(f"  {'✓' if ok else '✗'} $vectorSearch self-match on {TARGET_INDEX}")


# ---------------------------------------------------------------------------
# Azure CosmosDB (Lab 4)
# ---------------------------------------------------------------------------


def _target_container_settings(props, dims):
    """Partition key / indexing / vector policies for documents_csp, mirrored from documents."""
    from azure.cosmos import PartitionKey

    pk = props["partitionKey"]
    paths = pk["paths"]
    partition_key = PartitionKey(
        path=paths[0] if len(paths) == 1 else paths,
        kind=pk.get("kind", "Hash"),
        version=pk.get("version", 2),
    )
    vector_policy = copy.deepcopy(props.get("vectorEmbeddingPolicy"))
    if vector_policy:
        for emb in vector_policy.get("vectorEmbeddings", []):
            emb["dimensions"] = dims
    indexing_policy = copy.deepcopy(props.get("indexingPolicy"))
    return partition_key, indexing_policy, vector_policy


def reembed_cosmos(profile, flink, mode):
    from azure.cosmos import CosmosClient

    dims = profile["dims"]
    write_key = os.environ.get("COSMOS_WRITE_KEY")
    key = write_key or os.environ.get("COSMOS_READ_KEY")
    if not key:
        sys.exit("Set COSMOS_WRITE_KEY (or COSMOS_READ_KEY for --dry-run / --inspect)")
    if mode == "write" and not write_key:
        sys.exit("COSMOS_WRITE_KEY is required to write documents_csp (use --dry-run otherwise)")

    db = CosmosClient(COSMOS_ENDPOINT, credential=key).get_database_client(DATABASE)
    source = db.get_container_client(SOURCE_COLLECTION)
    props = source.read()
    docs = [
        {k: v for k, v in d.items() if k not in COSMOS_SYSTEM_FIELDS}
        for d in source.query_items("SELECT * FROM c", enable_cross_partition_query=True)
    ]
    print(f"\nLab 4 (CosmosDB {DATABASE}): {len(docs)} docs in {SOURCE_COLLECTION}")
    partition_key, indexing_policy, vector_policy = _target_container_settings(props, dims)
    vec_paths = [e["path"] for e in (vector_policy or {}).get("vectorEmbeddings", [])] or ["/embedding"]

    if mode == "inspect":
        src_dims = {len(d.get("embedding") or []) for d in docs}
        print(f"  source embedding dims: {sorted(src_dims)}")
        print(f"  partitionKey: {props.get('partitionKey')}")
        print(f"  vectorEmbeddingPolicy: {props.get('vectorEmbeddingPolicy')}")
        print(f"  indexingPolicy.vectorIndexes: {(props.get('indexingPolicy') or {}).get('vectorIndexes')}")
        existing = {c["id"] for c in db.list_containers()}
        print(f"  {TARGET_COLLECTION} exists: {TARGET_COLLECTION in existing}")
        return

    vecs = embed_all(flink, docs, "id", dims)
    if mode == "dry-run":
        print(f"  dry run: would create container {TARGET_COLLECTION} (pk {props['partitionKey']['paths']}, vector paths {vec_paths}) and upsert {len(docs)} docs")
        return

    kwargs = {"partition_key": partition_key, "indexing_policy": indexing_policy}
    if vector_policy:
        kwargs["vector_embedding_policy"] = vector_policy
    target = db.create_container_if_not_exists(id=TARGET_COLLECTION, **kwargs)
    print(f"  ✓ container {TARGET_COLLECTION} ready")
    for n, d in enumerate(docs, 1):
        target.upsert_item({**d, "embedding": vecs[str(d["id"])]})
        if n % 50 == 0 or n == len(docs):
            print(f"  upserted {n}/{len(docs)}")

    probe = docs[0]
    field = vec_paths[0].lstrip("/").replace("/", ".")
    hits = list(
        target.query_items(
            f"SELECT TOP 1 c.id FROM c ORDER BY VectorDistance(c.{field}, @v)",
            parameters=[{"name": "@v", "value": vecs[str(probe["id"])]}],
            enable_cross_partition_query=True,
        )
    )
    ok = bool(hits) and hits[0]["id"] == probe["id"]
    print(f"  {'✓' if ok else '✗'} VectorDistance self-match on {TARGET_COLLECTION}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--azure", action="store_true", help="Azure corpora (text-embedding-3-small) instead of AWS (Titan v2)")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Embed and check dims, but write nothing")
    group.add_argument("--inspect", action="store_true", help="Read-only source report; no Flink, no writes")
    all_keys = sorted({k for p in PROFILES.values() for k in p["clusters"]})
    ap.add_argument("--only", choices=all_keys, action="append")
    args = ap.parse_args()

    profile = PROFILES["azure" if args.azure else "aws"]
    keys = args.only or list(profile["clusters"])
    bad = [k for k in keys if k not in profile["clusters"]]
    if bad:
        ap.error(f"{', '.join(bad)} not in the {'azure' if args.azure else 'aws'} set: {', '.join(profile['clusters'])}")
    mode = "inspect" if args.inspect else "dry-run" if args.dry_run else "write"

    creds = {**dotenv_values(Path(".scratch/credentials-keepalive.env")), **os.environ}
    flink = None if mode == "inspect" else Flink(profile["model"], profile["flink_endpoint"])
    for key in keys:
        if key == "cosmos":
            reembed_cosmos(profile, flink, mode)
        else:
            reembed_atlas(key, profile, flink, creds, mode)


if __name__ == "__main__":
    main()
