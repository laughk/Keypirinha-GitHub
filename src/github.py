# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet

from .github_api_helper import fetch_repos_by_name, fetch_user_id


class github(kp.Plugin):
    """
    GitHub Plugin

    - repository
    - my account access
    """

    CMD_PREFIX = {
        "root": "github:",
        "repos": "github repos:",
        "repos_choise": "github repos choice:",
        "repos_action": "github repos action:",
        "my_account": "github my:",
        "my_account_action": "github my action:",
    }

    CMD_GH = CMD_PREFIX["root"]
    CMD_GH_REPOS = CMD_PREFIX["repos"]
    CMD_GH_REPO_CHOICE = CMD_PREFIX["repos_choise"] + "{reponame}"
    CMD_GH_REPO_ACTION = CMD_PREFIX["repos_action"] + "{action}"
    CMD_GITHUB_MY_ACCOUNT = CMD_PREFIX["my_account"]
    CMD_GITHUB_MY_ACCOUNT_ACTION = CMD_PREFIX["my_account_action"] + "{action}"

    LABEL_PREFIX = "GitHub: "

    def __init__(self):
        super().__init__()

    def on_start(self):
        self.token = self.load_settings().get(
            "github_access_token", "var", unquote=True
        )

    def on_catalog(self):
        catalog = []
        catalog.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="GitHub",
                short_desc="Github Plugin",
                target=self.CMD_GH,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL,
            )
        )
        self.set_catalog(catalog)

    def on_suggest(self, user_input: str, items_chain: list):
        if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = []

        if items_chain[0].target() == self.CMD_GH:
            suggestions = self.gen_categories()

            if len(items_chain) >= 2:

                if items_chain[1].target() == self.CMD_GH_REPOS:
                    suggestions = self.gen_repos_suggestion(user_input)

                    if len(items_chain) >= 3:
                        reponame = str(items_chain[2]).replace(self.LABEL_PREFIX, "")
                        suggestions = self.gen_repos_action_suggestion(reponame)

                if items_chain[1].target() == self.CMD_GITHUB_MY_ACCOUNT:
                    suggestions = self.gen_my_account_sugestions()

        self.set_suggestions(suggestions, kp.Match.FUZZY, kp.Sort.NONE)

    def on_execute(self, item, action):

        target = item.target()
        p = ""

        if target == self.CMD_GH:
            return
        elif self.CMD_PREFIX["repos_action"] in target:
            p = target.replace(self.CMD_PREFIX["repos_action"], "")
            print(p)
        elif self.CMD_PREFIX["my_account_action"] in target:
            p = target.replace(self.CMD_PREFIX["my_account_action"], "")

        if "https://" in p:
            url = p
        else:
            url = f"https://github.com{p}"

        kpu.web_browser_command(url=url, execute=True)

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass

    def gen_categories(self) -> list:  # -> list[kp.CatalogItem]
        catalog = []

        repository_cmd = self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label=self.LABEL_PREFIX + "Repository",
            short_desc="Github Repository Search",
            target=self.CMD_GH_REPOS,
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.KEEPALL,
        )
        catalog.append(repository_cmd)

        my_account_cmd = self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label=self.LABEL_PREFIX + "My Account",
            short_desc="Github My Account",
            target=self.CMD_GITHUB_MY_ACCOUNT,
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.KEEPALL,
        )
        catalog.append(my_account_cmd)

        return catalog

    def gen_my_account_sugestions(self):  # -> list[kp.CatalogItem]

        try:
            user_id = fetch_user_id(self.token)
        except Exception as e:
            self.err(e)
            return "fetching data from github graphql api has failed."

        my_account_pages = [
            # ("name", "path")
            ("dashboard", "/"),
            ("notifications", "/notifications"),
            ("issues", "/issues"),
            ("pulls", "/pulls"),
            ("settings", "/settings/profile"),
            ("personal access tokens", "/settings/tokens"),
            ("profile", f"/{user_id}"),
            ("repos", f"/{user_id}/?tab=repositories"),
            ("stars", f"/{user_id}/?tab=stars"),
            ("gists", f"https://gist.github.com/{user_id}"),
        ]

        return [
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=label,
                target=self.CMD_GITHUB_MY_ACCOUNT_ACTION.format(action=path),
                short_desc="",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS,
            )
            for label, path in my_account_pages
        ]

    def gen_repos_suggestion(self, user_input: str) -> list:  # -> list[kp.CatalogItem]

        try:
            repo_names = fetch_repos_by_name(user_input, self.token)
        except Exception as e:
            self.err(e)
            return "fetching data from github graphql api has failed."

        suggestions = []
        for r in repo_names:
            desc = r["description"] if r.get("description") else ""
            suggestions.append(
                self.create_item(
                    category=kp.ItemCategory.KEYWORD,
                    label=self.LABEL_PREFIX + r["nameWithOwner"],
                    target=self.CMD_GH_REPO_CHOICE.format(reponame=r["nameWithOwner"]),
                    short_desc=desc,
                    args_hint=kp.ItemArgsHint.REQUIRED,
                    hit_hint=kp.ItemHitHint.KEEPALL,
                )
            )

        return suggestions

    def gen_repos_action_suggestion(
        self, reponame: str, gh_host: str = "github.com"
    ) -> list:  # -> list[kp.CatalogItem]

        actions = [
            # (action, path, desctiption)
            ("Open", f"/{reponame}", "Open github repository"),
            ("issues", f"/{reponame}/issues", ""),
            ("new issue", f"/{reponame}/issues/new", ""),
            ("milestones", f"/{reponame}/milestones", ""),
            ("pulls", f"/{reponame}/pulls", ""),
            ("projects", f"/{reponame}/projects", ""),
            ("pulse", f"/{reponame}/pulse", ""),
            ("releases", f"/{reponame}/releases", ""),
            ("wiki", f"/{reponame}/wiki", ""),
        ]

        return [
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=self.LABEL_PREFIX + f"{action}: {gh_host}{path}",
                target=self.CMD_GH_REPO_ACTION.format(action=path),
                short_desc=desc,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS,
            )
            for action, path, desc in actions
        ]
