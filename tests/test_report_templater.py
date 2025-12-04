"""Comprehensive tests for report templater module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from report.templater import (
    format_metrics_table,
    format_news_section,
    generate_executive_summary,
    generate_metric_explanation,
    render_report_template,
    save_report_to_file,
    validate_report_request,
)


class TestValidation:
    """Test validation functions."""

    def test_validate_report_request_valid(self):
        """Test validation with valid parameters."""
        is_valid, error = validate_report_request(days=30, months=12, max_news=5)
        assert is_valid is True
        assert error == ""

    def test_validate_report_request_days_too_low(self):
        """Test validation with days too low."""
        is_valid, error = validate_report_request(days=5, months=12, max_news=5)
        assert is_valid is False
        assert "7 and 90" in error

    def test_validate_report_request_days_too_high(self):
        """Test validation with days too high."""
        is_valid, error = validate_report_request(days=100, months=12, max_news=5)
        assert is_valid is False
        assert "7 and 90" in error

    def test_validate_report_request_months_too_low(self):
        """Test validation with months too low."""
        is_valid, error = validate_report_request(days=30, months=0, max_news=5)
        assert is_valid is False
        assert "1 and 24" in error

    def test_validate_report_request_months_too_high(self):
        """Test validation with months too high."""
        is_valid, error = validate_report_request(days=30, months=30, max_news=5)
        assert is_valid is False
        assert "1 and 24" in error

    def test_validate_report_request_max_news_too_high(self):
        """Test validation with max_news too high."""
        is_valid, error = validate_report_request(days=30, months=12, max_news=10)
        assert is_valid is False
        assert "5" in error

    def test_validate_report_request_max_news_negative(self):
        """Test validation with negative max_news."""
        is_valid, error = validate_report_request(days=30, months=12, max_news=-1)
        assert is_valid is False
        assert "0-5" in error

    def test_validate_report_request_boundary_values(self):
        """Test validation with boundary values."""
        # Minimum valid
        is_valid, _ = validate_report_request(days=7, months=1, max_news=0)
        assert is_valid is True

        # Maximum valid
        is_valid, _ = validate_report_request(days=90, months=24, max_news=5)
        assert is_valid is True


class TestLLMGeneration:
    """Test LLM-based text generation functions."""

    @patch("report.templater._llm")
    def test_generate_executive_summary(self, mock_llm):
        """Test executive summary generation."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Este é um resumo executivo gerado pelo LLM."
        mock_llm.invoke.return_value = mock_response

        metrics = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        news = []
        location = "Brasil"

        result = generate_executive_summary(metrics, news, location)

        assert result == "Este é um resumo executivo gerado pelo LLM."
        assert mock_llm.invoke.called

    @patch("report.templater._llm")
    def test_generate_executive_summary_with_news(self, mock_llm):
        """Test executive summary generation with news context."""
        mock_response = MagicMock()
        mock_response.content = "Resumo com contexto de notícias."
        mock_llm.invoke.return_value = mock_response

        metrics = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        news = [
            {
                "title": "Test News",
                "content": "This is test news content",
                "url": "https://example.com",
            }
        ]
        location = "São Paulo"

        result = generate_executive_summary(metrics, news, location)

        assert "Resumo com contexto de notícias" in result
        # Verify news was included in prompt
        call_args = mock_llm.invoke.call_args[0][0]
        assert "Test News" in call_args

    @patch("report.templater._llm")
    def test_generate_executive_summary_llm_error(self, mock_llm):
        """Test executive summary fallback on LLM error."""
        mock_llm.invoke.side_effect = Exception("LLM error")

        metrics = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        news = []
        location = "Brasil"

        result = generate_executive_summary(metrics, news, location)

        # Should have fallback text
        assert "Brasil" in result
        assert len(result) > 0

    @patch("report.templater._llm")
    def test_generate_metric_explanation(self, mock_llm):
        """Test metric explanation generation."""
        mock_response = MagicMock()
        mock_response.content = "Esta métrica indica um crescimento moderado."
        mock_llm.invoke.return_value = mock_response

        result = generate_metric_explanation(
            "case_increase_rate",
            15.3,
            {"current_period_cases": 150, "previous_period_cases": 130},
            [],
        )

        assert "crescimento moderado" in result
        assert mock_llm.invoke.called

    @patch("report.templater._llm")
    def test_generate_metric_explanation_with_news(self, mock_llm):
        """Test metric explanation with news context."""
        mock_response = MagicMock()
        mock_response.content = "Explicação com contexto de notícias."
        mock_llm.invoke.return_value = mock_response

        news = [{"title": "Relevant News", "content": "News content"}]

        result = generate_metric_explanation(
            "mortality_rate", 8.7, {"total_deaths": 100, "total_cases": 1150}, news
        )

        assert "Explicação" in result
        # Verify news was included
        call_args = mock_llm.invoke.call_args[0][0]
        assert "Relevant News" in call_args

    @patch("report.templater._llm")
    def test_generate_metric_explanation_llm_error(self, mock_llm):
        """Test metric explanation fallback on LLM error."""
        mock_llm.invoke.side_effect = Exception("LLM error")

        result = generate_metric_explanation(
            "case_increase_rate", 15.3, {}, []
        )

        # Should have fallback explanation
        assert len(result) > 0
        assert "taxa de aumento de casos" in result.lower()


class TestFormatting:
    """Test formatting functions."""

    @patch("report.templater.generate_metric_explanation")
    def test_format_metrics_table(self, mock_explanation):
        """Test metrics table formatting."""
        mock_explanation.return_value = "Explicação de teste"

        metrics = {
            "case_increase": {"rate": 15.3, "current_period_cases": 150},
            "mortality": {"rate": 8.7, "total_deaths": 100},
            "icu_occupancy": {"occupancy_rate": 62.4, "patients_in_icu": 500},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        news = []

        result = format_metrics_table(metrics, news)

        # Should be a table
        assert "| Métrica |" in result
        assert "| Valor |" in result
        assert "| Explicação Contextualizada |" in result

        # Should have all 4 metrics
        assert "Taxa de Aumento de Casos" in result
        assert "Taxa de Mortalidade" in result
        assert "Taxa de Ocupação de UTI" in result
        assert "Taxas de Vacinação" in result

        # Should have values
        assert "15.3%" in result
        assert "8.7%" in result
        assert "62.4%" in result

        # Should call explanation for each metric
        assert mock_explanation.call_count == 4

    def test_format_news_section_empty(self):
        """Test news section formatting with no news."""
        result = format_news_section([], detailed=True)
        assert result == ""

    def test_format_news_section_detailed(self):
        """Test detailed news section formatting."""
        news = [
            {
                "title": "Test News 1",
                "url": "https://example.com/1",
                "date": "2025-12-05",
                "content": "This is test content for news article 1",
            },
            {
                "title": "Test News 2",
                "url": "https://example.com/2",
                "date": "2025-12-04",
                "content": "This is test content for news article 2",
            },
        ]

        result = format_news_section(news, detailed=True)

        assert "## Notícias Recentes" in result
        assert "Test News 1" in result
        assert "Test News 2" in result
        assert "https://example.com/1" in result
        assert "2025-12-05" in result

    def test_format_news_section_brief(self):
        """Test brief news section formatting."""
        news = [
            {
                "title": "Test News",
                "url": "https://example.com",
                "date": "2025-12-05",
                "content": "Content",
            }
        ]

        result = format_news_section(news, detailed=False)

        assert "Test News" in result
        assert "https://example.com" in result
        # Should be link format
        assert "[Test News]" in result


class TestTemplateRendering:
    """Test template rendering."""

    def test_render_report_template_all_sections(self):
        """Test rendering with all sections."""
        result = render_report_template(
            location="Brasil",
            executive_summary="Resumo executivo",
            metrics_table="| Métrica | Valor |",
            charts_section="Gráficos aqui",
            news_section="Notícias aqui",
            include_executive_summary=True,
            include_metrics=True,
            include_charts=True,
            include_news=True,
        )

        assert "# Relatório SRAG — Brasil" in result
        assert "Resumo Executivo" in result
        assert "Resumo executivo" in result
        assert "Métricas Principais" in result
        assert "Visualizações" in result
        assert "Gráficos aqui" in result
        assert "Notícias aqui" in result

    def test_render_report_template_selective_sections(self):
        """Test rendering with selective sections."""
        result = render_report_template(
            location="São Paulo",
            executive_summary="Resumo",
            metrics_table="Tabela",
            charts_section="Gráficos",
            news_section="Notícias",
            include_executive_summary=False,
            include_metrics=True,
            include_charts=False,
            include_news=False,
        )

        assert "# Relatório SRAG — São Paulo" in result
        assert "Resumo Executivo" not in result
        assert "Métricas Principais" in result
        assert "Visualizações" not in result
        assert "Notícias" not in result

    def test_render_report_template_no_news_when_empty(self):
        """Test that news section is not included when empty."""
        result = render_report_template(
            location="Brasil",
            executive_summary="Resumo",
            metrics_table="Tabela",
            charts_section="Gráficos",
            news_section="",  # Empty
            include_executive_summary=True,
            include_metrics=True,
            include_charts=True,
            include_news=True,
        )

        # News section should not appear if empty
        assert "Notícias Recentes" not in result


class TestFileOperations:
    """Test file save operations."""

    def test_save_report_to_file(self, tmp_path):
        """Test saving report to file."""
        content = "# Test Report\n\nThis is test content."
        location = "Test Location"

        file_path = save_report_to_file(content, location, output_dir=tmp_path)

        assert file_path.exists()
        assert file_path.suffix == ".md"
        assert "relatorio_srag" in file_path.name.lower()
        assert "test_location" in file_path.name.lower()

        # Verify content
        saved_content = file_path.read_text(encoding="utf-8")
        assert saved_content == content

    def test_save_report_to_file_creates_directory(self, tmp_path):
        """Test that directory is created if it doesn't exist."""
        output_dir = tmp_path / "reports" / "subdir"
        content = "# Test"
        location = "Test"

        file_path = save_report_to_file(content, location, output_dir=output_dir)

        assert output_dir.exists()
        assert file_path.exists()

    def test_save_report_to_file_sanitizes_location(self, tmp_path):
        """Test that location name is sanitized in filename."""
        content = "# Test"
        location = "São Paulo/SP"  # Has special characters

        file_path = save_report_to_file(content, location, output_dir=tmp_path)

        # Should sanitize / and spaces
        assert "/" not in file_path.name
        assert " " not in file_path.name or "_" in file_path.name

    def test_save_report_to_file_default_directory(self):
        """Test saving with default directory."""
        content = "# Test Report"
        location = "Brasil"

        # This will create reports/ in project root
        file_path = save_report_to_file(content, location)

        assert file_path.exists()
        assert file_path.suffix == ".md"

        # Cleanup
        file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()


class TestIntegration:
    """Integration tests combining multiple functions."""

    @patch("report.templater._llm")
    def test_full_report_generation_flow(self, mock_llm):
        """Test complete report generation flow."""
        # Mock LLM responses
        mock_summary = MagicMock()
        mock_summary.content = "Resumo executivo completo."
        mock_explanation = MagicMock()
        mock_explanation.content = "Explicação contextualizada."

        mock_llm.invoke.return_value = mock_explanation

        metrics = {
            "case_increase": {"rate": 15.3},
            "mortality": {"rate": 8.7},
            "icu_occupancy": {"occupancy_rate": 62.4},
            "vaccination": {"covid_rate": 71.2, "flu_rate": 45.2},
        }
        news = [{"title": "News", "url": "https://example.com", "content": "Content"}]

        # Generate summary (using mocked LLM)
        summary = generate_executive_summary(metrics, news, "Brasil")

        # Format table
        table = format_metrics_table(metrics, news)

        # Format news
        news_section = format_news_section(news, detailed=True)

        # Render template
        report = render_report_template(
            location="Brasil",
            executive_summary=summary,
            metrics_table=table,
            charts_section="Gráficos",
            news_section=news_section,
        )

        # Verify complete report
        assert "# Relatório SRAG — Brasil" in report
        assert "Resumo Executivo" in report
        assert "Métricas Principais" in report
        assert "News" in report
        # The summary should contain the mocked content
        assert "Explicação contextualizada" in report or "Resumo executivo completo" in report

