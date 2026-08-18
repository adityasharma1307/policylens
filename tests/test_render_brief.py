from civiclens.report.render_brief import _split_front_matter


def test_split_front_matter_extracts_title_and_subtitle():
    text = '---\ntitle: "My Title"\nsubtitle: "My Subtitle"\n---\n# Body\n\nHello.'
    meta, body = _split_front_matter(text)
    assert meta["title"] == "My Title"
    assert meta["subtitle"] == "My Subtitle"
    assert body.strip() == "# Body\n\nHello."


def test_split_front_matter_handles_missing_front_matter():
    text = "# Just a body\n\nNo front matter here."
    meta, body = _split_front_matter(text)
    assert meta == {}
    assert body == text
