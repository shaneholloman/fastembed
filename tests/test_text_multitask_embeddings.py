import os

import numpy as np
import pytest

from fastembed import TextEmbedding
from fastembed.text.multitask_embedding import JinaEmbeddingV3, Task
from tests.utils import delete_model_cache


CANONICAL_VECTOR_VALUES = {
    "jinaai/jina-embeddings-v3": [
        {
            "task_id": Task.RETRIEVAL_QUERY,
            "vectors": np.array(
                [
                    [0.0623, -0.0402, 0.1706, -0.0143, 0.0617],
                    [-0.1064, -0.0733, 0.0353, 0.0096, 0.0667],
                ]
            ),
        },
        {
            "task_id": Task.RETRIEVAL_PASSAGE,
            "vectors": np.array(
                [
                    [0.0513, -0.0247, 0.1751, -0.0075, 0.0679],
                    [-0.0987, -0.0786, 0.09, 0.0087, 0.0577],
                ]
            ),
        },
        {
            "task_id": Task.SEPARATION,
            "vectors": np.array(
                [
                    [0.094, -0.1065, 0.1305, 0.0547, 0.0556],
                    [0.0315, -0.1468, 0.065, 0.0568, 0.0546],
                ]
            ),
        },
        {
            "task_id": Task.CLASSIFICATION,
            "vectors": np.array(
                [
                    [0.0606, -0.0877, 0.1384, 0.0065, 0.0722],
                    [-0.0502, -0.119, 0.032, 0.0514, 0.0689],
                ]
            ),
        },
        {
            "task_id": Task.TEXT_MATCHING,
            "vectors": np.array(
                [
                    [0.0911, -0.0341, 0.1305, -0.026, 0.0576],
                    [-0.1432, -0.05, 0.0133, 0.0464, 0.0789],
                ]
            ),
        },
    ]
}
docs = ["Hello World", "Follow the white rabbit."]


@pytest.mark.parametrize("dim,model_name", [(1024, "jinaai/jina-embeddings-v3")])
def test_batch_embedding(dim: int, model_name: str):
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    if is_ci and not is_manual:
        pytest.skip("Skipping multitask models in CI non-manual mode")

    docs_to_embed = docs * 10
    default_task = Task.RETRIEVAL_PASSAGE

    model = TextEmbedding(model_name=model_name)

    embeddings = list(model.embed(documents=docs_to_embed, batch_size=6))
    embeddings = np.stack(embeddings, axis=0)

    assert embeddings.shape == (len(docs_to_embed), dim)

    canonical_vector = CANONICAL_VECTOR_VALUES[model_name][default_task]["vectors"]
    assert np.allclose(
        embeddings[: len(docs), : canonical_vector.shape[1]], canonical_vector, atol=1e-4
    ), model_name

    if is_ci:
        delete_model_cache(model.model._model_dir)


def test_single_embedding():
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    if is_ci and not is_manual:
        pytest.skip("Skipping multitask models in CI non-manual mode")

    for model_desc in JinaEmbeddingV3._list_supported_models():
        # todo: once we add more models, we should not test models >1GB size locally
        model_name = model_desc.model
        dim = model_desc.dim

        model = TextEmbedding(model_name=model_name)

        for task in CANONICAL_VECTOR_VALUES[model_name]:
            print(f"evaluating {model_name} task_id: {task['task_id']}")

            embeddings = list(model.embed(documents=docs, task_id=task["task_id"]))
            embeddings = np.stack(embeddings, axis=0)

            assert embeddings.shape == (len(docs), dim)

            canonical_vector = task["vectors"]
            assert np.allclose(
                embeddings[:, : canonical_vector.shape[1]], canonical_vector, atol=1e-4
            ), model_desc.model

        classification_embeddings = list(model.embed(documents=docs, task_id=Task.CLASSIFICATION))
        classification_embeddings = np.stack(classification_embeddings, axis=0)

        assert classification_embeddings.shape == (len(docs), dim)

        model = TextEmbedding(model_name=model_name, task_id=Task.CLASSIFICATION)
        default_embeddings = list(model.embed(documents=docs))
        default_embeddings = np.stack(default_embeddings, axis=0)

        assert default_embeddings.shape == (len(docs), dim)

        assert np.allclose(
            classification_embeddings,
            default_embeddings,
            atol=1e-4,
        ), model_desc.model
        if is_ci:
            delete_model_cache(model.model._model_dir)


def test_single_embedding_query():
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    if is_ci and not is_manual:
        pytest.skip("Skipping multitask models in CI non-manual mode")

    task_id = Task.RETRIEVAL_QUERY

    for model_desc in JinaEmbeddingV3._list_supported_models():
        # todo: once we add more models, we should not test models >1GB size locally
        model_name = model_desc.model
        dim = model_desc.dim

        model = TextEmbedding(model_name=model_name)

        print(f"evaluating {model_name} query_embed task_id: {task_id}")

        embeddings = list(model.query_embed(query=docs))
        embeddings = np.stack(embeddings, axis=0)

        assert embeddings.shape == (len(docs), dim)

        canonical_vector = CANONICAL_VECTOR_VALUES[model_name][task_id]["vectors"]
        assert np.allclose(
            embeddings[:, : canonical_vector.shape[1]], canonical_vector, atol=1e-4
        ), model_desc.model

        if is_ci:
            delete_model_cache(model.model._model_dir)


def test_single_embedding_passage():
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    if is_ci and not is_manual:
        pytest.skip("Skipping multitask models in CI non-manual mode")

    task_id = Task.RETRIEVAL_PASSAGE

    for model_desc in JinaEmbeddingV3._list_supported_models():
        # todo: once we add more models, we should not test models >1GB size locally

        model_name = model_desc.model
        dim = model_desc.dim

        model = TextEmbedding(model_name=model_name)

        print(f"evaluating {model_name} passage_embed task_id: {task_id}")

        embeddings = list(model.passage_embed(texts=docs))
        embeddings = np.stack(embeddings, axis=0)

        assert embeddings.shape == (len(docs), dim)

        canonical_vector = CANONICAL_VECTOR_VALUES[model_name][task_id]["vectors"]
        assert np.allclose(
            embeddings[:, : canonical_vector.shape[1]], canonical_vector, atol=1e-4
        ), model_desc.model

        if is_ci:
            delete_model_cache(model.model._model_dir)


@pytest.mark.parametrize("dim,model_name", [(1024, "jinaai/jina-embeddings-v3")])
def test_parallel_processing(dim: int, model_name: str):
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    if is_ci and not is_manual:
        pytest.skip("Skipping in CI non-manual mode")

    docs = ["Hello World", "Follow the white rabbit."] * 10

    model = TextEmbedding(model_name=model_name)

    task_id = Task.SEPARATION
    embeddings_1 = list(model.embed(docs, batch_size=10, parallel=None, task_id=task_id))
    embeddings_1 = np.stack(embeddings_1, axis=0)

    embeddings_2 = list(model.embed(docs, batch_size=10, parallel=1, task_id=task_id))
    embeddings_2 = np.stack(embeddings_2, axis=0)

    assert embeddings_1.shape[0] == len(docs) and embeddings_1.shape[-1] == dim
    assert np.allclose(embeddings_1, embeddings_2, atol=1e-4)

    canonical_vector = CANONICAL_VECTOR_VALUES[model_name][task_id]["vectors"]
    assert np.allclose(embeddings_2[:2, : canonical_vector.shape[1]], canonical_vector, atol=1e-4)

    if is_ci:
        delete_model_cache(model.model._model_dir)


@pytest.mark.parametrize("model_name", ["jinaai/jina-embeddings-v3"])
def test_lazy_load(model_name: str):
    is_ci = os.getenv("CI")
    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

    if is_ci and not is_manual:
        pytest.skip("Skipping in CI non-manual mode")

    model = TextEmbedding(model_name=model_name, lazy_load=True)
    assert not hasattr(model.model, "model")

    list(model.embed(docs))
    assert hasattr(model.model, "model")

    if is_ci:
        delete_model_cache(model.model._model_dir)
