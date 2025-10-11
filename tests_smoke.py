# Kommentarer: Svenska
# Kod: Engelska


from count_planets import pipeline_run


def test_smoke():
    res = pipeline_run()
    assert res["rows"] > 0
    assert sum(res["counts"].values()) == res["rows"]
    for k in ["read_ms", "sort_ms", "write_ms", "verify_ms", "e_ms", "total_ms"]:
        assert isinstance(res[k], float)
    top = max(res["counts"].items(), key=lambda kv: kv[1])[0]
    assert isinstance(top, str)


if __name__ == "__main__":
    test_smoke()
    print("Okej!")
