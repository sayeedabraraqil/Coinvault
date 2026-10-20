import sys
import unittest
import json
from pathlib import Path
from datetime import datetime, timezone

# Ensure parent directory in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models.user import User, ApiToken
from app.models.coin import CoinEntry
from app.services.badges import init_default_badges

class CoinVaultTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        init_default_badges()

        # Seed sample test user
        self.user = User(
            username='test_grinder',
            email='grinder@test.local',
            display_name='Test Grinder',
            country='JP'
        )
        self.user.set_password('Password123!')
        db.session.add(self.user)

        # Seed admin
        self.admin = User(
            username='admin_test',
            email='admin@test.local',
            display_name='Admin Test',
            is_admin=True
        )
        self.admin.set_password('AdminPass123!')
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_landing_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'COINVAULT', response.data)
        self.assertIn(b'eFootball Coin', response.data)

    def test_leaderboards_page(self):
        response = self.client.get('/leaderboards?metric=richest')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Global Coin Leaderboards', response.data)

    def test_analytics_page(self):
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Global Coin Analytics', response.data)
        self.assertIn(b'Growth Score Formula', response.data)

    def test_compare_page(self):
        response = self.client.get('/compare')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Head-to-Head Vault Duel', response.data)

    def test_auth_login_success(self):
        response = self.client.post('/auth/login', data={
            'identity': 'test_grinder',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Terminal Dashboard', response.data)

    def test_api_token_and_userscript_endpoint(self):
        # 1. Generate API token for user
        raw_token, prefix, token_hash = ApiToken.generate_token()
        token = ApiToken(
            user_id=self.user.id,
            name='Test Script',
            prefix=prefix,
            token_hash=token_hash
        )
        db.session.add(token)
        db.session.commit()

        # 2. Transmit coin log via Bearer token
        payload = {
            'amount': 25400,
            'note': 'Verified Tampermonkey Sync Test'
        }
        response = self.client.post(
            '/api/v1/coins/log',
            headers={'Authorization': f'Bearer {raw_token}'},
            json=payload
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['amount'], 25400)
        self.assertEqual(data['source'], 'script')

        # 3. Check database entry
        entry = CoinEntry.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.amount, 25400)
        self.assertEqual(entry.source, 'script')

    def test_anti_cheat_anomaly_detection(self):
        # Initial normal entry
        entry1 = CoinEntry(
            user_id=self.user.id,
            amount=5000,
            source='self',
            logged_at=datetime.now(timezone.utc),
            is_flagged=False
        )
        db.session.add(entry1)
        db.session.commit()

        # Log an impossible sudden surge (+500,000 in short period)
        from app.services.anti_cheat import evaluate_entry_for_outliers
        is_flagged, reason = evaluate_entry_for_outliers(self.user, 505000, datetime.now(timezone.utc), 'self')
        self.assertTrue(is_flagged)
        self.assertIn('Sudden surge', reason)

    def test_search_users_api(self):
        response = self.client.get('/api/v1/search/users?q=test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]['username'], 'test_grinder')

if __name__ == '__main__':
    unittest.main()
