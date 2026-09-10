from pathlib import Path

from tools.build_unistrut_ohio_manifest import build_manifest


def test_build_manifest_extracts_shopify_documents():
    html = """
    <h2>Metal Framing</h2>
    <a href="https://cdn.shopify.com/s/files/foo/P1000.pdf">P1000</a>
    <a href="/pages/not-a-pdf">Ignore me</a>
    <h2>Fittings</h2>
    <a href="https://cdn.shopify.com/s/files/foo/P1026.pdf">P1026</a>
    """

    manifest = build_manifest(html)
    docs = manifest["documents"]

    assert manifest["schema_version"] == 1
    assert [d["label"] for d in docs] == ["P1026", "P1000"]
    assert {d["category"] for d in docs} == {"Fittings", "Metal Framing"}
    assert all(d["document_url"].startswith("https://cdn.shopify.com/") for d in docs)


def test_manifest_has_no_duplicate_document_urls():
    html = """
    <h2>Metal Framing</h2>
    <a href="https://cdn.shopify.com/s/files/foo/P1000.pdf">P1000</a>
    <a href="https://cdn.shopify.com/s/files/foo/P1000.pdf">P1000 duplicate label</a>
    """

    manifest = build_manifest(html)
    urls = [d["document_url"] for d in manifest["documents"]]
    assert len(urls) == len(set(urls))
