def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"AI-Agentic Career Guidance" in response.data

def test_module_health_endpoints(client):
    endpoints = [
        '/api/profile/health',
        '/api/career/health',
        '/api/education/health',
        '/api/opportunities/health',
        '/api/eligibility/health',
        '/api/skill-gap/health',
        '/api/planner/health',
        '/api/notifications/health',
        '/api/agents/health'
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'healthy'
