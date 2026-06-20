from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, StudyRecord


class StudyRecordApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            username='user',
            password='password',
        )
        self.category = Category.objects.create(name='tech')
        self.record = StudyRecord.objects.create(
            user=self.user,
            category=self.category,
            title='Python',
            study_date=date(2026, 5, 25),
            duration_minutes=60,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_update_persists_review_fields(self):
        response = self.client.patch(
            f'/api/study/records/{self.record.id}/',
            {
                'understanding': 4,
                'questions': '疑問点',
                'struggles': '難しかったこと',
                'achievements': 'できたこと',
                'solutions': '解決したこと',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.understanding, 4)
        self.assertEqual(self.record.questions, '疑問点')
        self.assertEqual(self.record.struggles, '難しかったこと')
        self.assertEqual(self.record.achievements, 'できたこと')
        self.assertEqual(self.record.solutions, '解決したこと')

    def test_list_returns_review_fields_for_study_log(self):
        self.record.understanding = 5
        self.record.questions = '疑問点'
        self.record.struggles = '難しかったこと'
        self.record.achievements = 'できたこと'
        self.record.solutions = '解決したこと'
        self.record.save()

        response = self.client.get('/api/study/records/')

        self.assertEqual(response.status_code, 200)
        item = response.data['results'][0]
        self.assertEqual(item['understanding'], 5)
        self.assertEqual(item['questions'], '疑問点')
        self.assertEqual(item['struggles'], '難しかったこと')
        self.assertEqual(item['achievements'], 'できたこと')
        self.assertEqual(item['solutions'], '解決したこと')
