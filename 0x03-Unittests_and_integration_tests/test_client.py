#!/usr/bin/env python3
"""Unit & integration tests for client.py"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient (Tasks 4–7)"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """org property calls get_json and returns payload"""
        expected = {
            "login": org_name,
            "repos_url": (
                "https://api.github.com/orgs/{}/repos".format(org_name)
            ),
        }
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)

        self.assertEqual(client.org, expected)
        org_url = "https://api.github.com/orgs/{}".format(org_name)
        mock_get_json.assert_called_once_with(org_url)

    def test_public_repos_url(self):
        """_public_repos_url comes from org['repos_url']"""
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos returns repo names and supports license filter"""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value="http://api/repos",
        ):
            client = GithubOrgClient("any")
            self.assertEqual(
                client.public_repos(), ["repo1", "repo2", "repo3"]
            )
            self.assertEqual(
                client.public_repos(license="apache-2.0"), ["repo2"]
            )
            mock_get_json.assert_called_once_with("http://api/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns True/False based on license key"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key), expected
        )


@parameterized_class([{
    "org_payload": TEST_PAYLOAD[0][0],
    "repos_payload": TEST_PAYLOAD[0][1],
    "expected_repos": TEST_PAYLOAD[0][2],
    "apache2_repos": TEST_PAYLOAD[0][3],
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return fixture payloads"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # blank line before nested def to satisfy E306

        def _mock_get(url):
            resp = Mock()
            if url.endswith("/orgs/google"):
                resp.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                resp.json.return_value = cls.repos_payload
            else:
                resp.json.return_value = {}
            return resp

        mock_get.side_effect = _mock_get

    @classmethod
    def tearDownClass(cls):
        """Stop requests.get patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """All repo names returned (no license filter)"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Only repos with Apache-2.0 license are returned"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"), self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
