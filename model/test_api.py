import sys, os, json
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app

with app.test_client() as client:
    # Simulate admin session
    with client.session_transaction() as sess:
        sess['admin_logged_in'] = True
        sess['admin_id'] = 8

    # Test 1: Page with auth
    r = client.get('/admin/predictions')
    print('GET /admin/predictions (auth):', r.status_code, '(should be 200)')

    # Test 2: Valid prediction
    print()
    print('=== VALID FORECASTS ===')
    tests = ['2026-10', '2026-11', '2027-01']
    for month in tests:
        r = client.post('/admin/predict', data=json.dumps({'forecast_month': month}), content_type='application/json')
        resp = r.get_json()
        if resp and resp.get('success'):
            print(f"Forecast for {month}: Rs {resp['predicted_revenue']:,.2f}")
        else:
            print('ERROR:', resp)

    # Test 3: Invalid inputs
    print()
    print('=== VALIDATION ERRORS ===')
    invalid_tests = [
        {'forecast_month': ''},
        {'forecast_month': 'October 2026'},
        {'forecast_month': '2026-05'} # Before start date
    ]
    for tc in invalid_tests:
        r = client.post('/admin/predict', data=json.dumps(tc), content_type='application/json')
        resp = r.get_json()
        print(f"Input {tc} -> success={resp.get('success')} error='{resp.get('error','')}'")

print('\nAll tests complete.')
