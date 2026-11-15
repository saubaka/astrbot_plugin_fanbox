import json

from fanbox_stats import LOG_LIMIT, Stats

H = 3600
NOW = 1_800_000_000.0  # 整点附近的固定时间，方便算窗口


def test_checks_pushes_and_periods():
    st = Stats()
    for i in range(30):  # 过去 30 小时，每小时一次检查
        st.record_check("a", "ok", 100, NOW - i * H, name="作者A", latest={"id": "1"})
    st.record_check("a", "blocked", 50, NOW - 10, message="HTTP 403")
    st.record_push(
        "a",
        name="作者A",
        post_id="9",
        title="t",
        post_url="u",
        umo="p:GroupMessage:1",
        style="text",
        ok=True,
        now=NOW - 2 * H,
    )
    st.record_push(
        "a",
        name="作者A",
        post_id="8",
        title="t",
        post_url="u",
        umo="p:GroupMessage:1",
        style="card",
        ok=False,
        error="找不到会话",
        now=NOW - 5 * H,
    )
    s = st.summary(NOW)
    assert s["series"]["checks"]["periods"]["day"] == 25
    assert s["series"]["checks"]["periods"]["total"] == 31
    assert s["series"]["pushes"]["periods"] == {
        "hour": 0,
        "day": 1,
        "week": 1,
        "total": 1,
    }
    assert s["series"]["push_failures"]["periods"]["day"] == 1
    assert len(s["series"]["checks"]["hourly"]) == 24
    c = s["creators"]["a"]
    assert (
        c["name"] == "作者A"
        and c["last_outcome"] == "blocked"
        and c["last_error"] == "HTTP 403"
    )
    assert c["outcomes_day"] == {"ok": 24, "not_found": 0, "blocked": 1, "error": 0}
    assert c["pushes"]["day"] == 1 and c["counts"]["push_failures"] == 1
    assert sum(c["hourly_pushes"]) == 1
    assert [p["post_id"] for p in s["pushes"]] == ["8", "9"]  # 新的在前


def test_round_trip_through_json():
    st = Stats()
    st.record_check("a", "ok", 120, NOW, name="A")
    st.record_error("card_failed", "no font", creator="a", now=NOW)
    st.record_card(True, 300)
    st.record_card(False, 0)
    again = Stats(json.loads(json.dumps(st.to_dict())))
    s1, s2 = st.summary(NOW), again.summary(NOW)
    assert s1 == s2
    assert s2["card"] == {"renders": 2, "failures": 1, "avg_ms": 300}


def test_bad_data_is_ignored():
    st = Stats(
        {
            "series": {"checks": {"x": 1, "5": "y"}},
            "creators": {"a": "nope"},
            "pushes": [1, None],
            "totals": {"checks": "z"},
        }
    )
    assert st.summary(NOW)["series"]["checks"]["periods"]["total"] == 0
    assert st.creators == {} and st.pushes == []


def test_prune_and_log_limits():
    st = Stats()
    for i in range(LOG_LIMIT + 10):
        st.record_error("blocked", f"e{i}", creator="a", now=NOW - i)
    assert len(st.errors) == LOG_LIMIT
    st.record_error("list_failed", "old", now=NOW - 40 * 86400)
    st.record_check("a", "ok", 1, NOW - 100 * 86400)
    st.prune(NOW)
    assert all(e["message"] != "old" for e in st.errors)
    assert st.series["checks"] == {}
    assert st.creators["a"]["hourly"]["checks"] == {}


def test_unknown_kinds_are_normalised():
    st = Stats()
    st.record_check("a", "weird", 1, NOW)
    st.record_error("weird", "x", now=NOW)
    assert st.creators["a"]["last_outcome"] == "error"
    assert st.errors[0]["kind"] == "list_failed"


def test_forget_creator():
    st = Stats()
    st.record_check("a", "ok", 1, NOW)
    st.forget_creator("a")
    assert "a" not in st.summary(NOW)["creators"]
