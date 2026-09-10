import sys, os, json
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app

with app.test_client() as client:
    # 1. Simulate admin session
    with client.session_transaction() as sess:
        sess['admin_logged_in'] = True
        sess['admin_id'] = 8

    # 2. Test GET /admin/predictions-v2
    print("=== TEST 1: GET /admin/predictions-v2 ===")
    r = client.get('/admin/predictions-v2')
    print('Status code:', r.status_code, '(expected 200)')
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    html = r.get_data(as_text=True)
    assert 'Prediction Model 2' in html, "Missing 'Prediction Model 2' in HTML"
    assert 'What Has Happened' in html, "Missing 'What Has Happened' in HTML"
    assert 'Why It Happened' in html, "Missing 'Why It Happened' in HTML"
    assert 'What Will Happen' in html, "Missing 'What Will Happen' in HTML"
    print("HTML checks passed: All 3 core sections rendered successfully.")

    # 3. Test POST /admin/api/predict-v2 with various scenarios
    print("\n=== TEST 2: POST /admin/api/predict-v2 ===")
    scenarios = [
        {'forecast_month': '2026-10', 'scenario': 'baseline', 'growth_adj': 0.0},
        {'forecast_month': '2026-11', 'scenario': 'optimistic', 'growth_adj': 10.0},
        {'forecast_month': '2027-01', 'scenario': 'conservative', 'growth_adj': -5.0},
        {'forecast_month': '2027-03', 'scenario': 'baseline', 'growth_adj': 5.0}
    ]

    for sc in scenarios:
        res = client.post('/admin/api/predict-v2', data=json.dumps(sc), content_type='application/json')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        payload = res.get_json()
        assert payload.get('success') is True, f"Failed payload: {payload}"
        data = payload['data']
        rev = data['predicted_revenue']
        orders = data['predicted_orders']
        print(f"[{sc['scenario'].upper()}] {sc['forecast_month']} (growth adj {sc['growth_adj']}%): Rs {rev:,.2f} (~{orders} orders)")
        assert rev > 0, "Forecast revenue should be > 0"
        assert orders > 0, "Forecast orders should be > 0"

    # 4. Test validation error handling
    print("\n=== TEST 3: Validation checks ===")
    res_err = client.post('/admin/api/predict-v2', data=json.dumps({'forecast_month': ''}), content_type='application/json')
    assert res_err.status_code == 200
    p_err = res_err.get_json()
    assert p_err.get('success') is False
    print("Empty forecast_month rejected successfully:", p_err.get('error'))

print("\nAll Model 2 tests passed with 100% success!")
