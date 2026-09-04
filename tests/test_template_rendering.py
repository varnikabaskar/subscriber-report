import fitz
import numpy as np

from src.report.template_renderer import render_report, mock_report_data


def test_mock_report_matches_master_page_count(tmp_path):
    output = render_report(mock_report_data(), tmp_path / "sample_report.pdf")
    document = fitz.open(output)
    assert document.page_count == 3
    assert document[0].rect == fitz.Rect(0, 0, 595.5, 842.25)
    assert document[1].rect == document[0].rect
    assert document[2].rect == document[0].rect
    document.close()


def test_static_template_areas_are_unchanged(tmp_path):
    output = render_report(mock_report_data(), tmp_path / "sample_report.pdf")
    master = fitz.open("src/report/template/template.pdf")
    generated = fitz.open(output)
    dynamic = {
        0: [(55, 525, 260, 570)],
        1: [(55, 130, 540, 252), (300, 293, 535, 490), (55, 565, 540, 805)],
        2: [(55, 135, 500, 330), (55, 375, 505, 680), (60, 800, 540, 825)],
    }
    for index in range(3):
        original_pixmap = master[index].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        current_pixmap = generated[index].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        original = np.frombuffer(original_pixmap.samples, dtype=np.uint8).reshape(
            original_pixmap.height, original_pixmap.width, 3
        )
        current = np.frombuffer(current_pixmap.samples, dtype=np.uint8).reshape(
            current_pixmap.height, current_pixmap.width, 3
        )
        mask = np.zeros(original.shape[:2], dtype=bool)
        scale_x = original_pixmap.width / 595.5
        scale_y = original_pixmap.height / 842.25
        for left, top, right, bottom in dynamic[index]:
            mask[int(top * scale_y):int(bottom * scale_y), int(left * scale_x):int(right * scale_x)] = True
        difference = np.abs(original[~mask].astype(np.int16) - current[~mask].astype(np.int16))
        assert np.max(difference) <= 3
    master.close()
    generated.close()