#!/usr/bin/env python3
"""Unit & integration tests for client.py"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient (Tasks 4–7)"""

    # Task 4: parameterize and patch as decorators
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """org property calls get_json with ORG_URL and returns payload"""
        expected = {"login": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    # Task 5: mock a property via patching the memoized org
    def test_public_repos_url(self):
        """_public_repos_url derives from org['repos_url']"""
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch.object(GithubOrgClient, "org", new_callable=Mock(return_value=payload)):
            client = GithubOrgClient("google")
            self.assertEqual(
                client._public_repos_url, "https://api.github.com/orgs/google/repos"
            )

    # Task 6: more patching
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos returns repo names and calls dependencies once"""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},  # no license
        ]
        mock_get_json.return_value = repos_payload
        # Mock the URL property used by repos_payload
        with patch.object(GithubOrgClient, "_public_repos_url", new="http://api/repos"):
            client = GithubOrgClient("any")
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])

            # license filter
            repos_apache = client.public_repos(license="apache-2.0")
            self.assertEqual(repos_apache, ["repo2"])

            # called once because repos_payload is memoized per instance
            mock_get_json.assert_called_once_with("http://api/repos")

    # Task 7: parameterize has_license
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns True/False depending on license key"""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


# Task 8: Integration tests (fixtures) — only external boundary (HTTP) is mocked
@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos using fixtures"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get with proper side effects"""
        # We’ll simulate requests.get(...).json() returning different payloads
        # depending on the URL
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Build a side_effect that returns a mock whose .json() yields the
        # corresponding payload for the URL passed to requests.get
        def _mock_get(url):
            resp = Mock()
            if url.endswith("/orgs/google"):
                resp.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                resp.json.return_value = cls.repos_payload
            else:
                # Fallback in case of unexpected URL
                resp.json.return_value = {}
            return resp

        mock_get.side_effect = _mock_get

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """All repo names returned (no license filter)"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Only repos matching Apache-2.0 license are returned"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
