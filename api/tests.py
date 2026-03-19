from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class NotesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_health_check_allows_anonymous(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "API is running"})

    def test_register_and_me(self):
        register_response = self.client.post(
            "/api/register/",
            {"username": "newuser", "password": "password123"},
            format="json",
        )
        self.assertEqual(register_response.status_code, 201)
        user_id = register_response.json()["id"]

        token_response = self.client.post(
            "/api/token/",
            {"username": "newuser", "password": "password123"},
            format="json",
        )
        self.assertEqual(token_response.status_code, 200)
        access = token_response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        me_response = self.client.get("/api/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["id"], user_id)

    def test_list_requires_auth(self):
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, 401)

    def test_create_validation_errors(self):
        self.authenticate(self.user)
        response = self.client.post("/api/notes/", {"content": "Missing title"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_and_list_only_own_notes(self):
        self.authenticate(self.user)
        create_response = self.client.post(
            "/api/notes/",
            {"title": "First", "content": "Hello"},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["user"], self.user.id)

        self.authenticate(self.other_user)
        self.client.post(
            "/api/notes/",
            {"title": "Other", "content": "Secret"},
            format="json",
        )

        self.authenticate(self.user)
        list_response = self.client.get("/api/notes/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(list_response.json()[0]["title"], "First")

    def test_cannot_access_other_users_note(self):
        self.authenticate(self.other_user)
        create_response = self.client.post(
            "/api/notes/",
            {"title": "Private", "content": "Hidden"},
            format="json",
        )
        note_id = create_response.json()["id"]

        self.authenticate(self.user)
        response = self.client.get(f"/api/notes/{note_id}/")
        self.assertEqual(response.status_code, 403)

    def test_note_not_found(self):
        self.authenticate(self.user)
        response = self.client.get("/api/notes/99999/")
        self.assertEqual(response.status_code, 404)

    def test_update_and_delete_own_note(self):
        self.authenticate(self.user)
        create_response = self.client.post(
            "/api/notes/",
            {"title": "Draft", "content": "Body"},
            format="json",
        )
        note_id = create_response.json()["id"]

        update_response = self.client.put(
            f"/api/notes/{note_id}/",
            {"title": "Updated", "content": "New"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["title"], "Updated")

        delete_response = self.client.delete(f"/api/notes/{note_id}/")
        self.assertEqual(delete_response.status_code, 204)


class ProductsOrdersApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_product_crud_and_filtering(self):
        self.authenticate(self.user)
        create_response = self.client.post(
            "/api/products/",
            {"name": "Widget", "description": "Test", "price": "9.99", "stock": 5},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        product_id = create_response.json()["id"]

        list_response = self.client.get("/api/products/?search=widget")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["count"], 1)

        detail_response = self.client.get(f"/api/products/{product_id}/")
        self.assertEqual(detail_response.status_code, 200)

        update_response = self.client.put(
            f"/api/products/{product_id}/",
            {"name": "Widget", "description": "Test", "price": "8.50", "stock": 3},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)

    def test_orders_are_scoped_to_user(self):
        self.authenticate(self.user)
        product_response = self.client.post(
            "/api/products/",
            {"name": "Gadget", "description": "X", "price": "5.00", "stock": 10},
            format="json",
        )
        product_id = product_response.json()["id"]

        order_response = self.client.post(
            "/api/orders/",
            {"product": product_id, "quantity": 2, "status": "pending"},
            format="json",
        )
        self.assertEqual(order_response.status_code, 201)
        order_id = order_response.json()["id"]

        self.authenticate(self.other_user)
        forbidden = self.client.get(f"/api/orders/{order_id}/")
        self.assertEqual(forbidden.status_code, 404)
