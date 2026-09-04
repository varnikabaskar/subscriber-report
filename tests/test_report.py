import fitz

from src.report.template_renderer import mock_report_data, render_report


def test_generate_mock_report(tmp_path):
    report_path = render_report(mock_report_data(), tmp_path / "sample_report.pdf")
    document = fitz.open(report_path)
    assert document.page_count == 3
    assert "Subscribers" in document[0].get_text()
    assert "125,432" in document[1].get_text()
    document.close()