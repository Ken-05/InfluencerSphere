"""
firestore_service.py
--------------------
Abstracts all interactions with the Google Firestore database.
Handles initialization, authentication, and core CRUD operations on documents
and collections for all backend services (Influencers, Alerts, ML Data).
"""
import json
import os
from typing import Dict, Any, Optional, Callable, List
from firebase_admin import credentials, initialize_app, firestore, auth

# Simulate the interaction of firebase admin using simple classes for type hinting and structure for now

class MockFirestoreClient:
    """Mock class representing the Firestore database client."""

    def collection(self, path: str):
        return MockCollectionRef(path)

    def document(self, path: str):
        return MockDocumentRef(path)


class MockCollectionRef:
    """Mock class representing a Firestore Collection reference."""

    def __init__(self, path: str):
        self.path = path
        print(f"DEBUG: Initialized collection ref for: {path}")

    def add(self, data: Dict[str, Any]):
        """Simulates adding a new document."""
        mock_id = f"mock-doc-{len(data)}"
        print(f"INFO: Added new document to {self.path} with mock ID {mock_id}")
        return mock_id, MockDocumentRef(f"{self.path}/{mock_id}")

    def stream(self):
        """Simulates streaming documents (e.g., for large queries)."""
        # Return mock data structure
        return [
            MockDocumentSnapshot(f"{self.path}/doc1", {"id": "doc1", "data": "Influencer 1"}),
            MockDocumentSnapshot(f"{self.path}/doc2", {"id": "doc2", "data": "Influencer 2"}),
        ]

    def where(self, field: str, op: str, value: Any):
        """Simulates a query condition."""
        print(f"DEBUG: Query condition added: {field} {op} {value}")
        return self

    def get(self):
        """Simulates getting documents from a collection."""
        return self.stream()


class MockDocumentRef:
    """Mock class representing a Firestore Document reference."""

    def __init__(self, path: str):
        self.path = path
        print(f"DEBUG: Initialized document ref for: {path}")

    def get(self):
        """Simulates getting a single document."""
        return MockDocumentSnapshot(self.path, {"id": self.path.split('/')[-1], "mock_field": "test_data"})

    def set(self, data: Dict[str, Any], merge: bool = False):
        """Simulates setting or merging data into a document."""
        print(f"INFO: Document {self.path} updated/set. Merge={merge}")

    def update(self, data: Dict[str, Any]):
        """Simulates updating existing fields in a document."""
        print(f"INFO: Document {self.path} updated.")

    def delete(self):
        """Simulates deleting a document."""
        print(f"INFO: Document {self.path} deleted.")


class MockDocumentSnapshot:
    """Mock class representing a Firestore Document snapshot."""

    def __init__(self, ref: str, data: Dict[str, Any]):
        self.id = ref.split('/')[-1]
        self._data = data
        self.exists = True

    def to_dict(self) -> Dict[str, Any]:
        """Returns the document data."""
        return self._data


class FirestoreService:
    """
    Manages connections and operations with Firestore.
    Uses public and private data paths based on the application ID and user ID.
    """

    def __init__(self):
        # Retrieve mandatory global variables from the runtime environment
        self.app_id = os.getenv('__app_id', 'default-influencersphere-app')

        # Load the mock or real Firebase Config
        try:
            config_str = os.getenv('__firebase_config', '{}')
            self.firebase_config = json.loads(config_str)
        except json.JSONDecodeError:
            self.firebase_config = {}

        # The initial auth token is provided for securing the connection
        self.initial_auth_token = os.getenv('__initial_auth_token')

        # Later: initialize the Firebase Admin SDK
        # initialize a mock client for now
        self.db: MockFirestoreClient = self._initialize_db_client()
        self.current_user_id: Optional[str] = None
        self._authenticate_mock_user()

    def _initialize_db_client(self) -> MockFirestoreClient:
        """Initializes the Firestore client (mocked)."""
        print(f"INFO: Initializing Firestore client for App ID: {self.app_id}")
        # Placeholder for real Admin SDK initialization
        return MockFirestoreClient()

    def _authenticate_mock_user(self):
        """Simulates successful authentication using the provided token."""
        # Later: use the Admin SDK to verify the token and extract the UID.
        if self.initial_auth_token:
            # Mocking user ID extraction from a valid token
            self.current_user_id = f"fastapi-user-{self.app_id}-authenticated"
            print(f"INFO: Successfully authenticated mock user: {self.current_user_id}")
        else:
            # Fallback for unauthenticated access or testing
            self.current_user_id = f"fastapi-guest-{self.app_id}"
            print(f"WARNING: No auth token found. Using guest ID: {self.current_user_id}")

    # --- Path Helpers ---

    def _get_private_collection_path(self, collection_name: str) -> str:
        """
        Generates the path for user-private collections (e.g., user alerts).
        Path: /artifacts/{appId}/users/{userId}/{collection_name}
        """
        if not self.current_user_id:
            raise Exception("Authentication required for private data access.")
        return f"artifacts/{self.app_id}/users/{self.current_user_id}/{collection_name}"

    def _get_public_collection_path(self, collection_name: str) -> str:
        """
        Generates the path for public/shared collections (e.g., influencer profiles).
        Path: /artifacts/{appId}/public/data/{collection_name}
        """
        return f"artifacts/{self.app_id}/public/data/{collection_name}"

    # --- Core CRUD Operations ---

    async def get_document(self, collection_name: str, doc_id: str, is_private: bool = False) -> Optional[
        Dict[str, Any]]:
        """Retrieves a single document by ID."""
        path = (self._get_private_collection_path(collection_name) if is_private else self._get_public_collection_path(
            collection_name))
        doc_ref = self.db.document(f"{path}/{doc_id}")

        snapshot = doc_ref.get()
        if snapshot.exists:
            data = snapshot.to_dict()
            # Ensure the document ID is included in the returned data
            data['id'] = snapshot.id
            return data
        return None

    async def get_collection(self, collection_name: str, is_private: bool = False) -> List[Dict[str, Any]]:
        """Retrieves all documents from a collection."""
        path = (self._get_private_collection_path(collection_name) if is_private else self._get_public_collection_path(
            collection_name))
        collection_ref = self.db.collection(path)

        results = []
        for doc in collection_ref.stream():
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
        return results

    async def add_document(self, collection_name: str, data: Dict[str, Any], is_private: bool = False) -> str:
        """Adds a new document to a collection, returning the generated ID."""
        path = (self._get_private_collection_path(collection_name) if is_private else self._get_public_collection_path(
            collection_name))
        collection_ref = self.db.collection(path)

        # Simulate an asynchronous add operation
        doc_id, _ = collection_ref.add(data)
        return doc_id

    async def set_document(self, collection_name: str, doc_id: str, data: Dict[str, Any], is_private: bool = False,
                           merge: bool = False):
        """Sets a document, potentially overwriting or merging."""
        path = (self._get_private_collection_path(collection_name) if is_private else self._get_public_collection_path(
            collection_name))
        doc_ref = self.db.document(f"{path}/{doc_id}")

        # Simulate an asynchronous set operation
        doc_ref.set(data, merge=merge)

    async def delete_document(self, collection_name: str, doc_id: str, is_private: bool = False):
        """Deletes a document by ID."""
        path = (self._get_private_collection_path(collection_name) if is_private else self._get_public_collection_path(
            collection_name))
        doc_ref = self.db.document(f"{path}/{doc_id}")

        # Simulate an asynchronous delete operation
        doc_ref.delete()


# Use a factory function to ensure a single, cached instance is used throughout the FastAPI app
# Later: use functools.lru_cache for singleton pattern.
_firestore_instance: Optional[FirestoreService] = None


def get_firestore_service() -> FirestoreService:
    """Dependency for FastAPI to get a singleton instance of the service."""
    global _firestore_instance
    if _firestore_instance is None:
        _firestore_instance = FirestoreService()
    return _firestore_instance