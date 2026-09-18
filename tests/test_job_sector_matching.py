import pytest
from app import create_app
from opportunities.services import OpportunityService


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_get_sectors_private_and_govt(client):
    """Verify dynamic sectors calculation returns correct sectors and job counts."""
    # Private sectors
    res_priv = client.get('/api/opportunities/sectors?category=private_job')
    assert res_priv.status_code == 200
    data_priv = res_priv.get_json()
    assert data_priv['status'] == 'success'
    assert data_priv['category'] == 'private_job'
    assert data_priv['total_sectors'] >= 5
    assert data_priv['total_jobs'] >= 10
    sector_names = [s['name'] for s in data_priv['sectors']]
    assert 'IT & Software' in sector_names
    assert 'Finance & Accounting' in sector_names
    assert 'Sales & Marketing' in sector_names

    # Govt sectors
    res_govt = client.get('/api/opportunities/sectors?category=govt_job')
    assert res_govt.status_code == 200
    data_govt = res_govt.get_json()
    assert data_govt['status'] == 'success'
    assert data_govt['category'] == 'govt_job'
    assert data_govt['total_sectors'] >= 4
    govt_sector_names = [s['name'] for s in data_govt['sectors']]
    assert 'Central Ministries & Administration' in govt_sector_names
    assert 'Railways & Transport' in govt_sector_names


def test_get_available_skills(client):
    """Verify unique available skills retrieval per category and sector."""
    # All private skills
    res = client.get('/api/opportunities/skills?category=private_job')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert len(data['skills']) > 10
    assert 'Python' in data['skills'] or 'Communication' in data['skills']

    # IT sector skills
    res_it = client.get('/api/opportunities/skills?category=private_job&sector=IT%20%26%20Software')
    assert res_it.status_code == 200
    data_it = res_it.get_json()
    assert 'Python' in data_it['skills']
    assert 'JavaScript' in data_it['skills']


def test_match_jobs_no_limit_rule(client):
    """
    CRITICAL REQUIREMENT: Match results must return ALL matching opportunities
    ordered by relevance score and must NOT slice/limit results to top 3.
    """
    # Query all private jobs with Undergraduate education
    payload = {
        "category": "private_job",
        "sector": None,
        "education_level": "Undergraduate",
        "skills": ["Python", "MS Excel", "Communication"]
    }
    res = client.post('/api/opportunities/match', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['total_matches'] > 3, "Must NOT limit results to top 3!"
    assert len(data['matches']) == data['total_matches']

    # Verify results are sorted by match_score descending
    scores = [m['match_score'] for m in data['matches']]
    assert scores == sorted(scores, reverse=True)


def test_match_jobs_explainability_metadata(client):
    """Verify explainable match cards have all required explainability fields."""
    payload = {
        "category": "private_job",
        "sector": "IT & Software",
        "education_level": "Undergraduate",
        "skills": ["Python", "Git"]
    }
    res = client.post('/api/opportunities/match', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_matches'] >= 4

    top_job = data['matches'][0]
    assert 'id' in top_job
    assert 'title' in top_job
    assert 'match_score' in top_job
    assert 'qualification_match' in top_job
    assert top_job['qualification_match'] is True
    assert 'matched_skills' in top_job
    assert 'Python' in top_job['matched_skills'] or 'Git' in top_job['matched_skills']
    assert 'missing_skills' in top_job
    assert 'why_matched' in top_job
    assert len(top_job['why_matched']) > 0


def test_match_govt_jobs_with_exam_info(client):
    """Verify government matching includes exam/selection process info."""
    payload = {
        "category": "govt_job",
        "sector": "Railways & Transport",
        "education_level": "Class 10",
        "skills": ["Mathematics"]
    }
    res = client.post('/api/opportunities/match', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_matches'] >= 1
    rail_job = next((j for j in data['matches'] if 'Railway' in j['title'] or 'RRB' in j['title']), None)
    assert rail_job is not None
    assert rail_job['exam_selection'] is not None
    assert 'CBT' in rail_job['exam_selection'] or 'Examination' in rail_job['exam_selection']


def test_match_jobs_empty_state_handling(client):
    """Verify safe empty state when no jobs match specific filters."""
    payload = {
        "category": "private_job",
        "sector": "Nonexistent Sector 999",
        "education_level": "Class 10",
        "skills": ["RandomSkillXYZ"]
    }
    res = client.post('/api/opportunities/match', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_matches'] == 0
    assert data['has_matches'] is False
    assert data['no_match_message'] is not None


def test_qualification_and_skills_detection_endpoint(client):
    """Verify profile context detection returns non-corrupting qualification and skills."""
    with client.session_transaction() as sess:
        sess['exploration_profile'] = {
            'education_level': 'Class 12',
            'skills': ['Communication', 'Typing Speed']
        }

    res = client.get('/api/opportunities/qualification')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['is_detected'] is True
    assert data['qualification'] == 'Class 12'
    assert 'Communication' in data['skills']


def test_education_flow_unaffected(client):
    """Regression test ensuring existing education flow endpoints remain untouched and healthy."""
    res_dir = client.get('/career-direction')
    assert res_dir.status_code == 200
    assert b'Do you know what career you want?' in res_dir.data

    res_health = client.get('/api/opportunities/health')
    assert res_health.status_code == 200

