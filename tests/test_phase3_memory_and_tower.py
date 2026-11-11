from pathlib import Path

from qdrant_client import QdrantClient

from tobi.core.road import Road
from tobi.core.rules import Lane
from tobi.core.vehicle import Vehicle
from tobi.memory.policy_rag import PolicyRAG
from tobi.tower.blackbox import BlackBox


def test_blackbox_persists_and_exports_polars(tmp_path: Path):
    db_file = tmp_path / "test_blackbox.duckdb"
    blackbox = BlackBox(db_path=db_file)
    road = Road(name="Audited_Road", blackbox=blackbox)

    vehicle = Vehicle(payload={"task": "test_persistence"})
    road.transit(vehicle, run_llm=False)

    df = blackbox.fetch_audit_dataframe()
    assert df.height == 1
    assert df["license_plate"][0] == vehicle.license_plate
    assert df["road_name"][0] == "Audited_Road"
    assert df["assigned_lane"][0] == Lane.FAST.value


def test_policy_rag_downgrades_unbacked_query_to_middle_lane():
    memory_qdrant = QdrantClient(":memory:")
    rag = PolicyRAG(client=memory_qdrant, similarity_threshold=0.75)
    rag.add_policy(
        policy_id="POL-01",
        content="architecture standard pydantic typing validation rules",
    )

    road = Road(name="RAG_Protected_Road", policy_rag=rag)
    vehicle = Vehicle(payload={"query": "quantum gravity warp drive propulsion"})
    result = road.transit(vehicle, run_llm=False)

    assert result.assigned_lane == Lane.MIDDLE


def test_policy_rag_keeps_fast_lane_when_policy_matches():
    memory_qdrant = QdrantClient(":memory:")
    rag = PolicyRAG(client=memory_qdrant, similarity_threshold=0.75)
    policy_text = "architecture standard pydantic typing validation rules"
    rag.add_policy(policy_id="POL-01", content=policy_text)

    road = Road(name="RAG_Protected_Road", policy_rag=rag)
    vehicle = Vehicle(payload={"query": "architecture standard pydantic typing"})
    result = road.transit(vehicle, run_llm=False)

    assert result.assigned_lane == Lane.FAST
    assert result.payload.get("policy_context") == policy_text