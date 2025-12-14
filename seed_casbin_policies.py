from app.core.casbin import get_casbin_enforcer


def main():
    e = get_casbin_enforcer()

    e.clear_policy()

    e.add_policy("admin", "1", "admin_panel", "read")
    e.add_policy("admin", "1", "admin_panel", "write")
    e.add_policy("admin", "1", "users", "read")
    e.add_policy("admin", "1", "users", "write")
    e.add_grouping_policy("alice", "1", "admin")

    e.add_policy("user", "2", "data1", "read")
    e.add_grouping_policy("bob", "2", "user")

    e.save_policy()


if __name__ == "__main__":
    main()