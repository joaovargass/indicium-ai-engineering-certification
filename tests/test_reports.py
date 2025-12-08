"""Comprehensive tests for report generation tools."""

# Add src to path
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from tools.reports import generate_chat_report, generate_download_report


class TestGenerateDownloadReport:
    """Test generate_download_report tool."""

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_download_report_basic(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test basic download report generation."""
        # Setup mocks
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo executivo"
        mock_metrics_table.return_value = "| Métrica | Valor |"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'
        mock_render.return_value = "# Relatório SRAG — Brasil\n\nConteúdo"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test_report.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test_report.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 1000
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        result = generate_download_report.invoke(
            {"uf": None, "days": 30, "months": 12, "include_news": False}
        )

        assert "report_content" in result
        assert "file_path" in result
        assert "file_size" in result
        assert result["file_size"] == 1000

    def test_generate_download_report_validation_fails(self):
        """Test validation failure."""
        result = generate_download_report.invoke(
            {"days": 5, "months": 12}  # days too low
        )

        assert "error" in result
        assert result["report_content"] == ""
        assert result["file_path"] == ""

    def test_generate_download_report_validation_months_fails(self):
        """Test validation failure for months."""
        result = generate_download_report.invoke(
            {"days": 30, "months": 30}  # months too high
        )

        assert "error" in result

    def test_generate_download_report_validation_max_news_fails(self):
        """Test validation failure for max_news."""
        result = generate_download_report.invoke(
            {"days": 30, "months": 12, "max_news": 10}  # max_news too high
        )

        assert "error" in result

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_download_report_with_customization(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test download report with user customization."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = "Notícias"
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'
        mock_render.return_value = "# Report"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 500
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        # Test with all sections disabled
        generate_download_report.invoke(
            {
                "uf": "SP",
                "include_executive_summary": False,
                "include_metrics": False,
                "include_charts": False,
                "include_news": False,
            }
        )

        # Verify render was called with correct flags
        call_kwargs = mock_render.call_args[1]
        assert call_kwargs["include_executive_summary"] is False
        assert call_kwargs["include_metrics"] is False
        assert call_kwargs["include_charts"] is False
        assert call_kwargs["include_news"] is False

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_download_report_includes_charts(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test that charts are generated and included."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"type": "scatter"}'
        mock_monthly_chart.invoke.return_value = '{"type": "bar"}'
        mock_render.return_value = "# Report"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 500
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        generate_download_report.invoke(
            {"uf": "SP", "days": 30, "months": 12, "include_charts": True}
        )

        # Verify charts were generated
        assert mock_daily_chart.invoke.called
        assert mock_monthly_chart.invoke.called

        # Verify chart parameters
        daily_call = mock_daily_chart.invoke.call_args[0][0]
        assert daily_call["uf"] == "SP"
        assert daily_call["days"] == 30

        monthly_call = mock_monthly_chart.invoke.call_args[0][0]
        assert monthly_call["uf"] == "SP"
        assert monthly_call["months"] == 12

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_download_report_with_city_code(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test download report with city code."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 10.0},
            "mortality": {"rate": 5.0},
            "icu_occupancy": {"occupancy_rate": 50.0},
            "vaccination": {"covid_rate": 60.0, "flu_rate": 40.0},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'
        mock_render.return_value = "# Report"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 500
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        generate_download_report.invoke(
            {"city_code": "3550308", "days": 30, "months": 12}
        )

        # Verify city code was used
        metrics_call = mock_fetch_metrics.call_args[0]
        assert metrics_call[1] == "3550308"  # city_code parameter

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_download_report_max_news_limit(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test that max_news limits news articles."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = [
            {"title": f"News {i}", "url": f"https://example.com/{i}"} for i in range(5)
        ]
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = "Notícias"
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'
        mock_render.return_value = "# Report"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 500
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        generate_download_report.invoke(
            {"uf": "SP", "max_news": 3, "include_news": True}
        )

        # Verify max_news was passed to _fetch_news
        news_call = mock_fetch_news.call_args
        # Check if it's positional or keyword argument
        if len(news_call[0]) >= 3:
            assert news_call[0][2] == 3  # positional max_results
        else:
            assert news_call[1]["max_results"] == 3  # keyword max_results


class TestGenerateChatReport:
    """Test generate_chat_report tool."""

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_chat_report_basic(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test basic chat report generation."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo executivo"
        mock_metrics_table.return_value = "| Métrica | Valor |"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"type": "scatter", "data": []}'
        mock_monthly_chart.invoke.return_value = '{"type": "bar", "data": []}'

        result = generate_chat_report.invoke(
            {"uf": None, "days": 30, "months": 12, "include_news": False}
        )

        assert "report_text" in result
        assert "daily_chart_json" in result
        assert "monthly_chart_json" in result
        assert "metrics" in result
        assert "news" in result

        # Verify charts are JSON strings
        assert isinstance(result["daily_chart_json"], str)
        assert isinstance(result["monthly_chart_json"], str)

    def test_generate_chat_report_validation_fails(self):
        """Test validation failure."""
        result = generate_chat_report.invoke(
            {"days": 100, "months": 12}  # days too high
        )

        assert "error" in result
        assert result["report_text"] == ""
        assert result["daily_chart_json"] == ""

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_chat_report_includes_charts(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test that chat report includes chart JSONs."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"type": "scatter"}'
        mock_monthly_chart.invoke.return_value = '{"type": "bar"}'

        result = generate_chat_report.invoke({"uf": "SP", "days": 30, "months": 12})

        # Verify charts were generated
        assert mock_daily_chart.invoke.called
        assert mock_monthly_chart.invoke.called

        # Verify chart JSONs are in result
        assert result["daily_chart_json"] == '{"type": "scatter"}'
        assert result["monthly_chart_json"] == '{"type": "bar"}'

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_chat_report_with_news(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test chat report with news included."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = [
            {"title": "Test News", "url": "https://example.com", "content": "Content"}
        ]
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = "- [Test News](https://example.com)"
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'

        result = generate_chat_report.invoke(
            {"uf": "SP", "include_news": True, "max_news": 5}
        )

        # Verify news is in report text
        assert "Test News" in result["report_text"]
        assert result["news"] == [
            {"title": "Test News", "url": "https://example.com", "content": "Content"}
        ]

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_generate_chat_report_customization(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test chat report with user customization."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = ""
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'

        # Test with executive summary disabled
        result = generate_chat_report.invoke(
            {
                "uf": "SP",
                "include_executive_summary": False,
                "include_metrics": True,
            }
        )

        # Verify executive summary is not in report text
        assert "Resumo Executivo" not in result["report_text"]
        # But metrics should be there
        assert "Tabela" in result["report_text"]


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports.validate_report_request")
    def test_generate_download_report_metrics_error(
        self, mock_validate, mock_fetch_metrics
    ):
        """Test handling of metrics fetch error."""
        mock_validate.return_value = (True, "")
        mock_fetch_metrics.side_effect = Exception("Metrics error")

        # Should raise exception or return error
        with pytest.raises(Exception, match="Metrics error"):
            generate_download_report.invoke({"uf": "SP"})

    @patch("tools.reports.validate_report_request")
    def test_generate_download_report_validation_error(self, mock_validate):
        """Test that validation errors are returned."""
        mock_validate.return_value = (False, "Custom validation error")

        result = generate_download_report.invoke({"uf": "SP"})

        assert "error" in result
        assert result["error"] == "Custom validation error"

    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.save_report_to_file")
    def test_generate_download_report_save_error(
        self,
        mock_save,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
    ):
        """Test handling of file save error."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_save.side_effect = PermissionError("Cannot write file")

        # Should handle error gracefully
        with pytest.raises(PermissionError):
            generate_download_report.invoke({"uf": "SP"})


class TestParameterCombinations:
    """Test various parameter combinations."""

    @pytest.mark.parametrize(
        "days,months,expected_valid",
        [
            (7, 1, True),  # Minimum valid
            (90, 24, True),  # Maximum valid
            (30, 12, True),  # Default
            (6, 12, False),  # Days too low
            (91, 12, False),  # Days too high
            (30, 0, False),  # Months too low
            (30, 25, False),  # Months too high
        ],
    )
    def test_parameter_validation_combinations(self, days, months, expected_valid):
        """Test various parameter combinations for validation."""
        result = generate_download_report.invoke({"days": days, "months": months})

        if expected_valid:
            assert "error" not in result or result.get("error") == ""
        else:
            assert "error" in result

    @pytest.mark.parametrize(
        "include_exec,include_met,include_chart,include_news",
        [
            (True, True, True, True),  # All included
            (False, True, True, True),  # No summary
            (True, False, True, True),  # No metrics
            (True, True, False, True),  # No charts
            (True, True, True, False),  # No news
            (False, False, False, False),  # Nothing (should still work)
        ],
    )
    @patch("tools.reports._fetch_all_metrics")
    @patch("tools.reports._fetch_news")
    @patch("tools.reports.generate_executive_summary")
    @patch("tools.reports.format_metrics_table")
    @patch("tools.reports.format_news_section")
    @patch("tools.reports.render_report_template")
    @patch("tools.reports.save_report_to_file")
    @patch("tools.reports.get_daily_chart_json")
    @patch("tools.reports.get_monthly_chart_json")
    def test_customization_combinations(
        self,
        mock_monthly_chart,
        mock_daily_chart,
        mock_save,
        mock_render,
        mock_news_section,
        mock_metrics_table,
        mock_summary,
        mock_fetch_news,
        mock_fetch_metrics,
        include_exec,
        include_met,
        include_chart,
        include_news,
    ):
        """Test all combinations of include flags."""
        mock_fetch_metrics.return_value = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        mock_fetch_news.return_value = []
        mock_summary.return_value = "Resumo"
        mock_metrics_table.return_value = "Tabela"
        mock_news_section.return_value = "Notícias"
        mock_daily_chart.invoke.return_value = '{"data": []}'
        mock_monthly_chart.invoke.return_value = '{"data": []}'
        mock_render.return_value = "# Report"
        mock_file_path = MagicMock(spec=Path)
        mock_file_path.__str__ = lambda self: "/tmp/test.md"
        mock_file_path.__fspath__ = lambda self: "/tmp/test.md"
        mock_stat = MagicMock()
        mock_stat.st_size = 500
        mock_file_path.stat.return_value = mock_stat
        mock_save.return_value = mock_file_path

        result = generate_download_report.invoke(
            {
                "uf": "SP",
                "include_executive_summary": include_exec,
                "include_metrics": include_met,
                "include_charts": include_chart,
                "include_news": include_news,
            }
        )

        # Should always return valid structure
        assert "report_content" in result
        assert "file_path" in result

        # Verify render was called with correct flags
        call_kwargs = mock_render.call_args[1]
        assert call_kwargs["include_executive_summary"] == include_exec
        assert call_kwargs["include_metrics"] == include_met
        assert call_kwargs["include_charts"] == include_chart
        assert call_kwargs["include_news"] == include_news
