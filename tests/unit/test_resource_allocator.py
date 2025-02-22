# tests/unit/test_resource_allocator.py
import pytest
from src.agent_management.resource_allocator import ResourceAllocator

@pytest.fixture
def allocator():
    return ResourceAllocator()

def test_resource_allocation(allocator):
    allocation = allocator.allocate(
        task_id="job_123",
        requirements={"cpu": 4, "memory": 8192}
    )
    assert allocation.status == "APPROVED"

def test_utilization_tracking(allocator):
    allocator.update_utilization("node05", {"cpu": 0.85, "memory": 0.92})
    assert allocator.calculate_cluster_utilization()["cpu"] > 0.8

def test_allocation_rejection(allocator):
    allocator.update_utilization("node01", {"cpu": 0.95, "memory": 0.88})
    allocation = allocator.allocate(
        task_id="job_456",
        requirements={"cpu": 2, "memory": 4096}
    )
    assert allocation.status == "DENIED"
