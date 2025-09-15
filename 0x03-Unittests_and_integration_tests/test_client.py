class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient (Tasks 4–7)"""

    # Task 4
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        expected = {"login": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    # Task 5
    def test_public_repos_url(self):
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    # Task 6
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = repos_payload

        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock, return_value="http://api/repos"):
            client = GithubOrgClient("any")
            self.assertEqual(client.public_repos(), ["repo1", "repo2", "repo3"])
            self.assertEqual(client.public_repos(license="apache-2.0"), ["repo2"])
            mock_get_json.assert_called_once_with("http://api/repos")

    # Task 7
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)
