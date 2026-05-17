# API tests for FinOpsGuard endpoints.
# Covers health, costs CRUD, validation, seed data, report generation,
# and budget percentage calculations.


VALID_COST = {
    "month": "2026-04",
    "aws_spend": 3500.0,
    "total_budget": 5000.0,
    "allocation_period": "Monthly",
}

# Health API testing

def test_health_returns_200(client):
    """GET /health returns service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FinOpsGuard Agent"
    assert data["version"] == "1.0.0"

# Costs CRUD testing

def test_get_costs_empty_returns_404(client):
    """GET /costs returns 404 when no records exist."""
    assert client.get("/costs").status_code == 404


def test_create_cost_returns_201(client):
    """POST /costs creates a record with valid payload."""
    response = client.post("/costs", json=VALID_COST)
    assert response.status_code == 201
    data = response.json()
    assert data["month"] == "2026-04"
    assert data["aws_spend"] == 3500.0
    assert data["total_budget"] == 5000.0
    assert data["allocation_period"] == "Monthly"
    assert data["budget_used_pct"] == 70.0
    assert data["id"] is not None


def test_get_costs_returns_all_ordered(client):
    """GET /costs returns records ordered by month."""
    client.post("/costs", json={**VALID_COST, "month": "2026-02", "aws_spend": 2000})
    client.post("/costs", json={**VALID_COST, "month": "2026-01", "aws_spend": 1000})
    response = client.get("/costs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["month"] == "2026-01"
    assert data[1]["month"] == "2026-02"


def test_delete_cost_success(client):
    """DELETE /costs/{id} removes an existing record."""
    resp = client.post("/costs", json=VALID_COST)
    cost_id = resp.json()["id"]
    assert client.delete(f"/costs/{cost_id}").status_code == 200
    assert client.get("/costs").status_code == 404


def test_delete_cost_nonexistent_returns_404(client):
    """DELETE /costs/{id} returns 404 for unknown ID."""
    assert client.delete("/costs/9999").status_code == 404


def test_delete_all_costs(client):
    """DELETE /costs clears all records."""
    client.post("/costs", json={**VALID_COST, "month": "2026-01"})
    client.post("/costs", json={**VALID_COST, "month": "2026-02"})
    resp = client.delete("/costs")
    assert resp.status_code == 200
    assert client.get("/costs").status_code == 404


# Input Validation testing

def test_create_cost_invalid_month_returns_422(client):
    """Invalid month format is rejected."""
    assert client.post("/costs", json={**VALID_COST, "month": "April-2026"}).status_code == 422


def test_create_cost_negative_spend_returns_422(client):
    """Negative spend is rejected."""
    assert client.post("/costs", json={**VALID_COST, "aws_spend": -50}).status_code == 422


def test_create_cost_zero_budget_returns_422(client):
    """Zero budget is rejected (must be greater than '0')."""
    assert client.post("/costs", json={**VALID_COST, "total_budget": 0}).status_code == 422


def test_create_cost_invalid_period_returns_422(client):
    """Invalid allocation period is rejected."""
    assert client.post("/costs", json={**VALID_COST, "allocation_period": "Weekly"}).status_code == 422


def test_create_cost_yearly_rejected_returns_422(client):
    """Yearly allocation period is no longer supported."""
    assert client.post("/costs", json={**VALID_COST, "allocation_period": "Yearly"}).status_code == 422


def test_create_cost_extra_field_returns_422(client):
    """Unexpected payload fields are rejected."""
    assert client.post("/costs", json={**VALID_COST, "hacked": True}).status_code == 422


# Budget Utilization testing

def test_budget_used_pct_computed_correctly(client):
    """budget_used_pct is calculated correctly."""
    client.post("/costs", json={**VALID_COST, "aws_spend": 2500, "total_budget": 5000})
    data = client.get("/costs").json()
    assert data[0]["budget_used_pct"] == 50.0


# Seed Demo Data testing

def test_seed_demo_data(client):
    """POST /costs/seed creates the expected demo records."""
    resp = client.post("/costs/seed")
    assert resp.status_code == 201
    data = resp.json()
    assert data["count"] == 5
    assert len(data["records"]) == 5
    # Ensure seeded records include expected fields
    record = data["records"][0]
    assert "month" in record
    assert "aws_spend" in record
    assert "total_budget" in record
    assert "budget_used_pct" in record


# Report testing

def test_report_no_data_returns_404(client):
    """GET /report returns 404 when no cost data exists."""
    assert client.get("/report").status_code == 404


def test_report_returns_records_and_analysis(client):
    """GET /report returns records plus analysis text."""
    client.post("/costs", json={**VALID_COST, "month": "2026-01", "aws_spend": 2500})
    client.post("/costs", json={**VALID_COST, "month": "2026-02", "aws_spend": 3500})
    resp = client.get("/report")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["records"]) == 2
    assert data["records"][0]["budget_used_pct"] == 50.0
    assert data["records"][1]["budget_used_pct"] == 70.0
    # Analysis response should be non-trivial text
    assert len(data["analysis"]) > 50