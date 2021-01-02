import urllib.request
import json


GITHUB_GRAPHQL_API_ENDPOINT = "https://api.github.com/graphql"


def fetch_data_by_query(
    query: str, token: str, endpoint: str = GITHUB_GRAPHQL_API_ENDPOINT
) -> list:

    headers = {"Authorization": f"bearer {token}"}
    post_data = {"query": query}

    req = urllib.request.Request(
        GITHUB_GRAPHQL_API_ENDPOINT, json.dumps(post_data).encode(), headers
    )

    res = ""
    with urllib.request.urlopen(req) as f:
        res = f.read().decode("utf-8")

    return json.loads(res)["data"]


def fetch_user_id(token: str, endpoint: str = GITHUB_GRAPHQL_API_ENDPOINT) -> str:

    q = "query { viewer { login } }"
    data = fetch_data_by_query(q, token, endpoint)

    return data["viewer"]["login"]


def fetch_repos_by_name(
    name: str, token: str, endpoint: str = GITHUB_GRAPHQL_API_ENDPOINT
) -> list:

    q = f"""
query {{
  search(query: "{name}", type: REPOSITORY, first: 10) {{
    nodes {{
      ... on Repository {{
        nameWithOwner
        description
      }}
    }}
  }}
}}
"""
    data = fetch_data_by_query(q, token, endpoint)

    return data["search"]["nodes"]
