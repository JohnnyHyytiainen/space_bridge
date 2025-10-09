# Kommentarer: Svenska
# Kod: Engelska


from count_planets import pipeline_run


def test_smoke():
    res = pipeline_run("data/space_logs.jsonl", "data/planet_counts.csv")
    assert res["rows"] > 0
    assert sum(res["counts"].values()) == res["rows"]
    assert isinstance(res["skipped_badjson"], int)
    assert isinstance(res["ms"], float)

    # basic sanity check: top planet är konsekvent definierad.
    top = max(res["counts"].items(), key=lambda kv: kv[1])[0]
    assert isinstance(top, str)


if __name__ == "__main__":
    test_smoke()
    print("Okej!")
